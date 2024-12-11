#version 330

uniform vec2 u_resolution;

void main() {
    // Normalize the fragment coordinates
    vec2 uv = gl_FragCoord.xy / u_resolution;

    // Use the normalized coordinates to set the color
    vec3 color = vec3(uv, 0.5);

    gl_FragColor = vec4(color, 1.0);
}