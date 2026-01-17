# Check if backend is running
Write-Host "`n=== Checking Backend Status ===" -ForegroundColor Cyan

# Check if port 8000 is in use
$portInUse = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

if ($portInUse) {
    Write-Host "`n✅ Port 8000 is in use" -ForegroundColor Green
    Write-Host "   Backend might be running" -ForegroundColor White
    
    # Try to test the endpoint
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/stats" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "`n✅ Backend is responding!" -ForegroundColor Green
        Write-Host "   Status: $($response.StatusCode)" -ForegroundColor White
    } catch {
        Write-Host "`n⚠️  Port 8000 is in use but backend is not responding" -ForegroundColor Yellow
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "`n💡 Try:" -ForegroundColor Cyan
        Write-Host "   1. Kill the process using port 8000" -ForegroundColor White
        Write-Host "   2. Restart the backend: .\start_backend.ps1" -ForegroundColor White
    }
} else {
    Write-Host "`n❌ Port 8000 is NOT in use" -ForegroundColor Red
    Write-Host "   Backend is NOT running" -ForegroundColor White
    Write-Host "`n💡 Start the backend:" -ForegroundColor Cyan
    Write-Host "   .\start_backend.ps1" -ForegroundColor White
}

Write-Host "`n" -ForegroundColor White

