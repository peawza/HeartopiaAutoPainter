@echo off
title Build DLL Injection Tester (Advanced Options)
color 0B

REM Change to script directory
cd /d "%~dp0"

echo ============================================================
echo   DLL Injection Tester - Advanced Build Options
echo ============================================================
echo.
echo Working Directory: %CD%
echo.
echo Choose build option:
echo.
echo [1] Standard Build (Console, ~5-6 MB)
echo [2] Silent Build (No console window, ~5-6 MB)
echo [3] Debug Build (With verbose output)
echo [4] Optimized Build (UPX compression, smaller size)
echo [5] Build with Icon (requires icon file)
echo.
echo [0] Cancel
echo.

set /p choice="Enter your choice (0-5): "

if "%choice%"=="0" goto :end
if "%choice%"=="1" goto :standard
if "%choice%"=="2" goto :silent
if "%choice%"=="3" goto :debug
if "%choice%"=="4" goto :optimized
if "%choice%"=="5" goto :withicon

echo Invalid choice!
pause
goto :end

:standard
echo.
echo ============================================================
echo   Building: STANDARD (Console mode)
echo ============================================================
echo.
pyinstaller --onefile ^
    --name="DLL_Injection_Tester" ^
    --console ^
    --clean ^
    --noconfirm ^
    dll_injection_tester.py
goto :check

:silent
echo.
echo ============================================================
echo   Building: SILENT (No console window)
echo ============================================================
echo.
echo WARNING: No console window means no output visible!
echo Recommended only if you wrap this in another GUI.
echo.
pause
pyinstaller --onefile ^
    --name="DLL_Injection_Tester" ^
    --noconsole ^
    --clean ^
    --noconfirm ^
    dll_injection_tester.py
goto :check

:debug
echo.
echo ============================================================
echo   Building: DEBUG (Verbose output)
echo ============================================================
echo.
pyinstaller --onefile ^
    --name="DLL_Injection_Tester" ^
    --console ^
    --clean ^
    --noconfirm ^
    --debug=all ^
    --log-level=DEBUG ^
    dll_injection_tester.py
goto :check

:optimized
echo.
echo ============================================================
echo   Building: OPTIMIZED (UPX compressed)
echo ============================================================
echo.
echo Checking for UPX...
where upx >nul 2>&1
if %errorlevel% neq 0 (
    echo UPX not found! Downloading...
    echo Please download UPX manually from:
    echo https://github.com/upx/upx/releases
    echo.
    echo Extract upx.exe to a folder in your PATH
    pause
    goto :end
)
pyinstaller --onefile ^
    --name="DLL_Injection_Tester" ^
    --console ^
    --clean ^
    --noconfirm ^
    --upx-dir=. ^
    dll_injection_tester.py
goto :check

:withicon
echo.
echo ============================================================
echo   Building: WITH ICON
echo ============================================================
echo.
if not exist "icon.ico" (
    echo ERROR: icon.ico not found in current directory!
    echo.
    echo Please create or download an icon file named "icon.ico"
    echo and place it in the project root folder.
    echo.
    pause
    goto :end
)
pyinstaller --onefile ^
    --name="DLL_Injection_Tester" ^
    --console ^
    --icon=icon.ico ^
    --clean ^
    --noconfirm ^
    dll_injection_tester.py
goto :check

:check
echo.
echo ============================================================
echo   Checking build result...
echo ============================================================
echo.
if exist "dist\DLL_Injection_Tester.exe" (
    echo SUCCESS! EXE built successfully!
    echo.
    echo File location: dist\DLL_Injection_Tester.exe
    echo.
    dir "dist\DLL_Injection_Tester.exe"
    echo.
    echo ============================================================
    echo   Testing the EXE...
    echo ============================================================
    echo.
    echo Press any key to test the EXE (or close this window to skip)
    pause
    "dist\DLL_Injection_Tester.exe"
) else (
    echo BUILD FAILED!
    echo Please check the error messages above.
)
echo.

:end
pause
