@echo off
TITLE JARVIS 5.0 - Smart Launcher
SETLOCAL EnableExtensions

:: ============================================================
:: CONFIGURAÇÕES BASE
:: ============================================================
cd /d "%~dp0"
SET "ROOT=%~dp0"
SET "BACK_DIR=%ROOT%backend"
SET "FRONT_DIR=%ROOT%frontend"
SET "VENV_ACT=%ROOT%.venv\Scripts\activate.bat"
SET "PYTHON_EXE=%ROOT%.venv\Scripts\python.exe"
SET "PYTHONOPTIMIZE=1"
SET "NODE_OPTIONS=--max-old-space-size=2048"

:: Carregar portas do .env se existir, caso contrário usa defaults
SET "BACKEND_PORT=8000"
SET "FRONTEND_PORT=3000"
if exist "%ROOT%.env" (
    for /f "tokens=2 delims==" %%v in ('findstr "BACKEND_PORT FRONTEND_PORT" "%ROOT%.env"') do (
        if "%%v"=="BACKEND_PORT" SET "BACKEND_PORT=%%v"
        if "%%v"=="FRONTEND_PORT" SET "FRONTEND_PORT=%%v"
    )
)

echo [JARVIS] Iniciando Smart Boot...

:: Verificar se o usuário pediu atualização forçada
set "FORCE_UPDATE=0"
if "%~1"=="--update" set "FORCE_UPDATE=1"

:: ============================================================
:: HARDWARE & OPTIMIZAÇÃO
:: ============================================================
echo [JARVIS] Calibrando hardware...
nvidia-smi >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [HW] GPU NVIDIA detectada - Modo CUDA Ativo
    SET "JARVIS_AI_DEVICE=cuda"
    SET "JARVIS_WHISPER_MODEL=tiny"
) else (
    echo [HW] Modo CPU Ativo
    SET "JARVIS_AI_DEVICE=cpu"
    SET "JARVIS_WHISPER_MODEL=base"
)

:: ============================================================
:: LIMPEZA DE PORTAS (PREVENTIVA)
:: ============================================================
echo [CLEAN] Liberando portas de comunicação...
call :kill_port %BACKEND_PORT%
call :kill_port %FRONTEND_PORT%
call :kill_port 3001
call :kill_port 8001

:: ============================================================
:: SMART CHECK: PYTHON & DEPENDÊNCIAS
:: ============================================================
if not exist ".venv\Scripts\activate.bat" (
    echo [SYS] Primeira execução: Criando ambiente virtual...
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 goto :fim_erro
)

call "%VENV_ACT%"
if %ERRORLEVEL% NEQ 0 goto :fim_erro

:: Só instala dependências se a pasta .venv for nova ou --update for passado
if "%FORCE_UPDATE%"=="1" (
    echo [SYS] Atualizando dependências Python...
    "%PYTHON_EXE%" -m pip install --upgrade pip "setuptools<82" wheel
    "%PYTHON_EXE%" -m pip install -r "backend\app\requirements.txt"
) else (
    echo [SYS] Ambiente Python validado (Fast Boot).
)

:: ============================================================
:: SMART CHECK: FRONTEND
:: ============================================================
if not exist "%FRONT_DIR%\node_modules" (
    echo [SYS] Primeira execução: Instalando dependências frontend...
    pushd "%FRONT_DIR%"
    call pnpm install
    popd
) else if "%FORCE_UPDATE%"=="1" (
    echo [SYS] Atualizando dependências frontend...
    pushd "%FRONT_DIR%"
    call pnpm install
    popd
) else (
    echo [SYS] Dependências Frontend validadas (Fast Boot).
)

:: ============================================================
:: EXECUÇÃO DO CORE (BACKEND)
:: ============================================================
echo [BACK] Lançando Core do JARVIS na porta %BACKEND_PORT%...
start "JARVIS_BACKEND" /D "%BACK_DIR%" /HIGH cmd /k "call ""%VENV_ACT%"" && "%PYTHON_EXE%" -m uvicorn app.main:app --host 127.0.0.1 --port %BACKEND_PORT% --reload --log-level info"

echo [BACK] Aguardando sincronização do sistema...
call :wait_http "http://127.0.0.1:%BACKEND_PORT%/health" 30
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Core do JARVIS falhou ao iniciar.
    goto :fim_erro
)
echo [BACK] Sistema Estável.

:: ============================================================
:: EXECUÇÃO DA UI (FRONTEND)
:: ============================================================
echo [FRONT] Lançando Interface Holográfica na porta %FRONTEND_PORT%...
start "JARVIS_FRONTEND" cmd /k "set PORT=%FRONTEND_PORT% && pnpm --dir ""%FRONT_DIR%"" run dev"

echo [FRONT] Sincronizando UI...
call :wait_port %FRONTEND_PORT% 60
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Interface falhou ao abrir.
    goto :fim_erro
)
echo [FRONT] UI Online.

:: ============================================================
:: CONCLUSÃO
:: ============================================================
echo.
echo [OK] JARVIS 5.0 ONLINE.
echo  Backend:   http://127.0.0.1:%BACKEND_PORT%
echo  Frontend:   http://127.0.0.1:%FRONTEND_PORT%
echo.
echo Pressione qualquer tecla para fechar este launcher...
pause >nul
exit /b 0

:: ============================================================
:: FUNÇÕES DE SUPORTE
:: ============================================================
:kill_port
set "PORT=%~1"
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
    if not "%%P"=="0" (
        echo [CLEAN] Encerrando PID %%P na porta %PORT%...
        taskkill /PID %%P /F >nul 2>&1
    )
)
exit /b 0

:wait_http
set "URL=%~1"
set "MAX_TRIES=%~2"
set /a TRY=0
:wait_http_loop
set /a TRY+=1
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; try { $r=Invoke-WebRequest -UseBasicParsing -Uri '%URL%' -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if %ERRORLEVEL% EQU 0 exit /b 0
if %TRY% GEQ %MAX_TRIES% exit /b 1
ping -n 1 127.0.0.1 >nul
goto :wait_http_loop

:wait_port
set "PORT=%~1"
set "MAX_TRIES=%~2"
set /a TRY=0
:wait_port_loop
set /a TRY+=1
netstat -ano | findstr /R /C:":%PORT% .*LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 exit /b 0
if %TRY% GEQ %MAX_TRIES% exit /b 1
ping -n 1 127.0.0.1 >nul
goto :wait_port_loop

:fim_erro
echo.
echo [FALHA] Erro crítico na inicialização do JARVIS.
echo Verifique as janelas de log para mais detalhes.
pause
exit /b 1
