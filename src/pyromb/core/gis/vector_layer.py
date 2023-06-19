
import abc

class VectorLayer(abc.ABC):
    """
    Interface for reading shapefiles. 
    
    Used by the Builder to access the geometry and attributes of the 
    shapefile to build the catchment objects. Given the various ways a shape file can 
    be read, the VectorLayer Class wrappes the functionality of the chosen library 
    in a consistnent interface to be used by the builder. 
    """
    @abc.abstractmethod
    def geometry(self, i) -> list:
        """
        Method to access the geometry of the ith vector in the shapefile.  
        Returns the geometry as a list of (x,y) tuples of the ith vector in the shapefile
        """
        pass

    @abc.abstractmethod
    def record(self, i) -> dict:
        """
        Method to access the attributes of the ith shapefile in the shapefile. 
        Returns the set of attributes for the ith vector in the shapefile as a dictionary"""
        pass

    @abc.abstractmethod
    def __len__(self) -> int:
        """
        Return the number of vectors in the shapefile
        """
        pass