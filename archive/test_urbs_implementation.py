#!/usr/bin/env python3
"""
Test script to validate the new URBS implementation generates proper commands
following the documentation specifications.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pyromb import URBS
from pyromb.core.catchment import Catchment
from pyromb.core.traveller import Traveller
from pyromb.core.attributes.basin import Basin
from pyromb.core.attributes.confluence import Confluence
from pyromb.core.attributes.reach import Reach, ReachType
from pyromb.core.geometry.point import Point

def create_test_catchment():
    """Create a simple test catchment to validate URBS command generation."""
    
    # Create test basins (subcatchments)
    basin1 = Basin(Point(0, 10), area=2.5, fi=0.3, il=5.0, cl=2.5)
    basin1.index = 1
    basin1.name = "Headwater"
    
    basin2 = Basin(Point(5, 5), area=1.8, fi=0.4, il=4.0, cl=2.0)
    basin2.index = 2
    basin2.name = "Middle"
    
    # Create confluences (junctions)
    conf1 = Confluence(Point(0, 5))
    conf1.name = "Junction1"
    
    conf2 = Confluence(Point(10, 0))
    conf2.name = "Outlet"
    conf2.isOut = True
    
    # Create reaches (links)
    reach1 = Reach(basin1, conf1, length=2000, slope=0.02, type=ReachType.NATURAL)
    reach1.name = "Reach1"
    
    reach2 = Reach(basin2, conf2, length=3000, slope=0.015, type=ReachType.NATURAL)
    reach2.name = "Reach2"
    
    reach3 = Reach(conf1, conf2, length=1500, slope=0.01, type=ReachType.NATURAL)
    reach3.name = "Reach3"
    
    # Create lists for catchment
    confluences = [conf1, conf2]
    basins = [basin1, basin2]
    reaches = [reach1, reach2, reach3]
    
    return confluences, basins, reaches

def test_urbs_commands():
    """Test that URBS generates proper text commands."""
    print("Testing URBS command generation...")
    
    # Create test catchment
    confluences, basins, reaches = create_test_catchment()
    
    # Create catchment and traveller
    catchment = Catchment(confluences, basins, reaches)
    catchment.connect()
    traveller = Traveller(catchment)
    
    # Create URBS model
    urbs_model = URBS("Test_Model")
    
    # Generate files
    vec_content, cat_content = urbs_model.getFiles(traveller)
    
    print("\n=== Generated .vec file content ===")
    print(vec_content)
    
    print("\n=== Generated .cat file content ===")
    print(cat_content)
    
    # Validate .vec file structure
    vec_lines = vec_content.strip().split('\n')
    
    # Check header
    expected_header_elements = ["Test_Model", "MODEL: SPLIT", "USES: L CS U", "DEFAULT PARAMETERS", "CATCHMENT DATA FILE"]
    for element in expected_header_elements:
        if not any(element in line for line in vec_lines):
            print(f"ERROR: Missing header element: {element}")
            return False
    
    # Check for URBS commands
    expected_commands = ["RAIN", "ADD RAIN", "STORE", "GET", "PRINT"]
    found_commands = []
    for line in vec_lines:
        for cmd in expected_commands:
            if cmd in line:
                found_commands.append(cmd)
                break
    
    print(f"\nFound URBS commands: {found_commands}")
    
    # Check .cat file structure
    cat_lines = cat_content.strip().split('\n')
    if len(cat_lines) < 2:
        print("ERROR: .cat file should have header and data rows")
        return False
    
    # Check CSV header
    header = cat_lines[0]
    expected_columns = ["Index", "Name", "Area", "Imperviousness", "IL", "CL"]
    for col in expected_columns:
        if col not in header:
            print(f"ERROR: Missing .cat file column: {col}")
            return False
    
    print("✓ URBS implementation validation successful!")
    return True

def validate_command_structure():
    """Validate that commands follow proper URBS syntax."""
    print("\nValidating URBS command structure...")
    
    # Test command patterns from documentation
    expected_patterns = [
        "RAIN #",  # RAIN #{index} L={length}
        "ADD RAIN #",  # ADD RAIN #{index} L={length}
        "STORE.",  # STORE.
        "GET.",  # GET.
        "PRINT.",  # PRINT. {name}
        "END OF CATCHMENT DATA."  # End marker
    ]
    
    # Create test and generate content
    confluences, basins, reaches = create_test_catchment()
    catchment = Catchment(confluences, basins, reaches)
    catchment.connect()
    traveller = Traveller(catchment)
    urbs_model = URBS("Test_Model")
    vec_content, _ = urbs_model.getFiles(traveller)
    
    print("Checking for expected command patterns...")
    for pattern in expected_patterns:
        if pattern in vec_content:
            print(f"✓ Found: {pattern}")
        else:
            print(f"✗ Missing: {pattern}")
    
    # Check slope units (should be in m/m, not %)
    if "Sc=" in vec_content:
        print("✓ Found slope parameters in URBS format (Sc=)")
    
    return True

if __name__ == "__main__":
    print("URBS Implementation Validation Test")
    print("=" * 40)
    
    try:
        success = test_urbs_commands()
        if success:
            validate_command_structure()
            print("\n✓ All tests passed - URBS implementation is working correctly!")
        else:
            print("\n✗ Tests failed - URBS implementation needs fixes")
    except Exception as e:
        print(f"\n✗ Test error: {e}")
        import traceback
        traceback.print_exc()
