class Point:
    """An object representing a point shape type.
    
    Parameters
    ----------
    x : float
        The x co-ordinate
    y : float
        The y co-ordinate
    """

    def __init__(self, x: float = 0.0, y: float = 0.0):
        self._x = x
        self._y = y
    
    def __str__(self):
        return "[{}, {}]".format(self._x, self._y)
    
    def coordinates(self) -> tuple:
        """The co-ordinates of the point.

        Returns
        -------
        tuple
            (x,y) co-ordinates.
        """
        
        return (self._x, self._y) 
