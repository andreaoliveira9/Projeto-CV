from lib import Vector3D


class Shape:
    def __init__(
        self,
        shapeId=None,
        operation=None,
        color=Vector3D(1, 0, 0),
        blendStrength=0,
        position=None,
    ):
        self.shapeId = shapeId
        self.operation = operation
        self.color = color
        self.blendStrength = blendStrength
        self.position = position

    def distance(self, eye):
        pass
