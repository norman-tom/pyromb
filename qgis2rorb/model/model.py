import abc

class Model(abc.ABC):
    '''
    Interface for the hydrological model classes. 
    '''
    @abc.abstractmethod
    def getVector(self, traveller):
        pass
