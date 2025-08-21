# URBS Quick Start Guide
Author: Lindsay Millard 21 Aug 2025
Purpose: To provide notes and roadmap for implementation of URBS plugin to work with pyromb
**URBS (Unified River Basin Simulator) Integration with pyromb**

## Overview

The URBS model generates text-based command files for rainfall-runoff simulation using a dual-file architecture:
- **`.vec` file**: Contains URBS commands and model configuration
- **`.cat` file**: Contains subcatchment parameter data in CSV format

## Prerequisites

### Required Software
- QGIS 3.x with Processing Toolbox
- Python 3.8+ environment 
- pyromb library installed
- Plugin Reloader plugin installed

### Required GIS Data Layers
Your QGIS project must contain these vector layers:
- **Basins** (polygons): Subcatchment areas with attributes
- **Centroids** (points): Basin outlet points  
- **Reaches** (lines): Stream network connections
- **Confluences** (points): Stream junction points

### Required Attributes

#### Basin Layer Attributes:
- `Area` - Catchment area (km²)
- `Imperv` - Imperviousness fraction (0.0-1.0)
- `IL` - Initial loss (mm)
- `CL` - Continuing loss (mm/h)

#### Reach Layer Attributes:
- `Length` - Reach length (m)
- `Slope` - Channel slope (m/m, not percentage)

## Quick Start

### 1. Install Build URBS Plugin

The Build URBS plugin should be installed in your QGIS plugins directory:
```
C:\Users\{Username}\AppData\Roaming\QGIS\QGIS3\profiles\{profile}\python\plugins\build_urbs\
```

### 2. Load Your Data

Open QGIS and load your required vector layers:
- basins.shp (or equivalent)
- centroids.shp  
- reaches.shp
- confluences.shp

### 3. Run the Algorithm

1. Open **Processing Toolbox** (Processing → Toolbox)
2. Navigate to **Runoff Model: URBS → Build URBS Control Vector**
3. Set input parameters:
   - **Basin Layer**: Select your basins layer
   - **Centroid Layer**: Select your centroids layer  
   - **Reach Layer**: Select your reaches layer
   - **Confluence Layer**: Select your confluences layer
   - **Output**: Choose output file location (`.vec` extension)

### 4. Output Files

The algorithm generates two files:
- **`{name}.vec`** - URBS command file with model structure
- **`{name}.cat`** - CSV file with subcatchment parameters

## URBS File Structure

### .vec File Example
```
MyModel
MODEL: SPLIT
USES: L CS U
DEFAULT PARAMETERS: alpha = 0.5 m = 0.8 beta = 3 n = 1.0 x = 0.25
CATCHMENT DATA FILE = MyModel.cat

RAIN #1 L=1000 Sc=0.010
STORE.
ADD RAIN #2 L=1500 Sc=0.008
STORE.
GET.
ROUTE #3 L=2000 Sc=0.005
STORE.
GET.
PRINT. MyModel_OUTLET

END OF CATCHMENT DATA.
```

### .cat File Example
```
Index,Name,Area,Imperviousness,IL,CL
1,Basin_1,2.5,0.3,5.0,2.5
2,Basin_2,3.1,0.25,4.8,2.8
3,Basin_3,1.8,0.4,5.2,2.3
```

## URBS Commands

- **`RAIN #{n}`** - Start rainfall input for subcatchment n
- **`ADD RAIN #{n}`** - Add rainfall from subcatchment n to existing flow
- **`STORE.`** - Store current hydrograph in reservoir
- **`GET.`** - Retrieve stored hydrograph and add to current flow
- **`ROUTE #{n}`** - Route flow through reach n
- **`PRINT. {name}`** - Output final hydrograph with given name

## Troubleshooting

### Common Issues

**"No basins processed"**
- Check that basin layer has required attributes (Area, Imperv, IL, CL)
- Verify basin polygons are valid geometries

**"Slope values incorrect"** 
- Ensure reach slopes are in m/m units, not percentages
- URBS uses different slope units than RORB

**"Missing confluences"**
- Verify confluence points exist at stream junctions
- Check confluence layer geometry is valid

### Debug Output

The algorithm prints debug information to QGIS Python Console:
- Number of basins and reaches processed
- Basin parameter values being used
- Catchment connectivity information

Enable **View → Panels → Python Console** to see debug output.

## Advanced Usage

### Custom Parameters

Edit the `.vec` file to modify URBS parameters:
- `alpha`, `m` - Non-linear loss parameters
- `beta`, `n` - Routing parameters  
- `x` - Baseflow parameter

### Multiple Storms

Add additional `RAIN` commands for different storm events:
```
RAIN #1 L=1000 Sc=0.01  # First storm
RAIN #2 L=800 Sc=0.015  # Second storm
```

## Support

For issues with the URBS implementation:
1. Check QGIS Python Console for debug output
2. Verify all required layer attributes are present
3. Ensure reach slopes are in correct units (m/m)
4. Confirm catchment connectivity is correct

For pyromb library issues, refer to the main project documentation.
