from ..attributes.basin import Basin
from ..attributes.confluence import Confluence
from ..attributes.reach import Reach
from ..attributes.reach import ReachType
from ..geometry.line import pointVector
from ..geometry.point import Point
from ..gis.vector_layer import VectorLayer
from ...math import geometry

class Builder():
    """
    Build the entities of the catchment.

    The Builder is responsible for creating the entities (geometry, attributes) that 
    the catchment will be built from. Building must take place before the 
    catchment is connected and traversed. 

    The objects returned from the Builder are to be passed to the Catcment. 
    """
    
    def reach(self, reach: VectorLayer) -> list:
        """Build the reach objects.

        Parameters
        ----------
        reach : VectorLayer
            The vector layer which the reaches are in.

        Returns
        -------
        list
            A list of the reache objects.
        """

        reaches = []
        for i in range(len(reach)):
            s = reach.geometry(i)
            r = reach.record(i)
            reaches.append(Reach(r['id'], s, ReachType(r['t']), r['s']))    
        return reaches

    def basin(self, centroid: VectorLayer, basin: VectorLayer) -> list:
        """Build the basin objects.

        Parameters
        ----------
        centroid : VectorLayer
            The vector layer which the centroids are in.
        basin : VectorLayer
            The vector layer which the basins are in.

        Returns
        -------
        list
            A list of the basin objects.
        """
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

    def confluence(self, confluence: VectorLayer) -> list:
        """Build the confluence objects

        Parameters
        ----------
        confluence : VectorLayer
            The vector layer the confluences are on. 

        Returns
        -------
        list
            A list of confluence objects.
        """
        confluences = []
        for i in range(len(confluence)):
            s = confluence.geometry(i)
            p = s[0]
            r = confluence.record(i)
            confluences.append(Confluence(r['id'], p[0], p[1],  bool(r['out'])))
        return confluences