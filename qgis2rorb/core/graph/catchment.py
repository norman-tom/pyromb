from shutil import ReadError

from matplotlib.cbook import Stack
from qgis2rorb.core.attributes.basin import Basin
from qgis2rorb.core.attributes.confluence import Confluence
from qgis2rorb.core.attributes.node import Node
from qgis2rorb.core.attributes.reach import Reach
from qgis2rorb.math import geometry
import numpy as np

class Catchment:
    """
    The representation of the catchment as an incidence matrix
  
    """
    def __init__(self, confluences: list[Confluence] = [], basins: list[Basin] = [],  reaches: list[Reach] = []) -> None:
        self._edges: list[Reach] = reaches
        self._vertices: list[Node] = confluences + basins
        self._incidenceMatrixDS: list = []
        self._incidenceMatrixUS: list = []
        self._out = 0
        self._endSentinel = -1

    def connect(self) -> tuple:
        """
        Determine which nodes are connected to which reaches.
        Uses nearest neighbour, k = 1
        US = 1
        DS = 2
        not connected = 0
        """
        __connectionMatrix = np.zeros((len(self._vertices), len(self._edges)), dtype=int)
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
            __connectionMatrix[closestStart][i] = 1
            __connectionMatrix[closestEnd][i] = 2   

        """
        Find the 'out' node
        Used to determine the starting point of breath first search
        and subsequently the direction of flow  
        """
        for k, conf in enumerate(self._vertices):  
            if conf.getType() == 1:
                if conf.isOut():
                    self._out = k
                    break
        
        """
        Determine incidence matrix relating reaches to nodes and map downstream direction between elements
        Matrix I (m * m - 1)
        m = nodes
        n = reaches
        value of m n =  the index of the downstream node
        Think about I as relating upstream nodes (m) to downstream nodes (m n) through reach (n) 
        (m n) of -1 indicates no downstream node for relationship m n
        """
        __newIncidenceDS = np.zeros((len(self._vertices), len(self._edges)), dtype=int)
        __newIncidenceDS.fill(self._endSentinel)
        __newIncidenceUS = __newIncidenceDS.copy()
        __queue = []
        __colour = np.zeros((len(self._vertices), len(self._edges)))
        i = self._out
        j = 0
        __queue.append((i, j))
        while(len(__queue) != 0):
            #Move in the n direction
            u = __queue.pop()
            idxi = u[0]
            j = u[1]
            for k in range(len(__connectionMatrix[u[0]])):
                idxj = j % len(__connectionMatrix[idxi])
                if __connectionMatrix[idxi][idxj] > 0:
                    if __colour[idxi][idxj] == 0:
                        __colour[idxi][idxj] = 1
                        u = (idxi, idxj)
                        __queue.append(u)
                j += 1

            #Move in the m direction
            i = u[0]
            idxj = u[1]
            for l in range(len(__connectionMatrix)):
                idxi = i % len(__connectionMatrix)
                if __connectionMatrix[idxi][idxj] > 0:
                    if __colour[idxi][idxj] == 0:
                        __colour[idxi][idxj] = 1
                        __queue.append((idxi, idxj))
                        __newIncidenceUS[u[0]][u[1]] = idxi
                        __newIncidenceDS[idxi][idxj] = u[0]
                i += 1
        self._incidenceMatrixDS = __newIncidenceDS.copy()
        self._incidenceMatrixUS = __newIncidenceUS.copy()
        
        return (self._incidenceMatrixDS, self._incidenceMatrixUS)