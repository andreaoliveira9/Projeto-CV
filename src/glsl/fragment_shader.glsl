#version 330

precision highp float;
uniform vec2 u_resolution;  // Width and height of the shader

#define M_PI 3.14159265358979
#define MAX_STEPS 100
#define MAX_DIST 100.
#define MIN_DIST .01
const vec3 BACKGROUND_COLOR = vec3(1.0, 0.0, 0.0);

out vec4 fragColor;  // Declare an output variable

float sphereSDF(vec3 p) {
    vec4 sphere = vec4(0.0, 1.0, 6.0, 1);
    float dist = length(p - sphere.xyz) - sphere.w;
    return dist;
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

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / u_resolution.y;
    vec3 ro = vec3(0, 1, 0); // Ray Origin/Camera
    vec3 rd = normalize(vec3(uv.x, uv.y, 1));
    float d = RayMarch(ro, rd); // Distance
    d /= 10.0;
    vec3 color = vec3(d);

    // Set the output color
    if (d > 4) {
        color = BACKGROUND_COLOR;
    }

    fragColor = vec4(color, 1.0);  // Use the output variable
}