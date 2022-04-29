import shapefile as sf
from qgis2rorb.core.attributes.basin import Basin
from qgis2rorb.core.attributes.confluence import Confluence
from qgis2rorb.core.attributes.reach import Reach
from qgis2rorb.core.geometry.line import Line, pointVector
from qgis2rorb.core.geometry.point import Point
from qgis2rorb.math import geometry

class Builder():
    def __init__(self, reaches: str, basins: str, centroids: str, confluence: str):
        self._shapeReach = sf.Reader(reaches)
        self._shapeBasin = sf.Reader(basins)
        self._shapeCentroid = sf.Reader(centroids)
        self._shapeConfluence = sf.Reader(confluence)

    def reach(self) -> list:
        reaches = []
        for i in range(len(self._shapeReach)):
            s = self._shapeReach.shape(i)
            r = self._shapeReach.record(i)
            reaches.append(Reach(r['id'], s.points, r['t'], r['s']))
        
        return reaches


    def basin(self):
        basins = []
        for i in range(len(self._shapeCentroid)):
            min = 0
            d = 999
            s = self._shapeCentroid.shape(i)
            r = self._shapeCentroid.record(i)
            p = s.points[0]
            for j in range(len(self._shapeBasin)):
                b = self._shapeBasin.shape(j)
                v = b.points
                c = geometry.polygon_centroid(pointVector(v))
                l = geometry.length([Point(p[0], p[1]), c])
                if l < d:
                    d = l
                    min = j
            a = geometry.polygon_area(pointVector(self._shapeBasin.shape(min).points))
            fi = r['fi']
            basins.append(Basin(r['id'], p[0], p[1], (a / 10E6), fi))
        return basins


    def confluence(self):
        confluence = []
        for i in range(len(self._shapeConfluence)):
            s = self._shapeConfluence.shape(i)
            p = s.points[0]
            r = self._shapeConfluence.record(i)
            confluence.append(Confluence(r['id'], p[0], p[1],  bool(r['out'])))
        
        return confluence