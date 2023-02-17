from qgis2rorb.model.model import Model
from qgis2rorb.core.traveller import Traveller

class RORB(Model):
    '''
    Create a RORB control vector for input to the RORB runoff routing model. 
    '''
    def __init__(self):
        self._storedHydro: list[int] = []
        self._runningHydro: bool = False
    
    def getVector(self, traveller: Traveller) -> str:
        '''
        Return the control vector for the RORB hydrological model.
        '''
        header = "Reach Name\n0\n"
        controlVector = []
        stateVector = []
        subArea = ""
        fImp = ""
        traveller.next()
        while(traveller._pos != traveller._endSentinel):
            stateVector.append(self._state(traveller))
            controlVector.append(self._codedStr(stateVector[-1], traveller))       
        subArea = self._subAreaStr(stateVector, traveller)
        fImp = self._fracImpStr(stateVector, traveller)
        catStr = header
        for s in controlVector:
            catStr += s + "\n"
        catStr += subArea + "\n"
        catStr += fImp + "\n"
        return catStr
    
    def _state(self, traveller: Traveller):
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
        i = traveller._pos
        up = traveller.top(i)
        
        if i == traveller._endSentinel:
            return(0, i)
        elif (self._runningHydro == False) and (traveller._catchment._vertices[i].getType() == 0):
            self._runningHydro = True
            traveller.next()
            return (1, i)
        elif (self._storedHydro) and (self._storedHydro[-1] == i) and (self._runningHydro):
            self._storedHydro.pop()
            return (4, i)
        elif (self._runningHydro) and (traveller._catchment._vertices[i].getType() == 0) and (up == i):
            traveller.next()
            return (2, i)
        elif (self._runningHydro) and (up != i):
            self._storedHydro.append(i)
            self._runningHydro = False
            traveller.next()
            return (3, i)
        elif (self._runningHydro) and (traveller._catchment._vertices[i].getType() == 1) and (up == i):
            traveller.next()
            return (5, i)
    

    def _codedStr(self, code: tuple, traveller: Traveller) -> str:
        """
        Format a control vector string according to the RORB manual Table 5-1 p.52 (version 6)
        """
        if (code[0] == 1) or (code[0] == 2) or (code[0] == 5):
            try:
                r = traveller.getReach(code[1])
                if (r.getType() == 1) or (r.getType() == 4):
                    return "{},{},{},-99".format(code[0], r.getType(), round(r.length() / 1000, 3))
                else:
                    return "{},{},{},{},-99".format(code[0], r.getType(), round(r.length() / 1000, 3), r.getSlope())
            except:
                return "{}\nout\n{}".format(7, 0)
        if (code[0] == 3) or (code[0] == 4):
            return "{}".format(code[0])
        if (code[0] == 0):
            return "{}\nout\n'{}".format(7, 0)

    def _subAreaStr(self, code: list, traveller: Traveller) -> str:
        areaStr = ""
        for c in code:
            if (c[0] == 1) or (c[0] == 2):
                areaStr += "{},".format(round(traveller._catchment._vertices[c[1]].getArea(), 6))
        areaStr += '-99'
        return areaStr
    
    def _fracImpStr(self, code: list, traveller: Traveller) -> str:
        fStr = "1,"
        for c in code:
            if (c[0] == 1) or (c[0] == 2):
                fStr += "{},".format(round(traveller._catchment._vertices[c[1]].getFI(), 3))
        fStr += '-99'
        return fStr