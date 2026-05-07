@echo off
title MediCare Clinic — Server Launcher
color 0B

echo.
echo  =====================================================
echo    MediCare Clinic — Django Backend Server
echo  =====================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found! Install from https://python.org
    pause
    exit /b 1
)

:: Activate virtual environment
if exist "backend\venv\Scripts\activate.bat" (
    call backend\venv\Scripts\activate.bat
    echo  [OK] Virtual environment activated
) else (
    echo  [WARN] No virtual environment found. Run: python setup.py
)

:: Start server
echo.
echo  Starting server at http://127.0.0.1:8000/
echo  Admin panel: http://127.0.0.1:8000/admin/
echo  Open frontend\index.html in your browser
echo.
echo  Press Ctrl+C to stop
echo.

cd backend
python manage.py runserver 0.0.0.0:8000

pause
