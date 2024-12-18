#version 330

precision highp float;

uniform vec2 u_resolution;        // Tamanho da janela
uniform vec3 u_camera_position;   // Posição da câmera
uniform vec2 u_camera_rotation;   // Rotação da câmera (pitch e yaw)
uniform float u_time;             // Tempo em segundos
uniform float u_blend_strength;   // Força do smooth blending
uniform float u_shadow_intensity; // Intensidade da sombra
uniform float u_brightness;       // Brilho da cena

#define M_PI 3.14159265358979
#define MAX_STEPS 100
#define MAX_DIST 100.0
#define MIN_DIST 0.01

out vec4 fragColor;  // Cor final do fragmento

// Constantes
const vec3 background_color = vec3(0.5); 
const vec3 global_light_dir = normalize(vec3(0.0, 10.0, 0.0));
const float epsilon = 0.001;

// Estrutura e funções SDF
float sphereSDF(vec3 p, vec3 center, float radius) {
    return length(p - center) - radius;
}

float roundedBoxSDF(vec3 p, vec3 b, float r) {
    vec3 q = abs(p) - b;
    return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0) - r;
}

// Função de blend suave de distâncias e cores
vec4 Blend(float a, float b, vec3 colA, vec3 colB, float k) {
    float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0);
    float blendDst = mix(b, a, h) - k * h * (1.0 - h);
    vec3 blendCol = mix(colB, colA, h);
    return vec4(blendCol, blendDst);
}

// Cena: retorna cor e distância
vec4 sceneDistColor(vec3 p) {
    // Primitivas:
    float sphere1 = sphereSDF(p, vec3(sin(u_time) * 2.0, 1.0, 6.0), 1.0);
    vec3 colSphere1 = vec3(1.0, 0.0, 0.0);

    float sphere2 = sphereSDF(p, vec3(-2.0, 1.0, 8.0), 1.0);
    vec3 colSphere2 = vec3(0.0, 0.0, 1.0);

    float sphere3 = sphereSDF(p, vec3(cos(u_time) * 2.0, 6.0, 6.0), 1.0);
    vec3 colSphere3 = vec3(0.0, 1.0, 0.5);

    float cube1 = roundedBoxSDF(p - vec3(2.0, 1.0, 6.0), vec3(1.0), 0.2);
    vec3 colCube1 = vec3(0.0, 1.0, 0.0);

    float cube2 = roundedBoxSDF(p - vec3(-2.0, -3.0, 6.0), vec3(1.0), 0.2);
    vec3 colCube2 = vec3(1.0, 1.0, 0.0);

    // Primeiro blend entre esfera1 e cubo1
    vec4 blend1 = Blend(sphere1, cube1, colSphere1, colCube1, u_blend_strength);

    // Segundo blend com esfera2
    vec4 blend2 = Blend(sphere2, blend1.w, colSphere2, blend1.xyz, u_blend_strength);

    // Terceiro blend com cube2
    vec4 blend3 = Blend(cube2, blend2.w, colCube2, blend2.xyz, u_blend_strength);

    // Quarto blend com esfera3
    vec4 finalBlend = Blend(sphere3, blend3.w, colSphere3, blend3.xyz, u_blend_strength);

    return finalBlend; // finalBlend.xyz = cor, finalBlend.w = distancia
}

// Apenas distância para cálculo de normal e raymarch
float sceneSDF(vec3 p) {
    return sceneDistColor(p).w;
}

// Cálculo da normal no ponto p
vec3 calculateNormal(vec3 p) {
    const vec2 e = vec2(0.001, 0.0);
    return normalize(vec3(
        sceneSDF(p + e.xyy) - sceneSDF(p - e.xyy),
        sceneSDF(p + e.yxy) - sceneSDF(p - e.yxy),
        sceneSDF(p + e.yyx) - sceneSDF(p - e.yyx)
    ));
}

// Raymarch simples
float RayMarch(vec3 ro, vec3 rd) {
    float d0 = 0.0;
    for (int i = 0; i < MAX_STEPS; i++) {
        vec3 p = ro + rd * d0;
        float d1 = sceneSDF(p);
        d0 += d1;
        if (d1 < MIN_DIST || d0 > MAX_DIST) break;
    }
    return d0;
}

// Estrutura de raio
struct Ray {
    vec3 origin;
    vec3 direction;
};

mat3 rotationMatrix(float pitch, float yaw) {
    float cp = cos(pitch);
    float sp = sin(pitch);
    float cy = cos(yaw);
    float sy = sin(yaw);

    return mat3(
        vec3(cy, 0, -sy),
        vec3(sp * sy, cp, sp * cy),
        vec3(cp * sy, -sp, cp * cy)
    );
}

// Cria o raio da câmera
Ray CreateCameraRay(vec2 uv) {
    vec3 ro = u_camera_position;
    mat3 rot = rotationMatrix(u_camera_rotation.x, u_camera_rotation.y);
    vec3 rd = normalize(rot * vec3(uv, 1.0));
    Ray r;
    r.origin = ro;
    r.direction = rd;
    return r;
}

// Cálculo de sombras simplificado
float CalculateShadow(vec3 p, vec3 lightDir) {
    float rayDst = 0.0;
    float shadowFactor = 1.0; // Começa sem sombra

    // Raymarch do ponto até a luz
    for (int i = 0; i < MAX_STEPS; i++) {
        vec3 samplePoint = p + lightDir * rayDst;
        float dist = sceneSDF(samplePoint);

        // Se encontramos um objeto entre o ponto e a luz
        if (dist < epsilon) {
            return 1 - u_shadow_intensity; // Sombra total
        }

        // Atenuação baseada na distância até o objeto
        shadowFactor = min(shadowFactor, 10.0 * dist / rayDst);

        rayDst += dist;

        // Se o raio ultrapassar a luz, paramos
        if (rayDst >= MAX_DIST) {
            break;
        }
    }

    return mix(1 - u_shadow_intensity, 1.0, shadowFactor); // Sombra parcial
}

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / u_resolution.y;
    Ray ray = CreateCameraRay(uv);

    // Realiza o raymarch
    float d = RayMarch(ray.origin, ray.direction);
    vec3 color = background_color;

    if (d < MAX_DIST) {
        vec3 p = ray.origin + ray.direction * d;
        vec3 normal = calculateNormal(p);

        // Obtém cor da superfície
        vec4 sceneInfo = sceneDistColor(p);
        color = sceneInfo.xyz;

        // Iluminação simples
        vec3 offset = p + normal * epsilon; // Evita auto-interseção
        vec3 dirToLight = normalize(global_light_dir);

        // Calcular sombra
        float shadow = CalculateShadow(offset, dirToLight);

        // Iluminação difusa
        float diff = max(dot(normal, dirToLight), 0.0);
        color *= shadow * diff;
    }

    // Ajuste de brilho
    color *= u_brightness;

    fragColor = vec4(color, 1.0);
}