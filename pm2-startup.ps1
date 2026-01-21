# PM2 Startup Script - Universal (works on any machine)
# Runs migrations and starts both backend and frontend with PM2

$ErrorActionPreference = "Stop"

# Wait for system to fully boot
Start-Sleep -Seconds 20

# Get the script's directory (project root)
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = $scriptPath

Write-Host "=== PM2 Startup Script ===" -ForegroundColor Cyan
Write-Host "Project root: $projectRoot" -ForegroundColor Gray

# Dynamically set PATH
$currentUser = $env:USERNAME
$npmPath = "C:\Users\$currentUser\AppData\Roaming\npm"
$pythonPath = (Get-ChildItem "C:\Program Files\Python*\python.exe","C:\Users\*\AppData\Local\Programs\Python\Python*\python.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty DirectoryName)

# Build PATH
$paths = @($npmPath, $pythonPath, "$pythonPath\Scripts")
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
foreach ($p in $paths) {
    if ($p -and ($env:Path -notlike "*$p*")) {
        $env:Path += ";$p"
    }
}

# Log file in project root
$logFile = Join-Path $projectRoot "pm2-startup.log"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

try {
    # Navigate to backend directory
    $backendPath = Join-Path $projectRoot "backend"
    Set-Location $backendPath
    Add-Content -Path $logFile -Value "$timestamp - Starting database migration process..."
    Write-Host "Running database migrations..." -ForegroundColor Yellow

    # Step 1: Auto-generate migration if schema changes exist
    Write-Host "Step 1: Auto-generating migration from schema changes..." -ForegroundColor Yellow
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "python"
    $psi.Arguments = "-m alembic revision --autogenerate -m `"Auto-generated migration at startup`""
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.WorkingDirectory = $backendPath

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    $process.Start() | Out-Null

    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()
    $revisionExitCode = $process.ExitCode

    $revisionOutput = $stdout + $stderr

    if ($revisionExitCode -eq 0) {
        Add-Content -Path $logFile -Value "$timestamp - Migration auto-generation completed"
        Add-Content -Path $logFile -Value "$timestamp - Revision output: $revisionOutput"
        Write-Host "OK - Migration revision created (if changes detected)" -ForegroundColor Green
    } else {
        Add-Content -Path $logFile -Value "$timestamp - WARNING: Migration auto-generation had issues with exit code $revisionExitCode"
        Add-Content -Path $logFile -Value "$timestamp - Revision output: $revisionOutput"
        Write-Host "WARNING - Migration revision had issues, continuing with upgrade..." -ForegroundColor Yellow
        Write-Host $revisionOutput -ForegroundColor Yellow
    }

    # Step 2: Apply all pending migrations
    Write-Host "Step 2: Applying all pending migrations..." -ForegroundColor Yellow
    $psi2 = New-Object System.Diagnostics.ProcessStartInfo
    $psi2.FileName = "python"
    $psi2.Arguments = "-m alembic upgrade head"
    $psi2.RedirectStandardOutput = $true
    $psi2.RedirectStandardError = $true
    $psi2.UseShellExecute = $false
    $psi2.CreateNoWindow = $true
    $psi2.WorkingDirectory = $backendPath

    $process2 = New-Object System.Diagnostics.Process
    $process2.StartInfo = $psi2
    $process2.Start() | Out-Null

    $stdout2 = $process2.StandardOutput.ReadToEnd()
    $stderr2 = $process2.StandardError.ReadToEnd()
    $process2.WaitForExit()
    $migrationExitCode = $process2.ExitCode

    $migrationOutput = $stdout2 + $stderr2

    if ($migrationExitCode -eq 0) {
        Add-Content -Path $logFile -Value "$timestamp - Database migrations applied successfully"
        Add-Content -Path $logFile -Value "$timestamp - Migration output: $migrationOutput"
        Write-Host "OK - Migrations applied successfully" -ForegroundColor Green
    } else {
        Add-Content -Path $logFile -Value "$timestamp - ERROR: Database migration failed with exit code $migrationExitCode"
        Add-Content -Path $logFile -Value "$timestamp - Migration error output: $migrationOutput"
        Write-Host "ERROR - Migration failed!" -ForegroundColor Red
        Write-Host $migrationOutput -ForegroundColor Red
        throw "Database migration failed. Backend startup aborted."
    }

    # Start backend from ecosystem file (only if migrations succeeded)
    Write-Host "Starting backend with PM2..." -ForegroundColor Yellow
    pm2 start ecosystem.config.js
    Add-Content -Path $logFile -Value "$timestamp - Backend started from ecosystem.config.js"
    Write-Host "OK - Backend started" -ForegroundColor Green

    # Build and start frontend
    $frontendPath = Join-Path $projectRoot "frontend"
    Set-Location $frontendPath

    Write-Host "Building frontend..." -ForegroundColor Yellow
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "WARNING - Frontend build had issues, but continuing..." -ForegroundColor Yellow
    } else {
        Write-Host "OK - Frontend built successfully" -ForegroundColor Green
    }

    Write-Host "Starting frontend with PM2..." -ForegroundColor Yellow
    pm2 start ecosystem.config.js
    Add-Content -Path $logFile -Value "$timestamp - Frontend started from ecosystem.config.js"
    Write-Host "OK - Frontend started" -ForegroundColor Green

    # Save PM2 state
    pm2 save --force
    Add-Content -Path $logFile -Value "$timestamp - PM2 state saved"
    Write-Host "OK - PM2 state saved" -ForegroundColor Green

    Write-Host ""
    Write-Host "=== Startup Complete ===" -ForegroundColor Cyan
    pm2 list

} catch {
    Add-Content -Path $logFile -Value "$timestamp - ERROR: $_"
    Write-Host "ERROR: $_" -ForegroundColor Red
    exit 1
}
