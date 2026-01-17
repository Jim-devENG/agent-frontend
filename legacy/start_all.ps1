# Start Both Frontend and Backend Script (with venv)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Frontend & Backend" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
Set-Location $PSScriptRoot

# Check if venv exists, create if not
if (-not (Test-Path "venv")) {
    Write-Host "[*] Creating virtual environment..." -ForegroundColor Yellow
    py -m venv venv
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
}

# Activate venv and install dependencies if needed
Write-Host "[*] Activating virtual environment..." -ForegroundColor Yellow
& "$PSScriptRoot\venv\Scripts\Activate.ps1"

# Check if requirements are installed
Write-Host "[*] Checking dependencies..." -ForegroundColor Yellow
try {
    $uvicornCheck = & "$PSScriptRoot\venv\Scripts\python.exe" -m uvicorn --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[*] Installing dependencies..." -ForegroundColor Yellow
        & "$PSScriptRoot\venv\Scripts\python.exe" -m pip install -q -r requirements.txt
        Write-Host "[OK] Dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "[OK] Dependencies already installed" -ForegroundColor Green
    }
} catch {
    Write-Host "[*] Installing dependencies..." -ForegroundColor Yellow
    & "$PSScriptRoot\venv\Scripts\python.exe" -m pip install -q -r requirements.txt
    Write-Host "[OK] Dependencies installed" -ForegroundColor Green
}

# Check if Node.js is available
Write-Host "[*] Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = & node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Found Node.js: $nodeVersion" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Node.js not found! Please install Node.js" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Node.js not found! Please install Node.js" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[*] Starting Backend Server..." -ForegroundColor Cyan
Write-Host "   Opening in new window..." -ForegroundColor Gray

# Start Backend in new window with venv activated
$backendCommand = @"
cd '$PSScriptRoot'
& '$PSScriptRoot\venv\Scripts\Activate.ps1'
Write-Host '[*] FastAPI Backend Server' -ForegroundColor Green
Write-Host 'Running on http://localhost:8000' -ForegroundColor Cyan
Write-Host 'Press Ctrl+C to stop' -ForegroundColor Yellow
Write-Host ''
& '$PSScriptRoot\venv\Scripts\python.exe' -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand -WindowStyle Normal

Write-Host "[OK] Backend starting..." -ForegroundColor Green
Write-Host ""

# Wait a moment for backend to start
Start-Sleep -Seconds 3

Write-Host "[*] Starting Frontend Server..." -ForegroundColor Cyan
Write-Host "   Opening in new window..." -ForegroundColor Gray

# Start Frontend in new window
$frontendCommand = @"
cd '$PSScriptRoot\frontend'
Write-Host '[*] Next.js Frontend Server' -ForegroundColor Green
Write-Host 'Running on http://localhost:3000' -ForegroundColor Cyan
Write-Host 'Press Ctrl+C to stop' -ForegroundColor Yellow
Write-Host ''
npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand -WindowStyle Normal

Write-Host "[OK] Frontend starting..." -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Both servers are starting!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[INFO] What to expect:" -ForegroundColor Yellow
Write-Host "   - Backend: http://localhost:8000" -ForegroundColor White
Write-Host "   - Frontend: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "[INFO] Wait for both to show:" -ForegroundColor Yellow
Write-Host "   - Backend: 'Application startup complete'" -ForegroundColor Gray
Write-Host "   - Frontend: 'Ready in X seconds'" -ForegroundColor Gray
Write-Host ""
Write-Host "[*] Then open: http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "[TIP] Keep both PowerShell windows open!" -ForegroundColor Yellow
Write-Host "      Close them to stop the servers" -ForegroundColor Gray
Write-Host ""
