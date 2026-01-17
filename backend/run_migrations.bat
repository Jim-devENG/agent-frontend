@echo off
REM Run Alembic migrations on Windows
echo Running Alembic migrations...
cd /d %~dp0
python run_migrations.py
if %ERRORLEVEL% NEQ 0 (
    echo Migration failed!
    pause
    exit /b %ERRORLEVEL%
)
echo Migrations completed successfully!
pause

