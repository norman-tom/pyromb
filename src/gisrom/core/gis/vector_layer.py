
import abc

class VectorLayer(abc.ABC):
    """
    Interface for reading shapefiles. 
    
    Used by the Builder to access the geometry and attributes of the 
    shapefile to build the catchment objects.
    """
    @abc.abstractmethod
    def geometry(self, i) -> list:
        """returns the geometry of the ith vector in the shapefile"""
        pass

    @abc.abstractmethod
    def record(self, i) -> dict:
        """returns the set of attributes for the ith vector in the shapefile"""
        pass

    @abc.abstractmethod
    def __len__(self) -> int:
        """return the number of vectors in the shapefile"""
        pass