from .node import Node

class Confluence(Node):
    def __init__(self, name: str = "", x: float = 0, y: float = 0, out: bool = False) -> None:
        super().__init__(name, x, y)
        self._isOut: bool = out
        """
        Identify if this confluence is the out node, which is the last node in the graph. 
        """
        self._type = 1
        """
        Identify that this is a confluence
        """
    
    def __str__(self):
        return "Name: {}\n[{}, {}]\n{}".format(self._name, round(self._x, 3), round(self._y, 3), self._isOut)

    def setOut(self):
        """
        Identify that this confluence is the last node in the graph.
        """
        self._isOut = True
    
    def isOut(self) -> bool:
        """
        Returns whether this confluence is the last node in the graph.
        """
        return self._isOut