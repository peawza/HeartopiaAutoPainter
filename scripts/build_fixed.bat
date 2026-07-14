@echo off
echo ========================================
echo Building Painter_Stealth.exe
echo (Fixed Binary Analysis Error)
echo ========================================
echo.

REM Activate venv
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

REM Clean previous build
echo Cleaning previous build...
if exist "build" rmdir /s /q build
if exist "dist\Painter_Stealth.exe" del /q dist\Painter_Stealth.exe

REM Set environment to skip strict binary analysis
set PYINSTALLER_STRICT_BINARY_ANALYSIS=0

REM Build with PyInstaller
echo.
echo Building with PyInstaller...
echo ----------------------------------------
python -m PyInstaller painter_stealth_fixed.spec --clean --noconfirm --log-level=WARN

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
pause
