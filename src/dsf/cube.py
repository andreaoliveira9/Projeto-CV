from .shape import Shape
import numpy as np


class Cube(Shape):
    def __init__(
        self,
        operation=None,
        color=np.array([1, 0, 0]),
        blendStrength=0,
        position=None,
        size=None,
    ):
        super().__init__(
            shapeId="cube",
            operation=operation,
            color=color,
            blendStrength=blendStrength,
            position=position,
        )
        self.size = size
