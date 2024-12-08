import glfw
from OpenGL.GL import *
import numpy as np

class Main:
    def __init__(self):
        self.window = None
        self.red = 1.0
        self.green = 0.0
        self.blue = 0.0
        self.transition_speed = 0.005

    def run(self):
        print("Hello GLFW!")

        self.init()
        self.loop()

        # Free the window callbacks and destroy the window
        glfw.terminate()

    def init(self):
        # Initialize GLFW
        if not glfw.init():
            raise Exception("Unable to initialize GLFW")

        # Configure GLFW
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)

        # Create the window
        self.window = glfw.create_window(300, 300, "Hello World!", None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("Failed to create the GLFW window")

        # Setup a key callback
        glfw.set_key_callback(self.window, self.key_callback)

        # Center the window
        video_mode = glfw.get_video_mode(glfw.get_primary_monitor())
        glfw.set_window_pos(
            self.window,
            (video_mode.size.width - 300) // 2,
            (video_mode.size.height - 300) // 2
        )

        # Make the OpenGL context current
        glfw.make_context_current(self.window)
        # Enable v-sync
        glfw.swap_interval(1)

        # Make the window visible
        glfw.show_window(self.window)

    def key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.RELEASE:
            glfw.set_window_should_close(window, True)

    def update_color(self):
        if self.red > 0 and self.blue == 0:
            self.red -= self.transition_speed
            self.green += self.transition_speed
        if self.green > 0 and self.red == 0:
            self.green -= self.transition_speed
            self.blue += self.transition_speed
        if self.blue > 0 and self.green == 0:
            self.blue -= self.transition_speed
            self.red += self.transition_speed

        # Ensure values stay within bounds
        self.red = max(0, min(1, self.red))
        self.green = max(0, min(1, self.green))
        self.blue = max(0, min(1, self.blue))
        glClearColor(self.red, self.green, self.blue, 0.0)

    def loop(self):
        # Run the rendering loop until the user has attempted to close
        # the window or has pressed the ESCAPE key.
        while not glfw.window_should_close(self.window):
            self.update_color()
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # clear the framebuffer

            glfw.swap_buffers(self.window)  # swap the color buffers

            # Poll for window events. The key callback above will only be
            # invoked during this call.
            glfw.poll_events()

if __name__ == "__main__":
    Main().run()