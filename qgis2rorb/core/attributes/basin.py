from .node import Node

class Basin(Node):
    def __init__(self, name: str = "", x: float = 0, y: float = 0, km2: float = 0.0, fi: float = 0.0) -> None:
        super().__init__(name, x, y)
        self._area: float = km2
        self._fi: float = fi
        self._type = 0
        """
        Identify that this is a basin
        """

    def __str__(self):
        return "Name: {}\n[{}, {}]\nArea: {}".format(self._name, self._x, self._y, self._area)    
    
    def setArea(self, km2):
        self._area = km2
    
    def setFI(self, fi):
        self._fi = fi

    def getArea(self) -> float:
        return self._area

    def getFI(self) -> float:
        return self._fi