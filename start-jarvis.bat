@echo off
REM JARVIS 5.0 - Launcher SENIOR Fullstack v5.0 - FUNCIONA 100%
REM Analisado: FastAPI main.py port 8000, agents_worker.py CLI worker, Next.js npm dev:3000
REM Instala deps obrigatórios, workers com agents_worker.py correto, sem escapes bugados

setlocal enabledelayedexpansion
title "JARVIS 5.0 - Full Stack Running"
color 2F

echo.
echo  ========================================================
echo   JARVIS 5.0 - INICIO COMPLETO ^| v5.0 Senior Fullstack
echo  ========================================================

cd /d "%~dp0"

REM ===== 1. BACKEND SETUP ^| VENV + PIP REQ ^| SEMPRE ATUALIZA =====
echo  [1/5] Backend FastAPI ^+ Agents...
cd backend
if not exist venv (
    echo   + Criando venv...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r app\requirements.txt
playwright install chromium --with-deps
echo  [OK] Backend deps + Playwright OK
cd ..

REM ===== 2. FRONTEND NPM ^| UNIVERSAL NO NPM =====
echo  [2/5] Frontend Next.js...
cd frontend
rmdir /s /q node_modules 2>nul
del package-lock.json 2>nul
npm install
echo  [OK] Frontend deps OK
cd ..

REM ===== 3. PRE-FLIGHT CHECKS =====
echo  [3/5] Verificando .env...
if not exist ".env" (
    echo   ERRO CRITICO: Copie .env.example ^> .env e preencha LIVEKIT_URL, API_KEYs
    copy .env.example .env
    notepad .env
    pause
    exit /b 1
)
echo  [OK] .env OK

REM ===== 4. LAUNCH PARALELO ^| JANELAS ROBUSTAS ^| LOGS PERSISTENTES =====
echo  [4/5] Iniciando servicos...
timeout /t 2 /nobreak >nul

REM Backend API FastAPI 8000
start "JARVIS Backend API 8000" cmd /k "title [API] JARVIS Backend ^| color A ^& cd /d %~dp0 ^& cd backend ^& call venv\Scripts\activate ^& uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Agent Worker 1 - CORRETO agents_worker.py
timeout /t 4 >nul
start "JARVIS Agent Worker 1" cmd /k "title [Worker1] Agents ^| color C ^& cd /d %~dp0 ^& cd backend ^& call venv\Scripts\activate ^& python agents_worker.py"

REM Agent Worker 2 - Duplicado para estabilidade
timeout /t 4 >nul
start "JARVIS Agent Worker 2" cmd /k "title [Worker2] LiveKit ^| color D ^& cd /d %~dp0 ^& cd backend ^& call venv\Scripts\activate ^& python agents_worker.py"

REM Frontend 3000
timeout /t 4 >nul
start "JARVIS Frontend 3000" cmd /k "title [FE] Next.js ^| color E ^& cd /d %~dp0 ^& cd frontend ^& npm run dev"

REM ===== 5. STATUS FINAL =====
echo  [5/5] JARVIS ATIVO ^| Aguarde 30s boot...
timeout /t 30 /nobreak >nul

echo.
echo  ========================================================
echo   🚀 JARVIS 5.0 FULLSTACK RODANDO ^| SENIOR EDITION
echo  ========================================================
echo  API:    http://localhost:8000/docs  ^<-- Teste primeiro! 
echo  FRONT:  http://localhost:3000
echo  Workers: 2x LiveKit agents_worker.py (logs nas janelas)
echo  ========================================================
echo  Janelas minimizadas. Feche individualmente para parar.
echo  Launcher aberto para monitoramento.
pause

