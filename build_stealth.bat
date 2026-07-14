@echo off
setlocal EnableExtensions

REM Always run relative to this batch file, even when launched from another folder.
cd /d "%~dp0"

set "VENV_DIR=.venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "OUTPUT_EXE=dist\Painter_Stealth.exe"
set "NO_PAUSE=0"
if /I "%~1"=="--no-pause" set "NO_PAUSE=1"

echo ========================================
echo Building Painter_Stealth.exe
echo ========================================
echo Project: %CD%
echo.

if not exist "%VENV_PYTHON%" (
    echo [SETUP] Virtual environment not found. Creating %VENV_DIR%...
    where python >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python was not found in PATH.
        echo Install Python 3.10 or newer, then run this file again.
        goto :fail
    )

    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERROR] Could not create the virtual environment.
        goto :fail
    )
)

echo [CHECK] Verifying build dependencies...
"%VENV_PYTHON%" -c "import PyInstaller, PySide6, PIL, mss, pynput, pyautogui, serial, psutil" >nul 2>&1
if errorlevel 1 (
    echo [SETUP] Installing project and build dependencies...
    "%VENV_PYTHON%" -m pip install -r requirements.txt pyinstaller psutil
    if errorlevel 1 (
        echo [ERROR] Dependency installation failed.
        echo Check the internet connection and pip output above.
        goto :fail
    )
)

if not exist "config.json" (
    echo [ERROR] config.json was not found in %CD%.
    goto :fail
)

if not exist "build_stealth.py" (
    echo [ERROR] build_stealth.py was not found in %CD%.
    goto :fail
)

echo [BUILD] Starting build with %VENV_PYTHON%...
echo.
"%VENV_PYTHON%" build_stealth.py
if errorlevel 1 (
    echo.
    echo [ERROR] Build script failed.
    goto :fail
)

if not exist "%OUTPUT_EXE%" (
    echo.
    echo [ERROR] Build script finished but %OUTPUT_EXE% was not created.
    goto :fail
)

echo.
echo ========================================
echo Build Complete
echo ========================================
echo Executable: %CD%\%OUTPUT_EXE%
echo.
if "%NO_PAUSE%"=="0" pause
exit /b 0

:fail
echo.
echo Build did not complete.
if "%NO_PAUSE%"=="0" pause
exit /b 1
