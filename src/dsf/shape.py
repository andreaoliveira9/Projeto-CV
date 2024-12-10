import numpy as np


class Shape:
    def __init__(
        self,
        shapeId=None,
        operation=None,
        color=np.array([1, 0, 0]),
        blendStrength=0,
        position=None,
    ):
        self.shapeId = shapeId
        self.operation = operation
        self.color = color
        self.blendStrength = blendStrength
        self.position = position
