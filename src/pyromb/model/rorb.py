from .model import Model
from ..core.traveller import Traveller
from ..core.attributes.basin import Basin
from ..core.attributes.confluence import Confluence
from ..core.attributes.reach import ReachType
from .. import resources
import json
import os

class VectorBlock():
    """
    Builds the vector block for the RORB control file.
    """

    def __init__(self) -> None:
        self._storedHydro: list[int] = []
        self._runningHydro: bool = False
        self._stateVector = []
        self._controlVector = []

        resources_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
        with open(os.path.join(resources_dir, 'formatting.json'), 'r') as f:
            self._formattingOptions = json.load(f)
    
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

        vectorStr = "0\n"                   # Start with code 0, reach types are specified in the control block.
        for s in self._controlVector:
            vectorStr += f"{s}\n"
        vectorStr += f"{self._subAreaStr(self._stateVector, traveller)}\n{self._fracImpStr(self._stateVector, traveller)}\n"
        return vectorStr

    def _state(self, traveller: Traveller) -> None:
        """ Store the current state of the traveller within the catchment at each time step.

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
        
    def _control(self, code: tuple, traveller: Traveller) -> None:
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
                    ret = f"{code[0]},{r.type.value},{r.length() / 1000:.3f},-99"
                else:
                    ret = f"{code[0]},{r.type.value},{r.length() / 1000:.3f},{r.getSlope()},-99"
            except:
                ret = f"{7}\n\n{0}"
        
        if (code[0] == 3) or (code[0] == 4):
            ret = f"{code[0]}"
        
        if (code[0] == 0):
            ret = f"{7}\n\n'{0}"
        
        self._controlVector.append(ret)
    
    def _subAreaStr(self, code: tuple, traveller: Traveller) -> str:
        """Format the subarea string according to the RORB manual

        Parameters
        ----------
        code : list
            A list of the states acting on the catchment in the order of travel.
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
                areaStr += f"{traveller._catchment._vertices[c[1]].area:{self._formattingOptions['area_table']['percision']}},"
        areaStr += '-99'

        values = areaStr.split(',')
        formatted_values = resources.rorb.AREA_TABLE_HEADER
        for i, val in enumerate(values[:-1]):
            if (i % 5 == 0) and (i != 0):
                formatted_values += f"\n{val:{self._formattingOptions['area_table']['column_width']}},"
            else:
                formatted_values += f"{val:{self._formattingOptions['area_table']['column_width']}},"
        formatted_values += f"\n{values[-1]}"

        return formatted_values
    
    def _fracImpStr(self, code: list, traveller: Traveller) -> str:
        """
        Format the fraction impervious string according to the RORB manual.
        
        Parameters
        ----------
        code : list
            A list of the states acting on the catchment in the order of travel.
        traveller : Traveller
            The traveller traversing this catchment.
            
        Returns
        -------
        str
            A fraction impervious string for the control file.
        """

        fStr = f"{resources.rorb.FI_TABLE_HEADER} 1,"
        for c in code:
            if (c[0] == 1) or (c[0] == 2):
                fStr += f"{traveller._catchment._vertices[c[1]].fi:{self._formattingOptions['fi_table']['percision']}},"
        fStr += ' -99'

        values = fStr.split(',')
        formatted_values = f"{values[0]} ,\n"
        for i, val in enumerate(values[1:-1]):
            if (i % 5 == 0) and (i != 0):
                formatted_values += f"\n{val:{self._formattingOptions['fi_table']['column_width']}},"
            else:
                formatted_values += f"{val:{self._formattingOptions['fi_table']['column_width']}},"
        formatted_values += f"\n{values[-1]}"

        return formatted_values
    
    @property
    def state(self):
        return (self._stateVector) 
    
    @state.setter
    def state(self):
        raise AttributeError('State vector is generated not set')

