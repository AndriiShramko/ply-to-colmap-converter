@echo off
REM ============================================================
REM Professional Build Script for Portable PLY Converter
REM Creates standalone executable for Windows 10/11
REM ============================================================

echo.
echo ============================================================
echo   PLY to COLMAP Converter - Portable Build
echo ============================================================
echo.
echo This script will create a standalone portable executable
echo that works on Windows 10/11 without any dependencies.
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.6+ and try again
    pause
    exit /b 1
)

echo [1/5] Checking PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller --quiet
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller
        pause
        exit /b 1
    )
    echo PyInstaller installed successfully
) else (
    echo PyInstaller is installed
)

echo.
echo [2/5] Checking required files...
if not exist "gui_converter.py" (
    echo [ERROR] gui_converter.py not found
    pause
    exit /b 1
)
if not exist "Shramko_Andrii_ply_to_colmap_converter.py" (
    echo [ERROR] Shramko_Andrii_ply_to_colmap_converter.py not found
    pause
    exit /b 1
)
echo All required files found

echo.
echo [3/5] Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"
echo Cleaned

echo.
echo [4/5] Building executable...
echo This may take a few minutes...
echo.

REM Use Python script for better control
python build_portable.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo [5/5] Build verification...
if exist "dist\PLY_to_COLMAP_Converter.exe" (
    echo.
    echo ============================================================
    echo   BUILD SUCCESSFUL!
    echo ============================================================
    echo.
    echo Portable executable created:
    echo   dist\PLY_to_COLMAP_Converter.exe
    echo.
    echo The executable is ready for distribution!
    echo You can copy it to any Windows 10/11 computer and run it.
    echo No installation or additional software required.
    echo.
) else (
    echo [ERROR] Executable not found after build
    pause
    exit /b 1
)

pause

