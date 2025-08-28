import os

import pytest
import pyromb

@pytest.mark.urbs
def test_urbs(vectors) -> None:
    model = pyromb.URBS()
    builder = pyromb.Builder()
    tr = builder.reach(vectors.reaches)
    tc = builder.confluence(vectors.confluences)
    tb = builder.basin(vectors.centroids, vectors.basins)

    catchment = pyromb.Catchment(tc, tb, tr)
    catchment.connect()
    traveller = pyromb.Traveller(catchment)

    urbs_vector = traveller.getVector(model)
    vec_content, cat_content = model.splitVector(urbs_vector)
    
    assert vec_content
    assert vec_content.startswith("URBS_Model")

    assert cat_content
    assert cat_content.startswith("Index,Name,Area,Imperviousness,IL,CL")