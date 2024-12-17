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
const vec3 background_color = vec3(0.5);  // Fundo cinza
// Função SDF para uma esfera
float sphereSDF(vec3 p, vec3 center, float radius) {
    return length(p - center) - radius;
}

// Função SDF para um cubo arredondado
float roundedBoxSDF(vec3 p, vec3 b, float r) {
    vec3 q = abs(p) - b;
    return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0) - r;
}

// Blend Suave
vec4 Blend( float a, float b, vec3 colA, vec3 colB, float k )
{
    float h = clamp( 0.5+0.5*(b - a)/k, 0.0, 1.0 );
    float blendDst = mix( b, a, h ) - k*h*(1.0-h);
    vec3 blendCol = mix(colB,colA,h);
    return vec4(blendCol, blendDst);
}

// Retorna cor e distância combinadas da cena
vec4 sceneDistColor(vec3 p) {
    // Definindo as primitivas e suas cores
    // Esfera móvel (vermelha)
    float sphere1 = sphereSDF(p, vec3(sin(u_time)*2.0, 1.0, 6.0), 1.0);
    vec3  colSphere1 = vec3(1.0, 0.0, 0.0);

    // Esfera fixa (azul)
    float sphere2 = sphereSDF(p, vec3(-2.0, 1.0, 4.0), 1.0);
    vec3 colSphere2 = vec3(0.0, 0.0, 1.0);

    // Cubo arredondado (verde)
    float cube = roundedBoxSDF(p - vec3(2.0,1.0,6.0), vec3(1.0), 0.2);
    vec3 colCube = vec3(0.0, 1.0, 0.0);

    // Combina esfera1 e cubo (união suave)
    vec4 blend1 = Blend(sphere1, cube, colSphere1, colCube, u_blend_strength);
    // blend1.xyz = cor combinada, blend1.w = distancia combinada

    // Combina com esfera2 (amarelo quando mesclado)
    // Vamos supor que a segunda fusão seja esfera2 com o resultado anterior,
    // resultando em algo entre azul e a cor resultante do primeiro blend.
    vec4 finalBlend = Blend(sphere2, blend1.w, colSphere2, blend1.xyz, u_blend_strength);

    // finalBlend.xyz = cor final combinada
    // finalBlend.w = distância final combinada
    return finalBlend;
}

// Função original sceneSDF retorna apenas a distância, para uso em cálculo de normais etc.
float sceneSDF(vec3 p) {
    return sceneDistColor(p).w;
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

        // Obter a cor naquele ponto (chamar sceneDistColor novamente)
        vec4 sceneInfo = sceneDistColor(p);
        color = sceneInfo.xyz; // cor resultante da combinação das primitivas

        // Luz simples
        vec3 light_position = ro + rot * vec3(2.0, 4.0, 2.0);  
        vec3 light_dir = normalize(light_position - p);
        float diff = max(dot(normal, light_dir), 0.0);

        // Aplica iluminação sobre a cor da superfície
        color *= diff;
    }

    fragColor = vec4(color, 1.0);
}