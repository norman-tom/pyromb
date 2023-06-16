from gisrom.core.geometry.point import Point

class Node(Point):
    def __init__(self, name: str = "", x: float = 0.0, y: float = 0.0, type: int = 0) -> None:
        super().__init__(x, y)
        self._name: str = name
        self._type: int = type

    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, name: str):
       self._name = name

    @property
    def type(self):
        return self._type