#!/usr/bin/env python3
"""
Update Script: Sync development pyromb to QGIS plugin folder
Embeds the latest pyromb development code into the Build_URBS plugin
"""

import os
import shutil
import sys
from pathlib import Path

# Configuration
DEV_PYROMB_PATH = r"E:\GitHub\pyromb2025\src\pyromb"
PLUGIN_PATH = r"C:\Users\Lindsay\AppData\Roaming\QGIS\QGIS3\profiles\take2\python\plugins\build_urbs"
PLUGIN_PYROMB_PATH = os.path.join(PLUGIN_PATH, "pyromb")

def backup_existing_plugin():
    """Create backup of existing plugin before modifications."""
    backup_path = PLUGIN_PATH + "_backup"
    if os.path.exists(PLUGIN_PATH) and not os.path.exists(backup_path):
        print(f"Creating backup: {backup_path}")
        shutil.copytree(PLUGIN_PATH, backup_path)
        print("✓ Backup created")

def copy_pyromb_to_plugin():
    """Copy development pyromb to plugin folder."""
    print(f"Copying pyromb from: {DEV_PYROMB_PATH}")
    print(f"                to: {PLUGIN_PYROMB_PATH}")
    
    # Remove existing pyromb in plugin if it exists
    if os.path.exists(PLUGIN_PYROMB_PATH):
        shutil.rmtree(PLUGIN_PYROMB_PATH)
        print("✓ Removed existing pyromb from plugin")
    
    # Copy development pyromb
    shutil.copytree(DEV_PYROMB_PATH, PLUGIN_PYROMB_PATH)
    print("✓ Copied development pyromb to plugin")

def update_plugin_imports():
    """Update plugin files to use embedded pyromb with relative imports."""
    
    # Update build_urbs_algorithm.py
    algorithm_file = os.path.join(PLUGIN_PATH, "build_urbs_algorithm.py")
    
    if os.path.exists(algorithm_file):
        print("Updating build_urbs_algorithm.py imports...")
        
        with open(algorithm_file, 'r') as f:
            content = f.read()
        
        # Replace absolute pyromb imports with relative imports
        replacements = [
            ('import pyromb', 'from . import pyromb'),
            ('from pyromb', 'from .pyromb'),
        ]
        
        for old, new in replacements:
            if old in content and new not in content:
                content = content.replace(old, new)
                print(f"✓ Replaced '{old}' with '{new}'")
        
        with open(algorithm_file, 'w') as f:
            f.write(content)
        
        print("✓ Updated algorithm imports")

def create_plugin_init():
    """Ensure plugin __init__.py properly handles embedded pyromb."""
    init_file = os.path.join(PLUGIN_PATH, "__init__.py")
    
    # Read existing __init__.py
    if os.path.exists(init_file):
        with open(init_file, 'r') as f:
            content = f.read()
    else:
        content = ""
    
    # Add pyromb path setup if not already present
    setup_code = """
# Add embedded pyromb to sys.path for this plugin
import sys
import os
plugin_dir = os.path.dirname(__file__)
pyromb_path = os.path.join(plugin_dir, 'pyromb')
if pyromb_path not in sys.path:
    sys.path.insert(0, pyromb_path)
"""
    
    if "Add embedded pyromb to sys.path" not in content:
        content = setup_code + content
        
        with open(init_file, 'w') as f:
            f.write(content)
        print("✓ Updated plugin __init__.py")

def validate_setup():
    """Validate that the setup is correct."""
    print("\nValidation:")
    
    checks = [
        ("Plugin folder exists", os.path.exists(PLUGIN_PATH)),
        ("Embedded pyromb exists", os.path.exists(PLUGIN_PYROMB_PATH)),
        ("URBS module exists", os.path.exists(os.path.join(PLUGIN_PYROMB_PATH, "model", "urbs.py"))),
        ("Algorithm file exists", os.path.exists(os.path.join(PLUGIN_PATH, "build_urbs_algorithm.py"))),
    ]
    
    all_good = True
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"{status} {check_name}")
        if not result:
            all_good = False
    
    return all_good

def main():
    """Main update process."""
    print("QGIS Plugin Update Script")
    print("=" * 40)
    
    try:
        # Check if source exists
        if not os.path.exists(DEV_PYROMB_PATH):
            print(f"✗ Development pyromb not found at: {DEV_PYROMB_PATH}")
            return False
        
        if not os.path.exists(PLUGIN_PATH):
            print(f"✗ Plugin folder not found at: {PLUGIN_PATH}")
            return False
        
        # Backup existing plugin
        backup_existing_plugin()
        
        # Copy development pyromb
        copy_pyromb_to_plugin()
        
        # Update imports
        update_plugin_imports()
        
        # Update plugin init
        create_plugin_init()
        
        # Validate
        if validate_setup():
            print("\n🎉 Plugin update successful!")
            print("\nNext steps:")
            print("1. Open QGIS")
            print("2. Use Plugin Reloader to reload Build_URBS")
            print("3. Test with sample data")
            return True
        else:
            print("\n❌ Plugin update had issues - check validation failures")
            return False
            
    except Exception as e:
        print(f"\n❌ Plugin update failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
