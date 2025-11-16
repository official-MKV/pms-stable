# Wait for system to fully boot
Start-Sleep -Seconds 15

# Permanently set PATH (in case it's lost)
$npmPath = "C:\Users\vem\AppData\Roaming\npm"
$pythonPath = (Get-ChildItem "C:\Program Files\Python*\python.exe","C:\Users\*\AppData\Local\Programs\Python\Python*\python.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty DirectoryName)

# Build PATH
$paths = @($npmPath, $pythonPath, "$pythonPath\Scripts")
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
foreach ($p in $paths) {
    if ($p -and ($env:Path -notlike "*$p*")) {
        $env:Path += ";$p"
    }
}

# Change directory
Set-Location C:\Users\vem\pms-stable

# Resurrect saved PM2 processes
try {
    pm2 resurrect
    
    # Log success
    $logFile = "C:\Users\vem\pms-stable\pm2-startup.log"
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logFile -Value "$timestamp - PM2 processes started successfully"
    
    # Show status
    pm2 list
} catch {
    # Log error
    $logFile = "C:\Users\vem\pms-stable\pm2-startup.log"
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logFile -Value "$timestamp - ERROR: $_"
}