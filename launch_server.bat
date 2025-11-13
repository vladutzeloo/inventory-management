@echo off
echo ========================================
echo Inventory Management System - Server
echo ========================================
echo.

:: Navigate to the project directory
cd /d "%~dp0inventory-management"

:: Check if virtual environment exists
if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first to initialize the project.
    pause
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo.

:: Display server information
echo ========================================
echo Starting Flask Development Server...
echo ========================================
echo.
echo Server will be available at:
echo   http://localhost:5001
echo   http://127.0.0.1:5001
echo.
echo Default login:
echo   Username: admin
echo   Password: admin123
echo.
echo Press CTRL+C to stop the server
echo ========================================
echo.

:: Start the Flask application
python app.py

:: If the server stops, pause to show any error messages
if errorlevel 1 (
    echo.
    echo ERROR: Server stopped with an error
    pause
)
