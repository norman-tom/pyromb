#!/usr/bin/env python3
"""
Fix Plugin Imports: Create a minimal pyromb import for QGIS plugin
Avoids circular import by only copying needed classes
"""

import os
import shutil
from pathlib import Path

# Configuration
DEV_PYROMB_PATH = r"E:\GitHub\pyromb2025\src\pyromb"
PLUGIN_PATH = r"C:\Users\Lindsay\AppData\Roaming\QGIS\QGIS3\profiles\take2\python\plugins\build_urbs"

def create_minimal_pyromb():
    """Create minimal pyromb structure with only needed classes."""
    plugin_pyromb = os.path.join(PLUGIN_PATH, "pyromb_minimal")
    
    # Remove existing minimal pyromb if exists
    if os.path.exists(plugin_pyromb):
        shutil.rmtree(plugin_pyromb)
    
    # Create directory structure
    os.makedirs(plugin_pyromb)
    os.makedirs(os.path.join(plugin_pyromb, "core"))
    os.makedirs(os.path.join(plugin_pyromb, "core", "attributes"))
    os.makedirs(os.path.join(plugin_pyromb, "model"))
    
    # Create __init__.py files
    init_files = [
        os.path.join(plugin_pyromb, "__init__.py"),
        os.path.join(plugin_pyromb, "core", "__init__.py"),
        os.path.join(plugin_pyromb, "core", "attributes", "__init__.py"),
        os.path.join(plugin_pyromb, "model", "__init__.py"),
    ]
    
    for init_file in init_files:
        with open(init_file, 'w') as f:
            f.write("# Minimal pyromb for QGIS plugin\n")
    
    # Copy only needed files
    files_to_copy = [
        # Core classes needed by URBS
        ("core/catchment.py", "core/catchment.py"),
        ("core/traveller.py", "core/traveller_minimal.py"),  # We'll modify this
        ("core/attributes/basin.py", "core/attributes/basin.py"),
        ("core/attributes/node.py", "core/attributes/node.py"),
        ("core/attributes/reach.py", "core/attributes/reach.py"),
        ("core/attributes/confluence.py", "core/attributes/confluence.py"),
        
        # Model classes
        ("model/urbs.py", "model/urbs.py"),
        ("model/model.py", "model/model.py"),
    ]
    
    for src, dst in files_to_copy:
        src_path = os.path.join(DEV_PYROMB_PATH, src)
        dst_path = os.path.join(plugin_pyromb, dst)
        
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            print(f"✓ Copied {src}")
    
    return plugin_pyromb

def create_minimal_traveller(plugin_pyromb):
    """Create a minimal traveller that avoids circular imports."""
    traveller_content = '''import numpy as np
from .attributes.reach import Reach
from .attributes.node import Node
from .catchment import Catchment

class Traveller:
    """Minimal Traveller class for URBS plugin - avoids circular imports."""
    
    def __init__(self, catchment):
        self._catchment = catchment
        self._path = []
        self._nodeindex = {}
        self._currentindex = 0
        self._current = None
        self._atconfluence = False
        self._reset()
    
    def _reset(self):
        """Reset traversal state."""
        self._currentindex = 0
        self._current = None
        self._atconfluence = False
    
    def getVector(self, model):
        """Generate vector output using the provided model."""
        # This is the key method the plugin uses
        return model.build(self)
    
    def getCatchment(self):
        """Get the catchment being traversed.""" 
        return self._catchment
    
    def atConfluence(self):
        """Check if currently at a confluence."""
        return self._atconfluence
    
    def getReach(self, pos=None):
        """Get reach at position or current position."""
        if pos is None:
            pos = self._currentindex
        if pos < len(self._path):
            return self._path[pos]
        return None
    
    def getBasin(self, pos=None):
        """Get basin at position or current position.""" 
        reach = self.getReach(pos)
        if reach and hasattr(reach, 'basin'):
            return reach.basin
        return None
    
    def getNode(self, pos=None):
        """Get node at position or current position."""
        reach = self.getReach(pos)
        if reach and hasattr(reach, 'from_node'):
            return reach.from_node
        return None
    
    def getRORBBasinIndex(self, pos=None):
        """Get RORB basin index (compatibility method)."""
        return pos if pos is not None else self._currentindex
        
    def hasNext(self):
        """Check if there are more elements in traversal."""
        return self._currentindex < len(self._path) - 1
    
    def next(self):
        """Move to next element in traversal."""
        if self.hasNext():
            self._currentindex += 1
            return True
        return False
'''
    
    traveller_file = os.path.join(plugin_pyromb, "core", "traveller_minimal.py")
    with open(traveller_file, 'w') as f:
        f.write(traveller_content)
    
    print("✓ Created minimal traveller")

def update_urbs_imports(plugin_pyromb):
    """Update URBS to use minimal imports."""
    urbs_file = os.path.join(plugin_pyromb, "model", "urbs.py")
    
    if os.path.exists(urbs_file):
        with open(urbs_file, 'r') as f:
            content = f.read()
        
        # Replace imports to use minimal versions
        replacements = [
            ('from ..core.traveller import Traveller', 'from ..core.traveller_minimal import Traveller'),
        ]
        
        for old, new in replacements:
            if old in content:
                content = content.replace(old, new)
                print(f"✓ Updated URBS import: {old} → {new}")
        
        with open(urbs_file, 'w') as f:
            f.write(content)

def update_plugin_algorithm():
    """Update plugin algorithm to use minimal pyromb."""
    algorithm_file = os.path.join(PLUGIN_PATH, "build_urbs_algorithm.py")
    
    if os.path.exists(algorithm_file):
        with open(algorithm_file, 'r') as f:
            content = f.read()
        
        # Replace pyromb import with minimal version
        replacements = [
            ('from . import pyromb', 'from . import pyromb_minimal as pyromb'),
            ('from .pyromb', 'from .pyromb_minimal'),
        ]
        
        for old, new in replacements:
            if old in content:
                content = content.replace(old, new)
                print(f"✓ Updated plugin import: {old} → {new}")
        
        with open(algorithm_file, 'w') as f:
            f.write(content)

def create_minimal_init(plugin_pyromb):
    """Create minimal __init__.py that exports only URBS."""
    init_content = '''"""
Minimal pyromb for QGIS Build_URBS plugin
Only includes URBS model to avoid circular imports
"""

from .model.urbs import URBS
from .core.traveller_minimal import Traveller

__all__ = ["URBS", "Traveller"]
'''
    
    init_file = os.path.join(plugin_pyromb, "__init__.py")
    with open(init_file, 'w') as f:
        f.write(init_content)
    
    print("✓ Created minimal __init__.py")

def main():
    """Main fix process."""
    print("Fixing Plugin Circular Import")
    print("=" * 40)
    
    try:
        # Create minimal pyromb structure
        plugin_pyromb = create_minimal_pyromb()
        
        # Create minimal traveller
        create_minimal_traveller(plugin_pyromb)
        
        # Update URBS imports
        update_urbs_imports(plugin_pyromb)
        
        # Create minimal init
        create_minimal_init(plugin_pyromb)
        
        # Update plugin algorithm
        update_plugin_algorithm()
        
        print("\n✅ Plugin import fix completed!")
        print("\nNext steps:")
        print("1. Use Plugin Reloader to reload Build_URBS")
        print("2. Test plugin with sample data")
        print("3. Check for any remaining import issues")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
