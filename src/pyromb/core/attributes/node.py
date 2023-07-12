from ..geometry.point import Point

class Node(Point):
    """Node in the catchment tree. 
    
    Encapsulates attributes of point like features in the catchment such as 
    basins and confluences.

    Attributes
    ----------
    name : str
        The name of the node
    """

    def __init__(self, name: str = "", x: float = 0.0, y: float = 0.0) -> None:
        super().__init__(x, y)
        self._name: str = name

    @property
    def name(self) -> str:
         return self._name
    
    @name.setter
    def name(self, name: str):
        self._name = name
