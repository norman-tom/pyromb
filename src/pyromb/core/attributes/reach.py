from ..geometry.line import Line
from enum import Enum

class ReachType(Enum):
    NATURAL = 1
    UNLINED = 2
    LINED = 3
    DROWNED = 4

class Reach(Line):
    """A Reach object represents a reach as defined in hydrological models.

    Attributes
    ----------
    name : str
        The name of the reach, should be unique
    type : ReachType
        The type of reach as specified by the hydrological model.
    slope : float
        The slope of the reach in m/m
    """

    def __init__(self, name: str = "", 
                 vector: list = [], 
                 type: ReachType = ReachType.NATURAL, 
                 slope: float = 0.0):
        super().__init__(vector)
        self._name: str = name
        self._type: ReachType = type
        self._slope: float = slope
        self._idx: int = 0
    
    def __str__(self) -> str:
        return "Name: {}\nLength: {}\nType: {}\nSlope: {}".format(self._name, round(self.length(), 3), self._type, self._slope)
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, name: str) -> None:
        self._name = name
    
    @property
    def type(self) -> ReachType:
        return self._type
    
    @type.setter
    def type(self, type: ReachType) -> None:
        self._type = type

    @property
    def slope(self) -> float:
        return self._slope  
    
    def slope(self, slope: float) -> None:
        self._slope = slope

    def getPoint(self, direction: str):
        """ Returns either the upstream or downstream 'ds' point of the reach.

        Parameters
        ----------
        direction : str
            'us' - for upstream point. \n
            'ds' - for downstream point

        Returns
        -------
        Point
            The US or DS point

        Raises
        ------
        KeyError
            If direction is not either 'us' or 'ds'
        """

        if direction == 'us':
            return self._vector[self._idx]
        elif direction == 'ds':
            return self._vector[self._end - self._idx]
        else:
            raise KeyError("Node direction not properly defines: \n")