# Script to archive old codebase to legacy/ folder
# This preserves the old code while cleaning up the root for new architecture

Write-Host "Archiving old codebase to legacy/ folder..." -ForegroundColor Yellow

# Create legacy directory structure
$legacyDirs = @(
    "legacy/api",
    "legacy/db", 
    "legacy/extractor",
    "legacy/scraper",
    "legacy/jobs",
    "legacy/utils",
    "legacy/ai",
    "legacy/emailer",
    "legacy/frontend",
    "legacy/docs"
)

foreach ($dir in $legacyDirs) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

# Move old directories
$dirsToMove = @(
    "api",
    "db",
    "extractor", 
    "scraper",
    "jobs",
    "utils",
    "ai",
    "emailer"
)

foreach ($dir in $dirsToMove) {
    if (Test-Path $dir) {
        Write-Host "Moving $dir/ to legacy/$dir/" -ForegroundColor Cyan
        Move-Item -Path $dir -Destination "legacy/$dir" -Force
    }
}

# Move old frontend
if (Test-Path "frontend") {
    Write-Host "Moving frontend/ to legacy/frontend/" -ForegroundColor Cyan
    Move-Item -Path "frontend" -Destination "legacy/frontend" -Force
}

# Move old Python files
$pythonFiles = @(
    "main.py",
    "extract_all_contacts.py",
    "generate_auth.py",
    "test_*.py",
    "verify_setup.py"
)

foreach ($pattern in $pythonFiles) {
    Get-ChildItem -Path . -Filter $pattern -File | ForEach-Object {
        Write-Host "Moving $($_.Name) to legacy/" -ForegroundColor Cyan
        Move-Item -Path $_.FullName -Destination "legacy/" -Force
    }
}

# Move old config/deployment files
$configFiles = @(
    "Dockerfile",
    "fly.toml",
    "deploy.sh",
    "vercel.json",
    "package.json",
    "requirements.txt",
    "seed_websites.txt",
    "art_outreach.db"
)

foreach ($file in $configFiles) {
    if (Test-Path $file) {
        Write-Host "Moving $file to legacy/" -ForegroundColor Cyan
        Move-Item -Path $file -Destination "legacy/" -Force
    }
}

# Move old documentation
$docFiles = Get-ChildItem -Path . -Filter "*.md" -File | Where-Object {
    $_.Name -notlike "README*" -and 
    $_.Name -notlike "ARCHITECTURE*" -and
    $_.Name -notlike "MIGRATION*"
}

foreach ($doc in $docFiles) {
    Write-Host "Moving $($doc.Name) to legacy/docs/" -ForegroundColor Cyan
    Move-Item -Path $doc.FullName -Destination "legacy/docs/" -Force
}

# Move old scripts
$scripts = Get-ChildItem -Path . -Filter "*.ps1" -File | Where-Object {
    $_.Name -ne "archive_old_code.ps1"
}

foreach ($script in $scripts) {
    Write-Host "Moving $($script.Name) to legacy/" -ForegroundColor Cyan
    Move-Item -Path $script.FullName -Destination "legacy/" -Force
}

# Move old batch files
Get-ChildItem -Path . -Filter "*.bat" -File | ForEach-Object {
    Write-Host "Moving $($_.Name) to legacy/" -ForegroundColor Cyan
    Move-Item -Path $_.FullName -Destination "legacy/" -Force
}

# Move old systemd configs
if (Test-Path "systemd") {
    Write-Host "Moving systemd/ to legacy/systemd/" -ForegroundColor Cyan
    Move-Item -Path "systemd" -Destination "legacy/systemd" -Force
}

# Move old nginx configs
if (Test-Path "nginx") {
    Write-Host "Moving nginx/ to legacy/nginx/" -ForegroundColor Cyan
    Move-Item -Path "nginx" -Destination "legacy/nginx" -Force
}

# Keep venv for now (can be recreated)
Write-Host "`nKeeping venv/ directory (can be removed if needed)" -ForegroundColor Yellow

Write-Host "`nArchive complete! Old code is now in legacy/ folder" -ForegroundColor Green
Write-Host "Root directory is now clean for new architecture" -ForegroundColor Green

