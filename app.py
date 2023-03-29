import os
import qgis2rorb as q2r
from plot_catchment import plot_catchment

def main():
    ### Config ###
    plot = True # Set True of you want the catchment to be plotted
    model = q2r.RORB() # Select your hydrology model, either q2r.RORB() or q2r.WBNM()

    ### Main ###
    dirname = os.path.dirname(__file__)
    # Call the builder and pass it the shape files. Shape files live in the ./data directory. 
    builder = q2r.Builder(os.path.join(dirname, 'data', 'reachs.shp'), os.path.join(dirname, 'data', 'basins.shp'), os.path.join(dirname, 'data', 'centroids.shp'), os.path.join(dirname, 'data', 'confluences.shp'))
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
    with open(os.path.join(dirname, 'vector.cat' if isinstance(model, q2r.RORB) else 'runfile.wbn'), 'w') as f:
        f.write(traveller.getVector(model))
    #Plot the data to make sure it is correct.
    if plot: plot_catchment(connected, tr, tc, tb)

if (__name__ == "__main__"):
    main()