@echo off
setlocal

REM THIS DIDN'T SEEM TO WORK, LIKELY USER ERROR.

REM Activate OSGeo4W environment
call "C:\OSGEO4W\bin\o4w_env.bat"

REM Define the directory where the built package is stored
set "PACKAGE_DIR=%~dp0dist"
echo Package directory: %PACKAGE_DIR%

REM Find the latest version of the package
for /f "delims=" %%i in ('dir /b /o-n "%PACKAGE_DIR%\pyromb-*.whl"') do (
    set "LATEST_PACKAGE=%%i"
    goto found
)

:found
if "%LATEST_PACKAGE%"=="" (
    echo No package found in the directory.
    pause
    endlocal
    goto :EOF
)

echo Installing or updating "%LATEST_PACKAGE%"

REM Install or update the package using pip from the OSGeo4W environment
pip install --upgrade "%PACKAGE_DIR%\%LATEST_PACKAGE%"

REM Check if the installation was successful
if %ERRORLEVEL% equ 0 (
    echo Installation completed successfully.
) else (
    echo Installation failed. Please check the path and try again.
)

endlocal
pause
goto :EOF
