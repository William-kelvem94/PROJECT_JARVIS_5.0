@echo off
TITLE JARVIS 5.0 - OMEGA ADAPTIVE ORCHESTRATOR
SETLOCAL EnableExtensions EnableDelayedExpansion

:: ============================================================
:: CONFIGURAÇÕES BASE — caminhos relativos à raiz do projeto
:: ============================================================
cd /d "%~dp0"
SET "ROOT=%~dp0"
SET "BACK_DIR=%ROOT%backend"
SET "FRONT_DIR=%ROOT%frontend"
SET "VENV_DIR=%ROOT%.venv"
SET "VENV_ACT=%VENV_DIR%\Scripts\activate.bat"
SET "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
SET "PYTHONOPTIMIZE=1"
SET "NODE_OPTIONS=--max-old-space-size=2048"

SET "BACKEND_PORT=8000"
SET "FRONTEND_PORT=3000"
call :load_env_ports

echo.
echo ================================================================
echo   JARVIS 5.0 ^| OMEGA ADAPTIVE ORCHESTRATOR
echo ================================================================
echo [OMEGA] Raiz do projeto: %ROOT%
echo [OMEGA] Iniciando Protocolo de Boot Adaptativo...
echo.

:: ------------------------------------------------------------
:: 1. VERIFICAÇÃO DE PRÉ-REQUISITOS
:: ------------------------------------------------------------
echo [PRE] Verificando Python do sistema...
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado no PATH.
    echo        Instale o Python 3.11+ e adicione ao PATH do sistema.
    goto :fim_erro
)
python --version 2>&1

echo [PRE] Verificando Node.js...
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Node.js nao encontrado. Frontend nao sera iniciado.
    SET "SKIP_FRONTEND=1"
) else (
    node --version 2>&1
)

echo [PRE] Verificando pnpm...
where pnpm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] pnpm nao encontrado. Tentando npm...
    SET "PKG_MANAGER=npm"
) else (
    SET "PKG_MANAGER=pnpm"
)

:: ------------------------------------------------------------
:: 2. SONDAGEM DE HARDWARE (HARDWARE INTELLIGENCE)
:: ------------------------------------------------------------
echo.
echo [Sonda] Analisando arquitetura do sistema...

SET "JARVIS_MODE=COMPAT"
SET "JARVIS_AI_DEVICE=cpu"
SET "JARVIS_WHISPER_MODEL=tiny"
SET "JARVIS_DISABLE_CAMERA=false"

nvidia-smi >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [HW] NVIDIA GPU Detectada.
    SET "JARVIS_AI_DEVICE=cuda"
    SET "JARVIS_MODE=PERFORMANCE"
    for /f "tokens=4" %%i in ('nvidia-smi --query-gpu^=memory.total --format^=csv,noheader,nounits 2^>nul') do set "VRAM=%%i"
    if defined VRAM (
        if !VRAM! LSS 6000 (
            echo [HW] VRAM baixa (!VRAM! MB). Modo BALANCED ativo.
            SET "JARVIS_MODE=BALANCED"
        )
    )
) else (
    wmic path win32_VideoController get name 2>nul | findstr /I "Intel Iris Intel Arc" >nul
    if !ERRORLEVEL! EQU 0 (
        echo [HW] Intel Iris Xe/Arc Detectada. Modo INTEL_OPT ativo.
        SET "JARVIS_AI_DEVICE=openvino"
        SET "JARVIS_MODE=INTEL_OPT"
        SET "JARVIS_DISABLE_CAMERA=true"
    ) else (
        echo [HW] Hardware Generico. Modo COMPAT ativo.
    )
)
echo [Sonda] Perfil: !JARVIS_MODE! ^| Device: !JARVIS_AI_DEVICE!

:: ------------------------------------------------------------
:: 3. SANITIZAÇÃO AMBIENTAL (SELF-HEALING)
:: ------------------------------------------------------------
echo.
echo [Clean] Eliminando processos zumbis...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1
if exist "%ROOT%.jarvis.lock" del /f /q "%ROOT%.jarvis.lock"

