@echo off
REM ============================================================================
REM PROJECT JARVIS 5.0 - Start Script
REM Inicializa o sistema completo com backend e frontend
REM ============================================================================

setlocal enabledelayedexpansion

REM Define cores para output
set "COLOR_RESET=[0m"
set "COLOR_GREEN=[32m"
set "COLOR_BLUE=[34m"
set "COLOR_YELLOW=[33m"

echo.
echo %COLOR_BLUE%=================================================%COLOR_RESET%
echo %COLOR_GREEN%PROJECT JARVIS 5.0 - Startup%COLOR_RESET%
echo %COLOR_BLUE%=================================================%COLOR_RESET%
echo.

REM Obtém o diretório do script
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Carrega funções comuns
if exist "scripts\common-functions.bat" (
    call scripts\common-functions.bat
) else (
    echo %COLOR_YELLOW%AVISO: common-functions.bat nao encontrado%COLOR_RESET%
)

REM Verifica Python
echo %COLOR_BLUE%[1/5]%COLOR_RESET% Verificando Python...
python --version >/dev/null 2>&1
if errorlevel 1 (
    echo %COLOR_YELLOW%ERRO: Python nao encontrado. Instale Python 3.10+%COLOR_RESET%
    pause
    exit /b 1
)

REM Verifica Node.js
echo %COLOR_BLUE%[2/5]%COLOR_RESET% Verificando Node.js...
node --version >/dev/null 2>&1
if errorlevel 1 (
    echo %COLOR_YELLOW%AVISO: Node.js nao encontrado. Frontend pode nao funcionar%COLOR_RESET%
)

REM Cria diretórios necessários
echo %COLOR_BLUE%[3/5]%COLOR_RESET% Criando estrutura de diretorios...
if not exist "logs" mkdir logs
if not exist "backend\data" mkdir backend\data
if not exist "frontend\dist" mkdir frontend\dist

REM Inicia o backend
echo %COLOR_BLUE%[4/5]%COLOR_RESET% Iniciando backend...
if exist "backend\main.py" (
    start "JARVIS Backend" python backend\main.py
    timeout /t 2 /nobreak
) else (
    echo %COLOR_YELLOW%ERRO: backend\main.py nao encontrado%COLOR_RESET%
)

REM Inicia o frontend
echo %COLOR_BLUE%[5/5]%COLOR_RESET% Iniciando frontend...
if exist "frontend\index.html" (
    start "JARVIS Frontend" cmd /c "cd frontend && python -m http.server 8000"
) else (
    echo %COLOR_YELLOW%AVISO: frontend\index.html nao encontrado%COLOR_RESET%
)

echo.
echo %COLOR_GREEN%✓ JARVIS 5.0 iniciado com sucesso!%COLOR_RESET%
echo %COLOR_BLUE%Backend: http://localhost:5000%COLOR_RESET%
echo %COLOR_BLUE%Frontend: http://localhost:8000%COLOR_RESET%
echo.
pause
