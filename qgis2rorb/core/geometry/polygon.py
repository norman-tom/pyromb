from .line import Line
from qgis2rorb.math import geometry

class Polygon(Line):
    def __init__(self, vector:list = []):
        super().__init__(vector)
        self.append(self[0])
        self._area = geometry.polygon_area(self.toVector())
        self._centroid = geometry.polygon_centroid(self.toVector())
    
    def area(self):
        return self._area
    
    def centroid(self):
        return self._centroid