echo [Clean] Liberando portas %BACKEND_PORT% e %FRONTEND_PORT%...
call :kill_port %BACKEND_PORT%
call :kill_port %FRONTEND_PORT%
call :kill_port 3001
call :kill_port 8001

:: ------------------------------------------------------------
:: 4. AMBIENTE VIRTUAL PYTHON (VENV)
:: ------------------------------------------------------------
echo.
echo [VENV] Verificando ambiente virtual em: %VENV_DIR%

if not exist "%VENV_ACT%" (
    echo [VENV] Ambiente virtual ausente. Criando com Python do sistema...
    python -m venv "%VENV_DIR%"
    if !ERRORLEVEL! NEQ 0 (
        echo [ERRO] Falha ao criar ambiente virtual.
        goto :fim_erro
    )
    echo [VENV] Ambiente virtual criado com sucesso.
)

echo [VENV] Ativando ambiente virtual...
call "%VENV_ACT%"
if !ERRORLEVEL! NEQ 0 (
    echo [ERRO] Falha ao ativar ambiente virtual.
    goto :fim_erro
)

:: Verificar integridade: uvicorn e fastapi devem estar presentes
"%PYTHON_EXE%" -c "import uvicorn, fastapi" >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo [VENV] Dependencias ausentes. Instalando...

    "%PYTHON_EXE%" -m pip install --upgrade pip setuptools wheel --quiet

    :: PyTorch: CUDA se GPU NVIDIA, CPU caso contrário
    if "!JARVIS_AI_DEVICE!"=="cuda" (
        echo [VENV] Instalando PyTorch com suporte CUDA 12.1...
        "%PYTHON_EXE%" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --quiet
    ) else (
        echo [VENV] Instalando PyTorch CPU...
        "%PYTHON_EXE%" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --quiet
    )

    :: webrtcvad-wheels ANTES do resemblyzer (dependência de compilação no Windows)
    "%PYTHON_EXE%" -m pip install webrtcvad-wheels --quiet
    "%PYTHON_EXE%" -m pip install resemblyzer --no-deps --quiet

    echo [VENV] Instalando requirements.txt...
    "%PYTHON_EXE%" -m pip install -r "%BACK_DIR%\app\requirements.txt" --ignore-requires-python --quiet
    if !ERRORLEVEL! NEQ 0 (
        echo [ERRO] Falha ao instalar dependencias.
        goto :fim_erro
    )
    echo [VENV] Dependencias instaladas com sucesso.
) else (
    echo [VENV] Ambiente virtual validado.
)

:: ------------------------------------------------------------
:: 5. VALIDAÇÃO DO BACKEND (IMPORT CHECK)
:: ------------------------------------------------------------
echo.
echo [CHECK] Validando imports criticos do backend...
"%PYTHON_EXE%" -c "import fastapi, uvicorn, loguru; print('[CHECK] Core OK')" 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo [ERRO] Imports criticos falharam.
    goto :fim_erro
)

:: ------------------------------------------------------------
:: 6. LANÇAMENTO DO BACKEND
:: ------------------------------------------------------------
echo.
echo [BACK] Lançando JARVIS Core ^(Mode: !JARVIS_MODE!^)...

if not exist "%BACK_DIR%" (
    echo [ERRO] Diretorio backend nao encontrado: %BACK_DIR%
    goto :fim_erro
)

start "JARVIS_BACKEND" /D "%BACK_DIR%" cmd /k ^
    "title JARVIS - Backend && ^
     call ""%VENV_ACT%"" && ^
     set JARVIS_AI_DEVICE=!JARVIS_AI_DEVICE! && ^
     set JARVIS_MODE=!JARVIS_MODE! && ^
     set JARVIS_WHISPER_MODEL=!JARVIS_WHISPER_MODEL! && ^
     set JARVIS_DISABLE_CAMERA=!JARVIS_DISABLE_CAMERA! && ^
     echo [BACK] Iniciando uvicorn na porta %BACKEND_PORT%... && ^
     ""%PYTHON_EXE%"" -m uvicorn app.main:app --host 127.0.0.1 --port %BACKEND_PORT% --reload --log-level info"

