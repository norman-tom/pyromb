import numpy as np
from qgis2rorb.core.attributes.reach import Reach
from qgis2rorb.core.attributes.node import Node
from qgis2rorb.core.catchment import Catchment
from qgis2rorb.model.model import Model

class Traveller:
    def __init__(self, catchment: Catchment):
        self._catchment: Catchment = catchment
        self._colour = np.zeros(len(catchment._incidenceMatrixDS), dtype=int)
        self._us = catchment._incidenceMatrixUS
        self._ds = catchment._incidenceMatrixDS
        self._endSentinel = catchment._endSentinel
        self._pos = self.getStart()

    def position(self) -> int:
        """
        Return the current position of the traveller. 
        """
        return self._pos
        
    def getStart(self) -> int:
        """
        Gets the position of the outlet node of the basin. That is the most downstream node.
        Assumes that there is only one outlet in a basin. I.e. only one node with no reaches downstream of it. 
        """
        for i, val in enumerate(self._ds):
            if sum(val) == (-len(val)):
                return i
    
    def getReach(self, i: int) -> Reach:
        """
        Return the downstream reach connected to node i. 
        """
        for j, val in enumerate(self._ds[i]):
            if val != self._endSentinel:
                return self._catchment._edges[j]
        raise KeyError
    
    def getNode(self, i: int) -> Node:
        """
        Return the node at position i.
        """
        return self._catchment._vertices[i]

    def top(self, i: int) -> int:
        """
        Returns the node index of the most upstream catchment avaiable from starting node i.
        Does not update the position of the traveller. 
        An avaiable catchment is one which has not been visited by _next().
        """
        for val in self._us[i]:
            if val != -1:
                if self._colour[val] == 0:
                    return self.top(val)
                else:
                    continue
        return i
    
    def up(self, i) -> list:
        """
        Returns the immediate upstream nodes from position i. A subarea can have multiple upstream nodes.
        """
        return [j for j in self._us[i] if -1 != j]

    def down(self, i: int) -> int:
        """
        returns the index of the next downstream node along the reach.
        Does not update the position of the traveller.
        If there is no downstream node then -1 is returned.
        """
        for val in self._ds[i]:
            if val != -1:
                return val
        return self._endSentinel
    
    def next(self) -> int:
        """
        This will return the next upstream node within the catchment available from the current node position. 
        If the node position is on a confluence _next() will return that node before going up the next reach.
        """
        up = self.top(self._pos)
        if up == self._pos:
            self._colour[self._pos] = 1
            self._pos = self.down(self._pos)
            return self._pos
        else:
            self._pos = up
            return self._pos
        
    def nextAbsolute(self) -> int:
        """
        This will return the next upper most node availabe from the current position.
        _nextAbsolute() ignores the nodes at confluences if it can reach a higher node and returns the higher node.
        """
        up = self.top(self._pos)
        if up == self._pos:
            self._colour[self._pos] = 1
            self._pos = self.down(self._pos)
            return up
        else:
            self._pos = up
            return self.next()

    def getVector(self, model: Model):
        """
        Ask to produce the vector from the chosen hydrology model. 
        Returns a correctly formated control vector for either a RORB or WBNM model.  
        """
        return model.getVector(self)