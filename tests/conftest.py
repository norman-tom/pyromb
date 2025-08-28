import os
from collections import namedtuple

import pytest
from shapefile import Reader

from pyromb import VectorLayer

class Vector(Reader, VectorLayer):
    """Wrap the shapefile.Reader() with the necessary interface
    to work with the builder. 
    """
    def __init__(self, path) -> None:
        super().__init__(path)

    def geometry(self, i) -> list:
        return self.shape(i).points

    def record(self, i) -> dict:
        return super().record(i)

    def __len__(self) -> int:
        return super().__len__()


@pytest.fixture
def vectors() -> tuple[Vector,...]:
    """
    Returns:
        namedtuple['basin','centroid','confluence','reach']: The vectors to build the catchment. 
    """
    root = os.path.dirname(os.path.abspath(__file__))
    basin_vector = Vector(os.path.join(root,'./data', 'basins.shp'))
    centroid_vector = Vector(os.path.join(root, './data', 'centroids.shp'))
    confluence_vector = Vector(os.path.join(root, './data', 'confluences.shp'))
    reach_vector = Vector(os.path.join(root, './data', 'reaches.shp'))

    nt = namedtuple('vectors', ['basins', 'centroids', 'confluences', 'reaches'])
    
    return nt(basin_vector, centroid_vector, confluence_vector, reach_vector)