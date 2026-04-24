@echo off
TITLE JARVIS 5.0 - LUXURY ENGINEERING EDITION
SETLOCAL EnableDelayedExpansion

:: Garante que o script rode sempre da pasta onde ele esta, independente de como foi iniciado
cd /d "%~dp0"

:: ======================================================================
:: CONFIGURAÇÃO DE MAESTRIA DE HARDWARE
:: ======================================================================
echo [SYSTEM] Iniciando Diagnostico de Hardware...

:: Verifica se há NVIDIA GPU (Perfil Desktop)
nvidia-smi >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [HARDWARE] GPU NVIDIA Detectada (Perfil Desktop/GPU-First)
    SET JARVIS_AI_DEVICE=cuda
    SET JARVIS_WHISPER_MODEL=tiny
) else (
    echo [HARDWARE] GPU Nao Detectada (Perfil Book2/CPU-Efficient)
    SET JARVIS_AI_DEVICE=cpu
    SET JARVIS_WHISPER_MODEL=base
)

:: Otimização de Threads para i7-12th (Book2) ou i3-10th (Desktop)
SET JARVIS_CPU_THREADS=4
if "%PROCESSOR_IDENTIFIER:~0,7%"=="Intel64" SET JARVIS_CPU_THREADS=8

:: ======================================================================
:: VERIFICAÇÃO DE AMBIENTE
:: ======================================================================

:: Verifica Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado no PATH. Por favor, instale o Python 3.10+.
    pause
    exit /b
)

:: Verifica Node.js
node -v >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Node.js nao encontrado. Necessario para o Cockpit (Frontend).
    pause
    exit /b
)

:: ======================================================================
:: INICIALIZAÇÃO DOS SERVIÇOS
:: ======================================================================

:: 1. Backend (IA Core) - Prioridade ALTA
echo [BACKEND] Iniciando Jarvis Core com Prioridade Alta...

if not exist backend (
    echo [ERRO] Pasta 'backend' nao encontrada. Verifique a estrutura do projeto.
    pause
    exit /b
)

:: Usa o .venv da raiz do projeto (padrao do JARVIS)
if not exist .venv (
    echo [SYSTEM] Criando Ambiente Virtual na raiz...
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERRO] Falha ao criar ambiente virtual Python.
        pause
        exit /b
    )
    call .venv\Scripts\activate.bat
    pip install -r backend\app\requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [ERRO] Falha ao instalar dependencias Python.
        pause
        exit /b
    )
) else (
    call .venv\Scripts\activate.bat
)

:: Seta flags de performance para o Windows
SET PYTHONOPTIMIZE=1
start "JARVIS_BACKEND" /high cmd /k "cd /d "%~dp0backend" && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info"

:: 2. Frontend (Cockpit) - Otimização de RAM
echo [FRONTEND] Iniciando Cockpit UI (Luxury Engineering)...

if not exist frontend (
    echo [ERRO] Pasta 'frontend' nao encontrada. Verifique a estrutura do projeto.
    pause
    exit /b
)

if not exist frontend\node_modules (
    echo [SYSTEM] Instalando dependencias do Frontend (isso pode demorar)...
    cd frontend
    npm install
    cd ..
)

:: Limita o uso de memória do Node para 2GB (Ideal para 16GB total com IA)
SET NODE_OPTIONS=--max-old-space-size=2048
start "JARVIS_FRONTEND" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo ======================================================================
echo [SUCESSO] JARVIS 5.0 esta decolando!
echo [INFO] Cockpit: http://localhost:3000
echo [INFO] Core API: http://localhost:8000
echo ======================================================================
pause
