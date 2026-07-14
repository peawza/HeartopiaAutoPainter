@echo off
set CLI="C:\Users\gamwi\AppData\Local\Programs\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe"

echo === Installed platforms ===
%CLI% core list
echo.

echo === All AVR boards available ===
%CLI% board listall arduino:avr
echo.

echo === Board details on COM6 ===
%CLI% board list --discovery-timeout 5s
