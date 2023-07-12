from .attributes.basin import Basin
from .attributes.confluence import Confluence
from .attributes.node import Node
from .attributes.reach import Reach
from ..math import geometry
import numpy as np

class Catchment:
    """The Catchment is a tree of attributes which describes how water 
    flows through the model and the entities which act upon it. 

    Parameters
    ----------
    confluences : list[Confluence]
        The Confluences in the catchment
    basins : list[Basin]
        The Basins in the catchment
    reaches: list[Reach]
        The Reaches in the catchment
    """

    def __init__(self, confluences: list = [], basins: list = [],  reaches: list = []) -> None:
        self._edges: list[Reach] = reaches
        self._vertices: list[Node] = confluences + basins
        self._incidenceMatrixDS: list = []
        self._incidenceMatrixUS: list = []
        self._out = 0
        self._endSentinel = -1

    def connect(self) -> tuple:
        """Connect the individual attributes to create the catchment. 

        Returns
        -------
        tuple
            (downstream, upstream) incidence matricies of the catchment tree.
        """
        
        connectionMatrix = np.zeros((len(self._vertices), len(self._edges)), dtype=int)
        for i, edge in enumerate(self._edges):
            s = edge.getStart()
            e = edge.getEnd()
            minStart = 999
            minEnd = 999
            closestStart = 0
            closestEnd = 0
            for j, vert in enumerate(self._vertices):
                tempStart = geometry.length([vert, s])
                tempEnd = geometry.length([vert, e])
                if tempStart < minStart:
                    closestStart = j
                    minStart = tempStart
                if tempEnd < minEnd:
                    closestEnd = j
                    minEnd = tempEnd
            connectionMatrix[closestStart][i] = 1
            connectionMatrix[closestEnd][i] = 2   

        
        # Find the 'out' node
        # Used to determine the starting point of breath first search
        # And subsequently the direction of flow  
        for k, conf in enumerate(self._vertices):  
            if isinstance(conf, Confluence):
                if conf.isOut:
                    self._out = k
                    break
        
        
        # Determine incidence matrix relating reaches to nodes and map downstream direction between elements
        # Matrix I (m * m - 1)
        # m = nodes
        # n = reaches
        # value of m n =  the index of the downstream node
        # Think about I as relating upstream nodes (m) to downstream nodes (m n) through reach (n) 
        # (m n) of -1 indicates no downstream node for relationship m n
        newIncidenceDS = np.zeros((len(self._vertices), len(self._edges)), dtype=int)
        newIncidenceDS.fill(self._endSentinel)
        newIncidenceUS = newIncidenceDS.copy()
        queue = []
        colour = np.zeros((len(self._vertices), len(self._edges)))
        i = self._out
        j = 0
        queue.append((i, j))
        while(len(queue) != 0):
            #Move in the n direction
            u = queue.pop()
            idxi = u[0]
            j = u[1]
            for k in range(len(connectionMatrix[u[0]])):
                idxj = j % len(connectionMatrix[idxi])
                if connectionMatrix[idxi][idxj] > 0:
                    if colour[idxi][idxj] == 0:
                        colour[idxi][idxj] = 1
                        u = (idxi, idxj)
                        queue.append(u)
                j += 1

            #Move in the m direction
            i = u[0]
            idxj = u[1]
            for l in range(len(connectionMatrix)):
                idxi = i % len(connectionMatrix)
                if connectionMatrix[idxi][idxj] > 0:
                    if colour[idxi][idxj] == 0:
                        colour[idxi][idxj] = 1
                        queue.append((idxi, idxj))
                        newIncidenceUS[u[0]][u[1]] = idxi
                        newIncidenceDS[idxi][idxj] = u[0]
                i += 1
        self._incidenceMatrixDS = newIncidenceDS.copy()
        self._incidenceMatrixUS = newIncidenceUS.copy()
        
        return (self._incidenceMatrixDS, self._incidenceMatrixUS)