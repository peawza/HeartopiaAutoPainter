@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Restore Original Arduino Leonardo USB
echo ========================================
echo.

REM Find Arduino15 directory
set ARDUINO_DIR=%LOCALAPPDATA%\Arduino15\packages\arduino\hardware\avr

if not exist "%ARDUINO_DIR%" (
    echo ERROR: Arduino AVR package not found!
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
set BACKUP_FILE=%BOARDS_FILE%.backup_original

echo Found Arduino AVR version: %AVR_VERSION%
echo.

if not exist "%BACKUP_FILE%" (
    echo ERROR: No backup file found!
    echo Original boards.txt may not have been modified.
    pause
    exit /b 1
)

echo Restoring original boards.txt...
copy /y "%BACKUP_FILE%" "%BOARDS_FILE%" >nul

if errorlevel 1 (
    echo ERROR: Failed to restore backup
    pause
    exit /b 1
)

echo ========================================
echo SUCCESS! Original USB descriptor restored.
echo ========================================
echo.
echo Please restart Arduino IDE for changes to take effect.
echo.

pause
