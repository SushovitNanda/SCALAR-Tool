@echo off
echo === SCALAR ===
echo.
echo Starting SCALAR...

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

:: Run the Python script which handles everything else
python launch_app.py

:: If the script exits with an error, pause to show the error message
if %errorlevel% neq 0 (
    pause
)
