@echo off
REM JARVIS 5.0 - OMEGA ADAPTIVE ORCHESTRATOR
REM UTF-8 with BOM
setlocal enableextensions enabledelayedexpansion

cd /d "%~dp0"
set "ROOT=%~dp0"

echo.
echo ================================================================
echo   JARVIS 5.0 - OMEGA ADAPTIVE ORCHESTRATOR
echo ================================================================
echo [OMEGA] Raiz do projeto: %ROOT%
echo.

REM ============================================================
REM 1. VERIFICAÇÃO E INSTALAÇÃO DE PYTHON (CRÍTICO)
REM ============================================================
echo [PRE] Verificando Python do sistema...
where python >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo [AVISO] Python NAO encontrado no PATH do sistema.
    echo.
    echo Opções:
    echo   1. Instalar Python 3.11+ manualmente: https://python.org/downloads
    echo   2. Tentar instalação automática via Chocolatey (se disponível)
    echo.

    REM Tentar instalar via Chocolatey
    where choco >nul 2>&1
    if !errorlevel! equ 0 (
        echo [SYS] Chocolatey detectado. Tentando instalar Python...
        choco install python311 -y
        if !errorlevel! neq 0 (
            echo [ERRO] Falha ao instalar Python via Chocolatey.
            goto :python_not_found
        )
        echo [SYS] Python instalado. Reinicie este script.
        pause
        exit /b 1
    ) else (
        goto :python_not_found
    )
)

REM Detectar versão do Python
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo [PRE] Python detectado: %PYTHON_VERSION%

REM ============================================================
REM 2. USAR ARQUITETURA MODULAR (SE DISPONÍVEL)
REM ============================================================
if exist "%ROOT%scripts\common-functions.bat" (
    echo [OMEGA] Usando arquitetura modular Split Batch Files...
    echo.

    REM Executar scripts em sequência
    call "%ROOT%scripts\check-prerequisites.bat"
    if !errorlevel! neq 0 goto :fim_erro

    call "%ROOT%scripts\detect-hardware.bat"
    if !errorlevel! neq 0 goto :fim_erro

    call "%ROOT%scripts\setup-venv.bat"
    if !errorlevel! neq 0 goto :fim_erro

    call "%ROOT%scripts\launch-backend.bat"
    if !errorlevel! neq 0 goto :fim_erro

    call "%ROOT%scripts\launch-frontend.bat"
    REM Frontend é opcional, não falha

    goto :fim_ok
)

REM ============================================================
REM 3. FALLBACK: EXECUÇÃO INTEGRADA (se scripts modulares não existem)
REM ============================================================
echo [OMEGA] Iniciando Protocolo de Boot Adaptativo...
echo.

REM Configurações base
set "BACK_DIR=%ROOT%backend"
set "FRONT_DIR=%ROOT%frontend"
set "VENV_DIR=%ROOT%.venv"
set "VENV_ACT=%VENV_DIR%\Scripts\activate.bat"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "PYTHONOPTIMIZE=1"
set "NODE_OPTIONS=--max-old-space-size=2048"
set "BACKEND_PORT=8000"
set "FRONTEND_PORT=3000"

REM Carregar portas do .env
if exist "%ROOT%.env" (
    for /f "usebackq tokens=1,2 delims==" %%A in (`findstr /R /C:"^BACKEND_PORT=" /C:"^FRONTEND_PORT=" "%ROOT%.env"`) do (
        if /I "%%A"=="BACKEND_PORT" set "BACKEND_PORT=%%B"
        if /I "%%A"=="FRONTEND_PORT" set "FRONTEND_PORT=%%B"
    )
)

REM ============================================================
REM 4. SONDAGEM DE HARDWARE
REM ============================================================
echo [Sonda] Analisando arquitetura do sistema...
set "JARVIS_MODE=COMPAT"
set "JARVIS_AI_DEVICE=cpu"
set "JARVIS_WHISPER_MODEL=tiny"
set "JARVIS_DISABLE_CAMERA=false"

