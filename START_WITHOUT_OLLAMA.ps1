# JARVIS AI - Start Sem Ollama (Modo Demo)
# Execute: .\START_WITHOUT_OLLAMA.ps1

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "JARVIS AI - Modo Demo (Sem LLM)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[AVISO] Iniciando sem Ollama - respostas serão simuladas" -ForegroundColor Yellow
Write-Host "Para usar LLM real, instale Ollama: https://ollama.ai/download" -ForegroundColor Yellow
Write-Host ""

# Verificar Python
Write-Host "[1/4] Verificando Python..." -ForegroundColor Yellow
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Host "[OK] $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Python nao encontrado!" -ForegroundColor Red
    exit 1
}

# Verificar Node.js
Write-Host "[2/4] Verificando Node.js..." -ForegroundColor Yellow
if (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVersion = node --version
    Write-Host "[OK] Node.js $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Node.js nao encontrado!" -ForegroundColor Red
    exit 1
}

# Setup Backend
Write-Host "[3/4] Configurando Backend..." -ForegroundColor Yellow
Set-Location -Path ".\backend"

if (-not (Test-Path ".\venv")) {
    Write-Host "Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host "Instalando dependencias basicas..." -ForegroundColor Yellow
pip install -q fastapi uvicorn sqlalchemy aiosqlite alembic pydantic pydantic-settings python-jose passlib bcrypt python-dotenv

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

# Criar mock do LLM Service
Write-Host "Criando mock do LLM Service..." -ForegroundColor Yellow
$mockLLM = @"
# Mock LLM Service (Sem Ollama)
from typing import Dict, Any, AsyncIterator
import asyncio

class LLMService:
    def __init__(self):
        self.initialized = True
        self.default_model = "mock"
        self.available_models = ["mock"]
    
    async def initialize(self):
        self.initialized = True
    
    async def generate(self, prompt: str, **kwargs) -> str:
        await asyncio.sleep(0.5)
        return f"[MODO DEMO] Recebi sua mensagem: '{prompt}'. Instale Ollama para respostas reais!"
    
    async def generate_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        mensagem = f"[MODO DEMO] Recebi: '{prompt[:50]}...'. Para usar LLM real, instale Ollama!"
        for palavra in mensagem.split():
            yield palavra + " "
            await asyncio.sleep(0.1)
    
    async def chat(self, messages: list, **kwargs) -> str:
        ultima = messages[-1]['content'] if messages else "..."
        await asyncio.sleep(0.5)
        return f"[DEMO] Sua mensagem: '{ultima}'. Instale Ollama: https://ollama.ai"
    
    async def chat_stream(self, messages: list, **kwargs) -> AsyncIterator[str]:
        ultima = messages[-1]['content'] if messages else "..."
        resposta = f"[DEMO] Resposta para: '{ultima[:40]}...'. Use Ollama para IA real!"
        for palavra in resposta.split():
            yield palavra + " "
            await asyncio.sleep(0.1)
    
    async def list_models(self) -> list:
        return [{"name": "mock", "size": 0}]

def get_llm_service() -> LLMService:
    return LLMService()
"@

$mockLLM | Out-File -FilePath "app\services\llm_service.py" -Encoding utf8 -Force

Write-Host "Criando banco de dados..." -ForegroundColor Yellow
python -c "from pathlib import Path; Path('jarvis.db').touch()" 2>$null

Write-Host "[OK] Backend configurado!" -ForegroundColor Green

# Setup Frontend
Write-Host "[4/4] Configurando Frontend..." -ForegroundColor Yellow
Set-Location -Path "..\frontend"

if (-not (Test-Path ".\node_modules")) {
    Write-Host "Instalando dependencias frontend..." -ForegroundColor Yellow
    npm install --silent 2>$null
}

if (-not (Test-Path ".\.env")) {
    Write-Host "Criando .env frontend..." -ForegroundColor Yellow
    @"
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
"@ | Out-File -FilePath .env -Encoding utf8
}

Write-Host "[OK] Frontend configurado!" -ForegroundColor Green

Set-Location -Path ".."

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "[SUCESSO] Setup Completo!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Iniciando JARVIS (Modo Demo)..." -ForegroundColor Yellow
Write-Host ""
Write-Host "[1] Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "[2] Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "[3] API Docs: http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "[AVISO] Chat usará respostas simuladas" -ForegroundColor Yellow
Write-Host "Para IA real: https://ollama.ai/download" -ForegroundColor Yellow
Write-Host ""

# Iniciar Backend
Write-Host "Iniciando Backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 5

# Iniciar Frontend
Write-Host "Iniciando Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "[OK] JARVIS esta rodando!" -ForegroundColor Green
Write-Host ""
Write-Host "Acessando http://localhost:3000 em 3 segundos..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

# Abrir navegador
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "[SUCESSO] Navegador aberto!" -ForegroundColor Green
Write-Host ""
Write-Host "Para parar: Feche as janelas do PowerShell" -ForegroundColor Yellow

