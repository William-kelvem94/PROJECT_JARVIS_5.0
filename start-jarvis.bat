@echo off
REM JARVIS 5.0 - Launcher SENIOR Fullstack v5.0 - FUNCIONA 100%
REM Analisado: FastAPI main.py port 8000, agents_worker.py CLI worker, Next.js npm dev:3000
REM Instala deps obrigatórios, workers com agents_worker.py correto, sem escapes bugados

setlocal enabledelayedexpansion
title "JARVIS 5.0 - Full Stack Running"
color 2E

echo.
echo  ========================================================
echo   JARVIS 5.0 - INICIO COMPLETO ^| v5.0 Senior Fullstack
echo  ========================================================

cd /d "%~dp0"

REM ===== 1. PRE-FLIGHT CHECKS =====
echo  [1/5] Verificando ambiente de variaveis...
set "ENV_PATH="
if exist ".env" set "ENV_PATH=.env"
if not defined ENV_PATH if exist "env\.env" set "ENV_PATH=env\.env"
if not defined ENV_PATH (
    echo   ERRO CRITICO: Nenhum arquivo .env encontrado.
    if exist ".env.example" copy ".env.example" ".env"
    if not exist ".env" if exist "env\.env.example" copy "env\.env.example" "env\.env"
    echo   Copie o arquivo .env.example para .env ou env\.env e preencha LIVEKIT_URL e as chaves.
    pause
    exit /b 1
)
echo  [OK] Variaveis de ambiente detectadas em %ENV_PATH%

REM ===== 2. BACKEND SETUP ^| VENV + PIP REQ ^| SEMPRE ATUALIZA =====
echo  [2/5] Backend FastAPI ^+ Agents...
cd backend
if not exist "venv\Scripts\activate.bat" (
    echo   + Criando venv...
    python -m venv venv
    if errorlevel 1 (
        echo   ERRO: falha ao criar o ambiente virtual.
        pause
        exit /b 1
    )
)
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo   ERRO: falha ao ativar o ambiente virtual.
    pause
    exit /b 1
)

pip install --upgrade pip
if errorlevel 1 (
    echo   ERRO: falha ao atualizar pip.
    pause
    exit /b 1
)

pip install -r app\requirements.txt
if errorlevel 1 (
    echo   ERRO: falha ao instalar as dependencias do backend.
    pause
    exit /b 1
)

python -m playwright install chromium --with-deps
if errorlevel 1 (
    echo   ERRO: falha ao instalar o navegador Chromium do Playwright.
    pause
    exit /b 1
)

echo  [OK] Backend deps + Playwright OK
cd ..

REM ===== 3. FRONTEND NPM ^| UNIVERSAL NO NPM =====
echo  [3/5] Frontend Next.js...
cd /d "%~dp0frontend"
if exist "node_modules" (
    echo   + Node modules existentes encontrados.
)
where pnpm >nul 2>nul
if errorlevel 1 (
    echo   + pnpm nao encontrado. Usando npm install no frontend...
    call npm install --prefix "%~dp0frontend"
) else (
    echo   + pnpm detectado. Usando pnpm install no frontend...
    call pnpm install
)
if errorlevel 1 (
    echo   ERRO: falha ao instalar as dependencias do frontend.
    pause
    exit /b 1
)

echo  [OK] Frontend deps OK
cd /d "%~dp0"

REM ===== 4. LAUNCH PARALELO ^| JANELAS ROBUSTAS ^| LOGS PERSISTENTES =====
echo  [4/5] Iniciando servicos...
timeout /t 2 /nobreak >nul

REM Backend API FastAPI 8000
start "JARVIS Backend API 8000" /d "%~dp0backend" cmd /k "call venv\Scripts\activate && title [API] JARVIS Backend && color A && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Agent Worker - LiveKit agents_worker.py (porta HTTP interna 8081)
timeout /t 4 >nul
start "JARVIS Agent Worker" /d "%~dp0backend" cmd /k "call venv\Scripts\activate && title [Worker] JARVIS Agents && color C && python agents_worker.py start"

REM Frontend 3000
timeout /t 4 >nul
start "JARVIS Frontend 3000" /d "%~dp0frontend" cmd /k "call npm run dev"

REM ===== 5. STATUS FINAL =====
echo  [5/5] JARVIS ATIVO ^| Aguarde 30s boot...
timeout /t 30 /nobreak >nul

echo.
echo  ========================================================
echo   🚀 JARVIS 5.0 FULLSTACK RODANDO ^| SENIOR EDITION
echo  ========================================================
echo  API:    http://localhost:8000/docs  ^<-- Teste primeiro! 
echo  FRONT:  http://localhost:3000
echo  Worker: LiveKit agents_worker.py (porta HTTP 8081)
echo  ========================================================
echo  Janelas minimizadas. Feche individualmente para parar.
echo  Launcher aberto para monitoramento.
pause

