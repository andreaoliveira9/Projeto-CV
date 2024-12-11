import glfw
from OpenGL.GL import *
import numpy as np
from dsf import Sphere, Cube
from numba import jit


@jit(nopython=True)
def norm(vector):
    return np.sqrt(np.sum(vector**2))


@jit(nopython=True)
def calculate_distance(
    point, object_positions, object_sizes, object_colors, object_types
):
    """
    Calcula a menor distância do ponto até os objetos na cena.

    :param point: Posição atual (np.ndarray).
    :param object_positions: Array de posições dos objetos.
    :param object_sizes: Array de tamanhos/raios dos objetos.
    :param object_colors: Array de cores dos objetos.
    :param object_types: Array de tipos dos objetos (0=sphere, 1=cube).
    :return: (distância mínima, cor do objeto mais próximo).
    """
    min_distance = float("inf")
    color = np.array([0.0, 0.0, 0.0])  # Cor de fundo

    for i in range(len(object_positions)):
        if object_types[i] == 0:  # Sphere
            dist = norm(point - object_positions[i]) - object_sizes[i]
        elif object_types[i] == 1:  # Cube
            half_size = np.array([object_sizes[i] / 2] * 3)
            delta = np.abs(point - object_positions[i]) - half_size
            outside = np.sqrt(np.sum(np.maximum(delta, 0) ** 2))
            inside = np.max(np.minimum(delta, 0))
            dist = outside + inside
        else:
            continue

        if dist < min_distance:
            min_distance = dist
            color = object_colors[i]

    return min_distance, color


@jit(nopython=True)
def estimate_normal(
    point, object_positions, object_sizes, object_types, object_colors, epsilon
):
    """
    Estima a normal da superfície em um ponto.

    :param point: Ponto na superfície (np.ndarray).
    :param object_positions: Array de posições dos objetos.
    :param object_sizes: Array de tamanhos/raios dos objetos.
    :param object_types: Array de tipos dos objetos (0=sphere, 1=cube).
    :param object_colors: Array de cores dos objetos.
    :param epsilon: Delta pequeno para aproximação.
    :return: Vetor normal (np.ndarray).
    """
    dx = np.array([epsilon, 0, 0])
    dy = np.array([0, epsilon, 0])
    dz = np.array([0, 0, epsilon])

    nx, _ = calculate_distance(
        point + dx, object_positions, object_sizes, object_colors, object_types
    )
    px, _ = calculate_distance(
        point - dx, object_positions, object_sizes, object_colors, object_types
    )
    ny, _ = calculate_distance(
        point + dy, object_positions, object_sizes, object_colors, object_types
    )
    py, _ = calculate_distance(
        point - dy, object_positions, object_sizes, object_colors, object_types
    )
    nz, _ = calculate_distance(
        point + dz, object_positions, object_sizes, object_colors, object_types
    )
    pz, _ = calculate_distance(
        point - dz, object_positions, object_sizes, object_colors, object_types
    )

    normal = np.array([nx - px, ny - py, nz - pz])
    return normal / norm(normal)


@jit(nopython=True)
def calculate_lighting(
    point, normal, color, light_position, light_color, ambient_light
):
    """
    Calcula a iluminação de um ponto na superfície.

    :param point: Ponto na superfície (np.ndarray).
    :param normal: Normal da superfície (np.ndarray).
    :param color: Cor do objeto (np.ndarray).
    :param light_position: Posição da luz (np.ndarray).
    :param light_color: Cor da luz (np.ndarray).
    :param ambient_light: Intensidade da luz ambiente (np.ndarray).
    :return: Cor iluminada (np.ndarray).
    """
    # Direção da luz
    light_dir = light_position - point
    light_dir /= norm(light_dir)

    # Intensidade difusa
    diffuse_intensity = max(0, np.dot(normal, light_dir))
    diffuse = color * diffuse_intensity * light_color

    # Luz ambiente
    ambient = color * ambient_light

    # Cor final
    return diffuse + ambient


@jit(nopython=True)
def ray_march(
    ray_origin,
    ray_direction,
    object_positions,
    object_sizes,
    object_colors,
    object_types,
    max_distance,
    epsilon,
    max_steps,
    light_position,
    light_color,
    ambient_light,
):
    """
    Realiza o Ray Marching para encontrar interseções com objetos na cena, incluindo iluminação.

    :param ray_origin: Origem do raio (np.ndarray).
    :param ray_direction: Direção do raio (np.ndarray).
    :param object_positions: Array de posições dos objetos.
    :param object_sizes: Array de tamanhos/raios dos objetos.
    :param object_colors: Array de cores dos objetos.
    :param object_types: Array de tipos dos objetos (0=sphere, 1=cube).
    :param max_distance: Distância máxima do raio.
    :param epsilon: Tolerância para considerar uma interseção.
    :param max_steps: Número máximo de passos.
    :param light_position: Posição da luz (np.ndarray).
    :param light_color: Cor da luz (np.ndarray).
    :param ambient_light: Intensidade da luz ambiente (np.ndarray).
    :return: Cor iluminada ou cor de fundo.
    """
    distance_traveled = 0.0

    for _ in range(max_steps):
        current_position = ray_origin + ray_direction * distance_traveled
        min_distance, color = calculate_distance(
            current_position,
            object_positions,
            object_sizes,
            object_colors,
            object_types,
        )

        if min_distance < epsilon:
            # Estimar a normal na superfície
            normal = estimate_normal(
                current_position,
                object_positions,
                object_sizes,
                object_types,
                object_colors,
                epsilon,
            )
            # Calcular iluminação
            return calculate_lighting(
                current_position,
                normal,
                color,
                light_position,
                light_color,
                ambient_light,
            )

        distance_traveled += min_distance
        if distance_traveled > max_distance:
            break

    return np.array([0.0, 0.0, 0.0])  # Cor de fundo


