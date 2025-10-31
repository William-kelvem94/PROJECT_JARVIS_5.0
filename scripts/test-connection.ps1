# Script para testar conexão com JARVIS e Ollama

Write-Host "=== TESTANDO CONEXÃO JARVIS ===" -ForegroundColor Green

# Testar Ollama
Write-Host "`n1. Testando Ollama..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Ollama está rodando!" -ForegroundColor Green
        $models = ($response.Content | ConvertFrom-Json).models
        Write-Host "  Modelos disponíveis:" -ForegroundColor Yellow
        foreach ($model in $models) {
            Write-Host "    - $($model.name)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "✗ Ollama não está rodando ou não está acessível" -ForegroundColor Red
    Write-Host "  Verifique se o Ollama está instalado e rodando" -ForegroundColor Yellow
}

# Testar JARVIS
Write-Host "`n2. Testando JARVIS..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/status" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ JARVIS está rodando!" -ForegroundColor Green
        $status = $response.Content | ConvertFrom-Json
        Write-Host "  Status: $($status.status)" -ForegroundColor Yellow
        Write-Host "  Modelo atual: $($status.current_model)" -ForegroundColor Yellow
        Write-Host "  Ollama conectado: $($status.ollama_connected)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ JARVIS não está rodando ou não está acessível" -ForegroundColor Red
    Write-Host "  Inicie com: docker-compose up -d" -ForegroundColor Yellow
}

# Testar WebSocket (básico)
Write-Host "`n3. Testando chat..." -ForegroundColor Cyan
try {
    $chatResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/chat" -Method POST -ContentType "application/json" -Body '{"message":"Teste"}' -TimeoutSec 30
    if ($chatResponse.StatusCode -eq 200) {
        Write-Host "✓ Chat funcionando!" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Chat não está funcionando" -ForegroundColor Red
}

Write-Host "`n=== TESTE CONCLUÍDO ===" -ForegroundColor Green

