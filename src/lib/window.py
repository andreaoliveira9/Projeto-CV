import pygame as pg
import pygame.mouse
from pygame.locals import *
import numpy as np

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


class Window:

    def __init__(
        self, width: int = 1280, height: int = 800, fps: int = 60, renderer: int = 0
    ) -> None:
        self.width = width
        self.height = height
        self.screen = None
        self.max_fps = fps
        self.running = False
        self.renderer = renderer
        self.clock = pg.time.Clock()
        self.program = None

        # Shader stuff
        self.resolution_location = None

    def create_window(self) -> None:
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(
            pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE
        )

        self.screen = pg.display.set_mode(
            (self.width, self.height), OPENGL | DOUBLEBUF | RESIZABLE
        )
        self._shader_init()
        pygame.mouse.set_visible(False)

    def _shader_init(self):
        # Locations
        vertex_shader_source = self._read_shader("glsl/vertex_shader.glsl")
        fragment_shader_source = self._read_shader("glsl/fragment_shader.glsl")

        # Compile shaders
        vertex_shader = compileShader(vertex_shader_source, GL_VERTEX_SHADER)
        fragment_shader = compileShader(fragment_shader_source, GL_FRAGMENT_SHADER)

        # Create and bind a VAO for validation
        VAO = glGenVertexArrays(1)
        glBindVertexArray(VAO)

        # Compile the shader program
        self.program = compileProgram(vertex_shader, fragment_shader)

        # Unbind the VAO after validation
        glBindVertexArray(0)

        glUseProgram(self.program)

        # Variable locations and first-time setting
        self.resolution_location = glGetUniformLocation(self.program, "u_resolution")
        glUniform2f(self.resolution_location, self.width, self.height)

    def _read_shader(self, path: str) -> str:
        with open(path, "r") as file:
            return file.read()

    def _process_keys(self) -> None:
        """process keys that are being pressed and perform some actions"""
        keys = pg.key.get_pressed()

    def _process_events(self) -> None:
        """process events that are being triggered"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            if event.type == pg.VIDEORESIZE:
                self.width = event.w
                self.height = event.h
                self.screen = pg.display.set_mode(
                    (self.width, self.height), OPENGL | DOUBLEBUF | RESIZABLE
                )
                glUniform2f(self.resolution_location, self.width, self.height)

    def run(self) -> None:
        self.running = True

        # Define the vertex data
        vertices = np.array(
            [-1.0, -1.0, 0.0, 1.0, -1.0, 0.0, 1.0, 1.0, 0.0, -1.0, 1.0, 0.0],
            dtype=np.float32,
        )

        indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

        # Create and bind a Vertex Array Object (VAO)
        VAO = glGenVertexArrays(1)
        glBindVertexArray(VAO)

        # Create a Vertex Buffer Object (VBO)
        VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, VBO)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # Create an Element Buffer Object (EBO)
        EBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        # Define the position attribute
        position = glGetAttribLocation(self.program, "vPosition")
        glEnableVertexAttribArray(position)
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 0, None)

        # Unbind the VAO to avoid unintended modifications
        glBindVertexArray(0)

        while self.running:
            self._process_events()
            self._process_keys()

            # OpenGl stuff
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Bind the VAO and draw
            glBindVertexArray(VAO)
            glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)
            glBindVertexArray(0)

            # Draw stuff here
            pg.display.flip()
            self.clock.tick(self.max_fps)
