from .line import Line
from math import geometry
from .point import Point

class Polygon(Line):
    """An object representing a polyline shape type. 

    A polyline is a closed line which makes an area.

    Attributes
    ----------
    area : float
        The cartesian area of the polygon
    centroid : Point
        The centroid of the polygon
    
    Parameters
    ----------
    vector : list[Points]
        The points which form the polygon
    """
    
    def __init__(self, vector:list = []):
        super().__init__(vector)
        self.append(self[0])
        self._area = geometry.polygon_area(self.toVector())
        self._centroid = geometry.polygon_centroid(self.toVector())
    
    @property
    def area(self) -> float:
        return self._area
    
    @property
    def centroid(self) -> Point:
        return self._centroid