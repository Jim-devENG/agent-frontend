# Start Backend Server Script (with venv)
Write-Host "Starting FastAPI backend server..." -ForegroundColor Green

# Change to project directory
Set-Location $PSScriptRoot

# Check if venv exists, create if not
if (-not (Test-Path "venv")) {
    Write-Host "[*] Creating virtual environment..." -ForegroundColor Yellow
    py -m venv venv
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
}

# Activate venv
Write-Host "[*] Activating virtual environment..." -ForegroundColor Yellow
& "$PSScriptRoot\venv\Scripts\Activate.ps1"

# Check if requirements are installed
Write-Host "[*] Checking dependencies..." -ForegroundColor Yellow
try {
    $uvicornCheck = & "$PSScriptRoot\venv\Scripts\python.exe" -m uvicorn --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[*] Installing requirements..." -ForegroundColor Yellow
        & "$PSScriptRoot\venv\Scripts\python.exe" -m pip install -r requirements.txt
        Write-Host "[OK] Dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "[OK] Dependencies already installed" -ForegroundColor Green
    }
} catch {
    Write-Host "[*] Installing requirements..." -ForegroundColor Yellow
    & "$PSScriptRoot\venv\Scripts\python.exe" -m pip install -r requirements.txt
    Write-Host "[OK] Dependencies installed" -ForegroundColor Green
}

# Start the server
Write-Host ""
Write-Host "[*] Starting server on http://localhost:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

& "$PSScriptRoot\venv\Scripts\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
