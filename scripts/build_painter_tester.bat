@echo off
echo ========================================
echo Building Painter Protection Tester
echo ========================================
echo.

REM Activate venv
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    echo Please create it first: python -m venv .venv
    pause
    exit /b 1
)

REM Build with PyInstaller
echo Building test_painter_protection.py...
python -m PyInstaller ^
    --onefile ^
    --console ^
    --name="Painter_Protection_Tester" ^
    --icon=NONE ^
    --clean ^
    test_painter_protection.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build SUCCESS!
echo ========================================
echo.
echo Executable: dist\Painter_Protection_Tester.exe
echo.
echo Usage:
echo   1. Build Painter_Stealth.exe first: build_stealth.bat
echo   2. Run tester: dist\Painter_Protection_Tester.exe
echo.
pause
