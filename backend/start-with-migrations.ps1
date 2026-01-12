# Wrapper script that runs migrations before starting the backend
# Use this with PM2 to ensure migrations are always applied

$ErrorActionPreference = "Stop"
$backendPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $backendPath

Write-Host "=== Starting PMS Backend with Migrations ===" -ForegroundColor Cyan
Write-Host "Backend directory: $backendPath" -ForegroundColor Gray
Write-Host "Current working directory: $(Get-Location)" -ForegroundColor Gray
Write-Host "Python path: $(Get-Command python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source)" -ForegroundColor Gray
Write-Host ""

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found in $backendPath" -ForegroundColor Red
    Write-Host "Please create .env file with DATABASE_URL and other configuration" -ForegroundColor Yellow
    exit 1
}

Write-Host "OK - .env file found" -ForegroundColor Green
Write-Host ""

# Run migrations
Write-Host "Running database migrations..." -ForegroundColor Yellow
# Temporarily allow stderr output without stopping
$ErrorActionPreference = "Continue"
$migrationOutput = python -m alembic upgrade head 2>&1
$migrationExitCode = $LASTEXITCODE
$ErrorActionPreference = "Stop"

if ($migrationExitCode -eq 0) {
    Write-Host "OK - Migrations completed successfully" -ForegroundColor Green
    Write-Host $migrationOutput
    Write-Host ""
} else {
    Write-Host "ERROR - Migration failed!" -ForegroundColor Red
    Write-Host $migrationOutput -ForegroundColor Red
    Write-Host ""
    Write-Host "Backend will not start due to migration failure." -ForegroundColor Yellow
    exit 1
}

# Start the backend
Write-Host "Starting uvicorn server..." -ForegroundColor Yellow
python -m uvicorn main:app --host 0.0.0.0 --port 8000
