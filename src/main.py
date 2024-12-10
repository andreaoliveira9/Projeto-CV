import glfw
from OpenGL.GL import *
import numpy as np
from lib import Vector3D
from dsf import Sphere, Cube


class Main:
    def __init__(self):
        self.window = None
        self.resolution = 300
        self.camera_position = Vector3D(0.0, 0.0, 0.0)  # Posição da câmera
        self.camera_direction = Vector3D(0.0, 0.0, 1.0)  # Direção da câmera
        self.light_position = Vector3D(5.0, 5.0, -5.0)  # Posição da luz
        self.light_color = Vector3D(1.0, 1.0, 1.0)  # Cor da luz
        self.ambient_light = Vector3D(0.2, 0.2, 0.2)  # Luz ambiente
        self.move_speed = 1
        self.objects = [
            Sphere(
                position=Vector3D(0.0, 0.0, 5.0),
                radius=1.0,
                color=Vector3D(1.0, 0.0, 0.0),
            ),
            Cube(
                position=Vector3D(3.0, 3.0, 5.0),
                size=1.0,
                color=Vector3D(0.0, 1.0, 0.0),
            ),
        ]
        self.max_distance = 80.0
        self.epsilon = 0.001
        self.keys = set()

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
        glfw.swap_interval(1)

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
        right = Vector3D(-forward.z, 0, forward.x).normalize()
        up = Vector3D(0, 1, 0)

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
        if glfw.KEY_LEFT_SHIFT in self.keys:
            self.camera_position -= up * self.move_speed

    def scene_distance(self, point):
        if not isinstance(point, Vector3D):
            point = Vector3D(*point)

        min_distance = float("inf")
        color = Vector3D(0.0, 0.0, 0.0)

        for obj in self.objects:
            distance = obj.distance(point)
            if distance < min_distance:
                min_distance = distance
                color = obj.color

        return min_distance, color

    def estimate_normal(self, point):
        epsilon = self.epsilon
        dx = Vector3D(epsilon, 0, 0)
        dy = Vector3D(0, epsilon, 0)
        dz = Vector3D(0, 0, epsilon)

        nx = self.scene_distance(point + dx)[0] - self.scene_distance(point - dx)[0]
        ny = self.scene_distance(point + dy)[0] - self.scene_distance(point - dy)[0]
        nz = self.scene_distance(point + dz)[0] - self.scene_distance(point - dz)[0]

        normal = Vector3D(nx, ny, nz).normalize()
        return normal

    def calculate_lighting(self, point, normal, color):
        light_dir = (self.light_position - point).normalize()
        diffuse_intensity = max(0, normal.dot(light_dir))
        diffuse = color * diffuse_intensity * self.light_color
        ambient = color * self.ambient_light
        return diffuse + ambient

    def ray_march(self, ray_origin, ray_direction):
        distance_traveled = 0.0

        for _ in range(100):  # Max steps
            current_position = ray_origin + ray_direction * distance_traveled
            distance, color = self.scene_distance(current_position)

            if distance < self.epsilon:
                normal = self.estimate_normal(current_position)
                lighting = self.calculate_lighting(current_position, normal, color)
                return lighting
            distance_traveled += distance

            if distance_traveled > self.max_distance:
                break

        return Vector3D(0.0, 0.0, 0.0)  # Background color

    def render(self):
        width, height = self.resolution, self.resolution
        glClear(GL_COLOR_BUFFER_BIT)
        glBegin(GL_POINTS)

        for y in range(height):
            for x in range(width):
                uv = np.array([x / width * 2 - 1, y / height * 2 - 1])
                uv[1] *= -1  # Inverter Y para alinhar
                ray_direction = Vector3D(uv[0], uv[1], 1.0).normalize()

                color = self.ray_march(self.camera_position, ray_direction)
                glColor3f(color.x, color.y, color.z)
                glVertex2f(uv[0], uv[1])

        glEnd()
        glfw.swap_buffers(self.window)

    def loop(self):
        while not glfw.window_should_close(self.window):
            self.handle_camera_movement()
            self.render()
            glfw.poll_events()


if __name__ == "__main__":
    Main().run()
