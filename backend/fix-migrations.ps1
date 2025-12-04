# Emergency Migration Fix Script
# Run this on the remote server to diagnose and fix migration issues

param(
    [switch]$DiagnoseOnly,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$backendPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $backendPath

Write-Host "=== PMS Migration Diagnostic & Fix Tool ===" -ForegroundColor Cyan
Write-Host ""

# Function to run SQL query
function Run-SqlQuery {
    param([string]$query)

    # Try to get DATABASE_URL from environment or ecosystem.config.js
    $dbUrl = $env:DATABASE_URL
    if (-not $dbUrl) {
        Write-Host "Trying to read DATABASE_URL from ecosystem.config.js..." -ForegroundColor Yellow
        $ecosystemContent = Get-Content "ecosystem.config.js" -Raw
        if ($ecosystemContent -match "DATABASE_URL:\s*'([^']+)'") {
            $dbUrl = $matches[1]
            $env:DATABASE_URL = $dbUrl
        }
    }

    if (-not $dbUrl) {
        Write-Host "ERROR: Could not find DATABASE_URL" -ForegroundColor Red
        return $null
    }

    # Extract connection details from DATABASE_URL
    if ($dbUrl -match "postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)") {
        $user = $matches[1]
        $pass = $matches[2]
        $host = $matches[3]
        $port = $matches[4]
        $db = $matches[5]

        $env:PGPASSWORD = $pass
        $result = psql -h $host -p $port -U $user -d $db -t -c $query 2>&1
        Remove-Item Env:\PGPASSWORD
        return $result
    }

    return $null
}

# Step 1: Check if alembic_version table exists
Write-Host "Step 1: Checking alembic_version table..." -ForegroundColor Cyan
$versionCheck = Run-SqlQuery "SELECT version_num FROM alembic_version LIMIT 1;"

if ($LASTEXITCODE -ne 0 -or -not $versionCheck) {
    Write-Host "ERROR: Cannot connect to database or alembic_version table doesn't exist!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible causes:" -ForegroundColor Yellow
    Write-Host "1. Database is not running"
    Write-Host "2. DATABASE_URL is incorrect"
    Write-Host "3. Migrations have never been run"
    Write-Host ""
    Write-Host "To fix: Run 'python -m alembic upgrade head' manually" -ForegroundColor Green
    exit 1
}

$currentVersion = $versionCheck.Trim()
Write-Host "Current migration version: $currentVersion" -ForegroundColor Green
Write-Host ""

# Step 2: Check Alembic history
Write-Host "Step 2: Checking migration history..." -ForegroundColor Cyan
$historyOutput = python -m alembic history 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host $historyOutput
} else {
    Write-Host "ERROR: Could not get migration history" -ForegroundColor Red
    Write-Host $historyOutput -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 3: Check for pending migrations
Write-Host "Step 3: Checking for pending migrations..." -ForegroundColor Cyan
$headsOutput = python -m alembic heads 2>&1
$headsVersion = ($headsOutput | Select-String -Pattern "([a-f0-9]+) \(head\)" | ForEach-Object { $_.Matches.Groups[1].Value })

Write-Host "Latest migration (head): $headsVersion" -ForegroundColor Green
Write-Host ""

if ($currentVersion -ne $headsVersion) {
    Write-Host "WARNING: Database is not at the latest migration!" -ForegroundColor Yellow
    Write-Host "Current: $currentVersion" -ForegroundColor Red
    Write-Host "Expected: $headsVersion" -ForegroundColor Green
    Write-Host ""

    # Show pending migrations
    Write-Host "Pending migrations:" -ForegroundColor Cyan
    python -m alembic history -r "${currentVersion}:head"
    Write-Host ""
} else {
    Write-Host "✓ Database is at the latest migration" -ForegroundColor Green
    Write-Host ""
}

# Step 4: Check for the specific missing column
Write-Host "Step 4: Checking for missing column (onboarding_token_expires_at)..." -ForegroundColor Cyan
$columnCheck = Run-SqlQuery "SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='onboarding_token_expires_at';"

if (-not $columnCheck -or $columnCheck.Trim() -eq "") {
    Write-Host "✗ Column 'onboarding_token_expires_at' is MISSING!" -ForegroundColor Red
    Write-Host ""
    Write-Host "This indicates migration b3d53f692103 was not applied properly." -ForegroundColor Yellow
    $needsMigration = $true
} else {
    Write-Host "✓ Column 'onboarding_token_expires_at' exists" -ForegroundColor Green
    $needsMigration = $false
}
Write-Host ""

# Summary
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "DIAGNOSTIC SUMMARY" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Current Version: $currentVersion"
Write-Host "Latest Version:  $headsVersion"
Write-Host "Status: $(if ($currentVersion -eq $headsVersion) { 'Up to date' } else { 'NEEDS UPDATE' })"
Write-Host "Missing Column:  $(if ($needsMigration) { 'YES (needs migration)' } else { 'NO (all good)' })"
Write-Host ""

if ($DiagnoseOnly) {
    Write-Host "Diagnosis complete. Run without -DiagnoseOnly to apply fixes." -ForegroundColor Yellow
    exit 0
}

# Apply fix if needed
if ($needsMigration -or $currentVersion -ne $headsVersion) {
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "APPLYING FIX" -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""

    if (-not $Force) {
        $confirm = Read-Host "Apply migrations now? (yes/no)"
        if ($confirm -ne "yes") {
            Write-Host "Migration cancelled by user." -ForegroundColor Yellow
            exit 0
        }
    }

    Write-Host "Running: python -m alembic upgrade head" -ForegroundColor Yellow
    Write-Host ""

    $upgradeOutput = python -m alembic upgrade head 2>&1
    $upgradeExitCode = $LASTEXITCODE

    Write-Host $upgradeOutput
    Write-Host ""

    if ($upgradeExitCode -eq 0) {
        Write-Host "✓ Migrations applied successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "New status:" -ForegroundColor Cyan
        python -m alembic current
        Write-Host ""
        Write-Host "You can now restart your PM2 application:" -ForegroundColor Yellow
        Write-Host "  pm2 restart pms-backend" -ForegroundColor Green
    } else {
        Write-Host "✗ Migration failed!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please review the errors above and fix manually." -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "✓ No fixes needed - database is up to date!" -ForegroundColor Green
}
