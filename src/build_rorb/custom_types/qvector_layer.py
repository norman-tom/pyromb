from pyromb.core.gis.vector_layer import VectorLayer

class QVectorLayer(VectorLayer):
    def __init__(self, feature_source) -> None:
        self._features = [f for f in feature_source.getFeatures()]

    def geometry(self, i) -> list:
        """returns the geometry of the ith vector in the shapefile"""
        return [(p.x(), p.y()) for p in self._features[i].geometry().vertices()]

    def record(self, i) -> dict:
        """returns the set of attributes for the ith vector in the shapefile"""
        return self._features[i]

    def __len__(self) -> int:
        """return the number of vectors in the shapefile"""
        return self._features.__len__()
