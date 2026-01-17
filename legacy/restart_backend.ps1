# Restart Backend Server Script (with venv)
Write-Host "=== Restarting Backend Server ===" -ForegroundColor Cyan

# Change to project directory
Set-Location $PSScriptRoot

# Kill any process using port 8000
Write-Host "`n1. Stopping any existing backend processes..." -ForegroundColor Yellow
try {
    $connections = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
    if ($connections) {
        $processIds = $connections | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($processId in $processIds) {
            $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "   Stopping process: $($process.ProcessName) (PID: $processId)" -ForegroundColor Gray
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            }
        }
        Start-Sleep -Seconds 2
        Write-Host "   Processes stopped" -ForegroundColor Green
    } else {
        Write-Host "   No processes found on port 8000" -ForegroundColor Gray
    }
} catch {
    Write-Host "   Could not check processes: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Check if venv exists, create if not
Write-Host "`n2. Checking virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    Write-Host "   Creating virtual environment..." -ForegroundColor Yellow
    py -m venv venv
    Write-Host "   Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "   Virtual environment exists" -ForegroundColor Green
}

# Activate venv and check dependencies
Write-Host "`n3. Activating virtual environment..." -ForegroundColor Yellow
& "$PSScriptRoot\venv\Scripts\Activate.ps1"

Write-Host "`n4. Checking dependencies..." -ForegroundColor Yellow
try {
    $uvicornCheck = & "$PSScriptRoot\venv\Scripts\python.exe" -m uvicorn --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   Installing requirements..." -ForegroundColor Yellow
        & "$PSScriptRoot\venv\Scripts\python.exe" -m pip install -r requirements.txt
        Write-Host "   Dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "   Dependencies OK" -ForegroundColor Green
    }
} catch {
    Write-Host "   Installing requirements..." -ForegroundColor Yellow
    & "$PSScriptRoot\venv\Scripts\python.exe" -m pip install -r requirements.txt
    Write-Host "   Dependencies installed" -ForegroundColor Green
}

# Start the server
Write-Host "`n5. Starting backend server..." -ForegroundColor Green
Write-Host "   URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "`n   Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "`n" + "="*60 -ForegroundColor Gray
Write-Host ""

& "$PSScriptRoot\venv\Scripts\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
