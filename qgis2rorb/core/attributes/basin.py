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

    @property
    def area(self) -> float:
        return self._area
    
    @area.setter
    def area(self, km2: float):
        self._area = km2
    
    @property
    def fi(self) -> float:
        return self._fi
    
    @fi.setter
    def fi(self, fi: float):
        self._fi = fi