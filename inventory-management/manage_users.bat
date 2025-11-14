@echo off
echo ========================================
echo User Management Tool
echo ========================================
echo.

call venv\Scripts\activate.bat
python manage_users.py

pause
