from gisrom.core.attributes.basin import Basin
from gisrom.core.attributes.confluence import Confluence
from gisrom.core.attributes.reach import Reach
from gisrom.core.geometry.line import pointVector
from gisrom.core.geometry.point import Point
from gisrom.core.gis.vector_layer import VectorLayer
from gisrom.math import geometry

class Builder():
    def reach(self, reach: VectorLayer) -> list:
        reaches = []
        for i in range(len(reach)):
            s = reach.geometry(i)
            r = reach.record(i)
            reaches.append(Reach(r['id'], s, r['t'], r['s']))    
        return reaches

    def basin(self, centroid: VectorLayer, basin: VectorLayer):
        basins = []
        for i in range(len(centroid)):
            min = 0
            d = 999
            s = centroid.geometry(i)
            r = centroid.record(i)
            p = s[0]
            for j in range(len(basin)):
                b = basin.geometry(j)
                v = b
                c = geometry.polygon_centroid(pointVector(v))
                l = geometry.length([Point(p[0], p[1]), c])
                if l < d:
                    d = l
                    min = j
            a = geometry.polygon_area(pointVector(basin.geometry(min)))
            fi = r['fi']
            basins.append(Basin(r['id'], p[0], p[1], (a / 1E6), fi))
        return basins

    def confluence(self, confluence: VectorLayer):
        confluences = []
        for i in range(len(confluence)):
            s = confluence.geometry(i)
            p = s[0]
            r = confluence.record(i)
            confluences.append(Confluence(r['id'], p[0], p[1],  bool(r['out'])))
        return confluences