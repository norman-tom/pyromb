from .model import Model
from ..core.traveller import Traveller
from ..core.attributes.basin import Basin
from ..core.attributes.confluence import Confluence
from ..core.attributes.reach import ReachType
from .. import resources

def nextIDgenerator():
    i = 0
    while True:
        i += 1
        yield i

class RORB(Model):
    """Create a RORB control vector for input to the RORB runoff routing model. 
    """
    
    def __init__(self):
        self._storedHydro: list[int] = []
        self._runningHydro: bool = False
        self.nodeID = nextIDgenerator()
        self.reachID = nextIDgenerator()
    
    def getVector(self, traveller: Traveller) -> str:
        reachIDMap = {}
        nodeIDMap = {}
        controlVector = []
        stateVector = []
        gNodeVector = []
        gReachVector = []
        subArea = ""
        fImp = ""
        traveller.next()
        
        while(traveller._pos != traveller._endSentinel):
            stateVector.append(self._state(traveller))
            controlVector.append(self._codedStr(stateVector[-1], traveller))

            gn = self._graphicalNode(stateVector[-1], traveller, nodeIDMap)
            if gn is not None: gNodeVector.append(gn)

            gr = self._graphicalReach(stateVector[-1], traveller, reachIDMap)
            if gr is not None: gReachVector.append(gr)
        
        # Building the control vector information strin
        subArea = self._subAreaStr(stateVector, traveller)
        fImp = self._fracImpStr(stateVector, traveller)
        catStr = resources.rorb.VECTOR_HEADER
        for s in controlVector:
            catStr += s + "\n"
        catStr += subArea + "\n"
        catStr += fImp + "\n"
        
        # Building the graphical information string
        for i, row in enumerate(gNodeVector):
            for j, item in enumerate(row):
                if item in nodeIDMap:
                    gNodeVector[i][j] = nodeIDMap[item]
        
        for i, row in enumerate(gReachVector):
            for j, item in enumerate(row):
                if item in nodeIDMap:
                    gReachVector[i][j] = nodeIDMap[item]
                elif item in reachIDMap:
                    gReachVector[i][j] = reachIDMap[item]
        
        # Normalise the co-ordinates
        xs = [x[1] for x in gNodeVector]
        ys = [y[2] for y in gNodeVector]
        scale_x = max(xs) - min(xs)
        scale_y = max(ys) - min(ys)

        for i, row in enumerate(gNodeVector):
            gNodeVector[i][1] = (row[1] - min(xs)) / scale_x * 100
            gNodeVector[i][2] = (row[2] - min(ys)) / scale_y * 100
        
        for i, row in enumerate(gReachVector):
            gReachVector[i][11] = (row[11] - min(xs)) / scale_x * 100
            gReachVector[i][12] = (row[12] - min(ys)) / scale_y * 100

        
        node_str = ""
        for row in gNodeVector:
            node_str += 'C'
            node_str  += str(row[0]).rjust(7, " ")
            node_str += str(round(row[1], 3)).rjust(15, " ")
            node_str += str(round(row[2], 3)).rjust(15, " ")
            node_str += ("%.3f" % round(row[3], 3)).rjust(15, " ")
            node_str += str(row[4]).rjust(2, " ")
            node_str += str(row[5]).rjust(2, " ")
            node_str += str(row[6]).rjust(6, " ")
            node_str += " "
            node_str += str(row[7]).ljust(2, " ")
            node_str += ("%.6f" % round(row[8], 6)).rjust(33, " ")
            node_str += ("%.6f" % round(row[9], 6)).rjust(15, " ")
            node_str += str(row[10]).rjust(3, " ")
            node_str += str(row[11]).rjust(3, " ")
            node_str += str(row[12]).rjust(3, " ")
            node_str += '\nC\n'
        
        reach_str = ""
        for row in gReachVector:
            reach_str += 'C'
            reach_str += str(row[0]).rjust(7, " ")
            reach_str += " "
            reach_str += str(row[1]).ljust(8, " ")
            reach_str += str(row[2]).rjust(18, " ")
            reach_str += str(row[3]).rjust(6, " ")
            reach_str += str(row[4]).rjust(15, " ")
            reach_str += str(row[5]).rjust(2, " ")
            reach_str += str(row[6]).rjust(2, " ")
            reach_str += ("%.3f" % round(row[7], 3)).rjust(15, " ")
            reach_str += ("%.3f" % round(row[8], 3)).rjust(15, " ")
            reach_str += str(row[9]).rjust(6, " ")
            reach_str += str(row[10]).rjust(3, " ")
            reach_str += '\nC'
            reach_str += ("%.3f" % round(row[11], 3)).rjust(16, " ")
            reach_str += '\nC'
            reach_str += ("%.3f" % round(row[12], 3)).rjust(16, " ")
            reach_str += '\n'

        gStr = resources.rorb.GRAPHICAL_HEADER
        gStr += "C #NODES\n"
        gStr += "C " + str(len([s for s in gNodeVector if s != ""])) + "\n"
        gStr += node_str
        
        gStr += "C\nC #REACHES\n"
        gStr += 'C' + str(len(gReachVector)).rjust(7, " ") + "\n"
        gStr += reach_str
        gStr += "C\nC #STORAGES\nC      0\nC\nC #INFLOW/OUTFLOW\nC      0\nC\nC END RORB_GE\nC\n"
        
        # CATG file is graphical and control string concatenated together
        return gStr + catStr
    
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

    def _subAreaStr(self, code: tuple, traveller: Traveller) -> str:
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
    
    def _graphicalNode(self, code, traveller: Traveller, mapping: dict) -> list:
        pos = code[1]
        if (code[0] == 1) or (code[0] == 2) or (code[0] == 5):
            node = traveller.getNode(pos)
            id = f"<{node.name}>"
            mapping[id] = next(self.nodeID)
            x, y = node.coordinates()
            icon_size = 1
            is_basin = int(isinstance(node, Basin))
            is_end = int(node.isOut) if isinstance(node, Confluence) else 0
            ds_node = f"<{traveller.getNode(traveller.down(pos)).name}>"
            name = node.name
            area = node.area if isinstance(node, Basin) else 0.000
            fi = node.fi if isinstance(node, Basin) else 0.000
            prt = 0
            out_excess = 0
            has_comment = 0
            return [id, x, y, icon_size, is_basin, is_end, ds_node, name, area, fi, prt, out_excess, has_comment]
        else:
            return None

    def _graphicalReach(self, code: tuple, traveller: Traveller, mapping) -> list:
        pos = code[1]
        if (code[0] == 1) or (code[0] == 2) or (code[0] == 5):
            try:
                reach = traveller.getReach(pos)
                id = f"<{reach.name}>"
                name = reach.name
                mapping[id] = next(self.reachID)
                ep = reach.getEnd().coordinates()
                sp = reach.getStart().coordinates()
                x = (ep[0] - sp[0]) / 2 + sp[0]
                y = (ep[1] - sp[1]) / 2 + sp[1]
                us_node = f"<{traveller.getNode(pos).name}>"
                ds_node = f"<{traveller.getNode(traveller.down(pos)).name}>"
                translation = 0
                rtype =reach.type
                prt = 0
                ln = reach.length() / 1000
                slope = reach.slope
                ngp = 1
                has_comment = 0
                return [id, name, us_node, ds_node, translation, rtype.value, prt, ln, slope, ngp, has_comment, x, y]
            except KeyError:
                return None
        else:
            return None