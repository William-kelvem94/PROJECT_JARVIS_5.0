# Instalar Ollama no Windows
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Instalando Ollama..." -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

$ollamaUrl = "https://ollama.ai/download/OllamaSetup.exe"
$installerPath = "$env:TEMP\OllamaSetup.exe"

Write-Host "`nBaixando Ollama..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $ollamaUrl -OutFile $installerPath -UseBasicParsing
    Write-Host "✅ Download completo!" -ForegroundColor Green
    
    Write-Host "`nInstalando Ollama..." -ForegroundColor Yellow
    Start-Process -FilePath $installerPath -Wait
    
    Write-Host "`n✅ Ollama instalado!" -ForegroundColor Green
    Write-Host "`nBaixando modelo llama2 (~4GB)..." -ForegroundColor Yellow
    Write-Host "Isso pode demorar alguns minutos..." -ForegroundColor Yellow
    
    Start-Sleep -Seconds 3
    ollama pull llama2
    
    Write-Host "`n✅ Ollama configurado!" -ForegroundColor Green
    Write-Host "`n✅ Testando..." -ForegroundColor Yellow
    ollama run llama2 "Hello" --verbose
    
} catch {
    Write-Host "`n❌ Erro: $_" -ForegroundColor Red
    Write-Host "`nBaixe manualmente em: https://ollama.ai/download" -ForegroundColor Yellow
}

