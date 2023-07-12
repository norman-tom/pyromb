from .point import Point
from ...math import geometry

class Line():
    """An object representing a line shape type.
    
    Attributes
    ----------
    length : float
    
    Parametersup
    ----------
    vector : list[Points]
        The points that make the line.
    """

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
        """Add an additional point to the line.

        Append adds the point to the head of the geometry.

        Parameters
        ----------
        point : Point
            The point to add to the line.
        """
        
        self._vector.append(point)
        self._end += 1
        self._length = geometry.length(self.toVector())
    
    def length(self) -> float:
        """The cartisian length of the line.

        Returns
        -------
        float
            The length
        """

        return self._length

    def toVector(self) -> list:
        """Convert the line into a vector of points.

        Returns
        -------
        list
            A list of points.
        """

        return self._vector

    def getStart(self) -> Point:
        """Get the starting point of the line.

        Returns
        -------
        Point
            The start point.
        """

        return self._vector[0]
    
    def getEnd(self) -> Point:
        """Get the end point of the line.

        Returns
        -------
        Point
            The end point
        """
        
        return self._vector[self._end]

def pointVector(vector:list) -> list:
    """Convert a list of x,y co-ordinates into a list of Points

    Parameters
    ----------
    vector : list
        A list of (x,y) co-ordinate tuple as floats.

    Returns
    -------
    list
        A list of (x,y) co-odinate tuple as points.
    """

    points = []
    for t in vector:
        points.append(Point(t[0], t[1]))
    return points