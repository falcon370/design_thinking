# Stop all Python and Uvicorn processes
Write-Host "Stopping all Python and Uvicorn processes..."

$processes = Get-Process python, uvicorn -ErrorAction SilentlyContinue

if ($processes) {
    foreach ($p in $processes) {
        Write-Host "Stopping PID $($p.Id) ($($p.ProcessName))..."
        Stop-Process -Id $p.Id -Force
    }
    Write-Host "All processes stopped."
} else {
    Write-Host "No Python/Uvicorn processes found."
}

# Double check ports
$ports = @(8000, 8081)
foreach ($port in $ports) {
    $p = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($p) {
        Write-Host "Force killing process on port $port (PID $($p.OwningProcess))..."
        Stop-Process -Id $p.OwningProcess -Force
    }
}

Write-Host "System is clean. You can now run .\start_system.ps1"