nvidia-smi >nul 2>&1
if !errorlevel! equ 0 (
    echo [HW] NVIDIA GPU Detectada.
    set "JARVIS_AI_DEVICE=cuda"
    set "JARVIS_MODE=PERFORMANCE"
    for /f "tokens=4" %%i in ('nvidia-smi --query-gpu^=memory.total --format^=csv,noheader,nounits 2^>nul') do set "VRAM=%%i"
    if defined VRAM (
        if !VRAM! lss 6000 (
            echo [HW] VRAM baixa ^(!VRAM! MB^). Modo BALANCED ativo.
            set "JARVIS_MODE=BALANCED"
        )
    )
) else (
    wmic path win32_VideoController get name 2>nul | findstr /I "Intel Iris Intel Arc" >nul
    if !errorlevel! equ 0 (
        echo [HW] Intel Iris Xe/Arc Detectada. Modo INTEL_OPT ativo.
        set "JARVIS_AI_DEVICE=openvino"
        set "JARVIS_MODE=INTEL_OPT"
        set "JARVIS_DISABLE_CAMERA=true"
    ) else (
        echo [HW] Hardware Genérico. Modo COMPAT ativo.
    )
)
echo [Sonda] Perfil: !JARVIS_MODE! ^| Device: !JARVIS_AI_DEVICE!

REM ============================================================
REM 5. SANITIZAÇÃO AMBIENTAL
REM ============================================================
echo.
echo [Clean] Eliminando processos zumbis...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1
if exist "%ROOT%.jarvis.lock" del /f /q "%ROOT%.jarvis.lock"

echo [Clean] Liberando portas %BACKEND_PORT%, %FRONTEND_PORT%, 3001, 8001...
call :kill_port %BACKEND_PORT%
call :kill_port %FRONTEND_PORT%
call :kill_port 3001
call :kill_port 8001

REM ============================================================
REM 6. AMBIENTE VIRTUAL PYTHON (VENV)
REM ============================================================
echo.
echo [VENV] Verificando ambiente virtual em: %VENV_DIR%

if not exist "%VENV_ACT%" (
    echo [VENV] Ambiente virtual ausente. Criando...
    python -m venv "%VENV_DIR%"
    if !errorlevel! neq 0 (
        echo [ERRO] Falha ao criar ambiente virtual.
        goto :fim_erro
    )
    echo [VENV] Ambiente virtual criado com sucesso.
)

echo [VENV] Ativando ambiente virtual...
call "%VENV_ACT%"

REM Verificar integridade: uvicorn e fastapi devem estar presentes
"%PYTHON_EXE%" -c "import uvicorn, fastapi" >nul 2>&1
if !errorlevel! neq 0 (
    echo [VENV] Dependências ausentes. Instalando...

    "%PYTHON_EXE%" -m pip install --upgrade pip setuptools wheel --quiet

    REM PyTorch: CUDA se GPU NVIDIA, CPU caso contrário
    if "!JARVIS_AI_DEVICE!"=="cuda" (
        echo [VENV] Instalando PyTorch com suporte CUDA 12.1...
        "%PYTHON_EXE%" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --quiet
    ) else (
        echo [VENV] Instalando PyTorch CPU...
        "%PYTHON_EXE%" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --quiet
    )

    REM webrtcvad-wheels ANTES do resemblyzer (dependência Windows)
    echo [VENV] Instalando pacotes de áudio...
    "%PYTHON_EXE%" -m pip install webrtcvad-wheels --quiet
    "%PYTHON_EXE%" -m pip install resemblyzer --no-deps --quiet

    echo [VENV] Instalando requirements.txt...
    "%PYTHON_EXE%" -m pip install -r "%BACK_DIR%\app\requirements.txt" --ignore-requires-python --quiet
    if !errorlevel! neq 0 (
        echo [ERRO] Falha ao instalar dependências.
        goto :fim_erro
    )
    echo [VENV] Dependências instaladas com sucesso.
) else (
    echo [VENV] Ambiente virtual validado.
)

REM ============================================================
REM 7. VALIDAÇÃO DO BACKEND
REM ============================================================
echo.
echo [CHECK] Validando imports críticos do backend...
"%PYTHON_EXE%" -c "import fastapi, uvicorn, loguru, torch; print('[CHECK] Core imports validados')" 2>&1
if !errorlevel! neq 0 (
    echo [ERRO] Imports críticos falharam.
    goto :fim_erro
)

REM ============================================================
REM 8. LANÇAMENTO DO BACKEND
REM ============================================================
echo.
echo [BACK] Lançando JARVIS Core ^(Mode: !JARVIS_MODE!^)...

