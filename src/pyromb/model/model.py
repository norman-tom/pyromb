import abc

class Model(abc.ABC):
    """Interface for the hydrology model classes.
    """
    
    @abc.abstractmethod
    def getVector(self, traveller) -> str:
        """Generate the control text file for the relevant hydrology model.

        Parameters
        ----------
        traveller : Traveller
            The traveller to traverse the catchment.

        Returns
        -------
        str
            The content of the hydrology control file. 
        """
    
        pass
