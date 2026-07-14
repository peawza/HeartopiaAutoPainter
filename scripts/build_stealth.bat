@echo off
echo ========================================
echo Building Painter_Stealth.exe
echo (with Anti-Detection)
echo ========================================
echo.

REM Check if config.json exists
if not exist "config.json" (
    echo ERROR: config.json not found!
    echo Please run setup_build.bat first.
    pause
    exit /b 1
)

REM Activate venv
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    echo Please run setup_build.bat first to set up the environment.
    pause
    exit /b 1
)

REM Run build_stealth.py
echo Building with anti-detection techniques...
python build_stealth.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Executable: dist\Painter_Stealth.exe
echo.
echo Next Steps:
echo   1. Test with: dist\Painter_Stealth.exe
echo   2. Or test protection: build_painter_tester.bat
echo.
pause
