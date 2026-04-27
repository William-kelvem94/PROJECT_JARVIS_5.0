@echo off
TITLE JARVIS 5.0 - Cold Start Launcher
SETLOCAL EnableExtensions

:: ============================================================
:: BASE
:: ============================================================
cd /d "%~dp0"
SET "ROOT=%~dp0"
SET "BACK_DIR=%ROOT%backend"
SET "FRONT_DIR=%ROOT%frontend"
SET "VENV_ACT=%ROOT%.venv\Scripts\activate.bat"
SET "PYTHONOPTIMIZE=1"
SET "NODE_OPTIONS=--max-old-space-size=2048"

echo [JARVIS] Inicializacao limpa (cold start)...
echo [INFO] ROOT=%ROOT%

:: ============================================================
:: HARDWARE
:: ============================================================
echo [JARVIS] Detectando hardware...
nvidia-smi >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [HW] GPU NVIDIA detectada - modo CUDA
    SET "JARVIS_AI_DEVICE=cuda"
    SET "JARVIS_WHISPER_MODEL=tiny"
) else (
    echo [HW] Sem GPU detectada - modo CPU
    SET "JARVIS_AI_DEVICE=cpu"
    SET "JARVIS_WHISPER_MODEL=base"
)
SET "JARVIS_CPU_THREADS=4"
echo %PROCESSOR_IDENTIFIER% | findstr /I "Intel" >nul && SET "JARVIS_CPU_THREADS=8"

:: ============================================================
:: PRE-REQUISITOS
:: ============================================================
echo [CHECK] Python...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado. Instale Python 3.10+.
    goto :fim_erro
)

echo [CHECK] Node.js...
node -v >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Node.js nao encontrado.
    goto :fim_erro
)

echo [CHECK] pnpm...
call pnpm -v >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [SYS] Instalando pnpm globalmente...
    call npm install -g pnpm
    if %ERRORLEVEL% NEQ 0 goto :fim_erro
)
echo [INFO] Pre-requisitos OK.

:: ============================================================
:: LIMPEZA DE PROCESSOS/PORTAS
:: ============================================================
echo [CLEAN] Finalizando janelas antigas do launcher...
taskkill /F /FI "WINDOWTITLE eq JARVIS_BACKEND*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq JARVIS_FRONTEND*" >nul 2>&1

call :kill_port 8000
call :kill_port 3000
call :kill_port 3001
call :kill_port 8001

:: ============================================================
:: AMBIENTE PYTHON + DEPENDENCIAS
:: ============================================================
if not exist ".venv\Scripts\activate.bat" (
    echo [SYS] Criando ambiente virtual Python na raiz...
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 goto :fim_erro
)

call "%VENV_ACT%"
if %ERRORLEVEL% NEQ 0 goto :fim_erro

echo [SYS] Atualizando pip/setuptools/wheel...
python -m pip install --upgrade pip "setuptools<82" wheel
if %ERRORLEVEL% NEQ 0 goto :fim_erro

echo [SYS] Instalando dependencias Python...
python -m pip install -r "backend\app\requirements.txt"
if %ERRORLEVEL% NEQ 0 goto :fim_erro

echo [SYS] Validando Playwright (opcional, sem falhar bootstrap)...
python -m playwright install chromium >nul 2>&1

:: ============================================================
:: FRONTEND DEPENDENCIAS
:: ============================================================
echo [SYS] Instalando/atualizando dependencias frontend...
pushd "%FRONT_DIR%"
call pnpm install
if %ERRORLEVEL% NEQ 0 (
    popd
    goto :fim_erro
)
popd

:: ============================================================
:: START BACKEND
:: ============================================================
echo [BACK] Iniciando backend na porta 8000...
start "JARVIS_BACKEND" /D "%BACK_DIR%" /HIGH cmd /k "call ""%VENV_ACT%"" && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --log-level info"

echo [BACK] Aguardando healthcheck do backend...
call :wait_http "http://127.0.0.1:8000/health" 45
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Backend nao respondeu em tempo habil.
    goto :fim_erro
)
echo [BACK] Backend OK.

:: ============================================================
:: START FRONTEND
:: ============================================================
echo [FRONT] Iniciando frontend na porta 3000...
start "JARVIS_FRONTEND" cmd /k "set PORT=3000 && pnpm --dir ""%FRONT_DIR%"" run dev"

echo [FRONT] Aguardando frontend abrir porta 3000...
call :wait_port 3000 180
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Frontend nao abriu a porta 3000 em tempo habil.
    echo [DICA] Verifique a janela JARVIS_FRONTEND para compilacao/travas.
    goto :fim_erro
)
echo [FRONT] Frontend OK.

:: ============================================================
:: CONCLUIDO
:: ============================================================
echo.
echo [OK] JARVIS iniciado com sucesso.
echo  Backend:   http://127.0.0.1:8000
echo  Frontend:  http://127.0.0.1:3000
echo.
echo Pressione qualquer tecla para fechar este launcher...
pause >nul
exit /b 0

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
ping -n 2 127.0.0.1 >nul
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
ping -n 2 127.0.0.1 >nul
goto :wait_port_loop

:fim_erro
echo.
echo [FALHA] Nao foi possivel iniciar em modo limpo.
echo [FALHA] Verifique as janelas de backend/frontend para detalhes.
pause
exit /b 1
