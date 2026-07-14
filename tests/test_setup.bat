@echo off
chcp 65001 > nul
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║       ESP32 Hardware Mouse - ตรวจสอบความพร้อม             ║
echo ║              HeartopiaAutoPainter v1.0                     ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is available
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python ไม่พบในระบบ!
    echo.
    echo กรุณาติดตั้ง Python 3.8+ จาก: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [INFO] กำลังตรวจสอบระบบ...
echo.

REM Run the test script
python test_esp32_setup.py

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                   ตรวจสอบเสร็จสิ้น                        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

pause
