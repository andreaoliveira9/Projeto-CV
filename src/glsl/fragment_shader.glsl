#version 330

precision highp float;

uniform vec2 u_resolution;        // Tamanho da janela
uniform vec3 u_camera_position;   // Posição da câmera
uniform vec2 u_camera_rotation;   // Rotação da câmera (pitch e yaw)
uniform float u_time;             // Tempo em segundos

#define M_PI 3.14159265358979
#define MAX_STEPS 100
#define MAX_DIST 100.
#define MIN_DIST .01

out vec4 fragColor;  // Cor final do fragmento

// Constantes para iluminação
const vec3 sphere_color = vec3(1.0, 0.0, 0.0);    // Cor da esfera (vermelho)
const vec3 background_color = vec3(0.5);          // Fundo preto

// Função para calcular a posição dinâmica da esfera
vec3 movingSpherePosition() {
    float x = sin(u_time) * 2.0;  // Oscila entre -2 e 2 no eixo X
    return vec3(x, 1.0, 6.0);     // Posição dinâmica da esfera
}

float sphereSDF(vec3 p) {
    vec3 sphere_pos = movingSpherePosition();  // Posição da esfera
    float dist = length(p - sphere_pos) - 1.0; // Raio da esfera é 1.0
    return dist;
}

// Calcula a normal da superfície no ponto p
vec3 calculateNormal(vec3 p) {
    const vec2 e = vec2(0.001, 0.0);
    return normalize(vec3(
        sphereSDF(p + e.xyy) - sphereSDF(p - e.xyy),
        sphereSDF(p + e.yxy) - sphereSDF(p - e.yxy),
        sphereSDF(p + e.yyx) - sphereSDF(p - e.yyx)
    ));
}

float RayMarch(vec3 ro, vec3 rd) {
    float d0 = 0.0;
    for (int i = 0; i < MAX_STEPS; i++) {
        vec3 p = ro + rd * d0;
        float d1 = sphereSDF(p);
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

    // Posição da luz baseada na câmera
    vec3 light_position = ro + rot * vec3(2.0, 0.0, 0.0);  // Luz deslocada para o lado

    // Ray marching
    float d = RayMarch(ro, rd);
    vec3 color = background_color;

    if (d < MAX_DIST) {
        vec3 p = ro + rd * d;  // Ponto de interseção
        vec3 normal = calculateNormal(p);  // Normal da superfície
        vec3 light_dir = normalize(light_position - p);  // Direção da luz
        float diff = max(dot(normal, light_dir), 0.0);  // Iluminação difusa

        // Combina a iluminação com a cor da esfera
        color = sphere_color * diff;
    }

    fragColor = vec4(color, 1.0);
}