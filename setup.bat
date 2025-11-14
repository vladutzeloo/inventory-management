@echo off
echo ========================================
echo Inventory Management System - Setup
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/6] Checking Python version...
python --version
echo.

:: Setup .env file with SECRET_KEY
echo [2/6] Setting up environment configuration...
cd /d "%~dp0"
if exist .env (
    echo .env file already exists, skipping...
) else (
    if not exist .env.example (
        echo ERROR: .env.example not found!
        pause
        exit /b 1
    )
    echo Generating secure SECRET_KEY...
    python -c "import secrets; key = secrets.token_hex(32); content = open('.env.example').read().replace('SECRET_KEY=your-secret-key-here-generate-a-random-string', f'SECRET_KEY={key}'); open('.env', 'w').write(content); print(f'Created .env with SECRET_KEY: {key[:16]}...')"
    if errorlevel 1 (
        echo ERROR: Failed to create .env file
        echo Please manually copy .env.example to .env and set SECRET_KEY
        pause
        exit /b 1
    )
    echo .env file created successfully!
)
echo.

:: Navigate to the project directory
cd /d "%~dp0inventory-management"

:: Create virtual environment
echo [3/6] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping creation...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
)
echo.

:: Activate virtual environment
echo [4/6] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo.

:: Install dependencies
echo [5/6] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

:: Initialize database with sample data
echo [6/6] Initializing database with sample data...
python sample_data.py
if errorlevel 1 (
    echo ERROR: Failed to initialize database
    pause
    exit /b 1
)
echo.

echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Default login credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo Alternative user:
echo   Username: manager
echo   Password: manager123
echo.
echo To start the server, run: launch_server.bat
echo ========================================
pause
