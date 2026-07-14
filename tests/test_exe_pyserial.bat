@echo off
echo ========================================
echo Testing Painter_Stealth.exe for pyserial
echo ========================================
echo.

cd dist

echo Checking if Painter_Stealth.exe exists...
if not exist "Painter_Stealth.exe" (
    echo ERROR: Painter_Stealth.exe not found!
    pause
    exit /b 1
)

echo Found Painter_Stealth.exe
echo.
echo File info:
dir Painter_Stealth.exe | findstr /C:"Painter_Stealth.exe"
echo.

echo ========================================
echo Please manually test:
echo 1. Run Painter_Stealth.exe
echo 2. Go to tab "จังหวะ / ความน่าเชื่อถือ"
echo 3. Click the refresh button (🔄)
echo 4. Check if there's NO error about pyserial
echo ========================================

pause