class Main:
    def __init__(self):
        self.window = None
        self.resolution = 300
        self.camera_position = np.array([0.0, 0.0, 0.0])
        self.camera_direction = np.array([0.0, 0.0, 1.0])
        self.light_position = np.array([5.0, 5.0, -5.0])
        self.light_color = np.array([1.0, 1.0, 1.0])
        self.ambient_light = np.array([0.2, 0.2, 0.2])
        self.move_speed = 0.05
        self.max_distance = 80.0
        self.epsilon = 0.001
        self.max_steps = 50
        self.keys = set()

        # Controle de desempenho
        self.dynamic_resolution = Falseb

        # Objetos da cena
        self.objects = [
            Sphere(
                position=np.array([0.0, 0.0, 5.0]),
                radius=1.0,
                color=np.array([1.0, 0.0, 0.0]),
            ),
            Cube(
                position=np.array([3.0, 3.0, 5.0]),
                size=1.0,
                color=np.array([0.0, 1.0, 0.0]),
            ),
        ]

    def run(self):
        print("Running Ray Marching!")
        self.init()
        self.loop()
        glfw.terminate()

    def init(self):
        if not glfw.init():
            raise Exception("Unable to initialize GLFW")

        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)
        self.window = glfw.create_window(
            self.resolution, self.resolution, "Ray Marching", None, None
        )

        if not self.window:
            glfw.terminate()
            raise Exception("Failed to create GLFW window")

        video_mode = glfw.get_video_mode(glfw.get_primary_monitor())
        glfw.set_window_pos(
            self.window,
            (video_mode.size.width - self.resolution) // 2,
            (video_mode.size.height - self.resolution) // 2,
        )
        glfw.set_key_callback(self.window, self.key_callback)
        glfw.make_context_current(self.window)
        glfw.swap_interval(0)  # Remove o bloqueio de sincronização com o monitor
        glfw.show_window(self.window)

    def key_callback(self, window, key, scancode, action, mods):
        if action == glfw.PRESS:
            self.keys.add(key)
        elif action == glfw.RELEASE:
            self.keys.discard(key)

        if key == glfw.KEY_ESCAPE and action == glfw.RELEASE:
            glfw.set_window_should_close(window, True)

    def handle_camera_movement(self):
        forward = self.camera_direction
        right = np.cross(forward, np.array([0, 1, 0]))
        right /= np.linalg.norm(right)
        up = np.array([0, 1, 0])

        if glfw.KEY_W in self.keys:
            self.camera_position += forward * self.move_speed
        if glfw.KEY_S in self.keys:
            self.camera_position -= forward * self.move_speed
        if glfw.KEY_A in self.keys:
            self.camera_position += right * self.move_speed
        if glfw.KEY_D in self.keys:
            self.camera_position -= right * self.move_speed
        if glfw.KEY_SPACE in self.keys:
            self.camera_position += up * self.move_speed
        if glfw.KEY_RIGHT_SHIFT in self.keys:
            self.camera_position -= up * self.move_speed

    def render(self):
        # Pré-processar os objetos para usar na função JIT
        object_positions = np.array([obj.position for obj in self.objects])
        object_sizes = np.array(
            [
                obj.radius if isinstance(obj, Sphere) else obj.size
                for obj in self.objects
            ]
        )
        object_colors = np.array([obj.color for obj in self.objects])
        object_types = np.array(
            [0 if isinstance(obj, Sphere) else 1 for obj in self.objects]
        )

        # Ajusta dinamicamente a resolução
        current_resolution = self.resolution
        if glfw.KEY_LEFT_CONTROL in self.keys:
            current_resolution = 150  # Resolução reduzida
        elif self.dynamic_resolution and len(self.keys) > 0:
            current_resolution = 150

        width, height = current_resolution, current_resolution
        inv_resolution = 2 / current_resolution

        glClear(GL_COLOR_BUFFER_BIT)
        glBegin(GL_POINTS)

        for y in range(height):
            for x in range(width):
                uv_x = x * inv_resolution - 1
                uv_y = 1 - y * inv_resolution
                ray_direction = np.array([uv_x, uv_y, 1.0])
                ray_direction /= np.linalg.norm(ray_direction)

                color = ray_march(
                    self.camera_position,
                    ray_direction,
                    object_positions,
                    object_sizes,
                    object_colors,
                    object_types,
                    self.max_distance,
                    self.epsilon,
                    self.max_steps,
                    self.light_position,
                    self.light_color,
                    self.ambient_light,
                )
                glColor3f(color[0], color[1], color[2])
                glVertex2f(uv_x, uv_y)

        glEnd()
        glfw.swap_buffers(self.window)

    def loop(self):
        while not glfw.window_should_close(self.window):
            self.handle_camera_movement()
            self.render()
            glfw.poll_events()


if __name__ == "__main__":
    Main().run()
