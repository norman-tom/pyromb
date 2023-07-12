from .node import Node

class Basin(Node):
    """A Basin object represents a sub-basin as defined in hydrological models.

    Attributes
    ----------
    name : str
        The name of the basin, should be unique
    x : float
        The x co-ordinate
    y : float
        The y co-ordinate
    area : float
        The cartesian area, unitless
    fi : float
        Fraction of the basin that is impervious [0,1]
    """

    def __init__(self, 
                 name: str = "", 
                 x: float = 0, 
                 y: float = 0, 
                 area: float = 0.0, 
                 fi: float = 0.0) -> None:
        super().__init__(name, x, y)
        self._area: float = area
        self._fi: float = fi

    def __str__(self):
        return "Name: {}\n[{}, {}]\nArea: {}".format(self._name, self._x, self._y, self._area)    

    @property
    def area(self) -> float:
        return self._area
    
    @area.setter
    def area(self, area: float):
        self._area = area
    
    @property
    def fi(self) -> float:
        return self._fi
    
    @fi.setter
    def fi(self, fi: float):
        self._fi = fi