echo [BACK] Aguardando backend responder em /health (max 45s)...
call :wait_http "http://127.0.0.1:%BACKEND_PORT%/health" 45
if !ERRORLEVEL! NEQ 0 (
    echo.
    echo [ERRO] Backend nao respondeu em 45 segundos.
    echo        Verifique a janela "JARVIS - Backend" para detalhes do erro.
    goto :fim_erro
)
echo [BACK] Backend online em http://127.0.0.1:%BACKEND_PORT%

:: ------------------------------------------------------------
:: 7. LANÇAMENTO DO FRONTEND
:: ------------------------------------------------------------
if defined SKIP_FRONTEND (
    echo [FRONT] Node.js ausente. Pulando frontend.
    goto :fim_ok
)

echo.
echo [FRONT] Lançando interface em http://127.0.0.1:%FRONTEND_PORT%...

if not exist "%FRONT_DIR%" (
    echo [AVISO] Diretorio frontend nao encontrado: %FRONT_DIR%
    goto :fim_ok
)

start "JARVIS_FRONTEND" /D "%FRONT_DIR%" cmd /k ^
    "title JARVIS - Frontend && ^
     set PORT=%FRONTEND_PORT% && ^
     echo [FRONT] Iniciando Next.js na porta %FRONTEND_PORT%... && ^
     %PKG_MANAGER% run dev"

echo [FRONT] Aguardando frontend responder (max 60s)...
call :wait_port %FRONTEND_PORT% 60
if !ERRORLEVEL! NEQ 0 (
    echo [AVISO] Frontend ainda nao respondeu. Pode estar compilando...
) else (
    echo [FRONT] Frontend online em http://127.0.0.1:%FRONTEND_PORT%
)

:fim_ok
echo.
echo ================================================================
echo   JARVIS 5.0 OMEGA ONLINE
echo   Perfil : !JARVIS_MODE! ^| Device: !JARVIS_AI_DEVICE!
echo   Backend : http://127.0.0.1:%BACKEND_PORT%
echo   Frontend: http://127.0.0.1:%FRONTEND_PORT%
echo   Docs API: http://127.0.0.1:%BACKEND_PORT%/docs
echo ================================================================
echo.
pause
exit /b 0

:: ============================================================
:: FUNÇÕES DE SUPORTE
:: ============================================================

:load_env_ports
if exist "%ROOT%.env" (
    for /f "usebackq tokens=1,2 delims==" %%A in (`findstr /R /C:"^BACKEND_PORT=" /C:"^FRONTEND_PORT=" "%ROOT%.env"`) do (
        if /I "%%A"=="BACKEND_PORT" SET "BACKEND_PORT=%%B"
        if /I "%%A"=="FRONTEND_PORT" SET "FRONTEND_PORT=%%B"
    )
)
exit /b 0

:kill_port
set "_KP=%~1"
if "%_KP%"=="" exit /b 0
for /f "tokens=5" %%P in ('netstat -ano 2^>nul ^| findstr /C:":%_KP% "') do (
    if not "%%P"=="0" taskkill /PID %%P /F >nul 2>&1
)
exit /b 0

:wait_http
set "_URL=%~1"
set "_MAX=%~2"
set /a _TRY=0
:_wh_loop
set /a _TRY+=1
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p='SilentlyContinue';$ProgressPreference=$p; try { $r=Invoke-WebRequest -UseBasicParsing -Uri '%_URL%' -TimeoutSec 2; exit ($r.StatusCode -ne 200) } catch { exit 1 }" >nul 2>&1
if !ERRORLEVEL! EQU 0 exit /b 0
if !_TRY! GEQ %_MAX% exit /b 1
timeout /t 1 /nobreak >nul
goto :_wh_loop

:wait_port
set "_WP=%~1"
set "_WM=%~2"
set /a _WT=0
:_wp_loop
set /a _WT+=1
netstat -ano 2>nul | findstr /C:":%_WP% " >nul
if !ERRORLEVEL! EQU 0 exit /b 0
if !_WT! GEQ %_WM% exit /b 1
timeout /t 1 /nobreak >nul
goto :_wp_loop

:fim_erro
echo.
echo ================================================================
echo   [FALHA] Erro critico na inicializacao do JARVIS.
echo   Verifique as mensagens acima para identificar o problema.
echo ================================================================
echo.
pause
exit /b 1
