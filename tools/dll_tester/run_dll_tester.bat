@echo off
title DLL Injection Tester
color 0B

REM Change to script directory
cd /d "%~dp0"

python dll_injection_tester.py
pause
