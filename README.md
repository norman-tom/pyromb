# Runoff Model Builder (pyromb)
Author: Tom Norman

The Pyromb (PR) library builds both RORB[1] and WBNM[2] model input files from ESRI shapefiles typically generated through a GIS package. This library's primary reason for existing is for use within the QGIS plugins **Runoff Model: RORB** and **Runoff Model: WBNM**

The library as it stands, is a minimal viable implementation of RORB and WBNM control files. It does however solve the primary issue with text file input models, that is, the need to manually transcribe information from GIS to the text file. For more advance models the user is encouraged to modify the RORB and WBNM files directly. 

MiRORB is a similar more advance tool which uses the GIS package MapInfo. The unavailability of MiRORB for QGIS inspired this project. This library is not however GIS package dependent. Pyromb is a stand alone python package able to be used directly by a python application if necessary. The QGIS plugins developed in conjunction with this project only feeds the shapefiles to this library for processing. As such this library can be used for any GIS software package. 

1. https://www.harc.com.au/software/rorb/
2. https://wbnm.com.au/

## Installing

### Dependencies
[Numpy](https://numpy.org/)

### Installing python package 

    $ pip install pyromb

### Installing for the QGIS Runoff Model Builder plugin:
For **MacOS or Linux**, QGIS does not have its own python environment so PR can be installed through pip directly from the terminal by using the command above.  

For **Windows**, QGIS has its own python environment. To install PR to work with QGIS, it needs to be installed via the OSGeo4W shell. 
1. Open the OSGeo4W Shell (may need admin permission)
2. Enter **py3_env**
3. Install via pip
###
    $ python -m pip install pyromb

### Installing the QGIS Runoff Model Builder Plugin
1. Install PR first
2. Open QGIS Plugin Manager, search for **Runoff Model: RORB** and install
3. Runoff Model: RORB is a processing plugin and is located in the processing toolbox under **Runoff Model**

## Setting Up A Catchment
PR uses four shapefiles to provide the necessary information to build the RORB and WBNM vector, these are detailed below. The attributes that must be present in the shapefile so that PR has can build the control files. The easiest way to ensure the necessary attributes are present is to use the example shapefiles in the data folder. 
### Reaches
Reaches are the connection between basins and confluences.  

**Type**  
Line geometry.  
**Attributes**  
'id' - The name of the reach [string].  
's' - The slope of the reach (m/m) [double].  
't' - The reach type. [integer].  
**Support**  
Type 1 reach only.  
**Notes**  
Reach length is derived from the shapefile geometry. 

### Centroids
Centroids represent the basin attributes and are located as close to the basin centroid as possible, while still intersecting a reach.  

**Type**  
Point geometry  
**Attributes**  
'id' The name of the basin [string]  
'fi' The fraction impervious $\in[0,1]$ [decimal]  
**Support**  
Fraction impervious  
**Notes**  
Centroid to Basin matching is done through nearest neighbour. If a centroid is moved too far away from the basin’s true centroid, it may match with another basin, or not match at all. 
### Basins
Basins are only necessary to provide the centroid with an area. This was done to avoid having to transcribe area information into the Centroid shapefile as an attribute.  

**Type**  
Polygon geometry.  
**Attributes**  
None  
**Support**  
None  
**Notes**  
None
### Confluences
Confluences are the location where reaches meet, which isn't a centroid (no basin information associated).  

**Type**  
Point geometry  
**Attributes**  
'id' The name of the confluence [string]  
'out' Flag whether this confluence is the outfall [integer]  
**Support**  
Confluence Only  
**Notes**  
In the future, these will represent other features like storage. 
### Example Catchment
![Catchment Overview](https://github.com/norman-tom/gisrom/blob/main/documentation/catchment_overview.png)

1. Basins are built in the preferred manner. There are various ways to produce the sub-catchments boundaries, please refer to your typical workflow to do so. These are nothing more than polygons that represent the boundaries of your subcatchments. 
2. Centroids are created from the basins, either using the in-built centroid tool in QGIS or estimating the location. Centroids represent a sub-area in the RORB Model. These don’t have the be at the centroid, these can be moved to suit the reaches. 
3. Confluences are manually located at junctions of reaches, these represent junction nodes in the RORB model and outlet locations in WBNM. 
4. Reach is the thalweg of the flow paths through the catchment. These are disjointed at each confluence and centroid, that is, they must start at an upstream confluence or centroid and end at the immediately downstream confluence or centroid.
5. Out location, the outlet of the catchment must be explicitly nominated by setting the GIS attribute as 1. All other confluence should of their out set at 0. 

An example of a built catchment can be found in the data folder. 

# Roadmap
Currently the roadmap is a by needs basis. If there is any functionality of RORB or WBNM that you wish to have implemented, please raise an issue and the squeaky wheel may get the grease.