@echo off
echo Starting FastAPI Backend Server...
echo.

cd /d "%~dp0"

REM Try to find Python
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Using Python launcher (py)...
    py -3.11 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    goto :end
)

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Using Python...
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    goto :end
)

echo ERROR: Python not found!
echo Please install Python 3.11+ and add it to your PATH
pause

:end

