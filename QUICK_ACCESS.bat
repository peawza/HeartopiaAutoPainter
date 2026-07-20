@echo off
title HeartopiaAutoPainter - Quick Access Menu
color 0B

:menu
cls
echo ================================================================
echo.
echo            HeartopiaAutoPainter - Quick Access Menu
echo.
echo ================================================================
echo.
echo  [1] Run Main Program
echo  [2] Run DLL Injection Tester
echo  [3] Test Anti-Detection Layer
echo  [4] Build Main Program to EXE
echo  [5] Build DLL Tester to EXE
echo.
echo  [6] Open Tools Folder
echo  [7] Open Documentation Index
echo  [8] View Project Structure
echo.
echo  [0] Exit
echo.
echo ================================================================
echo.

set /p choice="Enter your choice (0-8): "

if "%choice%"=="0" goto :end
if "%choice%"=="1" goto :run_main
if "%choice%"=="2" goto :run_dll_tester
if "%choice%"=="3" goto :test_anti_detection
if "%choice%"=="4" goto :build_main
if "%choice%"=="5" goto :build_dll_tester
if "%choice%"=="6" goto :open_tools
if "%choice%"=="7" goto :open_docs
if "%choice%"=="8" goto :view_structure

echo.
echo Invalid choice! Please enter 0-8.
echo.
pause
goto :menu

:run_main
echo.
echo ================================================================
echo  Running Main Program...
echo ================================================================
echo.
python main.py
pause
goto :menu

:run_dll_tester
echo.
echo ================================================================
echo  Running DLL Injection Tester...
echo ================================================================
echo.
cd tools\dll_tester
call run_dll_tester.bat
cd ..\..
goto :menu

:test_anti_detection
echo.
echo ================================================================
echo  Testing Anti-Detection Layer...
echo ================================================================
echo.
python test_anti_detection_simple.py
pause
goto :menu

:build_main
echo.
echo ================================================================
echo  Building Main Program to EXE...
echo ================================================================
echo.
call build_stealth.bat
goto :menu

:build_dll_tester
echo.
echo ================================================================
echo  Building DLL Tester to EXE...
echo ================================================================
echo.
cd tools\dll_tester
call build_dll_tester.bat
cd ..\..
goto :menu

:open_tools
echo.
echo Opening tools folder...
explorer tools
goto :menu

:open_docs
echo.
echo Opening documentation index...
start TOOLS_INDEX.md
goto :menu

:view_structure
echo.
echo ================================================================
echo  Project Structure:
echo ================================================================
echo.
echo HeartopiaAutoPainter/
echo ^|
echo +-- main.py                      (Main program)
echo +-- anti_detection.py            (Anti-detection layer)
echo ^|
echo +-- tools/
echo ^|   +-- dll_tester/              (DLL Injection Tester)
echo ^|       +-- dll_injection_tester.py
echo ^|       +-- run_dll_tester.bat
echo ^|       +-- build_dll_tester.bat
echo ^|
echo +-- esp32/                        (Arduino/ESP32 firmware)
echo +-- docs/                         (Documentation)
echo +-- tests/                        (Test files)
echo +-- src/                          (Source code)
echo ^|
echo +-- TOOLS_INDEX.md               (Tools documentation)
echo +-- README.md                    (Main readme)
echo +-- QUICK_ACCESS.bat             (This menu)
echo.
echo ================================================================
echo.
echo For detailed structure, see: PROJECT_STRUCTURE.md
echo For tools documentation, see: TOOLS_INDEX.md
echo.
pause
goto :menu

:end
echo.
echo Goodbye!
timeout /t 2 >nul
exit
