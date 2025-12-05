# Simple backend startup script
$env:PYTHONIOENCODING = "utf-8"
cd $PSScriptRoot

if (Test-Path "..\venv\Scripts\python.exe") {
    $pythonExe = "..\venv\Scripts\python.exe"
} elseif (Test-Path "venv\Scripts\python.exe") {
    $pythonExe = "venv\Scripts\python.exe"
} else {
    $pythonExe = "python"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FastAPI Backend Server" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Python: $pythonExe" -ForegroundColor White
Write-Host "Directory: $PWD" -ForegroundColor White

if (Test-Path ".env") {
    Write-Host ".env: Found" -ForegroundColor Green
} else {
    Write-Host ".env: Missing" -ForegroundColor Red
}

Write-Host ""
Write-Host "Starting server..." -ForegroundColor Yellow
Write-Host ""

& $pythonExe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

