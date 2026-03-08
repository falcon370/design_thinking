param (
    [string]$LogLevel = "INFO"
)

# --- Load Configuration ---
$ConfigPath = "src/edge_service/config.json"
if (Test-Path $ConfigPath) {
    try {
        $ConfigData = Get-Content -Raw -Path $ConfigPath | ConvertFrom-Json
        $ActiveProfile = $ConfigData.active_profile
        $ProfileSettings = $ConfigData.profiles.$ActiveProfile
        
        $HostIP = $ProfileSettings.backend_host
        $BackendPort = $ProfileSettings.backend_port
        
        Write-Host "Loaded Configuration Profile: $ActiveProfile"
        Write-Host "Backend Host: $HostIP"
    } catch {
        Write-Error "Failed to parse config.json. Using defaults."
        $ActiveProfile = "laptop"
        $HostIP = "192.168.68.107"
        $BackendPort = "8000"
    }
} else {
    Write-Warning "config.json not found. Using defaults."
    $ActiveProfile = "laptop"
    $HostIP = "192.168.68.107"
    $BackendPort = "8000"
}

# Determine Stream URL based on profile
$StreamURL = "http://192.168.68.106:5000/video" # Default/Original RPi URL
if ($ActiveProfile -eq "laptop") {
    $StreamURL = "http://$($HostIP):5000/video"
}

# 1. Configure Frontend
Write-Host "Configuring Frontend to connect to $HostIP..."
$ConfigContent = "const API_CONFIG = { BASE_URL: 'http://$($HostIP):$($BackendPort)', STREAM_URL: '$StreamURL', PROFILE: '$ActiveProfile' };"
Set-Content -Path "src/frontend/config.js" -Value $ConfigContent

# 2. Start Backend
Write-Host "Starting Backend Service with Log Level: $LogLevel..."
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "& {`$env:LOG_LEVEL='$LogLevel'; python -m uvicorn src.backend_service.main:app --host 0.0.0.0 --port $BackendPort}"

# 3. Start Frontend
Write-Host "Starting Frontend Service..."
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "& {python -m http.server 8081 --directory src/frontend}"

# 4. Start Edge Service (Based on Profile)
if ($ActiveProfile -eq "laptop") {
    Write-Host "Starting Local Edge Service (Canteen) with Log Level: $LogLevel connecting to $HostIP..."
    Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "& {`$env:LOG_LEVEL='$LogLevel'; `$env:BACKEND_HOST='$HostIP'; `$env:BACKEND_PORT='$BackendPort'; python src/edge_service/main.py canteen}"
} else {
    Write-Host "---------------------------------------------------------"
    Write-Host "Profile '$ActiveProfile' selected."
    Write-Host "Skipping local edge service startup."
    Write-Host "Please ensure the Edge Service is running on your remote device (RPi)."
    Write-Host "---------------------------------------------------------"
}

Write-Host "All local services started."
Write-Host "Backend: http://localhost:$BackendPort"
Write-Host "Frontend: http://localhost:8081"
