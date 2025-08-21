import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    import pyromb
    urbs_model = pyromb.URBS()
    print("URBS model imported and instantiated successfully")
    print(f"URBS model has formatting options: {hasattr(urbs_model, '_formattingOptions')}")
except Exception as e:
    print(f"Error importing URBS model: {e}")
    import traceback
    traceback.print_exc()
