@echo off
setlocal enabledelayedexpansion
REM Batch script to launch backend and frontend for Jarvis project on Windows.
REM Optimized for JARVIS 5.0

REM Ensure we are in the repository root
cd /d %~dp0

echo ==========================================
echo       JARVIS 5.0 - STARTUP SYSTEM
echo ==========================================

REM -- prepare backend environment if needed --
if not exist backend\venv\Scripts\activate.bat (
    echo [INFO] Creating Python virtual environment...
    python -m venv backend\venv
    call backend\venv\Scripts\activate.bat
    echo [INFO] Installing Python dependencies...
    pip install --upgrade pip
    pip install -r backend\app\requirements.txt
    deactivate
)

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
echo Escolha o modo de inicio:
echo [1] Modo Desenvolvedor -- Pesado (Hot-reload ativado)
echo [2] Modo Performance -- Leve e Estavel (Producao)
echo.
set "MODO=1"
set /p "MODO=Selecione (1 ou 2): [1] "

if "%MODO%"=="2" (
    echo [INFO] Iniciando em Modo Performance...
    echo [INFO] Verificando se o build e valido...
    if not exist frontend\.next\BUILD_ID (
        echo [INFO] Build nao encontrado ou incompleto. Gerando build...
        pushd frontend
        if "%FRONTEND_CMD%"=="pnpm" (
            pnpm build
        ) else if "%FRONTEND_CMD%"=="npx pnpm" (
            npx pnpm build
        ) else (
            npm run build
        )
        popd
        if errorlevel 1 (
            echo [ERROR] Falha ao gerar o build da aplicacao.
            pause
            exit /b 1
        )
    )
    
    start "Jarvis Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && echo Starting backend API... && uvicorn app.main:app --host 0.0.0.0 --port 8000"
    start "Jarvis Agent" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && echo Starting LiveKit Agent Worker... && python -m app.agents dev"
    start "Jarvis Frontend" cmd /k "cd /d %~dp0frontend && echo Starting frontend (Production)... && if "%FRONTEND_CMD%"=="pnpm" ( pnpm start ) else if "%FRONTEND_CMD%"=="npx pnpm" ( npx pnpm start ) else ( npm run start )"
) else (
    echo [INFO] Iniciando em Modo Desenvolvedor...
    start "Jarvis Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && echo Starting backend API... && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    start "Jarvis Agent" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && echo Starting LiveKit Agent Worker... && python -m app.agents dev"
    start "Jarvis Frontend" cmd /k "cd /d %~dp0frontend && echo Starting frontend (Dev)... && if "%FRONTEND_CMD%"=="pnpm" ( pnpm dev ) else if "%FRONTEND_CMD%"=="npx pnpm" ( npx pnpm dev ) else ( npm run dev )"
)

echo.
echo [SUCCESS] Backend e Frontend iniciados!
echo [TIP] Se o seu PC estiver lento, utilize o Modo Performance (2).
echo [TIP] Desative o fundo animado definindo NEXT_PUBLIC_ENABLE_VANTA=false no seu .env
echo.
pause