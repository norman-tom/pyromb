# QGIS2RORB
Author: Tom Norman

For now, have a look at 'app.py' for use.
Most of the lines are to plot the catchment to visually check it is being built correctly. 

You need to:
1. Build the confluences, basins and reaches with the Builder
2. Create the catchment from the elements returned from the calls to Builder
3. Call connect on the catchment, will build the catchment. Represented as US and DS Incidence Matrices.
4. Create the Traveller who will traverse the catchment and figure out what codes are to be called at each point. 
5. call Traveller.getVector to return a string of the RORB control vector.

## GIS Shape Files
### Reaches:
Reaches are the river connection between basins and confluences. These are a  line geometry type.
#### attributes
'id' - The name of the reach [string]
's' - The slope of the reach [double]. Is ignored for natural reaches.
't' - Type of reach. Refer to RORB Manual Table 2-2. Only type 1 channels are implemented so far. [integer]
Length is derived from the line geometry
### Centroids
Centroids are the centre of the basin, These are not necessarily the centroid however and can be moved to match the reach. However, centroid to basin matching is done through the nearest neighbour, so in rare circumstances, if a centroid is moved too far away from the basin’s true centroid, it may match with another basin, or not match at all.
Centroids are a point geometry type. 
#### attributes
'id' The name of the basin [string]
'fi' The fraction impervious (this is NOT percentage) [decimal]
### Basins
Basins are only necessary to provide the centroid with an area. This was done to avoid having to transcribe area information into the Centroid shapefile as an attribute. Basin shapefiles do not need any attributes. 
Basins are a polygon geometry type. 
#### attributes
None
### Confluences
These are the location where reaches meet, which isn't a centroid (no basin information associated). In the future, these will represent other features like storage. 
#### attributes
'id' The name of the confluence [string] 
'out' Flag whether this confluence is the out [integer]
