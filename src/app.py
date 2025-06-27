# app.py
import os
import pyromb
from plot_catchment import plot_catchment
import shapefile as sf
from shapely.geometry import shape as shapely_shape
import logging
import json
from typing import Any
from pyromb.core.geometry.shapefile_validation import (
    validate_shapefile_fields,
    validate_shapefile_geometries,
    validate_confluences_out_field,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DIR = os.path.dirname(__file__)
REACH_PATH = os.path.join(DIR, "../data", "reaches.shp")
BASIN_PATH = os.path.join(DIR, "../data", "basins.shp")
CENTROID_PATH = os.path.join(DIR, "../data", "centroids.shp")
CONFUL_PATH = os.path.join(DIR, "../data", "confluences.shp")

# Load expected fields from JSON file
with open(os.path.join(DIR, r"pyromb\resources", r"expected_fields.json"), "r") as f:
    EXPECTED_FIELDS_JSON = json.load(f)

# Convert JSON to the required dictionary format
EXPECTED_FIELDS = {
    key: [(field["name"], field["type"]) for field in fields]
    for key, fields in EXPECTED_FIELDS_JSON.items()
}


class SFVectorLayer(sf.Reader, pyromb.VectorLayer):
    """
    Wrap the shapefile.Reader() with the necessary interface
    to work with the builder.
    """

    def __init__(self, path) -> None:
        super().__init__(path)
        # Extract field names, skipping the first DeletionFlag field
        self.field_names = [field[0] for field in self.fields[1:]]
        # Precompute Shapely geometries for all shapes
        self.shapely_geometries = [
            shapely_shape(self.shape(i).__geo_interface__) for i in range(len(self))
        ]

    def geometry(self, i) -> list:
        return self.shape(i).points

    def shapely_geometry(self, i):
        """
        Return the Shapely geometry for the ith shape.
        """
        return self.shapely_geometries[i]

    def record(self, i) -> dict:
        """
        Return a dictionary mapping field names to their corresponding values.
        """
        rec = super().record(i)
        return dict(zip(self.field_names, rec))

    def __len__(self) -> int:
        return super().__len__()


def main(
    reach_path: str | None = None,
    basin_path: str | None = None,
    centroid_path: str | None = None,
    confluence_path: str | None = None,
    output_name: str | None = None,
    plot: bool = False,
    model: Any | None = None,
) -> None:
    """
    Main function to build and process catchment data.

    Parameters
    ----------
    reach_path : str
        Path to the reaches shapefile.
    basin_path : str
        Path to the basins shapefile.
    centroid_path : str
        Path to the centroids shapefile.
    confluence_path : str
        Path to the confluences shapefile.
    output_name : str
        Name of the output file.
    plot : bool
        Whether to plot the catchment.
    model : pyromb.Model
        The hydrology model to use.
    """
    # Set default paths if not provided
    reach_path = reach_path or REACH_PATH
    basin_path = basin_path or BASIN_PATH
    centroid_path = centroid_path or CENTROID_PATH
    confluence_path = confluence_path or CONFUL_PATH
    model = model or pyromb.RORB()
    if isinstance(model, pyromb.RORB):
        output_name = output_name or os.path.join(DIR, "../vector.catg")
    else:
        output_name = output_name or os.path.join(DIR, "../runfile.wbnm")
    model = model or pyromb.RORB()

    ### Build Catchment Objects ###
    # Vector layers
    reach_vector = SFVectorLayer(reach_path)
    basin_vector = SFVectorLayer(basin_path)
    centroid_vector = SFVectorLayer(centroid_path)
    confluence_vector = SFVectorLayer(confluence_path)

    # Validate shapefile fields
    validation_reaches = validate_shapefile_fields(
        reach_vector, "Reaches", EXPECTED_FIELDS["reaches"]
    )
    validation_basins = validate_shapefile_fields(
        basin_vector, "Basins", EXPECTED_FIELDS["basins"]
    )
    validation_centroids = validate_shapefile_fields(
        centroid_vector, "Centroids", EXPECTED_FIELDS["centroids"]
    )
    validation_confluences = validate_shapefile_fields(
        confluence_vector, "Confluences", EXPECTED_FIELDS["confluences"]
    )

    validate_confluences_out = validate_confluences_out_field(
        confluence_vector, "Confluences"
    )

    # Validate shapefile geometries
    validation_geometries_reaches = validate_shapefile_geometries(
        reach_vector, "Reaches"
    )
    validation_geometries_basins = validate_shapefile_geometries(basin_vector, "Basins")
    validation_geometries_centroids = validate_shapefile_geometries(
        centroid_vector, "Centroids"
    )
    validation_geometries_confluences = validate_shapefile_geometries(
        confluence_vector, "Confluences"
    )

    # Decide whether to proceed based on validation
    # Decide whether to proceed based on validation
    if not all(
        [
            validation_reaches,
            validation_basins,
            validation_centroids,
            validation_confluences,
            validate_confluences_out,
            validation_geometries_reaches,
            validation_geometries_basins,
            validation_geometries_centroids,
            validation_geometries_confluences,
        ]
    ):
        logging.warning(
            "One or more shapefiles failed validation. Proceeding with caution."
        )
    else:
        print("Shapefiles passed initial validation check.")

    # Create the builder.
    builder = pyromb.Builder()
    # Build each element as per the vector layer.
    tr = builder.reach(reach_vector)
    tc = builder.confluence(confluence_vector)
    tb = builder.basin(centroid_vector, basin_vector)

    ### Create the catchment ###
    catchment = pyromb.Catchment(tc, tb, tr)
    connected = catchment.connect()
    # Create the traveller and pass the catchment.
    traveller = pyromb.Traveller(catchment)

    ### Write ###
    # Control vector to file with a call to the Traveller's getVector method
    output_path = output_name
    with open(output_path, "w") as f:
        f.write(traveller.getVector(model))
        print(f"Output written to {output_name}")

    ### Plot the catchment ###.
    if plot:
        plot_catchment(connected, tr, tc, tb)


if __name__ == "__main__":
    main()
