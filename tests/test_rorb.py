import pytest

import pyromb

@pytest.mark.rorb
def test_rorb(vectors) -> None:
    model = pyromb.RORB()
    builder = pyromb.Builder()
    tr = builder.reach(vectors.reaches)
    tc = builder.confluence(vectors.confluences)
    tb = builder.basin(vectors.centroids, vectors.basins)

    catchment = pyromb.Catchment(tc, tb, tr)
    catchment.connect()
    traveller = pyromb.Traveller(catchment)

    control_str = traveller.getVector(model)
    
    assert control_str
    assert control_str.startswith("REACH")