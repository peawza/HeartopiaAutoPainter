@echo off
cd /d "%~dp0"
echo Current Directory: %CD%
echo.
echo Files in this directory:
dir /b *.py *.bat
echo.
echo Testing PyInstaller command:
pyinstaller --version
echo.
pause
