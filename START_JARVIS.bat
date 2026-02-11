@echo off
:: ============================================================================
:: JARVIS 5.0 - STARTUP SCRIPT - MODO UNIVERSAL
:: ============================================================================
:: Este script prepara o ambiente e inicia o SINGULARITY_LAUNCHER.
:: Toda a inteligencia de auto-cura e hardware esta no Launcher Python.
:: ============================================================================

setlocal enabledelayedexpansion

:: 1. VERIFICAR PRIVILEGIOS DE ADMINISTRADOR
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [SISTEMA] Solicitando Privilegios de Administrador...
    powershell -Command "Start-Process '%~dpnx0' -Verb RunAs"
    exit /b
)

:: 2. CONFIGURAR DIRETORIO RAIZ
set "ROOT=%~dp0"
cd /d "%ROOT%"

echo.
echo  [ STARK INDUSTRIES - INFRASTRUCTURE DIVISION ]
echo  ----------------------------------------------
echo  PROJETO: JARVIS 5.0 - Singularity
echo  STATUS: Inicializando Motores de Boot...
echo.

:: 3. CONFIGURACOES DE AMBIENTE - ESTABILIDADE
set "KMP_DUPLICATE_LIB_OK=TRUE"
set "PYTHONUTF8=1"
set "PYGAME_HIDE_SUPPORT_PROMPT=hide"
set "TF_CPP_MIN_LOG_LEVEL=3"

:: 4. ATIVACAO DO AMBIENTE VIRTUAL - VENV
if exist "%ROOT%venv\Scripts\activate.bat" (
    echo [OK] Ativando Ambiente Virtual...
    call "%ROOT%venv\Scripts\activate.bat"
) else (
    echo [ERRO] Ambiente Virtual - .venv - nao encontrado!
    echo Executando instalador de emergencia...
    call "%ROOT%INSTALL_JARVIS.bat"
    if %errorLevel% neq 0 exit /b 1
    call "%ROOT%venv\Scripts\activate.bat"
)

:: 5. INICIAR SINGULARITY LAUNCHER - ORQUESTRADOR
echo [SISTEMA] Delegando orquestracao para SINGULARITY_LAUNCHER...
echo.

python "%ROOT%SINGULARITY_LAUNCHER.py" %*

:: 6. TRATAMENTO DE ERROS DE SAIDA
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ------------------------------------------------------------------------
    echo [CRITICO] O Nucleo do JARVIS encerrou com erro - Codigo: %ERRORLEVEL%
    echo ------------------------------------------------------------------------
    echo Verifique os logs em: data/logs/latest_session/launcher.log
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [INFO] JARVIS encerrado normalmente.
timeout /t 5
exit /b 0
