@echo off
echo ========================================
echo Setting up Build Environment
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found in PATH!
    echo Please install Python and try again.
    pause
    exit /b 1
)

echo Step 1: Creating virtual environment...
if exist .venv (
    echo Virtual environment already exists.
) else (
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
)

echo.
echo Step 2: Activating virtual environment...
call .venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)

echo.
echo Step 3: Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Step 4: Installing requirements...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install requirements!
    pause
    exit /b 1
)

echo.
echo Step 5: Installing PyInstaller...
pip install pyinstaller
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install PyInstaller!
    pause
    exit /b 1
)

echo.
echo Step 6: Installing additional packages for stealth build...
pip install pyarmor psutil pywin32
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Some additional packages failed to install.
    echo Build may still work with basic functionality.
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo You can now run:
echo   - build_stealth.bat (for stealth executable)
echo   - Or directly: python main.py (to test)
echo.
pause
