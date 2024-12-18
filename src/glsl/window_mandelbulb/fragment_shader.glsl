#version 330

precision highp float;

uniform vec2 u_resolution;        // Tamanho da janela
uniform vec3 u_camera_position;   // Posição da câmera
uniform vec2 u_camera_rotation;   // Rotação da câmera (pitch e yaw)

uniform float power;
uniform float darkness;
uniform float blackAndWhite;
uniform vec3 colourAMix;
uniform vec3 colourBMix;
uniform int plusIteration;

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

vec2 SceneInfo(vec3 position) {
    vec3 z = position;
    float dr = 1.0;
    float r = 0.0;
    int iterations = 0;

    for (int i = 0; i < 50; i++) {
        iterations = i;
        r = length(z);

        if (r > 2.0) {
            break;
        }

        // convert to polar coordinates
        float theta = acos(z.z / r);
        float phi = atan(z.y, z.x);
        dr = pow(r, power - 1.0) * power * dr + 1.0;

        // scale and rotate the point
        float zr = pow(r, power);
        theta = theta * power;
        phi = phi * power;

        // convert back to cartesian coordinates
        z = zr * vec3(sin(theta) * cos(phi), sin(phi) * sin(theta), cos(theta));
        z += position;
    }
    float dst = 0.5 * log(r) * r / dr;
    return vec2(iterations, dst);
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

    vec4 result = mix(vec4(65.0 / 255.0, 3.0 / 255.0, 79.0 / 255.0, 1.0), vec4(16.0 / 255.0, 6.0 / 255.0, 28.0 / 255.0, 1.0), uv.y);

    Ray ray = CreateCameraRay(uv * 2.0 - 1.0);

    float rayDst = 0.0;
    int stepCount = 0;

    while (rayDst < maxDst && stepCount < maxStepCount) {
        stepCount++;
        vec2 sceneInfo = SceneInfo(ray.origin);
        float dst = sceneInfo.y;

        if (dst < epsilon) {
            float escapeIteration = sceneInfo.x;
            vec3 normal = EstimateNormal(ray.origin - ray.direction * epsilon * 2.0);

            float colourA = clamp(dot(normal * 0.5 + 0.5, -vec3(1.0, 1.0, 1.0)), 0.0, 1.0);
            float colourB = clamp(escapeIteration / 16.0, 0.0, 1.0);

            vec3 colour = clamp(colourA * colourAMix + colourB * colourBMix, 0.0, 1.0);
            result = vec4(colour, 1.0);
            break;
        }
        ray.origin += ray.direction * dst;
        rayDst += dst;
    }
    float rim = float(stepCount) / darkness;
    fragColor = mix(result, vec4(1.0), blackAndWhite) * rim;
}