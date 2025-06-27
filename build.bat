@echo off
setlocal

REM Verify Python and Pip paths
echo Using Python from:
where python
echo Using pip from:
where pip

REM Check setuptools version
python -m pip show setuptools

REM Upgrade setuptools and wheel
echo Upgrading setuptools and wheel...
python -m pip install --upgrade setuptools wheel

REM Define the directory where the package will be stored
set "PACKAGE_DIR=%~dp0dist"
echo Package directory: %PACKAGE_DIR%

REM Navigate to the directory containing the setup.py script
cd /d "%~dp0"

REM Clean previous builds
if exist "%PACKAGE_DIR%" (
    echo Cleaning previous builds...
    rmdir /s /q "%PACKAGE_DIR%"
)

REM Build the source distribution and wheel using setuptools
echo Building the package using setuptools...
python setup.py sdist bdist_wheel

REM Check if the build was successful
if %ERRORLEVEL% neq 0 (
    echo Build failed. Please check the setup.py and pyproject.toml for errors.
    endlocal
    pause
    goto :EOF
)

REM Create the dist directory if it doesn't exist
if not exist "%PACKAGE_DIR%" mkdir "%PACKAGE_DIR%"

REM Move the generated .tar.gz and .whl files to the desired folder
echo Moving built packages to %PACKAGE_DIR%...
move /Y "dist\*.tar.gz" "%PACKAGE_DIR%" >nul
move /Y "dist\*.whl" "%PACKAGE_DIR%" >nul

REM Check if the move was successful
if %ERRORLEVEL% neq 0 (
    echo Failed to move the package to the destination folder.
    endlocal
    pause
    goto :EOF
)

echo Package created and moved to %PACKAGE_DIR% successfully.
endlocal
pause
goto :EOF
