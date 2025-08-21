#!/usr/bin/env python3
"""
Standalone URBS test that avoids circular import issues.
Tests URBS classes directly without importing the full pyromb module.
"""

import sys
import os

# Add the local development path to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_urbs_standalone():
    """Test URBS classes directly without full module initialization."""
    print("URBS Standalone Test")
    print("=" * 30)
    print(f"Testing from: {os.path.join(os.path.dirname(__file__), 'src')}")
    
    try:
        # Import directly without going through pyromb.__init__.py
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'pyromb', 'model'))
        
        # Test UrbsVectorWriter directly
        print("\n1. Testing UrbsVectorWriter...")
        import importlib.util
        spec = importlib.util.spec_from_file_location("urbs", os.path.join(os.path.dirname(__file__), 'src', 'pyromb', 'model', 'urbs.py'))
        urbs_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(urbs_module)
        
        # Test UrbsVectorWriter
        vector_writer = urbs_module.UrbsVectorWriter("TestModel")
        print("✓ Successfully created UrbsVectorWriter")
        
        # Test basic file structure generation
        vec_content = vector_writer.build_vec_file()
        print("✓ Successfully generated .vec file structure")
        
        print("\nGenerated .vec content:")
        print("-" * 40)
        print(vec_content)
        print("-" * 40)
        
        # Test UrbsCatWriter
        print("\n2. Testing UrbsCatWriter...")
        cat_writer = urbs_module.UrbsCatWriter()
        print("✓ Successfully created UrbsCatWriter")
        
        # Test basic cat file structure
        cat_header = cat_writer.get_header()
        print("✓ Successfully generated .cat header")
        print(f"Cat header: {cat_header}")
        
        # Validate content
        print("\n3. Validation:")
        validations = [
            ("Model name in content", "TestModel" in vec_content),
            ("URBS model type", "MODEL: SPLIT" in vec_content),
            ("URBS parameters", "USES: L CS U" in vec_content),
            ("Default parameters", "DEFAULT PARAMETERS:" in vec_content),
            ("Catchment data reference", ".cat" in vec_content),
            ("File termination", "END OF CATCHMENT DATA." in vec_content),
        ]
        
        for test_name, result in validations:
            status = "✓" if result else "✗"
            print(f"{status} {test_name}")
        
        all_passed = all(result for _, result in validations)
        if all_passed:
            print("\n✅ All validations passed! URBS implementation working correctly.")
        else:
            print("\n⚠️ Some validations failed.")
            
        return all_passed
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_urbs_standalone()
    if success:
        print("\n🎉 URBS implementation ready for QGIS plugin testing!")
    else:
        print("\n❌ URBS implementation needs debugging.")
