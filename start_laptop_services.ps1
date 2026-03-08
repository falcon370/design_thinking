# Run the Laptop Side Services (Backend + Frontend)

Write-Host "Starting Backend Service on Port 8000..." -ForegroundColor Green
# Using python -m uvicorn which is more reliable than calling uvicorn.exe directly
$BackendProcess = Start-Process -FilePath "python" -ArgumentList "-m uvicorn src.backend_service.main:app --host 0.0.0.0 --port 8000 --reload" -PassThru -NoNewWindow

Start-Sleep -Seconds 3

Write-Host "Opening Frontend Dashboard..." -ForegroundColor Green
# We can just open the file directly in the browser for simplicity
Start-Process "src\frontend\index.html"

Write-Host "System Running. Press Enter to Stop." -ForegroundColor Cyan
Read-Host

Stop-Process -Id $BackendProcess.Id -Force
Write-Host "Backend Stopped." -ForegroundColor Yellow
