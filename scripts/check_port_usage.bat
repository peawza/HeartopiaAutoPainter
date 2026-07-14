@echo off
echo ============================================================
echo Checking which process is using COM ports
echo ============================================================
echo.

echo Method 1: Using PowerShell Get-Process
echo --------------------------------------------------------
powershell -Command "Get-Process | Where-Object {$_.Path -like '*Logitech*'} | Select-Object Name, Id, Path"

echo.
echo Method 2: Checking Device Manager
echo --------------------------------------------------------
echo Opening Device Manager...
echo Please check "Ports (COM ^& LPT)" to see COM6 details
devmgmt.msc

echo.
echo ============================================================
echo Instructions:
echo ============================================================
echo 1. Close Logitech Options / G HUB / Gaming Software
echo 2. If still blocked, unplug and replug the device
echo 3. Try connection again
echo ============================================================
pause
