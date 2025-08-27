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
    connected = catchment.connect()
    traveller = pyromb.Traveller(catchment)

    control_str = traveller.getVector(model)

    assert control_str