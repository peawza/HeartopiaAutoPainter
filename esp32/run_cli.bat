@echo off
set SRC=C:\Users\gamwi\AppData\Local\Programs\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe
copy "%SRC%" "C:\arduino-cli.exe" >nul 2>&1
echo Copied arduino-cli to C:\arduino-cli.exe
C:\arduino-cli.exe %*
