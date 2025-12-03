# PowerShell script to update Hunter.io API key in .env file
$newApiKey = "b8b197dff80f8cc991db92a6a37653c467c8b952"

Write-Host "Updating Hunter.io API key..." -ForegroundColor Cyan

# Navigate to backend directory
$backendDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $backendDir

# Check if .env exists
if (Test-Path .env) {
    Write-Host "Found .env file" -ForegroundColor Green
    
    $content = Get-Content .env -Raw
    
    # Check if key already exists
    if ($content -match "HUNTER_IO_API_KEY") {
        Write-Host "Updating existing HUNTER_IO_API_KEY..." -ForegroundColor Yellow
        
        # Remove old line and add new one
        $lines = Get-Content .env | Where-Object { $_ -notmatch "^HUNTER_IO_API_KEY" }
        $lines += "HUNTER_IO_API_KEY=$newApiKey"
        $lines | Set-Content .env -Encoding UTF8
    } else {
        Write-Host "Adding HUNTER_IO_API_KEY to .env..." -ForegroundColor Green
        Add-Content .env "`nHUNTER_IO_API_KEY=$newApiKey" -Encoding UTF8
    }
} else {
    Write-Host "Creating .env file..." -ForegroundColor Green
    "HUNTER_IO_API_KEY=$newApiKey" | Out-File .env -Encoding UTF8
}

Write-Host ""
Write-Host "✅ Hunter.io API key updated successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Restart your backend server for changes to take effect" -ForegroundColor White
Write-Host "2. The new Pro account key should resolve rate limit issues" -ForegroundColor White
Write-Host ""

