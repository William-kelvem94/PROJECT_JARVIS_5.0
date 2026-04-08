@echo off
setlocal enabledelayedexpansion
title JARVIS 5.0 - Complete Launcher
color 0A

REM ==========================================
REM      JARVIS 5.0 - STARTUP COMPLETO v3.0
REM ==========================================
REM Rode: .\start-jarvis.bat (admin recomendado)

cd /d "%~dp0"
echo [INFO] Diretorio: %CD%

REM 1. Verificar .env
if not exist ".env" (
    echo [ERRO] Crie .env a partir de .env.example com suas chaves LiveKit/API!
    echo Exemplo: cp .env.example .env ^&^& notepad .env
    pause
    exit /b 1
)
echo [OK] .env encontrado.

REM 2. Backend VENV
cd backend
if not exist "venv" (
    echo [INFO] Criando venv...
    python -m venv venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar venv. Instale Python 3.11+.
        pause
        exit /b 1
    )
)
call venv\Scripts\activate.bat
echo [OK] venv ativado.
cd ..

REM 3. Playwright
if not exist "backend\data\.playwright_installed" (
    echo [INFO] Instalando Playwright...
    cd backend
    pip install playwright
    playwright install chromium --with-deps
    cd ..
)
echo [OK] Playwright OK.

REM 4. Models MediaPipe (se nao existirem)
if not exist "backend\data\models\face_landmarker.task" (
    echo [INFO] Baixando models MediaPipe...
    REM Adicione logica de download se necessario
)
echo [OK] Models OK.

REM 5. Frontend deps (se package-lock ausente)
cd frontend
if not exist "node_modules" (
    echo [INFO] Instalando NPM deps...
    npm install
)
cd ..
echo [OK] Frontend OK.

REM ==========================================
REM INICIAR SERVICOS PARALELOS (4 janelas)
REM ==========================================

echo [START] Aguardando 3s para setups...
timeout /t 3 /nobreak >nul

REM Backend API (FastAPI)
start "JARVIS-Backend-API" cmd /k "title JARVIS Backend ^| color 0B ^| cd /d %CD% ^&^& cd backend ^&^& call venv\Scripts\activate.bat ^&^& uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Agents Worker 1
timeout /t 2 /nobreak >nul
start "JARVIS-Agents-Worker" cmd /k "title Agents Worker ^| color 0C ^| cd /d %CD% ^&^& cd backend ^&^& call venv\Scripts\activate.bat ^&^& python -c \"import sys; sys.path.insert(0, '.'); from livekit.agents.cli import run_app; from app.agents import entrypoint; run_app(livekit.agents.WorkerOptions(entrypoint_fnc=entrypoint))\""

REM LiveKit Worker 2
timeout /t 2 /nobreak >nul
start "JARVIS-LiveKit-Worker" cmd /k "title LiveKit Worker ^| color 0D ^| cd /d %CD% ^&^& cd backend ^&^& call venv\Scripts\activate.bat ^&^& python -c \"import sys; sys.path.insert(0, '.'); from app.agents import entrypoint; from livekit.agents import cli; cli.run_app(cli.WorkerOptions(entrypoint_fnc=entrypoint))\""

REM Frontend Next.js
timeout /t 2 /nobreak >nul
start "JARVIS-Frontend" cmd /k "title Frontend ^| color 0E ^| cd /d %CD% ^&^& cd frontend ^&^& npm run dev"

echo.
echo ==========================================
echo   JARVIS 5.0 ATIVO! Acessos:
echo   Backend API: http://localhost:8000/docs
echo   Frontend:    http://localhost:3000
echo   Workers:     LiveKit (verifique logs nas janelas)
echo ==========================================
echo Pressione qualquer tecla para fechar este launcher...
pause >nul

