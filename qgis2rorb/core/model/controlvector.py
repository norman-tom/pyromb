import numpy as np
from qgis2rorb.core.attributes.reach import Reach

from qgis2rorb.core.graph.catchment import Catchment

class Traveller:
    def __init__(self, catchment: Catchment):
        self._catchment: Catchment = catchment
        self._colour = np.zeros(len(catchment._incidenceMatrixDS), dtype=int)
        self._us = catchment._incidenceMatrixUS
        self._ds = catchment._incidenceMatrixDS
        self._endSentinel = catchment._endSentinel
        self._pos = self._getStart()
        self._storedHydro: list[int] = []
        self._runningHydro: bool = False

    def _getStart(self) -> int:
        for i, val in enumerate(self._ds):
            if sum(val) == (-len(val)):
                return i
    
    def _state(self):
        """
        if no running hydrograph and is sub-area:
            code = 1
            set running 
        if node has a stored hydrograph and their is a running hydrograph:
            code = 4
            pop storedHydrograph from the stack
        if running hydrograph and is sub-area and has no visitable other upstream reaches:
            code = 2
        if running hydrograph and has other visitable upstream reaches:
            code = 3
            push node index onto stored hydrograph stack 
            set the running hydrograph to zero
            move the the most upstream point on that reach
        if running hydrograph and is not a sub-area and does not have upstream and there is nothing stored:
            code = 5

        """
        i = self._pos
        up = self._up(i)
        
        if (self._runningHydro == False) and (self._catchment._vertices[i].getType() == 0):
            self._runningHydro = True
            self._next()
            return (1, i)
        elif (self._storedHydro) and (self._storedHydro[-1] == i) and (self._runningHydro):
            self._storedHydro.pop()
            return (4, i)
        elif (self._runningHydro) and (self._catchment._vertices[i].getType() == 0) and (up == i):
            self._next()
            return (2, i)
        elif (self._runningHydro) and (up != i):
            self._storedHydro.append(i)
            self._runningHydro = False
            self._next()
            return (3, i)
        elif (self._runningHydro) and (self._catchment._vertices[i].getType() == 1) and (up == i):
            self._next()
            return (5, i)
    

    def _codedStr(self, code: tuple) -> str:
        """
        Format a control vector string according to the RORB manual Table 5-1 p.52 (version 6)
        """
        if (code[0] == 1) or (code[0] == 2) or (code[0] == 5):
            try:
                r = self._findReach(code[1])
                if (r.getType() == 1) or (r.getType() == 4):
                    return "{},{},{},-99".format(code[0], r.getType(), round(r.length() / 1000, 3))
                else:
                    return "{},{},{},{},-99".format(code[0], r.getType(), round(r.length() / 1000, 3), r.getSlope())
            except:
                return "{}".format(0)
        if (code[0] == 3) or (code[0] == 4):
            return "{}".format(code[0])
        if (code[0] == 0):
            return "{}".format(0)

    def _subAreaStr(self, code: list) -> str:
        areaStr = ""
        for c in code:
            if c[0] == 1:
                areaStr += "{},".format(round(self._catchment._vertices[c[1]].getArea(), 6))
        areaStr += '-99'
        return areaStr
    
    def _fracImpStr(self, code: list) -> str:
        fStr = "1,"
        for c in code:
            if c[0] == 1:
                fStr += "{},".format(round(self._catchment._vertices[c[1]].getFI(), 3))
        fStr += '-99'
        return fStr


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

    """
    Keeping this here for now
    ---------------------------
    This will return the upper most node when available, ignoring the intermediate DS nodes.

    def _next(self) -> int:
        up = self._up(self._pos)
        if up == self._pos:
            self._colour[self._pos] = 1
            self._pos = self._down(self._pos)
            return up
        else:
            self._pos = up
            return self._next()
    """
    
    def setPos(self, i: int) -> None:
        self._pos = i

    def getVector(self):
        header = "Reach Name\n0\n"
        controlVector = []
        stateVector = []
        subArea = ""
        fImp = ""
        self._next()
        while(self._pos != self._endSentinel):
            stateVector.append(self._state())
            controlVector.append(self._codedStr(stateVector[-1]))
        subArea = self._subAreaStr(stateVector)
        fImp = self._fracImpStr(stateVector)
        catStr = header
        for s in controlVector:
            catStr += s + "\n"
        catStr += subArea + "\n"
        catStr += fImp + "\n"
        
        return catStr