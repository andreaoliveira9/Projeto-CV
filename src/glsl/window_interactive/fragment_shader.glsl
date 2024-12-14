#version 330

precision highp float;

uniform vec2 u_resolution;
uniform vec3 u_camera_position;
uniform vec2 u_camera_rotation;
uniform float u_time;
uniform float u_blend_strength;

#define MAX_PRIMITIVES 32

struct Primitive {
    int id;             // ID único
    int type;           // 0 = esfera, 1 = cubo arredondado
    vec3 position;      // Posição
    vec3 scale;         // Escala ou tamanho
    float radius;       // Raio (para esferas ou borda arredondada de cubos)
};

uniform Primitive u_primitives[MAX_PRIMITIVES];
uniform int u_primitive_count;

#define M_PI 3.14159265358979
#define MAX_STEPS 100
#define MAX_DIST 100.
#define MIN_DIST .01

out vec4 fragColor;

const vec3 background_color = vec3(0.5);

float sphereSDF(vec3 p, vec3 center, float radius) {
    return length(p - center) - radius;
}

float roundedBoxSDF(vec3 p, vec3 b, float r) {
    vec3 q = abs(p) - b;
    return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0) - r;
}

float smoothUnionSDF(float d1, float d2, float k) {
    float h = clamp(0.5 + 0.5 * (d2 - d1) / k, 0.0, 1.0);
    return mix(d2, d1, h) - k * h * (1.0 - h);
}

vec2 sceneSDF(vec3 p) {
    float dist = MAX_DIST;
    int hitID = -1;

    for (int i = 0; i < u_primitive_count; i++) {
        Primitive prim = u_primitives[i];
        float d;

        if (prim.type == 0) {
            d = sphereSDF(p, prim.position, prim.radius); 
        } else if (prim.type == 1) {
            d = roundedBoxSDF(p - prim.position, vec3(1.0), prim.radius);
        } else {
            continue;
        }

        if (i == 0) {
            dist = d;  // Inicializa a distância
            hitID = prim.id;
        } else {
            float prevDist = dist;
            dist = smoothUnionSDF(dist, d, u_blend_strength);
            
            // Atualiza o ID apenas se a primitiva atual estiver mais próxima
            if (d < prevDist) {
                hitID = prim.id;
            }
        }
    }

    return vec2(dist, float(hitID));
}

vec3 calculateNormal(vec3 p) {
    const vec2 e = vec2(0.001, 0.0);
    return normalize(vec3(
        sceneSDF(p + e.xyy).x - sceneSDF(p - e.xyy).x,
        sceneSDF(p + e.yxy).x - sceneSDF(p - e.yxy).x,
        sceneSDF(p + e.yyx).x - sceneSDF(p - e.yyx).x
    ));
}

vec2 RayMarch(vec3 ro, vec3 rd) {
    float d0 = 0.0;
    int hitID = -1;

    for (int i = 0; i < MAX_STEPS; i++) {
        vec3 p = ro + rd * d0;
        vec2 scene = sceneSDF(p);
        d0 += scene.x;
        hitID = int(scene.y);
        if (scene.x < MIN_DIST || d0 > MAX_DIST) break;
    }

    return vec2(d0, float(hitID));
}

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

    mat3 rot = rotationMatrix(u_camera_rotation.x, u_camera_rotation.y);
    vec3 rd = normalize(rot * vec3(uv, 1.0));

    vec2 rayResult = RayMarch(ro, rd);
    float d = rayResult.x;
    int hitID = int(rayResult.y);
    vec3 color = background_color;

    if (d < MAX_DIST) {
        vec3 p = ro + rd * d;
        vec3 normal = calculateNormal(p);
        vec3 light_position = ro + rot * vec3(2.0, 4.0, 2.0);
        vec3 light_dir = normalize(light_position - p);
        float diff = max(dot(normal, light_dir), 0.0);

        color = vec3(diff);
    }

    fragColor = vec4(color, float(hitID) / 255.0);  // Corrigido: combina cor e ID no alfa
}