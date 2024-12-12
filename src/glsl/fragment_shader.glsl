#version 330

precision highp float;

uniform vec2 u_resolution;        // Tamanho da janela
uniform vec3 u_camera_position;   // Posição da câmera
uniform vec2 u_camera_rotation;   // Rotação da câmera (pitch e yaw)
uniform float u_time;             // Tempo em segundos
uniform float u_blend_strength;   // Força do smooth blending (novo uniforme)

#define M_PI 3.14159265358979
#define MAX_STEPS 100
#define MAX_DIST 100.
#define MIN_DIST .01

out vec4 fragColor;  // Cor final do fragmento

// Constantes
const vec3 background_color = vec3(0.5);  // Fundo preto

// Função SDF para uma esfera
float sphereSDF(vec3 p, vec3 center, float radius) {
    return length(p - center) - radius;
}

// Função SDF para um cubo arredondado
float roundedBoxSDF(vec3 p, vec3 b, float r) {
    vec3 q = abs(p) - b;
    return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0) - r;
}

// Combina SDFs usando união suave
float smoothUnionSDF(float d1, float d2, float k) {
    float h = clamp(0.5 + 0.5 * (d2 - d1) / k, 0.0, 1.0);
    return mix(d2, d1, h) - k * h * (1.0 - h);
}

// Cena com múltiplos objetos
float sceneSDF(vec3 p) {
    // Esferas
    float sphere1 = sphereSDF(p, vec3(sin(u_time) * 2.0, 1.0, 6.0), 1.0);  // Esfera móvel
    float sphere2 = sphereSDF(p, vec3(-2.0, 1.0, 4.0), 1.0);              // Esfera fixa

    // Cubo arredondado
    float cube = roundedBoxSDF(p - vec3(2.0, 1.0, 6.0), vec3(1.0), 0.2);

    // Combina os objetos com união suave usando u_blend_strength
    float blend1 = smoothUnionSDF(sphere1, sphere2, u_blend_strength);  // Mistura das esferas
    return smoothUnionSDF(blend1, cube, u_blend_strength);              // Mistura com o cubo
}

// Calcula a normal da superfície no ponto p
vec3 calculateNormal(vec3 p) {
    const vec2 e = vec2(0.001, 0.0);
    return normalize(vec3(
        sceneSDF(p + e.xyy) - sceneSDF(p - e.xyy),
        sceneSDF(p + e.yxy) - sceneSDF(p - e.yxy),
        sceneSDF(p + e.yyx) - sceneSDF(p - e.yyx)
    ));
}

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

// Cria a matriz de rotação a partir do pitch e yaw
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

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / u_resolution.y;
    vec3 ro = u_camera_position;

    // Direção da câmera
    mat3 rot = rotationMatrix(u_camera_rotation.x, u_camera_rotation.y);
    vec3 rd = normalize(rot * vec3(uv, 1.0));

    // Ray marching
    float d = RayMarch(ro, rd);
    vec3 color = background_color;

    if (d < MAX_DIST) {
        vec3 p = ro + rd * d;  // Ponto de interseção
        vec3 normal = calculateNormal(p);  // Normal da superfície
        vec3 light_position = ro + rot * vec3(2.0, 4.0, 2.0);  // Luz acima da câmera
        vec3 light_dir = normalize(light_position - p);
        float diff = max(dot(normal, light_dir), 0.0);

        // Cor básica com iluminação
        color = vec3(diff);
    }

    fragColor = vec4(color, 1.0);
}