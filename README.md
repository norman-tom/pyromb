# QGIS2RORB
Author: Tom Norman

For now, have a look in 'app.py' for use.

Most of the lines are to plot the catchment to visually chech it is being built correctly. 

You need to:
1. Build the confulences, basins and reaches with the Builder
2. Create the catchment from the elements returned from the calls to Builder
3. Call connect on the catchment, will build the catchment. Represented as US and DS Incidence Matrices.
4. Create the Traveller who will traverse the catchment and figure out what codes are to be called at each point. 
5. call Traveller.getVector to return a string of the RORB control vector.
