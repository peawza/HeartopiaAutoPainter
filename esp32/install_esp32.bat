@echo off
setlocal
set CLI=C:\Users\gamwi\AppData\Local\Programs\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe

echo ========================================
echo Installing ESP32 Arduino Core
echo ========================================
echo.

echo [1/3] Adding ESP32 board manager URL...
"%CLI%" config init --overwrite
"%CLI%" config add board_manager.additional_urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
echo.

echo [2/3] Updating package index...
"%CLI%" core update-index
echo.

echo [3/3] Installing ESP32 core (this may take 2-5 minutes)...
"%CLI%" core install esp32:esp32
echo.

echo ========================================
echo Installation complete!
echo ========================================
echo.
echo Now installed platforms:
"%CLI%" core list
echo.

echo Press any key to close...
pause > nul
