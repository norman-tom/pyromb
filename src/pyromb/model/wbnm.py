from .model import Model
from ..core.traveller import Traveller
from ..core.attributes.basin import Basin
from ..core.attributes.confluence import Confluence
from ..core.geometry.point import Point
import numpy as np

class WBNM(Model):
    """The WBNM class creates a templated runfile based on a catchment 
    diagram produced in GIS.

    Only basic functionality is supported at this stage. Storm and 
    Structure blocks will need to be manually entered. 
    """

    def __init__(self):
        self.values = {"VERSION_NUMBER": "2021_000",
                       "CATCHMENT_NAME": "Catchment",
                       "NONLIN_EXP": 0.77,
                       "LAG_PARAM": 1.3,
                       "IMP_LAG_FACT": 0.1,
                       "DISCHARGE_SWITCH": -99,
                       "STREAM_ROUTING_TYPE": "#####ROUTING",
                       "STREAM_LAG_FACTOR": 1}
        self._subAreas: list[SubArea] = []

    def getVector(self, traveller: Traveller):
        self._subAreaFactory(traveller)
        return \
            self._createCodeBlock("preamble")   + \
            self._createCodeBlock("status")     + \
            self._createCodeBlock("display")    + \
            self._createCodeBlock("topology")   + \
            self._createCodeBlock("surface")    + \
            self._createCodeBlock("flowpaths")  + \
            self._createCodeBlock("local_structures")  + \
            self._createCodeBlock("outlet_structures")  + \
            self._createCodeBlock("storm")

    def _subAreaFactory(self, traveller: Traveller):
        """Produces a WBNM subarea.

        A subarea in WBNM is the main structure of the model, this method 
        produces them from the catchment.

        Parameters
        ----------
        traveller : Traveller
            The traveller traversing this catchment.
        """
        
        # go to the very top of the catchment.
        traveller.next()
        # Traverse the catchment and build each subarea.
        while(traveller.position() != traveller._endSentinel):
            if isinstance(traveller.getNode(traveller.position()), Basin):
                subArea = SubArea(traveller.getNode(traveller.position()))
                subArea.streamChannel = len(traveller.up(traveller.position())) != 0
                subArea.dsNodeIndex = self._getDsIndex(traveller, traveller.position())
                self._subAreas.append(subArea)
            traveller.nextAbsolute()
        for s in self._subAreas:
            if s.dsNodeIndex == traveller._endSentinel:
                node = traveller.getNode(traveller.getStart())
                s.dsSubArea = SubArea(Basin("SINK"))
                s.out = Point(node.coordinates()[0], node.coordinates()[1])
            else:
                s.dsSubArea = self._getDSSubArea(traveller, s.dsNodeIndex)
                s.out = self._getOutCoordinate(s)

    def _getDsIndex(self, traveller: Traveller, i: int):
        """Get the index of the downstream subarea from the current position i.
        Confluence are not considered subareas in WBNM and will be passed over. 
        """

        ds = traveller.down(i)
        if isinstance(traveller.getNode(ds), Basin):
            return ds
        if isinstance(traveller.getNode(ds), Confluence):
            if traveller.getNode(ds).isOut() == True:
                return traveller._endSentinel
        return self._getDsIndex(traveller, ds)

    def _getDSSubArea(self, traveller: Traveller, index):
        """Get the downstream subarea corresponding to an index.
        """
        
        node = traveller.getNode(index)
        name = node.name
        for s in self._subAreas:
            if s.name == name:
                return s
    
    def _getOutCoordinate(self, subarea) -> Point:
        """ Determine the out co-ordinate of the sub area. 

        The out location is the scaled vector between the two subarea centroids.
        Scaling of the vector is based on the ratio of subarea sizes.
        Matrx X =   |x2, x1|
                    |y2, y1|

        Vector a =  |alpha |
                    |-alpha|
        alpha = area1 / (area1 + area2)
        where: area1 and area2 are the areas of the upstream subArea and 
        downstream subarea respoectively. 
        """

        # Build X and a
        x1, y1 = subarea.centroid()
        x2, y2 = subarea.dsSubArea.centroid()
        a1 = subarea.area
        a2 = subarea.dsSubArea.area
        X = np.array([[x2, x1], [y2, y1]])
        a = np.array([a1 / (a1 + a2), -a1 / (a1 + a2)])

        # Calculate the out location between the basins. 
        co = (X @ a) + X[:, 1]

        # Return the location as a point
        return Point(co[0], co[1])
            
    def _createValueBlock(self, value) -> str:
        """Create a value block for insertions into a code block.
        
        Value blocks are a single value defined in the Runfile specification. \n
        For example 'NUMBER_OF_SUBAREAS' 
        would make up a single value block, and is part of the 'TOPOLOGY_BLOCK'. 
        The value block is 12 characters wide with space padding.  
        """

        try:
            string = str(value)
            if len(string) > 12:
                raise ValueError(f"Maximum string length is 12 characters, but {value} was {len(value)}")
        except ValueError:
            raise ValueError("cannot parse argument into a string")
        if isinstance(value, float) or isinstance(value, int):
            return string.rjust(12, ' ')
        elif isinstance(string, str):
            return string.ljust(12, ' ')
        else:
            raise ValueError("value must be a string or float")
    
    def _createCodeBlock(self, blockName: str):
        """A code block is the grouping of values per the Runfile specification.

        For example, the STATUS_BLOCK would include the lines: \n
        #####START_STATUS_BLOCK############|###########|###########|###########|\n
        PATHNAME_NAME_OF_CURRENT_RUNFILE  \n
        DATE_OF_LAST_EDIT                 \n
        NAME_OF_LAST_EDITOR               \n
        VERSION_NUMBER FILE_STATUS        \n
        #####END_STATUS_BLOCK##############|###########|###########|###########|\n
        """

        if blockName == "preamble":
            return self._blockPreamble() + "\n\n\n"
        if blockName == "status":
            return self._blockStatus() + "\n\n\n"
        if blockName == "display":
            return self._blockDisplay() + "\n\n\n"
        if blockName == "topology":
            return self._blockTopology() + "\n\n\n"
        if blockName == "surface":
            return self._blockSurface() + "\n\n\n"
        if blockName == "flowpaths":
            return self._blockFlowPaths() + "\n\n\n"
        if blockName == "local_structures":
            return self._blockLocalStructures() + "\n\n\n"
        if blockName == "outlet_structures":
            return self._blockOutletStructures() + "\n\n\n"
        if blockName == "storm":
            return self._blockStorm()
    
    def _blockPreamble(self):
        """Get the PREAMBLE_BLOCK, content is optional so not implementing at this stage
        """

        return \
        "#####START_PREAMBLE_BLOCK##########|###########|###########|###########|\n" + \
        "\n" * 8 + \
        "#####END_PREAMBLE_BLOCK############|###########|###########|###########|"
    
    def _blockStatus(self):
        """ Get the STATUS_BLOCK, only implementing required value blocks
        """

        return \
        "#####START_STATUS_BLOCK############|###########|###########|###########|\n" + \
        "\n" * 3 + \
        f"{self._createValueBlock(self.values['VERSION_NUMBER'])}\n" + \
        "#####END_STATUS_BLOCK##############|###########|###########|###########|"
    
    def _blockDisplay(self):
        """Get the DISPLAY_BLOCK, display block values are optional, not implementing at this stage
        """

        return \
        "#####START_DISPLAY_BLOCK###########|###########|###########|###########|\n" + \
        f"{self._createValueBlock(0)}{self._createValueBlock(0)}{self._createValueBlock(0)}{self._createValueBlock(0)}\n" + \
        f"{self._createValueBlock('none')}\n" + \
        f"{self._createValueBlock(0)}{self._createValueBlock(0)}{self._createValueBlock(0)}{self._createValueBlock(0)}{self._createValueBlock(0)}{self._createValueBlock(0)}\n" + \
        "#####END_DISPLAY_BLOCK#############|###########|###########|###########|"
    
    def _blockTopology(self):
        """Get the TOPOLOGY_BLOCK, only implementing necessary values at this stage. 
        """

        insertSubArea = ""
        for s in self._subAreas:
            insertSubArea += self._createValueBlock(s.name) + \
            self._createValueBlock(round(s.coordinates()[0], 3)) + self._createValueBlock(round(s.coordinates()[1], 3)) + \
            self._createValueBlock(round(s.out.coordinates()[0], 3)) + self._createValueBlock(round(s.out.coordinates()[1], 3)) + \
            " " + self._createValueBlock(s.dsSubArea.name) + "\n"
        return \
        "#####START_TOPOLOGY_BLOCK###########|###########|###########|###########|\n" + \
        f"{self._createValueBlock(len(self._subAreas))} {self._createValueBlock(self.values['CATCHMENT_NAME'])}\n" + \
        f"{insertSubArea}" +\
        "#####END_TOPOLOGY_BLOCK#############|###########|###########|###########|"
    
    def _blockSurface(self):
        insertSurface = ""
        for s in self._subAreas:
            insertSurface += f"{self._createValueBlock(s.name)}{self._createValueBlock(round(s.area * 100, 2))}{self._createValueBlock(round(s.fi, 2))}\n"
        return \
        "#####START_SURFACES_BLOCK##########|###########|###########|###########|\n" + \
        f"{self._createValueBlock(self.values['NONLIN_EXP'])}{self._createValueBlock(self.values['LAG_PARAM'])}{self._createValueBlock(self.values['IMP_LAG_FACT'])}\n" + \
        f"{self._createValueBlock(self.values['DISCHARGE_SWITCH'])}\n" + \
        insertSurface + \
        "#####END_SURFACES_BLOCK############|###########|###########|###########|"

    def _blockFlowPaths(self):
        insertFlow = ""
        for s in self._subAreas:
            if s.streamChannel:
                insertFlow += f"{self._createValueBlock(s.name)}\n" + \
                    f"{self._createValueBlock(self.values['STREAM_ROUTING_TYPE'])}\n" + \
                    f"{self._createValueBlock(self.values['STREAM_LAG_FACTOR'])}\n"
        return \
        "#####START_FLOWPATHS_BLOCK#########|###########|###########|###########|\n" + \
        f"{len([x for x in self._subAreas if x.streamChannel])}\n" + \
        insertFlow + \
        "#####END_FLOWPATHS_BLOCK###########|###########|###########|###########|"
    
    def _blockLocalStructures(self):
        return \
        "#####START_LOCAL_STRUCTURES_BLOCK##|###########|###########|###########|\n" + \
        "0\n" + \
        "#####END_LOCAL_STRUCTURES_BLOCK####|###########|###########|###########|"

    def _blockOutletStructures(self):
       return \
       "#####START_OUTLET_STRUCTURES_BLOCK#|###########|###########|###########|\n" + \
       "0\n" + \
       "#####END_OUTLET_STRUCTURES_BLOCK###|###########|###########|###########|"

    def _blockStorm(self):
        """Stormblock is a template at this stage. Catchment specific information will  
        eventually be injected into this block. This block will require manual configuration in
        the WBNM runfile. 
        """

        return \
        "#####START_STORM_BLOCK#############|###########|###########|###########|\n" + \
        f"{self._createValueBlock(1)}\n" + \
        "#####START_STORM#1\n" + \
        "1%AEP dura/patt spectrum  - losses 27/4 GLOBAL - ARF = Calculated from ARR\n" + \
        f"{self._createValueBlock(1.0)}\n" + \
        f"{self._createValueBlock(5.0)}\n" + \
        "#####START_DESIGN_RAIN_ARR\n" + \
        f"{self._createValueBlock(1.0)}{self._createValueBlock(-1)}{self._createValueBlock(-1)}{self._createValueBlock(-1)}\n" + \
        "IFD_DATA_IN_GAUGE_FILES\n" + \
        f"{self._createValueBlock(2)}\n" + \
        "sorell_lower\n" + \
        "sorell_upper\n" + \
        "PAT_DATA_IN_REGION_FILE\n" + \
        "sorell_increments.csv\n" + \
        "CAT_DATA_IN_CATCHMENT_FILE\n" + \
        "sorell_catchment_data.txt\n" + \
        "#####END_DESIGN_RAIN_ARR\n" + \
        "#####START_CALC_RAINGAUGE_WEIGHTS\n" + \
        "#####END_CALC_RAINGAUGE_WEIGHTS\n" + \
        "#####START_LOSS_RATES\n" + \
        f"{self._createValueBlock('GLOBAL')}{self._createValueBlock(27.0)}{self._createValueBlock(4.0)}{self._createValueBlock(0.0)}\n" + \
        "#####END_LOSS_RATES\n" + \
        "#####START_RECORDED_HYDROGRAPHS\n" + \
        f"{self._createValueBlock(0)}\n" + \
        "#####END_RECORDED_HYDROGRAPHS\n" + \
        "#####START_IMPORTED_HYDROGRAPHS\n" + \
        f"{self._createValueBlock(0)}\n" + \
        "#####END_IMPORTED_HYDROGRAPHS\n" + \
        "#####END_STORM#1\n" + \
        "#####END_STORM_BLOCK###############|###########|###########|###########|"

