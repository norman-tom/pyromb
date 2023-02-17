from qgis2rorb.model.model import Model
from qgis2rorb.core.traveller import Traveller
from qgis2rorb.core.attributes.basin import Basin
from qgis2rorb.core.attributes.confluence import Confluence

class WBNM(Model):
    def __init__(self):
        self.values = {"VERSION_NUMBER": "test",
                       "NUMBER_OF_SUBAREAS": "undefined"}
        self._subAreas = []

    def getVector(self, traveller: Traveller):
        self._subAreaFactory(traveller)
        return \
            self._createCodeBlock("preamble") + self._createCodeBlock("status") + \
            self._createCodeBlock("display") + self._createCodeBlock("topology")

    def _subAreaFactory(self, traveller: Traveller):
        traveller.nextAbsolute()
        while(traveller.position() != traveller._endSentinel):
            if isinstance(traveller.getNode(traveller.position()), Basin):
                subArea = SubArea(traveller.getNode(traveller.position()))
                subArea.bottomCoordinate = traveller.getNode(traveller.down(traveller.position())).coordinates()
                subArea.streamChannel = traveller.position() != traveller.nextAbsolute()
                subArea.dsNodeIndex = self._getDsIndex(traveller, traveller.position())
                self._subAreas.append(subArea)
            traveller.next()

        ### TODO Need to loop through subarea again and attached the DS index with a concrete SubArea. 

    def _getDsIndex(self, traveller: Traveller, i: int):
        """
        Get the index of the downstream subarea from the current position i.
        Confluence are not considered subareas in WBNM and will be passed over. 
        """
        ds = traveller.down(i)
        if isinstance(traveller.getNode(ds), Basin):
            return ds
        if isinstance(traveller.getNode(ds), Confluence):
            if traveller.getNode(ds).isOut() == True:
                return traveller._endSentinel
        return self._getDsIndex(traveller, ds)
            
    def _createValueBlock(self, value: str) -> str:
        """
        Create a value block for insertions into a code block.
        Value blocks are a single value defined in the Runfile specification. \n
        For example 'NUMBER_OF_SUBAREAS' 
        would make up a single value block, and is part of the 'TOPOLOGY_BLOCK'. The value block is 12 characters wide with space padding.  
        """
        try:
            value = str(value)
        except:
            ValueError("cant cast to string")
        if len(value) > 12:
            raise ValueError(f"Maximum string length is 12 characters, but {value} was {len(value)}")
        return value.ljust(12, ' ')
    
    def _createCodeBlock(self, blockName: str):
        """
        A code block is the grouping of values per the Runfile specification.\n
        For example, the STATUS_BLOCK would include 
        the lines: \n
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
    

    def _blockPreamble(self):
        """
        Get the PREAMBLE_BLOCK, content is optional so not implementing at this stage
        """
        return \
        "#####START_PREAMBLE_BLOCK##########|###########|###########|###########|\n" + \
        "#####END_PREAMBLE_BLOCK############|###########|###########|###########|"
    
    def _blockStatus(self):
        """
        Get the STATUS_BLOCK, only implementing required value blocks
        """
        if self.values["VERSION_NUMBER"] == "undefined": raise ValueError("VERSION_NUMBER must be defined")
        return \
        "#####START_STATUS_BLOCK############|###########|###########|###########|\n" + \
        f"{self._createValueBlock(self.values['VERSION_NUMBER'])}\n " + \
        "#####END_STATUS_BLOCK##############|###########|###########|###########|"
    
    def _blockDisplay(self):
        """
        Get the DISPLAY_BLOCK, display block values are optional, not implementing at this stage
        """
        return \
        "#####START_DISPLAY_BLOCK###########|###########|###########|###########|\n" + \
        "#####END_DISPLAY_BLOCK#############|###########|###########|###########|"
    
    def _blockTopology(self):
        """
        Get the TOPOLOGY_BLOCK, only implementing necessary values at this stage. 
        """
        insertSubArea = ""
        for s in self._subAreas:
            insertSubArea += self._createValueBlock(s.getName()) + \
            self._createValueBlock(round(s.coordinates()[0], 3)) + self._createValueBlock(round(s.coordinates()[1], 3)) + \
            self._createValueBlock(0) + self._createValueBlock(0) + \
            self._createValueBlock("bob") + "\n"
        return \
        "#####START_TOPOLOGY_BLOCK###########|###########|###########|###########|\n" + \
        f"{self._createValueBlock(len(self._subAreas))}\n" + \
        f"{insertSubArea}" +\
        "#####END_TOPOLOGY_BLOCK#############|###########|###########|###########|"
    
class SubArea(Basin):
    """
    SubArea as defined by the WBNM specification, is a subcatchment of the basin which generates a hydrograph and routes 
    the flow to the downstream subarea or to the sink. 
    """
    def __init__(self, basin: Basin):
        self._x: float = basin._x
        self._y:float = basin._y
        self._type: int = basin._type
        self._name: str = basin._name
        self._bottomCoordinate: tuple
        self._streamChannel: bool
        self._area: float = basin._area
        self._fi: float = basin._fi
        self._dsNodeIndex: int
        self._dsSubArea: SubArea

        @property
        def centroid(self) -> tuple:
            return (self._x, self._y)
        
        @centroid.setter
        def centroid(self, value: tuple):
            self._centroid = value

        @property
        def bottomCoordinate(self) -> tuple:
            return self._bottomCoordinate
        
        @bottomCoordinate.setter
        def bottomCoordinate(self, value: tuple):
            self._bottomCoordinate = value

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
        def dsNodeIndex(self) -> SubArea:
            return self._dsSubArea
        
        @dsNodeIndex.setter
        def dsNodeIndex(self, subarea: int):
            self._dsNodeIndex = subarea

        @property
        def dsSubArea(self) -> SubArea:
            return self._dsSubArea
        
        @dsSubArea.setter
        def dsSubArea(self, subarea: SubArea):
            self._dsSubArea = subarea