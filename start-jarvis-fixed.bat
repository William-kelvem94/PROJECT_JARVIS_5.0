@echo off
setlocal enabledelayedexpansion
title JARVIS 5.0 - Launcher FUNCIONAL Completo v4.0
color 0A

REM ==========================================
REM   JARVIS 5.0 STARTUP - FUNCIONA DE VERDADE
REM ==========================================
REM Sem limitações, instala tudo, roda tudo!

cd /d "%~dp0"
echo [INFO] JARVIS 5.0 inicializando...

REM 0. Verifica arquivos de ambiente
if not exist ".env" if not exist "env\.env" (
    echo ERRO CRITICO: Nenhum arquivo de ambiente encontrado.
    echo Copie .env.example para .env ou env\.env e configure LIVEKIT_URL, API keys e JARVIS_KB_PATH.
    pause
    exit /b 1
)

echo [OK] Arquivo de ambiente encontrado.

REM 1. .env OK (confirmado pelo user)
echo [OK] .env OK.

REM 2. BACKEND - VENV + DEPS COMPLETOS
echo [SETUP] Backend...
cd backend
if not exist "venv" (
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r app\requirements.txt --upgrade
) else (
    call venv\Scripts\activate.bat
    pip install -r app\requirements.txt --upgrade
)
echo [OK] Backend deps OK.
cd ..

REM 3. PLAYWRIGHT SEMPRE
echo [SETUP] Playwright...
cd backend
playwright install chromium --with-deps
cd ..
echo [OK] Playwright OK.

REM 4. FRONTEND NPM (universal, sem pnpm)
echo [SETUP] Frontend...
cd frontend
if not exist "node_modules" (
    npm install
) else (
    npm install
)
echo [OK] Frontend OK.
cd ..

echo [READY] Setup completo! Iniciando servicos...

timeout /t 2 >nul

REM ==========================================
REM SERVICOS PARALELOS - JANELAS PERMANENTES
REM ==========================================

REM Backend FastAPI
start /min "JARVIS Backend API:8000" cmd /k "color 0B ^& title Backend API ^| cd /d %CD% ^& cd backend ^& call venv\Scripts\activate ^& uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Worker 1 - agents_worker.py (usando arquivo existente)
timeout /t 3 >nul
start /min "JARVIS Agents Worker 1" cmd /k "color 0C ^& title Agents Worker ^| cd /d %CD% ^& cd backend ^& call venv\Scripts\activate ^& python agents_worker.py"

REM Worker 2 - outro worker (duplicado para LiveKit)
timeout /t 3 >nul
start /min "JARVIS LiveKit Worker 2" cmd /k "color 0D ^& title LiveKit Worker ^| cd /d %CD% ^& cd backend ^& call venv\Scripts\activate ^& python agents_worker.py --worker-id livekit"

REM Frontend Next.js
timeout /t 3 >nul
start "JARVIS Frontend:3000" cmd /k "color 0E ^& title Frontend ^| cd /d %CD% ^& cd frontend ^& npm run dev"

echo.
echo ==========================================
echo      🚀 JARVIS 5.0 RODANDO COMPLETO!
echo ==========================================
echo Backend API: http://localhost:8000/docs ^<-- Abra primeiro!
echo Frontend:    http://localhost:3000
echo Workers:     2 LiveKit agents ativos (logs nas janelas)
echo ==========================================
echo Launcher fica aberto para nao perder janelas.
echo Feche manualmente cada servico quando quiser parar.
pause

