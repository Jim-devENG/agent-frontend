# Emergency fix for missing discovery_query_id column

if (-not $env:DATABASE_URL) {
    Write-Host "❌ ERROR: DATABASE_URL not set" -ForegroundColor Red
    exit 1
}

Write-Host "🔧 Applying emergency fix..." -ForegroundColor Cyan
Get-Content fix_discovery_query_id.sql | psql $env:DATABASE_URL

Write-Host ""
Write-Host "✅ Fix applied. Verifying..." -ForegroundColor Green
psql $env:DATABASE_URL -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'prospects' AND column_name = 'discovery_query_id';"

