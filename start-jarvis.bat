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
REM 1. DETECÇÃO AGRESSIVA DE PYTHON
REM ============================================================
echo [PRE] Buscando Python no sistema...

set "PYTHON_FOUND=0"
set "PYTHON_EXE="

REM Tentar 1: where (PATH)
where python >nul 2>&1
if !errorlevel! equ 0 (
    set "PYTHON_FOUND=1"
    for /f "tokens=*" %%i in ('where python') do set "PYTHON_EXE=%%i"
)

REM Tentar 2: Program Files (instalação padrão Windows)
if !PYTHON_FOUND! equ 0 (
    for /d %%d in ("C:\Program Files\Python3*") do (
        if exist "%%d\python.exe" (
            set "PYTHON_FOUND=1"
            set "PYTHON_EXE=%%d\python.exe"
            goto :python_found_in_files
        )
    )
)

REM Tentar 3: Program Files (x86)
if !PYTHON_FOUND! equ 0 (
    for /d %%d in ("C:\Program Files (x86)\Python3*") do (
        if exist "%%d\python.exe" (
            set "PYTHON_FOUND=1"
            set "PYTHON_EXE=%%d\python.exe"
            goto :python_found_in_files
        )
    )
)

REM Tentar 4: AppData (user installation)
if !PYTHON_FOUND! equ 0 (
    if exist "%APPDATA%\Python" (
        for /d %%d in ("%APPDATA%\Python\Python3*") do (
            if exist "%%d\python.exe" (
                set "PYTHON_FOUND=1"
                set "PYTHON_EXE=%%d\python.exe"
                goto :python_found_in_files
            )
        )
    )
)

REM Tentar 5: LocalAppData (Microsoft Store Python)
if !PYTHON_FOUND! equ 0 (
    if exist "%LOCALAPPDATA%\Microsoft\WindowsApps" (
        if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
            set "PYTHON_FOUND=1"
            set "PYTHON_EXE=%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe"
            goto :python_found_in_files
        )
    )
)

:python_found_in_files

REM Se encontrou, adicionar ao PATH
if !PYTHON_FOUND! equ 0 (
    echo [PRE] Python nao encontrado em nenhuma localizacao.
    goto :instalar_python
)

echo [PRE] Python encontrado: !PYTHON_EXE!
"!PYTHON_EXE!" --version 2>&1

REM Adicionar ao PATH se não estiver lá
setx PATH "%PATH%;!PYTHON_EXE:..\python.exe=!\Scripts" >nul 2>&1
echo [PRE] Adicionado ao PATH do sistema.

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
REM 3. FALLBACK: EXECUÇÃO INTEGRADA
REM ============================================================
echo [OMEGA] Iniciando Protocolo de Boot Adaptativo...
echo.

REM Configurações base
set "BACK_DIR=%ROOT%backend"
set "FRONT_DIR=%ROOT%frontend"
set "VENV_DIR=%ROOT%.venv"
set "VENV_ACT=%VENV_DIR%\Scripts\activate.bat"
set "PYTHON_VENV=%VENV_DIR%\Scripts\python.exe"
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
    "!PYTHON_EXE!" -m venv "%VENV_DIR%"
    if !errorlevel! neq 0 (
        echo [ERRO] Falha ao criar ambiente virtual.
        goto :fim_erro
    )
    echo [VENV] Ambiente virtual criado com sucesso.
)

echo [VENV] Ativando ambiente virtual...
call "%VENV_ACT%"

