from .shape import Shape
from lib import Vector3D


class Cube(Shape):
    def __init__(
        self,
        operation=None,
        color=Vector3D(1, 0, 0),
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

    def distance(self, eye):
        """
        Calcula a distância mínima do ponto `eye` até a superfície do cubo.

        :param eye: Posição do ponto de origem do raio (Vector3D).
        :return: Distância escalar (float) até a superfície do cubo.
        """
        half_size = Vector3D(self.size / 2, self.size / 2, self.size / 2)

        # Vetor de distância absoluta entre o ponto e o centro do cubo
        o = abs(eye - self.position) - half_size

        # Distância externa (fora do cubo)
        ud = Vector3D(max(o.x, 0), max(o.y, 0), max(o.z, 0)).length()

        # Distância interna (dentro do cubo)
        n = max(max(min(o.x, 0), min(o.y, 0)), min(o.z, 0))

        # Retorna a soma das distâncias externa e interna
        return ud + n