if not exist "%BACK_DIR%" (
    echo [ERRO] Diretório backend não encontrado: %BACK_DIR%
    goto :fim_erro
)

start "JARVIS_BACKEND" /D "%BACK_DIR%" cmd /k ^
    "title JARVIS - Backend && ^
     call "%VENV_ACT%" && ^
     set JARVIS_AI_DEVICE=!JARVIS_AI_DEVICE! && ^
     set JARVIS_MODE=!JARVIS_MODE! && ^
     set JARVIS_WHISPER_MODEL=!JARVIS_WHISPER_MODEL! && ^
     set JARVIS_DISABLE_CAMERA=!JARVIS_DISABLE_CAMERA! && ^
     echo [BACK] Iniciando uvicorn na porta %BACKEND_PORT%... && ^
     "%PYTHON_EXE%" -m uvicorn app.main:app --host 127.0.0.1 --port %BACKEND_PORT% --reload --log-level info"

echo [BACK] Aguardando backend responder em /health ^(max 90s^)...
call :wait_http "http://127.0.0.1:%BACKEND_PORT%/health" 90
if !errorlevel! neq 0 (
    echo.
    echo [ERRO] Backend não respondeu em 90 segundos.
    echo        Verifique a janela "JARVIS - Backend" para detalhes do erro.
    goto :fim_erro
)
echo [BACK] Backend online em http://127.0.0.1:%BACKEND_PORT%

REM ============================================================
REM 9. LANÇAMENTO DO FRONTEND (OPCIONAL)
REM ============================================================
where node >nul 2>&1
if !errorlevel! neq 0 (
    echo [FRONT] Node.js não encontrado. Frontend será pulado.
    goto :fim_ok
)

where pnpm >nul 2>&1
if !errorlevel! neq 0 (
    where npm >nul 2>&1
    if !errorlevel! neq 0 (
        echo [FRONT] npm/pnpm não encontrados. Frontend será pulado.
        goto :fim_ok
    )
    set "PKG_MANAGER=npm"
) else (
    set "PKG_MANAGER=pnpm"
)

echo.
echo [FRONT] Lançando interface em http://127.0.0.1:%FRONTEND_PORT%...

if not exist "%FRONT_DIR%" (
    echo [AVISO] Diretório frontend não encontrado: %FRONT_DIR%
    goto :fim_ok
)

start "JARVIS_FRONTEND" /D "%FRONT_DIR%" cmd /k ^
    "title JARVIS - Frontend && ^
     set PORT=%FRONTEND_PORT% && ^
     echo [FRONT] Iniciando Next.js na porta %FRONTEND_PORT%... && ^
     %PKG_MANAGER% run dev"

echo [FRONT] Aguardando frontend responder ^(max 60s^)...
call :wait_port %FRONTEND_PORT% 60
if !errorlevel! neq 0 (
    echo [AVISO] Frontend ainda não respondeu. Pode estar compilando...
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

REM ============================================================
REM FUNÇÕES DE SUPORTE
REM ============================================================

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
if !errorlevel! equ 0 exit /b 0
if !_TRY! geq %_MAX% exit /b 1
timeout /t 1 /nobreak >nul
goto :_wh_loop

:wait_port
set "_WP=%~1"
set "_WM=%~2"
set /a _WT=0
:_wp_loop
set /a _WT+=1
netstat -ano 2>nul | findstr /C:":%_WP% " >nul
if !errorlevel! equ 0 exit /b 0
if !_WT! geq %_WM% exit /b 1
timeout /t 1 /nobreak >nul
goto :_wp_loop

:python_not_found
echo.
echo ================================================================
echo   [ERRO CRÍTICO] Python não encontrado no PATH
echo ================================================================
echo.
echo Para instalar Python:
echo   1. Acesse: https://python.org/downloads
echo   2. Baixe Python 3.11 ou superior
echo   3. IMPORTANTE: Marque "Add Python to PATH" durante instalação
echo   4. Reinicie este script após instalar Python
echo.
echo Alternativa com Chocolatey:
echo   choco install python311 -y
echo.
pause
exit /b 1

:fim_erro
echo.
echo ================================================================
echo   [FALHA] Erro crítico na inicialização do JARVIS.
echo   Verifique as mensagens acima para identificar o problema.
echo ================================================================
echo.
pause
exit /b 1
