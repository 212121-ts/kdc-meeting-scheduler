@echo off
title Meeting Poll App
echo ============================================
echo    MEETING POLL APP - Starting Server
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Install Flask if needed
echo Installing dependencies...
pip install flask >nul 2>&1

REM Start the application
echo.
echo Starting server at http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
echo Your browser should open automatically...
echo ============================================

REM Start the app
python run.py

echo.
echo Server stopped. Press any key to exit.
pause >nul