REM Verificar integridade: uvicorn e fastapi devem estar presentes
"!PYTHON_VENV!" -c "import uvicorn, fastapi" >nul 2>&1
if !errorlevel! neq 0 (
    echo [VENV] Dependências ausentes. Instalando...

    echo [VENV] Atualizando pip/setuptools/wheel...
    "!PYTHON_VENV!" -m pip install --upgrade pip setuptools wheel --quiet

    echo [VENV] Instalando PyTorch...
    if "!JARVIS_AI_DEVICE!"=="cuda" (
        echo [VENV] ... com suporte CUDA 12.1
        "!PYTHON_VENV!" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --quiet
    ) else (
        echo [VENV] ... modo CPU
        "!PYTHON_VENV!" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --quiet
    )

    echo [VENV] Instalando pacotes de áudio (webrtcvad-wheels, resemblyzer)...
    "!PYTHON_VENV!" -m pip install webrtcvad-wheels --quiet
    "!PYTHON_VENV!" -m pip install resemblyzer --no-deps --quiet

    echo [VENV] Instalando requirements.txt...
    if not exist "%BACK_DIR%\app\requirements.txt" (
        echo [ERRO] requirements.txt não encontrado em %BACK_DIR%\app\
        goto :fim_erro
    )
    "!PYTHON_VENV!" -m pip install -r "%BACK_DIR%\app\requirements.txt" --ignore-requires-python --quiet
    if !errorlevel! neq 0 (
        echo [ERRO] Falha ao instalar dependências de requirements.txt
        goto :fim_erro
    )

    echo [VENV] Validando imports críticos...
    "!PYTHON_VENV!" -c "import fastapi, uvicorn, loguru, torch, chromadb, sentence_transformers" 2>&1
    if !errorlevel! neq 0 (
        echo [AVISO] Alguns imports falharam, mas continuando...
    ) else (
        echo [VENV] Todos os imports validados!
    )

    echo [VENV] Dependências instaladas com sucesso!
) else (
    echo [VENV] Ambiente virtual validado. Dependências OK.
)

REM ============================================================
REM 7. LANÇAMENTO DO BACKEND
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
     "!PYTHON_VENV!" -m uvicorn app.main:app --host 127.0.0.1 --port %BACKEND_PORT% --reload --log-level info"

echo [BACK] Aguardando backend responder em /health ^(max 120s^)...
call :wait_http "http://127.0.0.1:%BACKEND_PORT%/health" 120
if !errorlevel! neq 0 (
    echo.
    echo [ERRO] Backend não respondeu em 120 segundos.
    echo        Verifique a janela "JARVIS - Backend" para detalhes.
    goto :fim_erro
)
echo [BACK] Backend online em http://127.0.0.1:%BACKEND_PORT%

REM ============================================================
REM 8. LANÇAMENTO DO FRONTEND (OPCIONAL)
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

:instalar_python
echo.
echo ================================================================
echo   INSTALANDO PYTHON 3.11 AUTOMATICAMENTE
echo ================================================================
echo.

REM Tentar instalar com Chocolatey
where choco >nul 2>&1
if !errorlevel! equ 0 (
    echo [SYS] Chocolatey detectado. Instalando Python 3.11...
    choco install python311 -y --force
    if !errorlevel! equ 0 (
        echo [SYS] Python instalado com sucesso via Chocolatey!
        REM Reiniciar script
        call start-jarvis.bat
        exit /b 0
    )
)

REM Se Chocolatey falhar, tentar instalador do site
echo [SYS] Baixando Python 3.11 installer...
powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%TEMP%\python-install.exe'" >nul 2>&1

if exist "%TEMP%\python-install.exe" (
    echo [SYS] Executando instalador do Python...
    REM Instalar com opção de adicionar ao PATH
    "%TEMP%\python-install.exe" /quiet InstallAllUsers=1 PrependPath=1
    if !errorlevel! equ 0 (
        echo [SYS] Python instalado com sucesso!
        del "%TEMP%\python-install.exe"
        REM Aguardar um pouco e reiniciar
        timeout /t 3
        call start-jarvis.bat
        exit /b 0
    )
    del "%TEMP%\python-install.exe"
)

echo.
echo ================================================================
echo   [ERRO] Não foi possível instalar Python automaticamente
echo ================================================================
echo.
echo Instalação manual necessária:
echo   1. Acesse: https://python.org/downloads
echo   2. Baixe Python 3.11 ou superior
echo   3. IMPORTANTE: Marque "Add Python to PATH" durante instalação
echo   4. Reinicie o PC
echo   5. Execute start-jarvis.bat novamente
echo.
pause
exit /b 1

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

:fim_erro
echo.
echo ================================================================
echo   [FALHA] Erro crítico na inicialização do JARVIS
echo ================================================================
echo.
echo Verifique os logs para detalhes do erro.
echo.
pause
exit /b 1
