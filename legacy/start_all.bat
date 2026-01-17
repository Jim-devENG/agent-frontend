@echo off
echo ========================================
echo   Starting Frontend ^& Backend (with venv)
echo ========================================
echo.

cd /d "%~dp0"

REM Check if venv exists, create if not
if not exist "venv" (
    echo Creating virtual environment...
    py -m venv venv
    echo Virtual environment created
)

REM Activate venv and install dependencies
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Checking dependencies...
venv\Scripts\python.exe -m uvicorn --version >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    venv\Scripts\python.exe -m pip install -r requirements.txt
    echo Dependencies installed
) else (
    echo Dependencies already installed
)

echo.
echo Starting Backend Server...
start "FastAPI Backend" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
start "Next.js Frontend" cmd /k "cd /d %~dp0\frontend && npm run dev"

echo.
echo ========================================
echo   Both servers are starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Wait for both to start, then open: http://localhost:3000
echo.
pause
