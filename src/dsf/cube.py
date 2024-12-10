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
        delta = abs(eye - self.position) - half_size

        # Distância máxima para as componentes externas ao cubo
        max_outside = max(delta.x, 0) + max(delta.y, 0) + max(delta.z, 0)

        # Distância interna, se o ponto estiver dentro do cubo
        max_inside = min(max(delta.x, max(delta.y, delta.z)), 0)

        # Retorna a soma das distâncias externas e internas
        return max_outside + max_inside
