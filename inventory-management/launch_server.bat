@echo off
echo ========================================
echo Inventory Management System - Server
echo ========================================
echo.

:: Get local IP address
echo Detecting network IP address...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4"') do (
    set "IP=%%a"
    goto :found
)
:found
:: Remove leading spaces
set IP=%IP: =%

echo.
echo ========================================
echo SERVER INFORMATION
echo ========================================
echo Local access (this computer only):
echo   http://127.0.0.1:5001
echo.
echo Network access (for colleagues):
echo   http://%IP%:5001
echo.
echo Share the network URL with your colleagues!
echo ========================================
echo.

:: Make sure firewall allows port 5001
echo Checking Windows Firewall...
netsh advfirewall firewall show rule name="Flask Port 5001" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Adding firewall rule for port 5001...
    netsh advfirewall firewall add rule name="Flask Port 5001" dir=in action=allow protocol=TCP localport=5001 >nul 2>&1
    if errorlevel 1 (
        echo WARNING: Could not add firewall rule automatically.
        echo You may need to manually allow port 5001 in Windows Firewall.
    ) else (
        echo ✓ Firewall rule added successfully!
    )
) else (
    echo ✓ Firewall rule already exists
)

echo.
echo ========================================
echo Starting server...
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

call venv\Scripts\activate.bat
python app.py

pause
