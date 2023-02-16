from turtle import down
import numpy as np
from qgis2rorb.core.attributes.reach import Reach
from qgis2rorb.core.catchment import Catchment
from qgis2rorb.model.model import Model

class Traveller:
    def __init__(self, catchment: Catchment):
        self._catchment: Catchment = catchment
        self._colour = np.zeros(len(catchment._incidenceMatrixDS), dtype=int)
        self._us = catchment._incidenceMatrixUS
        self._ds = catchment._incidenceMatrixDS
        self._endSentinel = catchment._endSentinel
        self._pos = self._getStart()

    def _getStart(self) -> int:
        """
        Gets the position of the outlet node of the basin. That is the most downstream node.
        Assumes that there is only one outlet in a basin. I.e. only one node with no reaches downstream of it. 
        """
        for i, val in enumerate(self._ds):
            if sum(val) == (-len(val)):
                return i
    
    def _findReach(self, i: int) -> Reach:
        """
        Find the downstream reach connected to node i. 
        """
        for j, val in enumerate(self._ds[i]):
            if val != self._endSentinel:
                return self._catchment._edges[j]
        raise KeyError

    def _up(self, i: int) -> int:
        """
        Traverse to the most upstream catchment avaiable from starting node i.
        An avaiable catchment is one which has not been visited by _next().
        """
        for val in self._us[i]:
            if val != -1:
                if self._colour[val] == 0:
                    return self._up(val)
                else:
                    continue
        return i

    def _down(self, i: int) -> int:
        """
        returns the next downstream node along the reach.
        """
        for val in self._ds[i]:
            if val != -1:
                return val
        return self._endSentinel
    
    def _next(self) -> int:
        """
        This will return the next upstream node within the catchment available from the current node position. 
        If the node position is on a confluence _next() will return that node before going up the next reach.
        """
        up = self._up(self._pos)
        if up == self._pos:
            self._colour[self._pos] = 1
            self._pos = self._down(self._pos)
            return self._pos
        else:
            self._pos = up
            return self._pos
        
    def _nextAbsolute(self) -> int:
        """
        This will return the next upper most node availabe from the current position.
        _nextAbsolute() ignores the nodes at confluences if it can reach a higher node at returns the higher node.
        """
        up = self._up(self._pos)
        if up == self._pos:
            self._colour[self._pos] = 1
            self._pos = self._down(self._pos)
            return up
        else:
            self._pos = up
            return self._next()

    def getVector(self, model: Model):
        """
        Ask to produce the vector from the chosen hydrology model. 
        Returns a correctly formated control vector for either a RORB or WBNM model.  
        """
        return model.getVector(self)