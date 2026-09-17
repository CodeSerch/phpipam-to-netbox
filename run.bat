@echo off

title phpIPAM to NetBox Converter

cd /d "%~dp0"

py --version >nul 2>&1

if errorlevel 1 (
    echo Python is not installed.
    echo.
    echo Run install.bat after installing Python.
    echo.
    pause
    exit /b 1
)

py src\main.py

if errorlevel 1 (
    echo.
    echo The application terminated with an error.
    echo.
    pause
)

exit /b