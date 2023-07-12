from .node import Node

class Confluence(Node):
    """A confluence is the location where reaches join into one. 

    Attributes
    ----------
    name : str
        The name of the Confluence, should be unique
    x : float
        The x co-ordinate
    y : float
        The y co-ordinate
    out : bool
        True if this confluence is the outfall of the model. 
    """

    def __init__(self, name: str = "", x: float = 0, y: float = 0, out: bool = False) -> None:
        super().__init__(name, x, y)
        self._isOut: bool = out
    
    def __str__(self):
        return "Name: {}\n[{}, {}]\n{}".format(self._name, round(self._x, 3), round(self._y, 3), self._isOut)
    
    @property
    def isOut(self) -> bool:
        return self._isOut
    
    @isOut.setter
    def isOut(self, val: bool):
        self._isOut = val