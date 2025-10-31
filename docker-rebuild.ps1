# Script de Rebuild Otimizado para JARVIS 5.0
# Aplica todas as otimizações de performance

Write-Host "🚀 Reconstruindo JARVIS com otimizações de performance..." -ForegroundColor Green

# Parar containers existentes
Write-Host "`n📦 Parando containers existentes..." -ForegroundColor Yellow
docker-compose down

# Limpar volumes antigos (opcional - descomente se necessário)
# Write-Host "`n🧹 Limpando volumes antigos..." -ForegroundColor Yellow
# docker-compose down -v

# Reconstruir imagens com cache limpo
Write-Host "`n🔨 Reconstruindo imagens..." -ForegroundColor Yellow
docker-compose build --no-cache

# Iniciar containers otimizados
Write-Host "`n▶️  Iniciando containers..." -ForegroundColor Yellow
docker-compose up -d

# Aguardar saúde dos containers
Write-Host "`n⏳ Aguardando containers ficarem saudáveis..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Mostrar status
Write-Host "`n📊 Status dos containers:" -ForegroundColor Cyan
docker ps --filter "name=jarvis" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Mostrar uso de recursos
Write-Host "`n📈 Uso de recursos:" -ForegroundColor Cyan
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | Select-Object -First 3

# Testar endpoints
Write-Host "`n🔍 Testando endpoints..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/status" -Method Get -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ JARVIS está online e responsivo!" -ForegroundColor Green
        $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 3
    }
} catch {
    Write-Host "⚠️  Aguarde alguns segundos para o JARVIS inicializar completamente" -ForegroundColor Yellow
}

Write-Host "`n📝 Próximos passos:" -ForegroundColor Cyan
Write-Host "  - Ver logs: docker-compose logs -f jarvis" -ForegroundColor White
Write-Host "  - Monitorar recursos: docker stats jarvis_ai jarvis_ollama" -ForegroundColor White
Write-Host "  - Acessar interface: http://localhost:8000" -ForegroundColor White
Write-Host "  - Ver API docs: http://localhost:8000/api/docs" -ForegroundColor White

Write-Host "`n✨ Rebuild concluído!" -ForegroundColor Green

