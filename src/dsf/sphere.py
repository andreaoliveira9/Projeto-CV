from .shape import Shape
from lib import Vector3D


class Sphere(Shape):
    def __init__(
        self,
        operation=None,
        color=Vector3D(1, 0, 0),
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

    def distance(self, eye):
        return self.position.distance(eye) - self.radius
