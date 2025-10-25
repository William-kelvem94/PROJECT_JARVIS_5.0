# Script para corrigir Docker + WSL
# Execute como ADMINISTRADOR

Write-Host "`n==== DIAGNOSTICO E CORRECAO DO DOCKER ====`n" -ForegroundColor Cyan

# 1. Verificar WSL
Write-Host "[1/7] Verificando WSL..." -ForegroundColor Yellow
try {
    wsl --version | Out-Null
    Write-Host "[OK] WSL instalado" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] WSL nao encontrado. Instalando..." -ForegroundColor Yellow
    Write-Host "IMPORTANTE: Precisa executar como ADMINISTRADOR!" -ForegroundColor Red
    exit 1
}

# 2. Verificar distribuicoes WSL
Write-Host "`n[2/7] Verificando distribuicoes WSL..." -ForegroundColor Yellow
wsl --list --verbose

# 3. Parar Docker
Write-Host "`n[3/7] Parando Docker Desktop..." -ForegroundColor Yellow
Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 5
Write-Host "[OK] Docker parado" -ForegroundColor Green

# 4. Limpar recursos WSL/Docker
Write-Host "`n[4/7] Limpando recursos WSL..." -ForegroundColor Yellow
wsl --shutdown
Start-Sleep -Seconds 3
Write-Host "[OK] WSL reiniciado" -ForegroundColor Green

# 5. Iniciar Docker
Write-Host "`n[5/7] Iniciando Docker Desktop..." -ForegroundColor Yellow
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
Write-Host "Aguardando Docker iniciar (60 segundos)..." -ForegroundColor Yellow

$maxAttempts = 20
$attempt = 0
$dockerRunning = $false

while ($attempt -lt $maxAttempts -and -not $dockerRunning) {
    Start-Sleep -Seconds 3
    try {
        docker ps | Out-Null
        $dockerRunning = $true
        Write-Host "[OK] Docker iniciado!" -ForegroundColor Green
    } catch {
        $attempt++
        Write-Host "Tentativa $attempt/$maxAttempts..." -ForegroundColor Gray
    }
}

if (-not $dockerRunning) {
    Write-Host "`n[ERRO] Docker nao iniciou. Tente:" -ForegroundColor Red
    Write-Host "1. Abrir Docker Desktop manualmente" -ForegroundColor Yellow
    Write-Host "2. Settings > General > Enable WSL 2" -ForegroundColor Yellow
    Write-Host "3. Settings > Resources > WSL Integration > Enable integration" -ForegroundColor Yellow
    Write-Host "4. Apply & Restart`n" -ForegroundColor Yellow
    exit 1
}

# 6. Testar Docker
Write-Host "`n[6/7] Testando Docker..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    docker ps | Out-Null
    Write-Host "[OK] Docker funcionando!" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] Docker ainda com problemas" -ForegroundColor Red
    Write-Host "Erro: $_" -ForegroundColor Red
    exit 1
}

# 7. Limpar imagens/containers antigos
Write-Host "`n[7/7] Limpando recursos antigos..." -ForegroundColor Yellow
docker system prune -f
Write-Host "[OK] Limpeza concluida!" -ForegroundColor Green

Write-Host "`n==== DOCKER CORRIGIDO! ====`n" -ForegroundColor Green
Write-Host "Agora execute: .\INSTALL_AND_RUN.ps1`n" -ForegroundColor Cyan

