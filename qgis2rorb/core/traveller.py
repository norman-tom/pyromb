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
        for i, val in enumerate(self._ds):
            if sum(val) == (-len(val)):
                return i
    
    def _findReach(self, i: int) -> Reach:
        for j, val in enumerate(self._ds[i]):
            if val != self._endSentinel:
                return self._catchment._edges[j]
        raise KeyError


    def _up(self, i: int) -> int:
            for val in self._us[i]:
                if val != -1:
                    if self._colour[val] == 0:
                        return self._up(val)
                    else:
                        continue
            return i

    def _down(self, i: int) -> int:
        for val in self._ds[i]:
            if val != -1:
                return val
        return self._endSentinel
    
    
    def _next(self) -> int:
        """
        This will return the intermediate downstream node before going up.
        """
        up = self._up(self._pos)
        if up == self._pos:
            self._colour[self._pos] = 1
            self._pos = self._down(self._pos)
            return self._pos
        else:
            self._pos = up
            return self._pos

    def getVector(self, model: Model):
        return model.getVector(self)