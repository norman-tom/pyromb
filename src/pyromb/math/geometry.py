import math
from ..core.geometry.point import Point

def length(vertices:list) -> float:
    """Calculate the cartesian length of a vector of co-ordinates. 

    Parameters
    ----------
    vertices : list
        The list of co-ordinates to calculate the length.

    Returns
    -------
    float
        The vector length.
    """

    length = 0
    for i in range(len(vertices) - 1):
        length += math.sqrt( \
        math.pow((vertices[i+1].coordinates()[0] - vertices[i].coordinates()[0]), 2) + \
        math.pow((vertices[i+1].coordinates()[1] - vertices[i].coordinates()[1]), 2)
        )
    return length

# Shoelace algorithm
def polygon_area(vertices:list) -> float:
    """Calculate the cartesian area of a polygon.

    Parameters
    ----------
    vertices : list
        A list of points representing the polygon.

    Returns
    -------
    float
        The polygon area.
    """

    psum = 0
    nsum = 0
    for i in range(len(vertices)):
        sindex = (i + 1) % len(vertices)
        prod = vertices[i].coordinates()[0] * vertices[sindex].coordinates()[1]
        psum += prod

    for i in range(len(vertices)):
        sindex = (i + 1) % len(vertices)
        prod = vertices[sindex].coordinates()[0] * vertices[i].coordinates()[1]
        nsum += prod

    return abs(1/2*(psum - nsum))

def polygon_centroid(vertices:list) -> Point:
    """Calculate the centroid of a polygon.

    Parameters
    ----------
    vertices : list
        A list of points representing the polygon.

    Returns
    -------
    Point
        The centroid.
    """
    
    sumx = 0
    sumy = 0
    suma = 0
    for i in range(len(vertices) - 1):
        p = [(vertices[i].coordinates()[0], vertices[i].coordinates()[1]), (vertices[i+1].coordinates()[0], vertices[i+1].coordinates()[1])]
        sumx += (p[0][0] + p[1][0]) * (p[0][0] * p[1][1] - p[1][0] * p[0][1])
        sumy += (p[0][1] + p[1][1]) * (p[0][0] * p[1][1] - p[1][0] * p[0][1])
        suma += p[0][0] * p[1][1] - p[1][0] * p[0][1]

    A = 0.5 * suma
    Cx = (1 / (6 * A)) * sumx
    Cy = (1 / (6 * A)) * sumy
    
    return Point(Cx, Cy)