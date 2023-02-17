import os
import qgis2rorb as q2r
from plot_catchment import plot_catchment

def main():
    plot = False
    dirname = os.path.dirname(__file__)
    
    # Call the builder and pass it the shape files
    builder = q2r.Builder(os.path.join(dirname, 'data', 'test_reach.shp'), os.path.join(dirname, 'data', 'test_basin.shp'), os.path.join(dirname, 'data', 'test_centroid.shp'), os.path.join(dirname, 'data', 'test_confluence.shp'))
    # Build each element
    tr = builder.reach()
    tc = builder.confluence()
    tb = builder.basin()
    # Create a catchment and call connect. 
    catchment = q2r.Catchment(tc, tb, tr)
    connected = catchment.connect()
    # Create the traveller and pass the catchment.
    traveller = q2r.Traveller(catchment)
    # Write the control vector to file with a call to the Traveller's getVector method
    model = q2r.WBNM()
    with open(os.path.join(dirname, 'vector.cat' if isinstance(model, q2r.RORB) else 'runfile.wbn'), 'w') as f:
        f.write(traveller.getVector(model))
    
    #Plot the data to make sure it is correct.
    if plot: plot_catchment(connected, tr, tc, tb)

if (__name__ == "__main__"):
    main()