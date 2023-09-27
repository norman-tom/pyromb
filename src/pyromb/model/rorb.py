from .model import Model
from ..core.traveller import Traveller
from ..core.attributes.basin import Basin
from ..core.attributes.confluence import Confluence
from ..core.attributes.reach import ReachType
from .. import resources

class VectorBlock():
    def __init__(self) -> None:
        self._storedHydro: list[int] = []
        self._runningHydro: bool = False
        self._stateVector = []
        self._controlVector = []
    
    def step(self, traveller: Traveller) -> None:
        """ Calculate action to take at the current node and store it in the VectorBlock's state.
        
        Step is to be used at every update of the Traveller so that the control vector block used 
        by RORB can be built when traversing the catchment is finished.

        Parameters
        ----------
        traveller : Traveller
            The traveller for the catchment being built. 
        """

        self._state(traveller)
        self._control(self._stateVector[-1], traveller)
    
    def build(self, traveller) -> str:
        """ Builds the vector block string.
        
        Parameters
        ----------
        traveller: Traveller
            The traveller that traversed the catchment.
            
        Returns
        -------
        str
            The vector block string to be used on the .catg file 
        """

        vectorStr = resources.rorb.VECTOR_HEADER
        for s in self._controlVector:
            vectorStr += s + "\n"
        vectorStr += self._subAreaStr(self._stateVector, traveller) + "\n"
        vectorStr += self._fracImpStr(self._stateVector, traveller) + "\n"
        
        return vectorStr

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
        
        Parameters
        ----------
        traveller : Traveller
            The traveller traversing this catchment        
        """

        i = traveller._pos
        up = traveller.top(i)
        
        if i == traveller._endSentinel:
            ret = (0, i)
        elif (self._runningHydro == False) and (isinstance(traveller._catchment._vertices[i], Basin)):
            self._runningHydro = True
            traveller.next()
            ret = (1, i)
        elif (self._storedHydro) and (self._storedHydro[-1] == i) and (self._runningHydro):
            self._storedHydro.pop()
            ret = (4, i)
        elif (self._runningHydro) and (isinstance(traveller._catchment._vertices[i], Basin)) and (up == i):
            traveller.next()
            ret = (2, i)
        elif (self._runningHydro) and (up != i):
            self._storedHydro.append(i)
            self._runningHydro = False
            traveller.next()
            ret = (3, i)
        elif (self._runningHydro) and (isinstance(traveller._catchment._vertices[i], Confluence)) and (up == i):
            traveller.next()
            ret = (5, i) 
        
        self._stateVector.append(ret)
        
    def _control(self, code: tuple, traveller: Traveller) -> str:
        """Format a control vector string according to the RORB manual Table 5-1 p.52 (version 6)

        Parameters
        ----------
        code : tuple
            A coded tuple with

            [0] - The command code.

            [1] - The position of the traveller when the command code was created.

        traveller : Traveller
            The traveller traversing this catchment
        """
        if (code[0] == 1) or (code[0] == 2) or (code[0] == 5):
            try:
                r = traveller.getReach(code[1])
                if (r.type == ReachType.NATURAL) or (r.type == ReachType.DROWNED):
                    ret = "{},{},{},-99".format(code[0], r.type.value, round(r.length() / 1000, 3))
                else:
                    ret = "{},{},{},{},-99".format(code[0], r.type.value, round(r.length() / 1000, 3), r.getSlope())
            except:
                ret = "{}\nout\n{}".format(7, 0)
        
        if (code[0] == 3) or (code[0] == 4):
            ret = "{}".format(code[0])
        
        if (code[0] == 0):
            ret = "{}\nout\n'{}".format(7, 0)
        
        self._controlVector.append(ret)
    
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
    
    @property
    def state(self):
        return (self._stateVector) 
    
    @state.setter
    def state(self):
        raise AttributeError('State vector is generated not set')

class GraphicsBlock():
    def __init__(self) -> None:
        self._idMap = {}
        self._nodeVector = []
        self._reachVector = []
        self._nodeID = self._idGenerator()
        self._reachID = self._idGenerator()

    def step(self, code: tuple, traveller: Traveller):
        self._nodeDisplay(code, traveller)
        self._reachDisplay(code, traveller)
    
    def build(self):
        # Replace ID tags with ID numbers
        for i, row in enumerate(self._nodeVector):
            for j, item in enumerate(row):
                if item in self._idMap:
                    self._nodeVector[i][j] = self._idMap[item]
        
        for i, row in enumerate(self._reachVector):
            for j, item in enumerate(row):
                if item in self._idMap:
                    self._reachVector[i][j] = self._idMap[item]
                elif item in self._idMap:
                    self._reachVector[i][j] = self._idMap[item]
        
        # Normalise the co-ordinates
        xs = [x[1] for x in self._nodeVector]
        ys = [y[2] for y in self._nodeVector]
        scale_x = max(xs) - min(xs)
        scale_y = max(ys) - min(ys)

        for i, row in enumerate(self._nodeVector):
            self._nodeVector[i][1] = (row[1] - min(xs)) / scale_x * 100
            self._nodeVector[i][2] = (row[2] - min(ys)) / scale_y * 100
        
        for i, row in enumerate(self._reachVector):
            self._reachVector[i][11] = (row[11] - min(xs)) / scale_x * 100
            self._reachVector[i][12] = (row[12] - min(ys)) / scale_y * 100
        
        nodeStr = ""
        for row in self._nodeVector:
            nodeStr += resources.rorb.LEADING_TOKEN
            nodeStr  += str(row[0]).rjust(7, " ")
            nodeStr += str(round(row[1], 3)).rjust(15, " ")
            nodeStr += str(round(row[2], 3)).rjust(15, " ")
            nodeStr += ("%.3f" % round(row[3], 3)).rjust(15, " ")
            nodeStr += str(row[4]).rjust(2, " ")
            nodeStr += str(row[5]).rjust(2, " ")
            nodeStr += str(row[6]).rjust(6, " ")
            nodeStr += " "
            nodeStr += str(row[7]).ljust(2, " ")
            nodeStr += ("%.6f" % round(row[8], 6)).rjust(33, " ")
            nodeStr += ("%.6f" % round(row[9], 6)).rjust(15, " ")
            nodeStr += str(row[10]).rjust(3, " ")
            nodeStr += str(row[11]).rjust(3, " ")
            nodeStr += str(row[12]).rjust(3, " ")
            nodeStr += '\n' + resources.rorb.LEADING_TOKEN + '\n'
        
        reachStr = ""
        for row in self._reachVector:
            reachStr += resources.rorb.LEADING_TOKEN
            reachStr += str(row[0]).rjust(7, " ")
            reachStr += " "
            reachStr += str(row[1]).ljust(8, " ")
            reachStr += str(row[2]).rjust(18, " ")
            reachStr += str(row[3]).rjust(6, " ")
            reachStr += str(row[4]).rjust(15, " ")
            reachStr += str(row[5]).rjust(2, " ")
            reachStr += str(row[6]).rjust(2, " ")
            reachStr += ("%.3f" % round(row[7], 3)).rjust(15, " ")
            reachStr += ("%.3f" % round(row[8], 3)).rjust(15, " ")
            reachStr += str(row[9]).rjust(6, " ")
            reachStr += str(row[10]).rjust(3, " ")
            reachStr += '\n' + resources.rorb.LEADING_TOKEN
            reachStr += ("%.3f" % round(row[11], 3)).rjust(16, " ")
            reachStr += '\n' + resources.rorb.LEADING_TOKEN
            reachStr += ("%.3f" % round(row[12], 3)).rjust(16, " ")
            reachStr += '\n'

        graphicalStr = resources.rorb.GRAPHICAL_HEADER
        graphicalStr += resources.rorb.NODE_HEADER
        graphicalStr += resources.rorb.LEADING_TOKEN + " " + str(len(self._nodeVector)) + "\n"
        graphicalStr += nodeStr
        
        graphicalStr += resources.rorb.LEADING_TOKEN + "\n" 
        graphicalStr += resources.rorb.REACH_HEADER
        graphicalStr += resources.rorb.LEADING_TOKEN + str(len(self._reachVector)).rjust(7, " ") + "\n"
        graphicalStr += reachStr
        graphicalStr += resources.rorb.GRAPHICAL_TAIL

        return graphicalStr

    def _nodeDisplay(self, code, traveller: Traveller):
        pos = code[1]
        if (code[0] == 1) or (code[0] == 2) or (code[0] == 5):
            node = traveller.getNode(pos)
            id = f"<{node.name}>"
            self._idMap[id] = next(self._nodeID)
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
            self._nodeVector.append([id, x, y, icon_size, is_basin, is_end, ds_node, name, area, fi, prt, out_excess, has_comment])

    def _reachDisplay(self, code: tuple, traveller: Traveller) -> list:
        pos = code[1]
        if (code[0] == 1) or (code[0] == 2) or (code[0] == 5):
            try:
                reach = traveller.getReach(pos)
                id = f"<{reach.name}>"
                name = reach.name
                self._idMap[id] = next(self._reachID)
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
                self._reachVector.append([id, name, us_node, ds_node, translation, rtype.value, prt, ln, slope, ngp, has_comment, x, y])
            except KeyError:
                pass
    
    @staticmethod
    def _idGenerator():
        i = 0
        while True:
            i += 1
            yield i

class RORB(Model):
    """Create a RORB control vector for input to the RORB runoff routing model. 
    """
    
    def __init__(self):
        pass
    
    def getVector(self, traveller: Traveller) -> str:
        
        traveller.next()
        vectorBlock = VectorBlock()
        graphicBlock = GraphicsBlock()

        while(traveller._pos != traveller._endSentinel):
            vectorBlock.step(traveller)
            graphicBlock.step(vectorBlock.state[-1], traveller)

        return graphicBlock.build() + vectorBlock.build(traveller)