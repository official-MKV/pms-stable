# Simple Backend Starter - No migrations, no PM2
# Use this for testing the backend directly

$ErrorActionPreference = "Stop"
$backendPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $backendPath

Write-Host "=== Simple PMS Backend Startup ===" -ForegroundColor Cyan
Write-Host "Backend directory: $backendPath" -ForegroundColor Gray
Write-Host "Current working directory: $(Get-Location)" -ForegroundColor Gray
Write-Host ""

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found in $backendPath" -ForegroundColor Red
    Write-Host "Please create .env file with DATABASE_URL and other configuration" -ForegroundColor Yellow
    exit 1
}

Write-Host "OK - .env file found" -ForegroundColor Green
Write-Host ""

# Start uvicorn directly - no migrations
Write-Host "=== Starting Uvicorn Server ===" -ForegroundColor Cyan
Write-Host "Command: python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor Gray
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
