@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Building Painter_Stealth.exe
echo ========================================
echo.

REM Check if venv exists
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

REM Check if config.json exists
if not exist "config.json" (
    echo ERROR: config.json not found!
    pause
    exit /b 1
)

echo Step 1: Cleaning old build files...
if exist "build\painter_stealth" rmdir /s /q "build\painter_stealth"
if exist "dist\Painter_Stealth.exe" del /q "dist\Painter_Stealth.exe"
echo Done.
echo.

echo Step 2: Building executable with PyInstaller...
echo This may take a few minutes...
echo.

.venv\Scripts\pyinstaller.exe painter_stealth.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD SUCCESSFUL!
echo ========================================
echo.

if exist "dist\Painter_Stealth.exe" (
    for %%F in ("dist\Painter_Stealth.exe") do set size=%%~zF
    set /a sizeMB=!size! / 1048576
    echo Executable created: dist\Painter_Stealth.exe
    echo Size: !sizeMB! MB
    echo.
    echo You can now run: dist\Painter_Stealth.exe
) else (
    echo Warning: Executable not found!
)

echo.
pause
