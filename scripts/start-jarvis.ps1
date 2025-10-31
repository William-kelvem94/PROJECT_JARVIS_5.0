# Script para iniciar JARVIS com Docker

Write-Host "=== INICIANDO JARVIS IA ===" -ForegroundColor Green

# Verificar Docker
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Host "ERRO: Docker não encontrado!" -ForegroundColor Red
    Write-Host "Instale Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Verificar Docker Compose
if (-not (Get-Command "docker-compose" -ErrorAction SilentlyContinue)) {
    Write-Host "ERRO: docker-compose não encontrado!" -ForegroundColor Red
    exit 1
}

Write-Host "Parando containers existentes..." -ForegroundColor Yellow
docker-compose down

Write-Host "Construindo e iniciando containers..." -ForegroundColor Cyan
docker-compose up --build -d

Write-Host "Aguardando serviços iniciarem..." -ForegroundColor Yellow
Start-Sleep 15

# Verificar status
Write-Host "`n=== STATUS DOS SERVIÇOS ===" -ForegroundColor Green
docker-compose ps

# Verificar se JARVIS está respondendo
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/status" -TimeoutSec 5
    Write-Host "`n✓ JARVIS está rodando!" -ForegroundColor Green
    Write-Host "`nAcesse: http://localhost:8000" -ForegroundColor Cyan
} catch {
    Write-Host "`nAguardando JARVIS iniciar completamente..." -ForegroundColor Yellow
    Write-Host "Verifique os logs: docker-compose logs jarvis" -ForegroundColor Yellow
}

Write-Host "`n=== COMANDOS ÚTEIS ===" -ForegroundColor Green
Write-Host "Ver logs: docker-compose logs -f" -ForegroundColor Cyan
Write-Host "Parar: docker-compose down" -ForegroundColor Cyan
Write-Host "Reiniciar: docker-compose restart" -ForegroundColor Cyan

