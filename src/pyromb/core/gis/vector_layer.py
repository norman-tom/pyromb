
import abc

class VectorLayer(abc.ABC):
    """
    Interface for reading shapefiles. 
    
    Used by the Builder to access the geometry and attributes of the 
    shapefile to build the catchment objects. Given the various ways a shapefile can 
    be read, the VectorLayer Class wrappes the functionality of reading the shapefile 
    by the chosen library in a consistent interface to be used by the builder. 
    """
    
    @abc.abstractmethod
    def geometry(self, i: int) -> list:
        """
        Method to access the geometry of the ith vector in the shapefile.

        Return the geometry as a list of (x,y) tuples.

        Parameters
        ----------
        i : int
            The index of the vector to return the geometry for.

        Returns
        -------
        list
            List of x,y co-ordinates tuples
        """
        pass

    @abc.abstractmethod
    def record(self, i: int) -> dict:
        """
        Method to access the attributes of the ith vector in the shapefile. 

        Return the set of attributes as a dictionary.

        Parameters
        ----------
        i : int
            The index of the vector to return the attributes of.

        Returns
        -------
        dict
            key:value pair of the attributes. 
        """
        pass

    @abc.abstractmethod
    def __len__(self) -> int:
        """The number of vectors in the shapefile.

        Returns
        -------
        int
            Vectors in the shapefile. 
        """
        pass