@echo off
title Build DLL Injection Tester to EXE
color 0B

REM Change to script directory
cd /d "%~dp0"

echo ============================================================
echo   Building DLL Injection Tester to Standalone EXE
echo ============================================================
echo.
echo Working Directory: %CD%
echo.

REM Check if PyInstaller is installed
echo [1/4] Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
) else (
    echo PyInstaller is already installed.
)
echo.

REM Clean previous build
echo [2/4] Cleaning previous build files...
if exist "dist\DLL_Injection_Tester.exe" (
    echo Removing old EXE...
    del /F /Q "dist\DLL_Injection_Tester.exe"
)
if exist "build\DLL_Injection_Tester" (
    echo Removing old build folder...
    rmdir /S /Q "build\DLL_Injection_Tester"
)
if exist "DLL_Injection_Tester.spec" (
    echo Removing old spec file...
    del /F /Q "DLL_Injection_Tester.spec"
)
echo.

REM Build EXE
echo [3/4] Building EXE with PyInstaller...
echo This may take 1-3 minutes...
echo.
pyinstaller --onefile ^
    --name="DLL_Injection_Tester" ^
    --console ^
    --clean ^
    --noconfirm ^
    dll_injection_tester.py

echo.

REM Check if build was successful
echo [4/4] Checking build result...
if exist "dist\DLL_Injection_Tester.exe" (
    echo ============================================================
    echo   SUCCESS! EXE built successfully!
    echo ============================================================
    echo.
    echo   File location: dist\DLL_Injection_Tester.exe
    echo.
    dir "dist\DLL_Injection_Tester.exe"
    echo.
    echo ============================================================
    echo   You can now distribute this EXE to users
    echo   No Python installation required!
    echo ============================================================
) else (
    echo ============================================================
    echo   BUILD FAILED!
    echo ============================================================
    echo   Please check the error messages above.
    echo.
    echo   Common issues:
    echo   1. Python not in PATH
    echo   2. Missing dependencies (pip install psutil)
    echo   3. Antivirus blocking PyInstaller
    echo ============================================================
)

echo.
pause