class SubArea(Basin):
    """SubArea as defined by the WBNM specification. 
    
    A subclass of  Basin, SubArea is the main object in the WBNM model. The SubArea
    generates a hydrograph for the SubArea and routes the flow to the downstream 
    SubArea or to the sink. Refer to WBNM manual for details. 

    SubArea is generated from a Basin retrieved from the catchment. The SubArea has
    some additional attributes to the Basin used by WBNM.
    """

    def __init__(self, basin: Basin):
        self._x: float = basin._x
        self._y:float = basin._y
        self._type: int = basin._type
        self._name: str = basin._name
        self._out: Point
        self._streamChannel: bool
        self._area: float = basin._area
        self._fi: float = basin._fi
        self._dsNodeIndex: int
        self._dsSubArea: SubArea

    @property
    def x(self) -> tuple:
        return self._x
    
    @x.setter
    def x(self, value: tuple):
        self._x = value

    @property
    def y(self) -> tuple:
        return self._y
    
    @y.setter
    def y(self, value: tuple):
        self._y = value

    @property
    def out(self) -> Point:
        return self._out
    
    @out.setter
    def out(self, value: Point):
        self._out = value

    @property
    def streamChannel(self) -> bool:
        return self._streamChannel
    
    @streamChannel.setter
    def streamChannel(self, value: bool):
        self._streamChannel = value

    @property
    def area(self) -> float:
        return self._area
    
    @area.setter
    def area(self, value: float):
        self._area = value

    @property
    def fractionImp(self) -> float:
        return self._fi
    
    @fractionImp.setter
    def fractionImp(self, value: float):
        self._fi = value

    @property
    def dsNodeIndex(self):
        return self._dsNodeIndex
    
    @dsNodeIndex.setter
    def dsNodeIndex(self, subarea: int):
        self._dsNodeIndex = subarea

    @property
    def dsSubArea(self):
        return self._dsSubArea
    
    @dsSubArea.setter
    def dsSubArea(self, subarea):
        self._dsSubArea = subarea

    def centroid(self):
        return (self.x, self.y)