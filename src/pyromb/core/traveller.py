import numpy as np
from .attributes.reach import Reach
from .attributes.node import Node
from .catchment import Catchment
from ..model.model import Model

class Traveller:
    """The Traveller walks through the catchment, proceeding from the very most upstream
    basin to the outfall location. 

    The walk is performed in a breadth first manner processing all the upstream catchments
    first, then walking down till it finds a confluence and jumps back up to the most
    upstream sub-basin. So that RORB can be built correctly, the traveller has the option to 
    pause on the confluence before proceeding to the next upstream reach. This allows for a 
    save step to be performed in the RORB model. WBNM does not require such a step.
    
    Parameters
    ----------
    catchment : Catchment
        A connected catchment to traverse.
    """

    def __init__(self, catchment: Catchment):
        self._catchment: Catchment = catchment
        self._colour = np.zeros(len(catchment._incidenceMatrixDS), dtype=int)
        self._us = catchment._incidenceMatrixUS
        self._ds = catchment._incidenceMatrixDS
        self._endSentinel = catchment._endSentinel
        self._pos = self.getStart()

    def position(self) -> int:
        """Position of the traveller.

        Returns
        -------
        int
            The current position of the traveller. 
        """
        return self._pos
        
    def getStart(self) -> int:
        """Gets the position of the outlet node of the basin. 
        
        That is the most downstream node. Assumes that there is only one 
        outlet in a basin. i.e. only one node with no reaches downstream of it.

        Returns
        -------
        int
            The index of the outlet node. 
        """

        for i, val in enumerate(self._ds):
            if sum(val) == (-len(val)):
                return i
    
    def getReach(self, i: int) -> Reach:
        """The downstream reach connected to ith node. 

        Parameters
        ----------
        i : int
            The index of the node we wish to get the downstream reach for. 

        Returns
        -------
        Reach
            The reach downstream of the ith node. 

        Raises
        ------
        KeyError
            If the ith node does not exist.
        """
        for j, val in enumerate(self._ds[i]):
            if val != self._endSentinel:
                return self._catchment._edges[j]
        raise KeyError
    
    def getNode(self, i: int) -> Node:
        """The ith node.

        Parameters
        ----------
        i : int
            The index of the node to return. 

        Returns
        -------
        Node
            The ith node.
        """
        return self._catchment._vertices[i]

    def top(self, i: int) -> int:
        """ The node index of the most upstream catchment avaiable from node i.

        Does not update the position of the traveller, that is the traveller does not travel
        to this node. An avaiable catchment is one which has not been visited by _next().

        Parameters
        ----------
        i : int
            The position to query the most upstream catchment from. 

        Returns
        -------
        int
            The index of the node. 
        """
        for val in self._us[i]:
            if val != -1:
                if self._colour[val] == 0:
                    return self.top(val)
                else:
                    continue
        return i
    
    def up(self, i: int) -> list:
        """Returns the immediate upstream nodes from position i. 
        
        A subarea can have multiple upstream nodes and so will return all of them.

        Parameters
        ----------
        i : int
            the position which the upstream nodes are to be queried. 

        Returns
        -------
        list
            The index of all upstream nodes.
        """
        return [j for j in self._us[i] if -1 != j]

    def down(self, i: int) -> int:
        """The index of the immediate downstream node along the reach.

        Does not update the position of the traveller. If there is no downstream 
        node then -1 is returned.

        Parameters
        ----------
        i : int
            The position at which the downstream nodes are to be queried from. 

        Returns
        -------
        int
            The index of the downstream node or -1 if none.
        """
        for val in self._ds[i]:
            if val != -1:
                return val
        return self._endSentinel
    
    def next(self) -> int:
        """The next upstream node within the catchment available from the current position. 
        
        If the current position is on a confluence next() will return that node before 
        going up the next reach. This is due to RORB needing to save the state at that 
        confluence before calculating the hydrographs of upstream sub basins. 
        
        Returns
        -------
        int
            The index of the upstream node. 
        """

        top = self.top(self._pos)
        if top == self._pos:
            self._colour[self._pos] = 1
            self._pos = self.down(self._pos)
            return self._pos
        else:
            self._pos = top
            return self._pos
        
    def nextAbsolute(self) -> int:
        """The absolute upper most node availabe from the current position.

        nextAbsolute ignores the intermediate confluences and moves to the most
        upstream point in the catchment that hasn't been visited. If it can reach a 
        higher node it will travel to this node and return it. next must be called 
        prior to using nextAbsolute as it assumes the traveller started at a node
        with no reaches above it, that is, at the top of the catchment. 
        
        Returns
        -------
        int
            The index of the upstream node.

        See Also
        --------
        next : next upstream node
        """

        self._colour[self._pos] = 1
        self._pos = self.down(self._pos)
        top = self.top(self._pos)
        if top == self._pos:
            return self._pos
        else:
            self._pos = top
            return self._pos

    def getVector(self, model: Model) -> str:
        """Produce the vector for the desired hydrology model. 
        
        Supports either RORB or WBNM.  

        Parameters
        ----------
        model : Model
            The hydrology model to generate the control file for. 

        Returns
        -------
        str
            The control file string.
        """

        return model.getVector(self)