class GraphicsBlock():
    """
    Builds the graphics block for the RORB control file.
    """

    def __init__(self) -> None:
        self._idMap = {}
        self._nodeVector = []
        self._reachVector = []
        self._nodeID = self._idGenerator()
        self._reachID = self._idGenerator()

        resources_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
        with open(os.path.join(resources_dir, 'formatting.json'), 'r') as f:
            self._formattingOptions = json.load(f)

    def step(self, code: tuple, traveller: Traveller):
        """
        Determine graphical information at each catchment position while travelling.

        Parameters
        ----------
        code : tuple
            A tuple containing the code for the graphics block.
        traveller : Traveller
            The traveller object which traverse the catchment.
        """

        self._nodeDisplay(code, traveller)
        self._reachDisplay(code, traveller)
    
    def build(self):
        """Build the graphical block string for the .catg file.
        
        Returns
        -------
        str
            The graphical block string for the .catg file.
        """

        self._replaceIDTags(self._nodeVector)
        self._replaceIDTags(self._reachVector)
        self._normalizeCoordinates()

        graphicalStr = (
            f"{resources.rorb.GRAPHICAL_HEADER}"
            f"{self._generateNodeString()}"
            f"{resources.rorb.LEADING_TOKEN}\n"
            f"{self._generateReachString()}"
            f"{resources.rorb.GRAPHICAL_TAIL}" 
        )

        return graphicalStr

    def _replaceIDTags(self, vector: list):
        """
        Replace the ID tags in the vector with the ID generated by the ID generator.
        
        Parameters
        ----------
        vector : list
            The vector to replace the ID tags in.
        """

        for i, row in enumerate(vector):
            for k, v in row.items():
                if v in self._idMap:
                    vector[i][k] = self._idMap[v]

    def _normalizeCoordinates(self, scale: float = 90.0, shift: float = 2.5):
        """
        Normalize the coordinates of the catchment to fit within the RORB GE window.

        Parameters
        ----------
        scale : int
            The scale factor to apply to the coordinates.
        """

        xs = [row['x'] for row in self._nodeVector]
        ys = [row['y'] for row in self._nodeVector]
        scale_x = max(xs) - min(xs)
        scale_y = max(ys) - min(ys)

        for i, row in enumerate(self._nodeVector):
            self._nodeVector[i]['x'] = (row['x'] - min(xs)) / scale_x * scale + shift
            self._nodeVector[i]['y'] = (row['y'] - min(ys)) / scale_y * scale + shift

        for i, row in enumerate(self._reachVector):
            self._reachVector[i]['x'] = (row['x'] - min(xs)) / scale_x * scale + shift
            self._reachVector[i]['y'] = (row['y'] - min(ys)) / scale_y * scale + shift
    
    def _generateNodeString(self):
        """
        Generates the display information string which is a representation of the node data.

        Returns:
            A formated display string for the node data, compatible with RORB GE.
        """

        nodeStr = resources.rorb.NODE_HEADER
        nodeStr += f"{resources.rorb.LEADING_TOKEN}{len(self._nodeVector):>7}\n"
        
        for row in self._nodeVector:
            nodeStr += resources.rorb.LEADING_TOKEN
            for item in row:
                nodeStr += f"{row[item]:{self._formattingOptions['node'][item]}}" 
            nodeStr += f"\n{resources.rorb.LEADING_TOKEN}\n"
        
        return nodeStr
    
    def _generateReachString(self):
        """
        Generates the display information string which is a representation of the reach data.

        Returns:
            A formated display string for the reach data, compatible with RORB GE.
        """

        reachStr = resources.rorb.REACH_HEADER
        reachStr += f"{resources.rorb.LEADING_TOKEN}{len(self._reachVector):>7}\n"

        for row in self._reachVector:
            reachStr += resources.rorb.LEADING_TOKEN
            for item in row:
                if (item == 'x') or (item == 'y'):
                    reachStr += f"\n{resources.rorb.LEADING_TOKEN}" 
                reachStr += f"{row[item]:{self._formattingOptions['reach'][item]}}"
            reachStr += "\n"

        return reachStr

    def _nodeDisplay(self, code, traveller: Traveller):
        """
        Add graphic information for a node to the node vector.

        The node vector holds the ordered information, in order of tranvel, for each node in the catchment.

        Parameters
        ----------
        code : tuple
            A tuple containing the code for the graphics block. Contains position information for the node to be displayed.
        traveller : Traveller
            The traveller object which traversed the catchment.
        """

        pos = code[1]
        if (code[0] == 1) or (code[0] == 2) or (code[0] == 5):
            node = traveller.getNode(pos)
            x, y = node.coordinates()
            prnt = 70 if (isinstance(node, Confluence) and node.isOut) else 0

            # Order is important here.
            data = {
                'id': f"<{node.name}>",
                'x': x,
                'y': y,
                'icon': 1,
                'basin': int(isinstance(node, Basin)),
                'end': int(node.isOut) if isinstance(node, Confluence) else 0,
                'ds': f"<{traveller.getNode(traveller.down(pos)).name}>",
                'name': f" {node.name}",                                        # Leading space is important here.
                'area': node.area if isinstance(node, Basin) else 0,
                'fi': node.fi if isinstance(node, Basin) else 0,
                'print': prnt,
                'excess': 0,
                'comment': 0
            }

            self._idMap[data['id']] = next(self._nodeID)
            self._nodeVector.append(data)

    def _reachDisplay(self, code: tuple, traveller: Traveller) -> list:
        """
        Add graphic information for a reach to the reach vector.
        
        The reach vector holds the ordered information, in order of travel, for each reach in the catchment.
        
        Parameters
        ----------
        code : tuple
            A tuple containing the code for the graphics block. Contains position information for the reach to be displayed.
        traveller : Traveller
            The traveller object which traversed the catchment.
        """

        pos = code[1]
        if (code[0] == 1) or (code[0] == 2) or (code[0] == 5):
            try:
                reach = traveller.getReach(pos)
                ep = reach.getEnd().coordinates()
                sp = reach.getStart().coordinates()
                x = (ep[0] - sp[0]) / 2 + sp[0]
                y = (ep[1] - sp[1]) / 2 + sp[1]

                # Order is important here.
                data = {
                    'id': f"<{reach.name}>",
                    'name': f" {reach.name}",                                    # Leading space is important here.
                    'us': f"<{traveller.getNode(pos).name}>",
                    'ds': f"<{traveller.getNode(traveller.down(pos)).name}>",
                    'translation': 0,
                    'type': reach.type.value,
                    'print': 0,
                    'length': reach.length() / 1000,
                    'slope': reach.slope,
                    'npoints': 1,
                    'comment': 0,
                    'x': x,
                    'y': y,
                }

                self._idMap[data['id']] = next(self._reachID)
                self._reachVector.append(data)

            except KeyError:
                pass
    
    @staticmethod
    def _idGenerator():
        """
        Generate a unique ID for each node and reach in the catchment.
        """

        i = 0
        while True:
            i += 1
            yield i

class RORB(Model):
    """
    Create a RORB GE control vector for input to the RORB runoff routing model. 
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