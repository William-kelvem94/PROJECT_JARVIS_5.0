@echo off
TITLE JARVIS 5.0
SETLOCAL

:: Ancora SEMPRE na pasta do proprio script
cd /d "%~dp0"
SET "ROOT=%~dp0"

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
echo [DEBUG] pnpm errorlevel=%ERRORLEVEL%
echo [INFO] Pre-requisitos OK.

:: ============================================================
:: AMBIENTE VIRTUAL PYTHON
:: ============================================================
if not exist ".venv\Scripts\activate.bat" (
    echo [SYS] Criando ambiente virtual Python na raiz...
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 goto :fim_erro
)

call ".venv\Scripts\activate.bat"
if %ERRORLEVEL% NEQ 0 goto :fim_erro

echo [SYS] Atualizando pip e instalando dependencias Python...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
if %ERRORLEVEL% NEQ 0 goto :fim_erro
python -m pip install -r "backend\app\requirements.txt"
if %ERRORLEVEL% NEQ 0 goto :fim_erro

:: ============================================================
:: BACKEND
:: Sem aspas aninhadas: caminho do projeto nao tem espacos.
:: Cada janela 'start' e um processo novo sem herdar o venv,
:: por isso o activate.bat e chamado explicitamente dentro dela.
:: ============================================================
echo [BACK] Iniciando backend na porta 8000...
SET "VENV_ACT=%ROOT%.venv\Scripts\activate.bat"
SET "BACK_DIR=%ROOT%backend"
SET PYTHONOPTIMIZE=1
echo [DEBUG] BACK_DIR=%BACK_DIR%
echo [DEBUG] VENV_ACT=%VENV_ACT%
start "JARVIS_BACKEND" /D "%BACK_DIR%" /HIGH cmd /k "call ""%VENV_ACT%"" && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info"

:: ============================================================
:: FRONTEND
:: ============================================================
echo [FRONT] Verificando dependencias frontend...
if not exist "frontend\node_modules" (
    echo [SYS] Instalando node_modules com pnpm...
    pushd frontend
    call pnpm install
    popd
)

echo [FRONT] Iniciando frontend na porta 3000...
SET "NODE_OPTIONS=--max-old-space-size=2048"
SET "FRONT_DIR=%ROOT%frontend"
start "JARVIS_FRONTEND" /D "%FRONT_DIR%" cmd /k "call pnpm run dev"

:: ============================================================
:: CONCLUIDO
:: ============================================================
echo.
echo  Backend:   http://localhost:8000
echo  Frontend:  http://localhost:3000
echo.
echo  Pressione qualquer tecla para fechar este launcher...
pause
exit /b 0

:fim_erro
echo.
echo [FALHA] Nao foi possivel iniciar. Verifique os erros acima.
pause
exit /b 1
