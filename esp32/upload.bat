@echo off
set CLI="C:\Users\gamwi\AppData\Local\Programs\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe"
set SKETCH="C:\Users\gamwi\Desktop\Arduino_Mouse"
set PORT=COM6

echo ==========================================
echo  Step 1: Detecting board on %PORT%
echo ==========================================
%CLI% board list
echo.

echo ==========================================
echo  Step 2: Compiling sketch...
echo ==========================================
%CLI% compile --fqbn arduino:avr:leonardo %SKETCH%
if errorlevel 1 (
    echo [ERROR] Compile failed! Trying Pro Micro...
    %CLI% compile --fqbn arduino:avr:promicro %SKETCH%
)
echo.

echo ==========================================
echo  Step 3: Uploading to %PORT%...
echo ==========================================
%CLI% upload -p %PORT% --fqbn arduino:avr:leonardo %SKETCH%
if errorlevel 1 (
    echo [ERROR] Upload failed with leonardo, trying promicro...
    %CLI% upload -p %PORT% --fqbn arduino:avr:promicro %SKETCH%
)
echo.
echo ==========================================
echo  Done!
echo ==========================================
pause
