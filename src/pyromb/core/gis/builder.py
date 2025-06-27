# builder.py
from ..attributes.basin import Basin
from ..attributes.confluence import Confluence
from ..attributes.reach import Reach
from ..attributes.reach import ReachType
from ..gis.vector_layer import VectorLayer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class Builder:
    """
    Build the entities of the catchment.

    The Builder is responsible for creating the entities (geometry, attributes) that
    the catchment will be built from. Building must take place before the
    catchment is connected and traversed.

    The objects returned from the Builder are to be passed to the Catchment.
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
            A list of the reach objects.
        """

        reaches = []
        for i in range(len(reach)):
            s = reach.geometry(i)
            r = reach.record(i)
            reaches.append(Reach(r["id"], s, ReachType(r["t"]), r["s"]))
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
        # Precompute Shapely polygons for all basins
        basin_geometries = [basin.shapely_geometry(j) for j in range(len(basin))]

        for i in range(len(centroid)):
            centroid_geom = centroid.shapely_geometry(i)
            centroid_point = centroid_geom.centroid  # Shapely Point object
            matching_basins = []

            # Find all basins that contain the centroid point
            for j, basin_geom in enumerate(basin_geometries):
                if basin_geom.contains(centroid_point):
                    matching_basins.append(j)

            if not matching_basins:
                logging.warning(
                    f"Centroid ID {centroid.record(i)['id']} at ({centroid_point.x}, {centroid_point.y}) "
                    f"is not contained within any basin polygon."
                )
                continue  # Skip this centroid or handle as needed

            if len(matching_basins) > 1:
                logging.error(
                    f"Centroid ID {centroid.record(i)['id']} at ({centroid_point.x}, {centroid_point.y}) "
                    f"is contained within multiple basins: {matching_basins}. "
                    f"Associating with the first matching basin."
                )

            # Associate with the first matching basin
            associated_basin_idx = matching_basins[0]
            associated_basin_geom = basin_geometries[associated_basin_idx]
            # Area in the units of the shapefile's projection
            a = associated_basin_geom.area
            r = centroid.record(i)
            fi = r["fi"]
            p = centroid_geom.centroid.coords[0]
            basins.append(Basin(r["id"], p[0], p[1], (a / 1e6), fi))

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
            confluences.append(Confluence(r["id"], p[0], p[1], bool(r["out"])))
        return confluences
