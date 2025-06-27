# app_testing.py
import os
import pyromb
from plot_catchment import plot_catchment
import shapefile as sf
from shapely.geometry import shape as shapely_shape
import logging

from app import (
    main,
    SFVectorLayer,
)  # Import main function and SFVectorLayer from app.py

# Configure logging (optional: configure in app.py instead)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Define testing paths
TEST_DIR = r"Q:/qgis/"
TEST_REACH_PATH = os.path.join(TEST_DIR, "BC_reaches.shp")
TEST_BASIN_PATH = os.path.join(TEST_DIR, "BC_basins.shp")
TEST_CENTROID_PATH = os.path.join(TEST_DIR, "BC_centroids.shp")
TEST_CONFUL_PATH = os.path.join(TEST_DIR, "BC_confluences.shp")

TEST_OUTPUT_PATH = r"Q:\qgis"
TEST_OUTPUT_NAME = r"testing_mod_python2.catg"
TEST_OUT = os.path.join(TEST_OUTPUT_PATH, TEST_OUTPUT_NAME)


def print_shapefile_fields(shp, name):
    fields = shp.fields[1:]  # skip DeletionFlag
    field_names = [field[0] for field in fields]
    print(f"{name} fields: {field_names}")


def test_main():
    ### Config ###
    plot = False  # Set to True if you want the catchment to be plotted
    model = pyromb.RORB()
    # Select your hydrology model, either pyromb.RORB() or pyromb.WBNM()

    ### Build Catchment Objects ###
    # Vector layers with test paths
    reach_vector = SFVectorLayer(TEST_REACH_PATH)
    basin_vector = SFVectorLayer(TEST_BASIN_PATH)
    centroid_vector = SFVectorLayer(TEST_CENTROID_PATH)
    confluence_vector = SFVectorLayer(TEST_CONFUL_PATH)

    # Print field names (optional, for debugging)
    print_shapefile_fields(reach_vector, "Reach")
    print_shapefile_fields(basin_vector, "Basin")
    print_shapefile_fields(centroid_vector, "Centroid")
    print_shapefile_fields(confluence_vector, "Confluence")

    ### Call the main function with test paths and parameters ###
    main(
        reach_path=TEST_REACH_PATH,
        basin_path=TEST_BASIN_PATH,
        centroid_path=TEST_CENTROID_PATH,
        confluence_path=TEST_CONFUL_PATH,
        output_name=TEST_OUT,
        plot=plot,
        model=model,
    )


if __name__ == "__main__":
    test_main()
