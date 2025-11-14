@echo off
echo ========================================
echo Database Migration - Internal Order Number
echo ========================================
echo.

echo This migration adds internal_order_number field to:
echo  - receipts table
echo  - transfers table
echo.

pause

echo Running migration...
call venv\Scripts\activate.bat
python migrations\add_internal_order_number.py

if errorlevel 1 (
    echo.
    echo ERROR: Migration failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Migration completed successfully!
echo ========================================
echo.
echo You can now use the Internal Order Number feature in:
echo  - Receipts (for internal production receipts)
echo  - Transfers (for production order tracking)
echo.
pause
