# PowerShell script to setup virtual environment for backend
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Backend Virtual Environment Setup" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backendDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $backendDir

# Check for Python
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
    Write-Host "✅ Found: python" -ForegroundColor Green
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
    Write-Host "✅ Found: py" -ForegroundColor Green
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
    Write-Host "✅ Found: python3" -ForegroundColor Green
} else {
    Write-Host "❌ Python not found in PATH!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Or add Python to your PATH environment variable." -ForegroundColor Yellow
    exit 1
}

# Check if venv exists in root
if (Test-Path "$rootDir\venv\Scripts\python.exe") {
    Write-Host "[*] Found venv in root directory, using it..." -ForegroundColor Cyan
    
    # Check if backend dependencies are installed
    Write-Host "[*] Checking backend dependencies..." -ForegroundColor Cyan
    $hasFastAPI = & "$rootDir\venv\Scripts\python.exe" -m pip show fastapi 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencies already installed!" -ForegroundColor Green
    } else {
        Write-Host "[*] Installing backend dependencies..." -ForegroundColor Cyan
        & "$rootDir\venv\Scripts\python.exe" -m pip install --upgrade pip
        & "$rootDir\venv\Scripts\python.exe" -m pip install -r "$backendDir\requirements.txt"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Dependencies installed!" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
            exit 1
        }
    }
    
    # Create junction/symlink if needed (or just use the root venv)
    Write-Host ""
    Write-Host "✅ Setup complete! Using venv from: $rootDir\venv" -ForegroundColor Green
    Write-Host ""
    Write-Host "To start the backend:" -ForegroundColor Yellow
    Write-Host "  ..\venv\Scripts\python.exe -m uvicorn app.main:app --reload" -ForegroundColor White
    
} else {
    # Create venv in backend directory
    Write-Host "[*] Creating virtual environment..." -ForegroundColor Cyan
    
    if (Test-Path "$backendDir\venv") {
        Write-Host "⚠️  Removing old venv..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force "$backendDir\venv"
    }
    
    & $pythonCmd -m venv "$backendDir\venv"
    
    if (-not (Test-Path "$backendDir\venv\Scripts\python.exe")) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Virtual environment created!" -ForegroundColor Green
    Write-Host ""
    
    # Install dependencies
    Write-Host "[*] Installing dependencies..." -ForegroundColor Cyan
    & "$backendDir\venv\Scripts\python.exe" -m pip install --upgrade pip
    & "$backendDir\venv\Scripts\python.exe" -m pip install -r "$backendDir\requirements.txt"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencies installed!" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "✅ Setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To start the backend:" -ForegroundColor Yellow
    Write-Host "  .\venv\Scripts\python.exe -m uvicorn app.main:app --reload" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

