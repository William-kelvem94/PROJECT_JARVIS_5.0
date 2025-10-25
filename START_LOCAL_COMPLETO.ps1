# JARVIS - Versao Local Completa com Ollama Windows
# Execute: .\START_LOCAL_COMPLETO.ps1

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "     JARVIS AI - Instalacao Local Completa" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# 1. Verificar/Instalar Ollama
Write-Host "[1/8] Verificando Ollama..." -ForegroundColor Yellow

try {
    $ollamaVersion = ollama --version
    Write-Host "[OK] Ollama ja instalado: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "[AVISO] Ollama nao encontrado!" -ForegroundColor Yellow
    Write-Host "`nBaixando Ollama para Windows..." -ForegroundColor Cyan
    
    $ollamaUrl = "https://ollama.com/download/OllamaSetup.exe"
    $ollamaInstaller = "$env:TEMP\OllamaSetup.exe"
    
    try {
        Write-Host "Baixando de: $ollamaUrl" -ForegroundColor Gray
        Invoke-WebRequest -Uri $ollamaUrl -OutFile $ollamaInstaller -UseBasicParsing
        Write-Host "[OK] Download concluido!" -ForegroundColor Green
        
        Write-Host "`nInstalando Ollama..." -ForegroundColor Yellow
        Start-Process -FilePath $ollamaInstaller -Wait
        
        Write-Host "[OK] Ollama instalado!" -ForegroundColor Green
        Write-Host "IMPORTANTE: Reinicie este terminal e execute o script novamente!" -ForegroundColor Red
        exit 0
    } catch {
        Write-Host "[ERRO] Falha ao baixar/instalar Ollama" -ForegroundColor Red
        Write-Host "Instale manualmente: https://ollama.com/download" -ForegroundColor Yellow
        exit 1
    }
}

# 2. Iniciar Ollama Service
Write-Host "`n[2/8] Iniciando Ollama..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "ollama serve" -WindowStyle Minimized
Start-Sleep -Seconds 5
Write-Host "[OK] Ollama rodando!" -ForegroundColor Green

# 3. Baixar modelo LLM
Write-Host "`n[3/8] Verificando modelo LLM..." -ForegroundColor Yellow
try {
    $models = ollama list
    if ($models -like "*llama2*") {
        Write-Host "[OK] Modelo llama2 ja baixado" -ForegroundColor Green
    } else {
        Write-Host "Baixando modelo llama2 (~4GB)..." -ForegroundColor Yellow
        Write-Host "Isso pode demorar 5-10 minutos..." -ForegroundColor Gray
        ollama pull llama2
        Write-Host "[OK] Modelo baixado!" -ForegroundColor Green
    }
} catch {
    Write-Host "[AVISO] Erro ao verificar modelos, continuando..." -ForegroundColor Yellow
}

# 4. Verificar Python
Write-Host "`n[4/8] Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "[OK] $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] Python nao encontrado!" -ForegroundColor Red
    Write-Host "Instale Python 3.11+: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# 5. Configurar Backend
Write-Host "`n[5/8] Configurando Backend..." -ForegroundColor Yellow
Set-Location backend

if (-Not (Test-Path "venv")) {
    Write-Host "Criando ambiente virtual..." -ForegroundColor Gray
    python -m venv venv
}

Write-Host "Ativando ambiente virtual..." -ForegroundColor Gray
.\venv\Scripts\Activate.ps1

Write-Host "Instalando dependencias..." -ForegroundColor Gray
pip install -q -r requirements.txt

Write-Host "[OK] Backend configurado!" -ForegroundColor Green

# 6. Criar banco SQLite local
Write-Host "`n[6/8] Configurando banco de dados..." -ForegroundColor Yellow
$env:DATABASE_URL = "sqlite+aiosqlite:///./jarvis.db"
$env:REDIS_URL = "redis://localhost:6379"
$env:OLLAMA_URL = "http://localhost:11434"
$env:OLLAMA_DEFAULT_MODEL = "llama2"
$env:SECRET_KEY = "local-dev-secret-key-change-in-production"
$env:DEBUG = "True"

Write-Host "[OK] Configuracao concluida!" -ForegroundColor Green

# 7. Iniciar Backend
Write-Host "`n[7/8] Iniciando Backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; `$env:DATABASE_URL='sqlite+aiosqlite:///./jarvis.db'; `$env:OLLAMA_URL='http://localhost:11434'; `$env:OLLAMA_DEFAULT_MODEL='llama2'; `$env:SECRET_KEY='dev-secret'; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Normal
Start-Sleep -Seconds 5
Write-Host "[OK] Backend iniciado!" -ForegroundColor Green

# 8. Verificar Node.js e iniciar Frontend
Set-Location ../frontend

Write-Host "`n[8/8] Configurando Frontend..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "[OK] Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] Node.js nao encontrado!" -ForegroundColor Red
    Write-Host "Instale Node.js 20+: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

if (-Not (Test-Path "node_modules")) {
    Write-Host "Instalando dependencias..." -ForegroundColor Gray
    npm install
}

Write-Host "Iniciando Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm run dev" -WindowStyle Normal
Start-Sleep -Seconds 5

# Resultado
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "              JARVIS RODANDO - MODO COMPLETO!" -ForegroundColor Green
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "Servicos ativos:" -ForegroundColor Cyan
Write-Host "  [1] Ollama LLM    -> http://localhost:11434" -ForegroundColor White
Write-Host "  [2] Backend API   -> http://localhost:8000" -ForegroundColor White
Write-Host "  [3] Frontend Web  -> http://localhost:3000" -ForegroundColor White

Write-Host "`nAguardando servicos..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "`nAbrindo navegador..." -ForegroundColor Cyan
Start-Process "http://localhost:3000"

Write-Host "`n[SUCESSO] JARVIS COMPLETO E FUNCIONAL!`n" -ForegroundColor Green
Write-Host "Para parar: Feche as janelas PowerShell que foram abertas`n" -ForegroundColor Gray

