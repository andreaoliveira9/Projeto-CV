class Vector3D:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        if isinstance(other, (int, float)):  # Multiplicação escalar
            return Vector3D(self.x * other, self.y * other, self.z * other)
        elif isinstance(other, Vector3D):  # Multiplicação por componente
            return Vector3D(self.x * other.x, self.y * other.y, self.z * other.z)
        else:
            raise TypeError(
                f"Unsupported operand type(s) for *: 'Vector3D' and '{type(other)}'"
            )

    def __truediv__(self, other):
        if isinstance(other, (int, float)):  # Divisão escalar
            return Vector3D(self.x / other, self.y / other, self.z / other)
        else:
            raise TypeError(
                f"Unsupported operand type(s) for /: 'Vector3D' and '{type(other)}'"
            )

    def __abs__(self):
        return Vector3D(abs(self.x), abs(self.y), abs(self.z))

    def distance(self, other):
        return (
            (self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2
        ) ** 0.5

    def length(self):
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5

    def normalize(self):
        length = self.length()
        if length == 0:
            return Vector3D(0, 0, 0)  # Evitar divisão por zero
        return self / length

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def __repr__(self):
        return f"Vector3D({self.x}, {self.y}, {self.z})"
