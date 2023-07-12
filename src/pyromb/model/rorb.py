from .model import Model
from ..core.traveller import Traveller
from ..core.attributes.basin import Basin
from ..core.attributes.confluence import Confluence
from ..core.attributes.reach import ReachType

class RORB(Model):
    """Create a RORB control vector for input to the RORB runoff routing model. 
    """
    
    def __init__(self):
        self._storedHydro: list[int] = []
        self._runningHydro: bool = False
    
    def getVector(self, traveller: Traveller) -> str:
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
        """ The current state of the traveller within the catchment.

        Necessary to know so that the correct control code can be returned.

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
        elif (self._runningHydro == False) and (isinstance(traveller._catchment._vertices[i], Basin)):
            self._runningHydro = True
            traveller.next()
            return (1, i)
        elif (self._storedHydro) and (self._storedHydro[-1] == i) and (self._runningHydro):
            self._storedHydro.pop()
            return (4, i)
        elif (self._runningHydro) and (isinstance(traveller._catchment._vertices[i], Basin)) and (up == i):
            traveller.next()
            return (2, i)
        elif (self._runningHydro) and (up != i):
            self._storedHydro.append(i)
            self._runningHydro = False
            traveller.next()
            return (3, i)
        elif (self._runningHydro) and (isinstance(traveller._catchment._vertices[i], Confluence)) and (up == i):
            traveller.next()
            return (5, i)
    

    def _codedStr(self, code: tuple, traveller: Traveller) -> str:
        """Format a control vector string according to the RORB manual Table 5-1 p.52 (version 6)

        Parameters
        ----------
        code : tuple
            code, position pair to add to control string.
        traveller : Traveller
            The traveller traversing this catchment
        
        Returns
        -------
        str
            A correctly coded line for the control string.
        """

        if (code[0] == 1) or (code[0] == 2) or (code[0] == 5):
            try:
                r = traveller.getReach(code[1])
                if (r.type == ReachType.NATURAL) or (r.type == ReachType.DROWNED):
                    return "{},{},{},-99".format(code[0], r.type.value, round(r.length() / 1000, 3))
                else:
                    return "{},{},{},{},-99".format(code[0], r.type.value, round(r.length() / 1000, 3), r.getSlope())
            except:
                return "{}\nout\n{}".format(7, 0)
        if (code[0] == 3) or (code[0] == 4):
            return "{}".format(code[0])
        if (code[0] == 0):
            return "{}\nout\n'{}".format(7, 0)

    def _subAreaStr(self, code: list, traveller: Traveller) -> str:
        """Format the subarea string according to the RORB manual

        Parameters
        ----------
        code : list
            a list of the states acting on the catchment in the order of travel.
        traveller : Traveller
            The traveller traversing this catchment. 

        Returns
        -------
        str
            A subarea string for the control file.
        """

        areaStr = ""
        for c in code:
            if (c[0] == 1) or (c[0] == 2):
                areaStr += "{},".format(round(traveller._catchment._vertices[c[1]].area, 6))
        areaStr += '-99'
        return areaStr
    
    def _fracImpStr(self, code: list, traveller: Traveller) -> str:
        
        fStr = "1,"
        for c in code:
            if (c[0] == 1) or (c[0] == 2):
                fStr += "{},".format(round(traveller._catchment._vertices[c[1]].fi, 3))
        fStr += '-99'
        return fStr