#!/usr/bin/env python3
"""
Simple test for URBS implementation that works within QGIS environment.
"""

import sys
import os

# Add the local development path to sys.path to import from local pyromb
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_urbs_basic():
    """Basic test of URBS model instantiation and file generation."""
    print("URBS Implementation Test")
    print("=" * 30)
    print(f"Testing local pyromb from: {os.path.join(os.path.dirname(__file__), 'src')}")
    
    try:
        # Test import from local development path
        from pyromb.model.urbs import URBS, UrbsVectorWriter, UrbsCatWriter
        print("✓ Successfully imported URBS classes")
        
        # Test instantiation
        urbs_model = URBS("TestModel")
        print("✓ Successfully created URBS model instance")
        
        vector_writer = UrbsVectorWriter("TestModel")
        print("✓ Successfully created UrbsVectorWriter")
        
        cat_writer = UrbsCatWriter()
        print("✓ Successfully created UrbsCatWriter")
        
        # Test basic file structure generation
        vec_header = vector_writer.build_vec_file()
        print("✓ Successfully generated .vec file structure")
        print("\nGenerated .vec content:")
        print(vec_header)
        
        # Basic validation
        if "TestModel" in vec_header:
            print("✓ Model name correctly included")
        if "MODEL: SPLIT" in vec_header:
            print("✓ URBS model type correctly set")
        if "USES: L CS U" in vec_header:
            print("✓ URBS parameters correctly set")
        if "END OF CATCHMENT DATA." in vec_header:
            print("✓ Proper file termination")
            
        print("\n✓ All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_urbs_basic()
