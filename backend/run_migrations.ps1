# PowerShell script to run Alembic migrations
# Usage: .\run_migrations.ps1

Write-Host "🔄 Running Alembic migrations..." -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = if (Test-Path "$scriptDir\backend") { "$scriptDir\backend" } else { $scriptDir }

# Change to backend directory
Push-Location $backendDir

try {
    # Check if alembic.ini exists
    if (-not (Test-Path "alembic.ini")) {
        Write-Host "❌ ERROR: alembic.ini not found in $backendDir" -ForegroundColor Red
        exit 1
    }
    
    # Check if DATABASE_URL is set
    if (-not $env:DATABASE_URL) {
        Write-Host "⚠️  WARNING: DATABASE_URL environment variable not set" -ForegroundColor Yellow
        Write-Host "   Migrations may fail if database connection is not configured" -ForegroundColor Yellow
    }
    
    Write-Host "📁 Working directory: $backendDir" -ForegroundColor Gray
    Write-Host "📋 Running: alembic upgrade head" -ForegroundColor Gray
    Write-Host ""
    
    # Run migrations
    $result = & alembic upgrade head 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Migrations completed successfully!" -ForegroundColor Green
        Write-Host ""
        
        # Show current revision
        Write-Host "📊 Checking current database revision..." -ForegroundColor Cyan
        $revision = & alembic current 2>&1
        Write-Host $revision
    } else {
        Write-Host ""
        Write-Host "❌ Migration failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        Write-Host "Output:" -ForegroundColor Yellow
        Write-Host $result
        exit $LASTEXITCODE
    }
} catch {
    Write-Host ""
    Write-Host "❌ ERROR: Failed to run migrations" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "✅ Done!" -ForegroundColor Green

