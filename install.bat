@echo off

title phpIPAM to NetBox - Installation

echo ==========================================
echo   phpIPAM to NetBox - Installation
echo ==========================================
echo.

py --version >nul 2>&1

if errorlevel 1 (
    echo Python is not installed.
    echo.
    echo Please install Python 3.12 or newer from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python detected:
py --version

echo.
echo Installing dependencies...
echo.

py -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Installation failed.
    pause
    exit /b 1
)

echo.
echo Installation completed successfully.
pause