# QGIS Development Workflow Plan
Author: Lindsay Millard 21 Aug 2025
Purpose: To provide notes and roadmap for implementation of URBS plugin to work with pyromb

**Testing Local pyromb + Build_URBS Plugin Integration**

## Overview
This workflow enables testing the local development version of pyromb with the Build_URBS plugin in QGIS without complex package installations.

## Key Paths
```
QGIS Python:     C:\Program Files\QGIS 3.40.8\apps\Python312\python.exe
Plugin Folder:   C:\Users\Lindsay\AppData\Roaming\QGIS\QGIS3\profiles\take2\python\plugins\build_urbs
Development:     E:\GitHub\pyromb2025\src\
```

## Strategy: Plugin-Embedded pyromb

Instead of trying to install pyromb into QGIS Python environment, embed the development pyromb directly into the plugin folder. This avoids circular import issues and simplifies testing.

## Step-by-Step Workflow

### Phase 1: Setup Plugin Development Environment

#### 1.1 Create Plugin Structure
```
build_urbs/
├── pyromb/                    # Embedded development pyromb
│   ├── core/
│   ├── model/
│   └── __init__.py
├── custom_types/
├── build_urbs_algorithm.py
├── __init__.py
└── metadata.txt
```

#### 1.2 Copy Development pyromb
- Copy `E:\GitHub\pyromb2025\src\pyromb\` → `plugin\pyromb\`
- This creates a self-contained plugin with embedded pyromb

#### 1.3 Update Plugin Imports
- Modify plugin files to use relative imports: `from .pyromb import...`
- Avoid system-wide pyromb conflicts

### Phase 2: Automated Update Scripts

#### 2.1 Plugin Update Script
Creates `update_plugin.py` to:
- Copy latest pyromb code to plugin folder
- Update plugin files 
- Trigger plugin reload in QGIS

#### 2.2 Development Sync Script  
Creates `sync_to_qgis.bat` for one-click updates:
- Syncs changes from development → plugin
- Preserves plugin-specific configurations

### Phase 3: Testing Workflow

#### 3.1 QGIS Testing Process
1. Make changes in `E:\GitHub\pyromb2025\src\`
2. Run `sync_to_qgis.bat`
3. Use Plugin Reloader in QGIS
4. Test with sample data
5. Iterate

#### 3.2 Validation Steps
- Test URBS file generation (.vec and .cat)
- Verify command structure 
- Check slope unit conversion
- Validate with different catchment topologies

## Implementation Scripts

### Script 1: update_plugin.py
```python
# Copies development pyromb to plugin folder
# Updates relative imports
# Handles file synchronization
```

### Script 2: sync_to_qgis.bat  
```batch
# One-click sync from development to QGIS
# Preserves existing plugin structure
# Provides feedback on success/failure
```

### Script 3: test_in_qgis.py
```python
# QGIS-specific test script
# Tests plugin functionality
# Validates URBS output
```

## Advantages of This Approach

✅ **No QGIS Python Environment Modification**
- Keeps QGIS installation clean
- No dependency conflicts

✅ **Self-Contained Plugin**  
- All dependencies embedded
- Easy distribution and testing

✅ **Rapid Development Cycle**
- One-click updates
- Plugin reloader compatibility
- No QGIS restarts needed

✅ **Isolated Testing**
- Development changes don't affect other tools
- Easy rollback if needed

## Risk Mitigation

⚠️ **Backup Original Plugin**
- Keep copy of working plugin before modifications

⚠️ **Version Control**
- Track plugin changes separately from pyromb development

⚠️ **Testing Isolation**
- Test with sample data first
- Validate output before using with important data

