# Script PowerShell para configurar Ollama e baixar modelos essenciais
# Execute como Administrador

Write-Host "=== CONFIGURANDO OLLAMA PARA JARVIS ===" -ForegroundColor Green

# Verificar se Ollama está instalado
if (-not (Get-Command "ollama" -ErrorAction SilentlyContinue)) {
    Write-Host "ERRO: Ollama não encontrado!" -ForegroundColor Red
    Write-Host "Baixe e instale: https://ollama.com/download/OllamaSetup.exe" -ForegroundColor Yellow
    exit 1
}

Write-Host "Ollama encontrado!" -ForegroundColor Green

# Iniciar Ollama em segundo plano
Write-Host "`nIniciando servidor Ollama..." -ForegroundColor Cyan
Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
Start-Sleep 10

# Verificar se está rodando
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
    Write-Host "Ollama está rodando!" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Ollama não está respondendo!" -ForegroundColor Red
    exit 1
}

# Lista de modelos essenciais
$models = @(
    "codellama:7b",          # Melhor para código
    "deepseek-coder:6.7b",   # Especializado em código
    "llama2:7b",             # Modelo geral
    "mistral:7b"             # Conversacional
)

Write-Host "`n=== BAIXANDO MODELOS ESSENCIAIS ===" -ForegroundColor Green
Write-Host "Isso pode demorar vários minutos dependendo da sua internet..." -ForegroundColor Yellow

foreach ($model in $models) {
    Write-Host "`nBaixando $model..." -ForegroundColor Cyan
    ollama pull $model
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ $model baixado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "✗ Erro ao baixar $model" -ForegroundColor Red
    }
}

# Listar modelos instalados
Write-Host "`n=== MODELOS INSTALADOS ===" -ForegroundColor Green
ollama list

Write-Host "`n=== CONFIGURAÇÃO CONCLUÍDA! ===" -ForegroundColor Green
Write-Host "Agora você pode iniciar o JARVIS com Docker:" -ForegroundColor Yellow
Write-Host "  docker-compose -f docker/docker-compose.yml up -d" -ForegroundColor Cyan

