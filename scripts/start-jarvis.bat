@echo off
TITLE JARVIS 5.0 - OMEGA ADAPTIVE ORCHESTRATOR
SETLOCAL EnableExtensions EnableDelayedExpansion

:: ============================================================
:: CONFIGURAÇÕES BASE
:: ============================================================
cd /d "%~dp0.."
SET "ROOT=%~dp0..\"
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

echo [OMEGA] Iniciando Protocolo de Boot Adaptativo...

:: ------------------------------------------------------------
:: 1. SONDAGEM DE HARDWARE (HARDWARE INTELLIGENCE)
:: ------------------------------------------------------------
echo [Sonda] Analisando arquitetura do sistema...

SET "JARVIS_MODE=COMPAT"
SET "JARVIS_AI_DEVICE=cpu"
SET "JARVIS_WHISPER_MODEL=tiny"
SET "JARVIS_DISABLE_CAMERA=false"

:: Check for NVIDIA GPU
nvidia-smi >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [HW] NVIDIA GPU Detectada.
    SET "JARVIS_AI_DEVICE=cuda"
    SET "JARVIS_MODE=PERFORMANCE"

    :: Check VRAM for 1050Ti (4GB) vs High End
    for /f "tokens=4" %%i in ('nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits') do set "VRAM=%%i"
    if !VRAM! LSS 6000 (
        echo [HW] Low VRAM detected (!VRAM! MB). Enabling BALANCED Mode.
        SET "JARVIS_MODE=BALANCED"
    )
) else (
    :: Check for Intel Iris Xe / Arc
    wmic path win32_VideoController get name | findstr /I "Intel Iris Intel Arc" >nul
    if !ERRORLEVEL! EQU 0 (
        echo [HW] Intel Iris Xe/Arc Detectada.
        SET "JARVIS_AI_DEVICE=openvino"
        SET "JARVIS_MODE=INTEL_OPT"
        SET "JARVIS_DISABLE_CAMERA=true"
        echo [HW] Ativando Modo Foco (Economia de CPU).
    ) else (
        echo [HW] Hardware Genérico detectado. Modo Compatibilidade ativo.
    )
)

echo [Sonda] Perfil Definido: !JARVIS_MODE! (Device: !JARVIS_AI_DEVICE!)

:: ------------------------------------------------------------
:: 2. SANITIZAÇÃO AMBIENTAL (SELF-HEALING)
:: ------------------------------------------------------------
echo [Clean] Eliminando processos zumbis e locks...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1
if exist "%ROOT%.jarvis.lock" del /f /q "%ROOT%.jarvis.lock"

echo [Clean] Liberando portas de comunicação...
call :kill_port %BACKEND_PORT%
call :kill_port %FRONTEND_PORT%
call :kill_port 3001
call :kill_port 8001

:: ------------------------------------------------------------
:: 3. SINCRONIA DE DEPENDÊNCIAS (VENV INTEGRITY)
:: ------------------------------------------------------------
if not exist "%VENV_ACT%" (
    echo [SYS] Ambiente virtual ausente. Criando...
    python -m venv "%VENV_DIR%"
    if !ERRORLEVEL! NEQ 0 goto :fim_erro
)

call "%VENV_ACT%"
if !ERRORLEVEL! NEQ 0 goto :fim_erro

:: Integrity Check: Verify if core packages are actually importable
"%PYTHON_EXE%" -c "import torch; import uvicorn" >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo [SYS] Corrupção detectada no venv. Reparando dependências...
    "%PYTHON_EXE%" -m pip install --upgrade pip setuptools wheel
    if !ERRORLEVEL! NEQ 0 goto :fim_erro

    :: Instala webrtcvad-wheels antes do resemblyzer (dependência de compilação no Windows)
    "%PYTHON_EXE%" -m pip install webrtcvad-wheels
    "%PYTHON_EXE%" -m pip install resemblyzer --no-deps

    :: Instala PyTorch com suporte CUDA se GPU NVIDIA disponível
    if "!JARVIS_AI_DEVICE!"=="cuda" (
        echo [SYS] GPU NVIDIA detectada. Instalando PyTorch com CUDA...
        "%PYTHON_EXE%" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
    ) else (
        echo [SYS] CPU mode. Instalando PyTorch CPU...
        "%PYTHON_EXE%" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
    )

    "%PYTHON_EXE%" -m pip install -r "%BACK_DIR%\app\requirements.txt" --ignore-requires-python
    if !ERRORLEVEL! NEQ 0 goto :fim_erro
) else (
    echo [SYS] Integridade do venv validada.
)

:: ------------------------------------------------------------
:: 4. LANÇAMENTO DO CORE (ADAPTIVE BOOT)
:: ------------------------------------------------------------
echo [BACK] Lançando Core do JARVIS (Mode: !JARVIS_MODE!)...
start "JARVIS_BACKEND" /D "%BACK_DIR%" cmd /k "call \"%VENV_ACT%\" && set JARVIS_AI_DEVICE=!JARVIS_AI_DEVICE! && set JARVIS_MODE=!JARVIS_MODE! && set JARVIS_WHISPER_MODEL=!JARVIS_WHISPER_MODEL! && \"%PYTHON_EXE%\" -m uvicorn app.main:app --host 127.0.0.1 --port %BACKEND_PORT% --reload --log-level info"

echo [BACK] Aguardando sincronização do sistema...
call :wait_http "http://127.0.0.1:%BACKEND_PORT%/health" 30
if !ERRORLEVEL! NEQ 0 (
    echo [ERRO] Core do JARVIS falhou ao iniciar.
    goto :fim_erro
)

:: ------------------------------------------------------------
:: 5. LANÇAMENTO DA UI
:: ------------------------------------------------------------
echo [FRONT] Lançando interface holográfica...
start "JARVIS_FRONTEND" /D "%FRONT_DIR%" cmd /k "set PORT=%FRONTEND_PORT% && pnpm run dev"

echo [FRONT] Sincronizando UI...
call :wait_port %FRONTEND_PORT% 60
if !ERRORLEVEL! NEQ 0 (
    echo [ERRO] Interface falhou ao abrir.
    goto :fim_erro
)

echo.
echo [OK] JARVIS 5.0 OMEGA ONLINE.
echo Perfil: !JARVIS_MODE! | Device: !JARVIS_AI_DEVICE!
echo Backend:  http://127.0.0.1:%BACKEND_PORT%
echo Frontend: http://127.0.0.1:%FRONTEND_PORT%
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
set "PORT=%~1"
if "%PORT%"=="" exit /b 0
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /C:":%PORT% "' ) do (
    if not "%%P"=="0" (
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
if !ERRORLEVEL! EQU 0 exit /b 0
if !TRY! GEQ %MAX_TRIES% exit /b 1
timeout /t 1 >nul
goto :wait_http_loop

:wait_port
set "PORT=%~1"
set "MAX_TRIES=%~2"
set /a TRY=0
:wait_port_loop
set /a TRY+=1
netstat -ano | findstr /C:":%PORT%" >nul 2>&1
if !ERRORLEVEL! EQU 0 exit /b 0
if !TRY! GEQ %MAX_TRIES% exit /b 1
timeout /t 1 >nul
goto :wait_port_loop

:fim_erro
echo.
echo [FALHA] Erro crítico na inicialização do JARVIS.
pause
exit /b 1
