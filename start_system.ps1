param (
    [string]$LogLevel = "INFO"
)

# Start Backend
Write-Host "Starting Backend Service with Log Level: $LogLevel..."
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "& {`$env:LOG_LEVEL='$LogLevel'; .\venv\Scripts\activate; uvicorn src.backend_service.main:app --host 0.0.0.0 --port 8000}"

# Start Frontend
Write-Host "Starting Frontend Service..."
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "& {python -m http.server 8081 --directory src/frontend}"

# Start Edge Service (Default: Canteen)
Write-Host "Starting Edge Service (Canteen) with Log Level: $LogLevel..."
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "& {`$env:LOG_LEVEL='$LogLevel'; .\venv\Scripts\activate; python src/edge_service/main.py canteen 0}"

# Start Edge Service (library)
#Write-Host "Starting Edge Service (library) with Log Level: $LogLevel..."
#Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "& {`$env:LOG_LEVEL='$LogLevel'; .\venv\Scripts\activate; python src/edge_service/main.py library 0}"

Write-Host "All services started."
Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: http://localhost:8081"
Write-Host "To add more cameras, run: `$env:LOG_LEVEL='$LogLevel'; python src/edge_service/main.py <location_id> <camera_source>"
Write-Host " 4 locations are supported: canteen, library, corridor, event."
