from .shape import Shape
import numpy as np


class Sphere(Shape):
    def __init__(
        self,
        operation=None,
        color=np.array([1, 0, 0]),
        blendStrength=0,
        position=None,
        radius=None,
    ):
        super().__init__(
            shapeId="sphere",
            operation=operation,
            color=color,
            blendStrength=blendStrength,
            position=position,
        )
        self.radius = radius
