@echo off
setlocal enabledelayedexpansion
REM Batch script to launch backend and frontend for Jarvis project on Windows.
REM Optimized for JARVIS 5.0

REM Ensure we are in the repository root
cd /d %~dp0

echo ==========================================
echo       JARVIS 5.0 - STARTUP SYSTEM
echo ==========================================

REM -- sanity checks --
if not exist env\.env (
    echo [ERROR] Arquivo env\.env nao encontrado! 
    echo [ERROR] Crie o arquivo com suas chaves de API antes de continuar.
    pause
    exit /b 1
)

REM -- prepare backend environment if needed --
if not exist backend\venv\Scripts\activate.bat (
    echo [INFO] Creating Python virtual environment...
    python -m venv backend\venv
    call backend\venv\Scripts\activate.bat
    echo [INFO] Installing Python dependencies...
    pip install --upgrade pip
    pip install -r backend\app\requirements.txt
    echo [INFO] Installing Playwright Browsers...
    playwright install chromium
    deactivate
)

REM ── JARVIS Auto-Configuration (auto-installs deps, patches, validates) ─────────
echo [INFO] Executando auto-configuração do JARVIS...
call backend\venv\Scripts\activate.bat
set PYTHONIOENCODING=utf-8
python backend\setup.py
if errorlevel 1 (
    echo [ERROR] Auto-configuração falhou. Verifique os erros acima.
    pause
    exit /b 1
)
deactivate

REM Propagate global env file to respective directories for safe native parsing
if exist env\.env (
    copy /Y "%~dp0env\.env" "%~dp0frontend\.env.local" > nul
    copy /Y "%~dp0env\.env" "%~dp0backend\.env" > nul
    echo [INFO] Global env\.env safely propagated to frontend and backend.
)

REM verify frontend tooling
set FRONTEND_CMD=npm
set USE_NPX_PNPM=0
where pnpm >nul 2>&1
if not errorlevel 1 (
    set FRONTEND_CMD=pnpm
    echo [INFO] pnpm detected. Performance will be better.
) else (
    if exist frontend\pnpm-lock.yaml (
        set FRONTEND_CMD=npx pnpm
        echo [INFO] pnpm-lock.yaml found. Using npx pnpm for better consistency.
    ) else (
        echo [WARN] pnpm not found. Using npm.
    )
)

REM ensure frontend dependencies are installed
if not exist frontend\node_modules (
    echo [INFO] Installing frontend dependencies...
    pushd frontend
    if "%FRONTEND_CMD%"=="pnpm" (
        pnpm install
    ) else if "%FRONTEND_CMD%"=="npx pnpm" (
        npx pnpm install
    ) else (
        npm install
    )
    popd
    if errorlevel 1 (
        echo [ERROR] Failed to install frontend packages.
        pause
        exit /b 1
    )
)

echo.
echo [INFO] Iniciando Sistema JARVIS Unificado...
echo.

REM Lança os 3 serviços diretamente
start "Jarvis Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && echo Starting backend API... && uvicorn app.main:app --host 0.0.0.0 --port 8000"
start "Jarvis Agent"   cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && echo Starting LiveKit Agent Worker... && python -m app.agents start"
if "%FRONTEND_CMD%"=="pnpm" (
    start "Jarvis Frontend" cmd /k "cd /d %~dp0frontend && pnpm dev"
) else if "%FRONTEND_CMD%"=="npx pnpm" (
    start "Jarvis Frontend" cmd /k "cd /d %~dp0frontend && npx pnpm dev"
) else (
    start "Jarvis Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
)

REM Aguarda 8 segundos para os serviços subirem antes de iniciar o monitor
echo [INFO] Aguardando serviços iniciarem (8s)...
timeout /t 8 /nobreak > nul

REM Lança o monitor de processos em background (reinicia serviços se travarem)
echo [INFO] Iniciando Monitor de Processos (auto-restart habilitado)...
start "Jarvis Monitor" powershell -NonInteractive -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\monitor-heartbeat.ps1" -Root "%~dp0"

echo.
echo [SUCCESS] JARVIS iniciado com supervisao automatica!
echo [INFO] - Backend:  http://localhost:8000
echo [INFO] - Frontend: http://localhost:3000
echo [INFO] - Monitor:  backend\data\logs\monitor.log
echo [INFO] Feche esta janela quando quiser encerrar manualmente.
echo.
pause
