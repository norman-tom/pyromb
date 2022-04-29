import math
from qgis2rorb.core.geometry.point import Point

def length(vertices:list):
    length = 0
    for i in range(len(vertices) - 1):
        length += math.sqrt( \
        math.pow((vertices[i+1].coordinates()[0] - vertices[i].coordinates()[0]), 2) + \
        math.pow((vertices[i+1].coordinates()[1] - vertices[i].coordinates()[1]), 2)
        )
    return length

# Shoelace algorithm
def polygon_area(vertices:list):
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