# Heartbeat e Monitoramento Automático

Este script monitora o backend e frontend, reiniciando automaticamente se travar.

```powershell
# monitor-heartbeat.ps1
$backendUrl = "http://localhost:8000/health"
$frontendUrl = "http://localhost:3000"
$interval = 10 # segundos

while ($true) {
    $backendStatus = Invoke-WebRequest -Uri $backendUrl -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
    $frontendStatus = Invoke-WebRequest -Uri $frontendUrl -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue

    if (-not $backendStatus) {
        Write-Host "Backend travado. Reiniciando..."
        Start-Process -FilePath "start-jarvis.bat"
    }
    if (-not $frontendStatus) {
        Write-Host "Frontend travado. Reiniciando..."
        Start-Process -FilePath "start-jarvis.bat"
    }
    Start-Sleep -Seconds $interval
}
```

> Adicione endpoint `/health` no backend para responder com status 200.
