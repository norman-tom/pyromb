# URBS Implementation Plan & Status Report

**Project:** Python Runoff Model Builder (pyromb) - URBS Integration  
**Date:** 2025-08-21  
Author: Lindsay Millard 21 Aug 2025
Purpose: To provide notes and roadmap for implementation of URBS plugin to work with pyromb 
**Objective:** Implement proper URBS functionality following documentation specifications  

## Executive Summary

Successfully implemented proper URBS functionality in pyromb, replacing the previous RORB-style implementation with a text-based command system that follows URBS specifications outlined in `URBS_logic.md` and `RORBvURBS_logic.md`.

## Key Implementation Changes

### ✅ 1. Complete URBS Model Rewrite
- **Location:** `src/pyromb/model/urbs.py`
- **Status:** COMPLETED
- **Changes:**
  - Replaced RORB-style numeric codes with URBS text commands
  - Implemented proper command structure: RAIN, ADD RAIN, STORE, GET, ROUTE, PRINT
  - Added named parameters (L= for length, Sc= for slope)
  - Proper slope unit handling (m/m for URBS vs % for RORB)

### ✅ 2. Dual File Architecture
- **Status:** COMPLETED
- **Implementation:**
  - `.vec` file: Contains URBS command sequence with proper headers
  - `.cat` file: Contains subcatchment data in CSV format
  - Separate writer classes: `UrbsVectorWriter` and `UrbsCatWriter`

### ✅ 3. URBS Command Structure
- **Status:** COMPLETED
- **Commands Implemented:**
  ```
  RAIN #{index} L={length} Sc={slope}     # Start branch at headwater
  ADD RAIN #{index} L={length} Sc={slope} # Add subcatchment inflow
  STORE.                                  # Store hydrograph at junction
  GET.                                    # Retrieve stored hydrograph
  ROUTE THRU #{index} L={length}          # Route without local inflow
  PRINT. {name}                           # Output at designated nodes
  ```

### ✅ 4. File Headers & Structure
- **Status:** COMPLETED
- **.vec file header:**
  ```
  {model_name}
  MODEL: SPLIT
  USES: L CS U
  DEFAULT PARAMETERS: alpha = 0.5 m = 0.8 beta = 3 n = 1.0 x = 0.25
  CATCHMENT DATA FILE = {model_name}.cat
  ```
- **.cat file format:**
  ```
  Index,Name,Area,Imperviousness,IL,CL
  1,Headwater,2.5,0.3,5.0,2.5
  2,Middle,1.8,0.4,4.0,2.0
  ```

### ✅ 5. Plugin Integration
- **Location:** `src/build_urbs/build_urbs_algorithm.py`
- **Status:** COMPLETED
- **Changes:**
  - Updated to use new dual-file URBS model
  - Generates both .vec and .cat files automatically
  - Enhanced user feedback and help text
  - Deployed to QGIS plugin folder

## Technical Architecture

### Class Structure
```
pyromb.model.urbs
├── UrbsVectorWriter    # Generates .vec file with URBS commands
├── UrbsCatWriter       # Generates .cat file with subcatchment data
└── URBS               # Main model class coordinating file generation
```

### Integration Points
1. **Traveller Class:** Uses existing depth-first traversal logic
2. **Builder Class:** Compatible with existing GIS layer processing
3. **Catchment Class:** Works with current node/reach/basin structure
4. **Plugin Interface:** Seamless integration with QGIS processing framework

## Key Differences from RORB Implementation

| Aspect | RORB | URBS (New Implementation) |
|--------|------|---------------------------|
| **Output Format** | Single .catg file | Separate .vec and .cat files |
| **Commands** | Numeric codes (1,2,3,4) | Text commands (RAIN, ADD RAIN, STORE, GET) |
| **Parameters** | Positional values | Named parameters (L=, Sc=) |
| **Slope Units** | Percentage (%) | Meter per meter (m/m) |
| **Data Structure** | Monolithic file | Modular two-file system |

## Testing & Validation

## File Locations & Dependencies

### Core Implementation Files
```
E:\GitHub\pyromb2025\
├── src\pyromb\model\urbs.py          # Main URBS implementation
├── src\build_urbs\                   # QGIS plugin files
│   ├── build_urbs_algorithm.py       # Updated algorithm
│   ├── custom_types\qvector_layer.py # Fixed QGIS integration
│   └── ...
├── documentation\
│   ├── URBS_logic.md                 # URBS specification
│   └── RORBvURBS_logic.md           # Comparison guide
└── test_urbs_simple.py              # Development test script
```

### QGIS Plugin Deployment
```
C:\Users\Lindsay\AppData\Roaming\QGIS\QGIS3\profiles\take2\python\plugins\build_urbs\
```

## Known Issues & Considerations

## Deployment Strategy

### Phase 1: Development Testing ✅
- [x] Local implementation complete
- [x] Basic functionality validated
- [x] QGIS plugin updated

### Phase 2: Integration Testing 🔄
- [x] Test with sample GIS data
- [x] Validate URBS file compatibility
- [o] Performance testing

### Phase 3: Production Deployment
- [ ] Merge to main pyromb repository
- [ ] Update QGIS plugin registry
- [ ] Release documentation

## Success Criteria

### ✅ Technical Requirements Met
- [x] Generates proper URBS text commands
- [x] Separate .vec and .cat file output
- [x] Correct unit conversions (slope m/m)
- [x] Compatible with existing pyromb architecture
- [x] QGIS plugin integration functional

**Testing Environment:** QGIS 3.40.8 with Python 3.12

