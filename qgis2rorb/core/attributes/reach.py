from qgis2rorb.core.geometry.line import Line

class Reach(Line):
    def __init__(self, name: str = "", vector: list = [], type: int = 0, slope: float = 0.0):
        super().__init__(vector)
        self._name: str = name
        self._type: int = type
        self._slope: float = slope
        self._idx: int = 0
        """
        Points to the upstream point in the line vector 
        There is no requirement on the user when drawing reaches inside QGIS that the reach is directional.
        Direction can be inferred from the graph and their relation to the 'out' node.
        """
    
    def __str__(self) -> str:
        return "Name: {}\nLength: {}\nType: {}\nSlope: {}".format(self._name, round(self.length(), 3), self._type, self._slope)
    
    def setName(self, name: str):
        self._name = name
    
    def setType(self, type: int):
        self._type = type

    def setSlope(self, slope: float):
        self._slope = slope

    def mapIdx(self, direction: str):
        """
        Maps the start of the geometry to either the downstream or upstream end of the reach.
        If the direction is "us" then the first coordinate in the vector is the upstream end.
        If the direcion is "ds" the the first coordinate in the vector is the downstream end. 
        """
        if direction == 'us':
            self._idx = 0
        elif direction == "ds":
            self._idx = self._end
        else:
            raise KeyError("Node direction not properly defines: \n")

    def getPoint(self, direction: str):
        """
        Returns either the point corresponding to the upstream 'us' or to the downstream 'ds'.
        """
        if direction == 'us':
            return self._vector[self._idx]
        elif direction == 'ds':
            return self._vector[self._end - self._idx]
        else:
            raise KeyError("Node direction not properly defines: \n")

    def getName(self) -> int:
        return self._name
    
    def getType(self) -> int:
        return self._type

    def getSlope(self) -> float:
        return self._slope    

    TYPES = {
        'natural': 1,
        'unlined': 2,
        'lined': 3,
        'drowned': 4}