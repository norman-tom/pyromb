@echo off
REM Quick sync script for QGIS plugin development
REM Runs the Python update script and provides feedback

echo QGIS Plugin Sync
echo ==================

cd /d "E:\GitHub\pyromb2025"

echo Running plugin update script...
python update_plugin.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Sync completed successfully!
    echo.
    echo Next steps in QGIS:
    echo 1. Use Plugin Reloader to reload 'Build URBS'
    echo 2. Test the plugin with your sample data
    echo.
) else (
    echo.
    echo ❌ Sync failed - check error messages above
    echo.
)

pause
