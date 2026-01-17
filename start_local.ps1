# PowerShell script to start both frontend and backend locally
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Frontend & Backend" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $rootDir "backend"
$frontendDir = Join-Path $rootDir "frontend"

# Check if directories exist
if (-not (Test-Path $backendDir)) {
    Write-Host "❌ Backend directory not found: $backendDir" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $frontendDir)) {
    Write-Host "❌ Frontend directory not found: $frontendDir" -ForegroundColor Red
    exit 1
}

# Start Backend
Write-Host "[*] Starting Backend Server..." -ForegroundColor Cyan
Write-Host "   Opening in new window..." -ForegroundColor Gray

$backendCommand = @"
cd '$backendDir'
Write-Host '[*] FastAPI Backend Server' -ForegroundColor Green
Write-Host 'Running on http://localhost:8000' -ForegroundColor Cyan
Write-Host 'API Docs: http://localhost:8000/docs' -ForegroundColor Cyan
Write-Host 'Press Ctrl+C to stop' -ForegroundColor Yellow
Write-Host ''
if (Test-Path 'venv\Scripts\python.exe') {
    & 'venv\Scripts\python.exe' -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
} else {
    Write-Host '⚠️  Virtual environment not found. Using system Python...' -ForegroundColor Yellow
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand -WindowStyle Normal

Write-Host "[OK] Backend starting..." -ForegroundColor Green
Write-Host ""

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "[*] Starting Frontend Server..." -ForegroundColor Cyan
Write-Host "   Opening in new window..." -ForegroundColor Gray

$frontendCommand = @"
cd '$frontendDir'
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
Write-Host "   - Backend API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   - Frontend: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "[INFO] Wait for both to start, then open:" -ForegroundColor Yellow
Write-Host "   http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit this window (servers will continue running)..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

