# QGIS2RORB
Author: Tom Norman

Please look under documentation for a user guide on how to get started.

## GIS Shape Files
### Reaches:
Reaches are the river connection between basins and confluences. These are a  line geometry type.
#### attributes
'id' - The name of the reach [string]</br>
's' - The slope of the reach [double]. Is ignored for natural reaches.</br>
't' - Type of reach. Refer to RORB Manual Table 2-2. Only type 1 channels are implemented so far. [integer]</br>
Length is derived from the line geometry
### Centroids
Centroids are the centre of the basin, These are not necessarily the centroid however and can be moved to match the reach. However, centroid to basin matching is done through the nearest neighbour, so in rare circumstances, if a centroid is moved too far away from the basin’s true centroid, it may match with another basin, or not match at all.</br>
Centroids are a point geometry type.
#### attributes
'id' The name of the basin [string]</br>
'fi' The fraction impervious (this is NOT percentage) [decimal]</br>
### Basins
Basins are only necessary to provide the centroid with an area. This was done to avoid having to transcribe area information into the Centroid shapefile as an attribute. Basin shapefiles do not need any attributes.</br>
Basins are a polygon geometry type.
#### attributes
None</br>
### Confluences
These are the location where reaches meet, which isn't a centroid (no basin information associated). In the future, these will represent other features like storage.</br>
#### attributes
'id' The name of the confluence [string]</br>
'out' Flag whether this confluence is the out [integer]
