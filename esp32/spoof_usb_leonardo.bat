@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Arduino Leonardo USB Spoofing Setup
echo Logitech G Pro X Superlight
echo ========================================
echo.

REM Find Arduino15 directory
set ARDUINO_DIR=%LOCALAPPDATA%\Arduino15\packages\arduino\hardware\avr

if not exist "%ARDUINO_DIR%" (
    echo ERROR: Arduino AVR package not found!
    echo Please install Arduino AVR boards first.
    echo.
    pause
    exit /b 1
)

REM Find the latest version
for /f "delims=" %%i in ('dir /b /ad /o-n "%ARDUINO_DIR%"') do (
    set AVR_VERSION=%%i
    goto :found_version
)

:found_version
set BOARDS_FILE=%ARDUINO_DIR%\%AVR_VERSION%\boards.txt

echo Found Arduino AVR version: %AVR_VERSION%
echo Boards file: %BOARDS_FILE%
echo.

if not exist "%BOARDS_FILE%" (
    echo ERROR: boards.txt not found!
    pause
    exit /b 1
)

REM Backup original boards.txt
set BACKUP_FILE=%BOARDS_FILE%.backup_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_FILE=%BACKUP_FILE: =0%

if not exist "%BOARDS_FILE%.backup_original" (
    echo Creating backup: %BACKUP_FILE%
    copy "%BOARDS_FILE%" "%BACKUP_FILE%" >nul
    copy "%BOARDS_FILE%" "%BOARDS_FILE%.backup_original" >nul
)

echo.
echo Modifying Leonardo USB descriptor...
echo.

REM Create modified boards.txt with Logitech spoofing
powershell -Command "(Get-Content '%BOARDS_FILE%') -replace 'leonardo\.build\.usb_product=\"Arduino Leonardo\"', 'leonardo.build.usb_product=\"G Pro X Superlight\"' -replace 'leonardo\.build\.usb_manufacturer=\"Arduino LLC\"', 'leonardo.build.usb_manufacturer=\"Logitech\"' -replace 'leonardo\.build\.vid=0x2341', 'leonardo.build.vid=0x046D' -replace 'leonardo\.build\.pid=0x8036', 'leonardo.build.pid=0xC07D' | Set-Content '%BOARDS_FILE%.new'"

if exist "%BOARDS_FILE%.new" (
    move /y "%BOARDS_FILE%.new" "%BOARDS_FILE%" >nul
    echo ========================================
    echo SUCCESS! USB descriptor modified.
    echo ========================================
    echo.
    echo Changes applied:
    echo   VID: 0x046D ^(Logitech^)
    echo   PID: 0xC07D ^(G Pro X Superlight^)
    echo   Product: "G Pro X Superlight"
    echo   Manufacturer: "Logitech"
    echo.
    echo IMPORTANT:
    echo 1. Restart Arduino IDE
    echo 2. Upload Arduino_Mouse.ino to Leonardo
    echo 3. Check Device Manager for "Logitech" device
    echo.
    echo To restore original: run restore_usb_leonardo.bat
    echo.
) else (
    echo ERROR: Failed to create modified file
    pause
    exit /b 1
)

pause
