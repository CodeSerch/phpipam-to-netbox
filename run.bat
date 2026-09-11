@echo off

title phpIPAM to NetBox Converter

py --version >nul 2>&1

if errorlevel 1 (
    echo Python is not installed.
    echo.
    echo Run install.bat after installing Python.
    echo.
    pause
    exit /b 1
)

py main.py

if errorlevel 1 (
    echo.
    echo The application terminated with an error.
    pause
)