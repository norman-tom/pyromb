# Runoff Model Builder (pyromb)
Author: Tom Norman

The Pyrom (PR) library builds both RORB[1] and WBNM[2] model input files from ESRI shapefiles typically generated through a GIS package. This library's primary reason for existing is for use within the QGIS plugins **Runoff Model: RORB** and **Runoff Model: WBNM**

1. https://www.harc.com.au/software/rorb/
2. https://wbnm.com.au/

## Installing

    $ pip install pyromb
    
### Installing for the QGIS Runoff Model Builder plugin:
For MacOS or Linux, QGIS does not have its own python environment so pyromb can be installed through pip directly from the terminal.  
  
For Windows, QGIS has its own python environment. To install pyromb to work with QGIS, it needs to be installed via the OSGeo4W shell.  
1. Open the OSGeo4W Shell (may need admin permission)
2. Enter **py3_env**
3. Install via pip
###
    $ python -m pip install pyromb

### Installing Runoff Model Builder Plugin
1. Install PR first
2. Open QGIS Plugin Manager, search for **Runoff Model: RORB** and install
3. Runoff Model: RORB is a processing plugin and is located in the processing toolbox under **Runoff Model**

## Setting Up A Catchment
PR uses four shapefiles to provide the necessary information to build the RORB and WBNM vector. These are detailed below, note the attributes that must be present in the shapefile so that PR has can build the control files. The easiest way to ensure the necessary attributes are present is to use the example shapefiles in the data folder. 
### Reaches:
Reaches are the river connection between basins and confluences. These are a line geometry type.  
**Attributes**:  
'id' - The name of the reach [string]  
's' - The slope of the reach [double]. Is ignored for natural reaches.  
't' - Type of reach. Refer to RORB Manual Table 2-2. Only type 1 channels are implemented so far. [integer].  
Note: reach length is derived from the shapefile geometry.  
### Centroids
Centroids are the centre of the basin, These are not necessarily the centroid however and can be moved to match the reach. However, centroid to basin matching is done through the nearest neighbour, so in rare circumstances, if a centroid is moved too far away from the basin’s true centroid, it may match with another basin, or not match at all. Centroids are a point geometry type.   
**Attributes**:  
'id' The name of the basin [string]  
'fi' The fraction impervious (this is NOT percentage) [decimal]  
### Basins
Basins are only necessary to provide the centroid with an area. This was done to avoid having to transcribe area information into the Centroid shapefile as an attribute. Basin shapefiles do not need any attributes. Basins are a polygon geometry type.  
**Attributes**:  
None  
### Confluences
These are the location where reaches meet, which isn't a centroid (no basin information associated). In the future, these will represent other features like storage.  
**Attributes**:  
'id' The name of the confluence [string]  
'out' Flag whether this confluence is the out [integer]  

![Catchment Overview](https://github.com/norman-tom/gisrom/blob/main/documentation/catchment_overview.png)

1.	Basins are built in the preferred manner. There are various ways to produce the sub-catchments boundaries, please refer to your typical workflow to do so. These are nothing more than polygons that represent the boundaries of your subcatchments. 
2.	Centroids are created from the basins, either using the in-built centroid tool in QGIS or estimating the location. Centroids represent a sub-area in the RORB Model. These don’t have the be at the centroid, these can be moved to suit the reaches. 
3.	Confluences are manually located at junctions of reaches, these represent junction nodes in the RORB model and outlet locations in WBNM. 
4.	Reach is the thalweg of the flow paths through the catchment. These are disjointed at each confluence and centroid, that is, they must start at an upstream confluence or centroid and end at the immediately downstream confluence or centroid.
5.	Out location, the outlet of the catchment must be explicitly nominated by setting the GIS attribute as 1. All other confluence should of their out set at 0.   

An example of a built catchment can be found in the data folder. 
