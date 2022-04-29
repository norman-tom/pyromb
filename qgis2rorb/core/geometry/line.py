from .point import Point
from qgis2rorb.math import geometry

class Line():
    def __init__(self, vector:list = []):
        super().__init__()
        self._vector = pointVector(vector)
        self._end = len(self._vector) - 1
        self._length = geometry.length(self.toVector())

    def __iter__(self):
        self.n = 0
        return self
    
    def __next__(self) -> Point:
        if self.n <= self._end:
            point = self._vector[self.n]
            self.n += 1
            return point
        else:
            raise StopIteration
    
    def __len__(self):
        return self._end

    def __getitem__(self, i):
        return self._vector[i]
    
    def __setitem__(self, i, v:Point):
        self._vector[i] = v
    
    def append(self, point:Point):
        self._vector.append(point)
        self._end += 1
        self._length = geometry.length(self.toVector())
    
    def length(self) -> float:
        return self._length

    def toVector(self) -> list:
        return self._vector

    def getStart(self) -> Point:
        return self._vector[0]
    
    def getEnd(self) -> Point:
        return self._vector[self._end]

def pointVector(vector:list):
    points = []
    for t in vector:
        points.append(Point(t[0], t[1]))
    return points