# JARVIS AI - Quick Local Start (Sem Docker)
# Execute: .\QUICK_LOCAL_START.ps1

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "JARVIS AI - Iniciando Localmente" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "[1/5] Verificando Python..." -ForegroundColor Yellow
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Host "[OK] $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Python não encontrado!" -ForegroundColor Red
    Write-Host "Instale em: https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# Verificar Node.js
Write-Host "[2/5] Verificando Node.js..." -ForegroundColor Yellow
if (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVersion = node --version
    Write-Host "[OK] Node.js $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Node.js não encontrado!" -ForegroundColor Red
    Write-Host "Instale em: https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Verificar Ollama
Write-Host "[3/5] Verificando Ollama..." -ForegroundColor Yellow
if (Get-Command ollama -ErrorAction SilentlyContinue) {
    Write-Host "[OK] Ollama instalado" -ForegroundColor Green
    
    # Verificar se está rodando
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        Write-Host "[OK] Ollama está rodando" -ForegroundColor Green
    } catch {
        Write-Host "[AVISO] Ollama não está rodando" -ForegroundColor Yellow
        Write-Host "Iniciando Ollama..." -ForegroundColor Yellow
        Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Seconds 3
    }
} else {
    Write-Host "[ERRO] Ollama não encontrado!" -ForegroundColor Red
    Write-Host "Instale em: https://ollama.ai/download/windows" -ForegroundColor Red
    exit 1
}

# Setup Backend
Write-Host "[4/5] Configurando Backend..." -ForegroundColor Yellow
Set-Location -Path ".\backend"

if (-not (Test-Path ".\venv")) {
    Write-Host "Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

Write-Host "Instalando dependências..." -ForegroundColor Yellow
pip install -q -r requirements.txt

if (-not (Test-Path ".\.env")) {
    Write-Host "Criando .env..." -ForegroundColor Yellow
    $secretKey = python -c "import secrets; print(secrets.token_urlsafe(32))"
    @"
DATABASE_URL=sqlite+aiosqlite:///./jarvis.db
REDIS_URL=memory://
OLLAMA_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama2
SECRET_KEY=$secretKey
CORS_ORIGINS=http://localhost:3000
DEBUG=True
ENVIRONMENT=development
LOG_LEVEL=INFO
"@ | Out-File -FilePath .env -Encoding utf8
}

Write-Host "Criando banco de dados..." -ForegroundColor Yellow
python -m alembic upgrade head 2>$null

Write-Host "[OK] Backend configurado!" -ForegroundColor Green

# Setup Frontend
Write-Host "[5/5] Configurando Frontend..." -ForegroundColor Yellow
Set-Location -Path "..\frontend"

if (-not (Test-Path ".\node_modules")) {
    Write-Host "Instalando dependências frontend..." -ForegroundColor Yellow
    npm install --silent
}

if (-not (Test-Path ".\.env")) {
    Write-Host "Criando .env frontend..." -ForegroundColor Yellow
    @"
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
"@ | Out-File -FilePath .env -Encoding utf8
}

Write-Host "[OK] Frontend configurado!" -ForegroundColor Green

# Voltar para raiz
Set-Location -Path ".."

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "[SUCESSO] Setup Completo!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Iniciando serviços..." -ForegroundColor Yellow
Write-Host ""

# Verificar modelo Ollama
Write-Host "Verificando modelo LLM..." -ForegroundColor Yellow
$models = ollama list
if ($models -match "llama2") {
    Write-Host "[OK] Modelo llama2 já instalado" -ForegroundColor Green
} else {
    Write-Host "[AVISO] Baixando modelo llama2 (~4GB)..." -ForegroundColor Yellow
    Write-Host "Isso pode demorar alguns minutos..." -ForegroundColor Yellow
    ollama pull llama2
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Iniciando JARVIS..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[1] Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "[2] Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "[3] API Docs: http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pressione Ctrl+C para parar todos os serviços" -ForegroundColor Yellow
Write-Host ""

# Iniciar Backend
Write-Host "Iniciando Backend..." -ForegroundColor Yellow
$backendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -PassThru

Start-Sleep -Seconds 5

# Iniciar Frontend
Write-Host "Iniciando Frontend..." -ForegroundColor Yellow
$frontendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -PassThru

Write-Host ""
Write-Host "[OK] JARVIS está rodando!" -ForegroundColor Green
Write-Host ""
Write-Host "Acesse: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para parar: Feche as janelas do PowerShell" -ForegroundColor Yellow
Write-Host ""
Write-Host "Pressione qualquer tecla para abrir o navegador..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Abrir navegador
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "Navegador aberto! Divirta-se! :)" -ForegroundColor Green

