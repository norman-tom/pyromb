# Test URBS model with QGIS Python
$env:PYTHONPATH = "e:\GitHub\pyromb2025\src"
& "C:\Program Files\QGIS 3.40.8\bin\python.exe" -c "
import sys
sys.path.append('e:/GitHub/pyromb2025/src')
try:
    import pyromb
    urbs_model = pyromb.URBS()
    print('URBS model imported and instantiated successfully')
    print('URBS model has formatting options:', hasattr(urbs_model, '_formattingOptions'))
except Exception as e:
    print('Error importing URBS model:', e)
    import traceback
    traceback.print_exc()
"
