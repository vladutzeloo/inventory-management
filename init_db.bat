@echo off
echo ========================================
echo Quick Database Initialization
echo ========================================
echo.

cd /d "%~dp0inventory-management"

:: Check if venv exists
if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat

echo Initializing database...
python sample_data.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to initialize database
    echo.
    echo If you see errors about missing modules, run setup.bat first.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Database initialized successfully!
echo ========================================
echo.
echo You can now run launch_server.bat to start the application
pause
