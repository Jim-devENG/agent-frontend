# Complete Database Reset Script (PowerShell)
# WARNING: This will DELETE ALL DATA

Write-Host "⚠️  WARNING: This script will DELETE ALL DATA from the database!" -ForegroundColor Red
Write-Host "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
Start-Sleep -Seconds 5

# Get database URL from environment
if (-not $env:DATABASE_URL) {
    Write-Host "❌ ERROR: DATABASE_URL environment variable is not set" -ForegroundColor Red
    exit 1
}

Write-Host "📊 Current database state:" -ForegroundColor Cyan
$env:PGPASSWORD = ($env:DATABASE_URL -split '@')[0] -replace '.*:', ''
$dbParts = ($env:DATABASE_URL -split '@')[1] -split '/'
$dbName = $dbParts[1]
$hostParts = $dbParts[0] -split ':'
$dbHost = $hostParts[0]
$dbPort = if ($hostParts.Length -gt 1) { $hostParts[1] } else { "5432" }
$dbUser = ($env:DATABASE_URL -split '@')[0] -replace '.*://', '' -replace ':.*', ''

psql -h $dbHost -p $dbPort -U $dbUser -d $dbName -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name;"

Write-Host ""
Write-Host "🗑️  Dropping all tables..." -ForegroundColor Yellow
psql -h $dbHost -p $dbPort -U $dbUser -d $dbName -c "DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;"

Write-Host ""
Write-Host "🔄 Running migrations from scratch..." -ForegroundColor Cyan
Set-Location $PSScriptRoot
alembic upgrade head

Write-Host ""
Write-Host "✅ Database reset complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 New database state:" -ForegroundColor Cyan
psql -h $dbHost -p $dbPort -U $dbUser -d $dbName -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name;"

Write-Host ""
Write-Host "🔍 Verifying migration version:" -ForegroundColor Cyan
psql -h $dbHost -p $dbPort -U $dbUser -d $dbName -c "SELECT * FROM alembic_version;"

Write-Host ""
Write-Host "✅ Reset complete! All tables created successfully." -ForegroundColor Green

