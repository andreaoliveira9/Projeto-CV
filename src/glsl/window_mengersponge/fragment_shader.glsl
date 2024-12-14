#version 330

precision highp float;

uniform vec2 u_resolution;        // Tamanho da janela
uniform vec3 u_camera_position;   // Posição da câmera
uniform vec2 u_camera_rotation;   // Rotação da câmera (pitch e yaw)

uniform float darkness;
uniform float blackAndWhite;
uniform vec3 colourAMix;
uniform vec3 colourBMix;

const float epsilon = 0.001f;
const float maxDst = 200.0;
const int maxStepCount = 250;

struct Ray {
    vec3 origin;
    vec3 direction;
};

Ray CreateRay(vec3 origin, vec3 direction) {
    Ray ray;
    ray.origin = origin;
    ray.direction = direction;
    return ray;
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

Ray CreateCameraRay(vec2 uv) {
    vec3 origin = u_camera_position;
    mat3 rot = rotationMatrix(u_camera_rotation.x, u_camera_rotation.y);
    vec3 direction = normalize(rot * vec3(uv, 1.0));
    return CreateRay(origin, direction);
}

float MengerSpongeSDF(vec3 p) {
    float scale = 3.0;
    vec3 q = abs(p);

    for (int i = 0; i < 5; i++) {
        if (q.x < q.z) q.xz = q.zx;
        if (q.y < q.z) q.yz = q.zy;
        q = abs(q);
        q = scale * q - vec3(scale - 1.0);

        if (q.x > q.z) q.xz = q.zx;
        if (q.y > q.z) q.yz = q.zy;
    }

    return length(q) / pow(scale, 5.0);
}

vec2 SceneInfo(vec3 position) {
    float sdf = MengerSpongeSDF(position);
    return vec2(0.0, sdf); // Aqui, o primeiro elemento poderia ser usado para iteração/coloração.
}

vec3 EstimateNormal(vec3 p) {
    float x = SceneInfo(vec3(p.x + epsilon, p.y, p.z)).y - SceneInfo(vec3(p.x - epsilon, p.y, p.z)).y;
    float y = SceneInfo(vec3(p.x, p.y + epsilon, p.z)).y - SceneInfo(vec3(p.x, p.y - epsilon, p.z)).y;
    float z = SceneInfo(vec3(p.x, p.y, p.z + epsilon)).y - SceneInfo(vec3(p.x, p.y, p.z - epsilon)).y;
    return normalize(vec3(x, y, z));
}

out vec4 fragColor;

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution;

    vec4 result = mix(vec4(0.1, 0.1, 0.3, 1.0), vec4(0.3, 0.1, 0.1, 1.0), uv.y);

    Ray ray = CreateCameraRay(uv * 2.0 - 1.0);

    float rayDst = 0.0;
    int stepCount = 0;

    while (rayDst < maxDst && stepCount < maxStepCount) {
        stepCount++;
        vec2 sceneInfo = SceneInfo(ray.origin);
        float dst = sceneInfo.y;

        if (dst < epsilon) {
            vec3 normal = EstimateNormal(ray.origin);
            float lighting = clamp(dot(normal, normalize(vec3(-1.0, 1.0, -1.0))), 0.0, 1.0);

            vec3 colour = mix(colourAMix, colourBMix, lighting);

            result = vec4(colour, 1.0);
            break;
        }
        ray.origin += ray.direction * dst;
        rayDst += dst;
    }
    float rim = float(stepCount) / darkness;
    fragColor = mix(result, vec4(1.0), blackAndWhite) * rim;
}