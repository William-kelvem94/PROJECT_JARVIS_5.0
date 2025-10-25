# JARVIS AI - Instalacao e Execucao Completa
# Execute: .\INSTALL_AND_RUN.ps1

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "     JARVIS AI Assistant v3.0 - Setup Completo" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Verificar Docker
Write-Host "[1/5] Verificando Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "[OK] $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] Docker nao encontrado!" -ForegroundColor Red
    Write-Host "`nInstale Docker Desktop:" -ForegroundColor Yellow
    Write-Host "   https://www.docker.com/products/docker-desktop`n" -ForegroundColor Yellow
    exit 1
}

# Verificar se Docker esta rodando
Write-Host "[2/5] Verificando se Docker esta rodando..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "[OK] Docker esta rodando!" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] Docker Desktop nao esta rodando!" -ForegroundColor Red
    Write-Host "`nIniciando Docker Desktop..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Write-Host "Aguarde ~30 segundos para Docker iniciar..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    
    try {
        docker ps | Out-Null
        Write-Host "[OK] Docker iniciado com sucesso!" -ForegroundColor Green
    } catch {
        Write-Host "[ERRO] Docker ainda nao iniciou. Por favor:" -ForegroundColor Red
        Write-Host "   1. Abra Docker Desktop manualmente" -ForegroundColor Yellow
        Write-Host "   2. Aguarde ele iniciar completamente" -ForegroundColor Yellow
        Write-Host "   3. Execute este script novamente`n" -ForegroundColor Yellow
        exit 1
    }
}

# Parar containers antigos
Write-Host "`n[3/5] Limpando containers antigos..." -ForegroundColor Yellow
docker-compose -f docker-compose.simple.yml down 2>$null
Write-Host "[OK] Limpeza concluida!" -ForegroundColor Green

# Construir e iniciar
Write-Host "`n[4/5] Construindo e iniciando servicos..." -ForegroundColor Yellow
Write-Host "   Isso pode demorar alguns minutos na primeira vez...`n" -ForegroundColor Yellow

docker-compose -f docker-compose.simple.yml up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[ERRO] Erro ao iniciar servicos!" -ForegroundColor Red
    Write-Host "Logs do erro:" -ForegroundColor Yellow
    docker-compose -f docker-compose.simple.yml logs
    exit 1
}

Write-Host "[OK] Servicos iniciados!" -ForegroundColor Green

# Aguardar servicos
Write-Host "`n[5/5] Aguardando servicos ficarem prontos..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Baixar modelo Ollama
Write-Host "`nBaixando modelo LLM (llama2 ~4GB)..." -ForegroundColor Yellow
Write-Host "   Isso pode demorar 5-10 minutos dependendo da internet..." -ForegroundColor Yellow
Write-Host "   Aguarde, nao feche esta janela!`n" -ForegroundColor Yellow

docker exec jarvis_ollama ollama pull llama2

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[OK] Modelo llama2 baixado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "`n[AVISO] Erro ao baixar modelo. Voce pode tentar manualmente depois:" -ForegroundColor Yellow
    Write-Host "   docker exec jarvis_ollama ollama pull llama2`n" -ForegroundColor Yellow
}

# Verificar saude dos servicos
Write-Host "`nVerificando servicos..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "              JARVIS ESTA RODANDO!" -ForegroundColor Green
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "Acesse:" -ForegroundColor Cyan
Write-Host "   Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host "   API Docs:  http://localhost:8000/api/docs" -ForegroundColor White
Write-Host "   Health:    http://localhost:8000/health" -ForegroundColor White
Write-Host "   Ollama:    http://localhost:11434`n" -ForegroundColor White

Write-Host "Comandos uteis:" -ForegroundColor Cyan
Write-Host "   Ver logs:     docker-compose -f docker-compose.simple.yml logs -f" -ForegroundColor White
Write-Host "   Parar:        docker-compose -f docker-compose.simple.yml down" -ForegroundColor White
Write-Host "   Reiniciar:    docker-compose -f docker-compose.simple.yml restart`n" -ForegroundColor White

Write-Host "Abrindo navegador em 5 segundos..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Start-Process "http://localhost:3000"

Write-Host "`n[SUCESSO] TUDO PRONTO! Divirta-se com o JARVIS!`n" -ForegroundColor Green
