# Script to help view backend logs
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Backend Log Viewer Helper" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[*] Finding backend process..." -ForegroundColor Cyan
$backendProcs = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*uvicorn*" -or $_.Path -like "*venv*"
}

if ($backendProcs) {
    Write-Host "✅ Found backend process(es):" -ForegroundColor Green
    foreach ($proc in $backendProcs) {
        Write-Host "   PID: $($proc.Id) - Started: $($proc.StartTime)" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "[*] To view logs:" -ForegroundColor Yellow
    Write-Host "   1. Check the PowerShell window where you started the backend" -ForegroundColor White
    Write-Host "   2. Look for startup messages and any errors" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "❌ No backend process found" -ForegroundColor Red
    Write-Host ""
}

Write-Host "[*] Checking port 8000..." -ForegroundColor Cyan
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    Write-Host "✅ Port 8000 is in use" -ForegroundColor Green
    Write-Host "   State: $($port8000.State)" -ForegroundColor White
    Write-Host "   Process ID: $($port8000.OwningProcess)" -ForegroundColor White
    
    if ($port8000.State -eq "Listen") {
        Write-Host "✅ Backend is listening on port 8000" -ForegroundColor Green
        Write-Host ""
        Write-Host "[*] Testing connection..." -ForegroundColor Cyan
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
            Write-Host "✅ Backend is responding! Status: $($response.StatusCode)" -ForegroundColor Green
            Write-Host "   Response: $($response.Content)" -ForegroundColor White
        } catch {
            Write-Host "⚠️  Backend is listening but not responding: $($_.Exception.Message)" -ForegroundColor Yellow
            Write-Host "   This might indicate a startup error. Check the backend window." -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️  Port is in use but not in Listen state: $($port8000.State)" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Port 8000 is not in use" -ForegroundColor Red
    Write-Host "   Backend is not running or not listening" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[*] Checking environment..." -ForegroundColor Cyan
if (Test-Path ".env") {
    Write-Host "✅ .env file exists" -ForegroundColor Green
    $hasDb = Get-Content ".env" -ErrorAction SilentlyContinue | Select-String -Pattern "DATABASE_URL"
    if ($hasDb) {
        Write-Host "✅ DATABASE_URL found in .env" -ForegroundColor Green
    } else {
        Write-Host "⚠️  DATABASE_URL not found in .env" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Next Steps:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Check the PowerShell window where backend was started" -ForegroundColor White
Write-Host "2. Look for error messages (usually in red)" -ForegroundColor White
Write-Host "3. Common issues:" -ForegroundColor White
Write-Host "   - Database connection failed" -ForegroundColor Gray
Write-Host "   - Missing environment variables" -ForegroundColor Gray
Write-Host "   - Import errors" -ForegroundColor Gray
Write-Host "   - Port already in use" -ForegroundColor Gray
Write-Host ""

