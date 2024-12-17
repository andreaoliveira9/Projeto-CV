#version 330

precision highp float;

uniform vec2 u_resolution;        // Tamanho da janela
uniform vec3 u_camera_position;   // Posição da câmera
uniform vec2 u_camera_rotation;   // Rotação da câmera (pitch e yaw)
uniform float u_time;             // Tempo em segundos

#define M_PI 3.14159265358979
#define MAX_STEPS 100
#define MAX_DIST 100.0
#define MIN_DIST 0.01

out vec4 fragColor;  // Cor final do fragmento

// Constantes
const vec3 background_color = vec3(0.5); 
const vec3 global_light_dir = normalize(vec3(10.0, 10.0, 0.0));
const float epsilon = 0.001;

// Estrutura e funções SDF
float sphereSDF(vec3 p, vec3 center, float radius) {
    return length(p - center) - radius;
}

float roundedBoxSDF(vec3 p, vec3 b, float r) {
    vec3 q = abs(p) - b;
    return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0) - r;
}

// Cena: retorna cor e distância para mask
vec4 sceneDistColor(vec3 p) {
    // Primitivas:
    float sphere1 = sphereSDF(p, vec3(sin(u_time)*2.0, 1.0, 6.0), 1.0);
    vec3 colSphere1 = vec3(1.0, 0.0, 0.0);

    float sphere2 = sphereSDF(p, vec3(-2.0, 1.0, 4.0), 1.0);
    vec3 colSphere2 = vec3(0.0, 0.0, 1.0);

    float cube = roundedBoxSDF(p - vec3(2.0, 1.0, 6.0), vec3(1.0), 0.2);
    vec3 colCube = vec3(0.0, 1.0, 0.0);

    // Determinação por proximidade (masking)
    float minDist = sphere1;
    vec3 finalColor = colSphere1;

    if (sphere2 < minDist) {
        minDist = sphere2;
        finalColor = colSphere2;
    }

    if (cube < minDist) {
        minDist = cube;
        finalColor = colCube;
    }

    return vec4(finalColor, minDist);
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
float CalculateShadow(Ray ray, float dstToShadePoint) {
    float rayDst = 0.0;
    float shadowIntensity = 0.7;
    float brightness = 300.0;

    for (int i = 0; i < MAX_STEPS && rayDst < dstToShadePoint; i++){
        vec3 p = ray.origin + ray.direction * rayDst;
        float dist = sceneSDF(p);
        if (dist < epsilon) {
            return shadowIntensity;
        }
        brightness = min(brightness, dist * 200.0);
        rayDst += dist;
    }
    return shadowIntensity + (1.0 - shadowIntensity) * brightness;
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
        vec3 offset = p + normal * epsilon;
        vec3 dirToLight = normalize(global_light_dir - offset);
        Ray shadowRay;
        shadowRay.origin = offset;
        shadowRay.direction = dirToLight;

        float dstToLight = distance(offset, global_light_dir);
        float shadow = CalculateShadow(shadowRay, dstToLight);

        float diff = max(dot(normal, normalize(global_light_dir)), 0.0);
        color *= shadow * diff;
    }

    fragColor = vec4(color, 1.0);
}