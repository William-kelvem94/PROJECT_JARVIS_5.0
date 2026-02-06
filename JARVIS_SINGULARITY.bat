@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: JARVIS SINGULARITY ULTIMATE LAUNCHER
:: ============================================================================
:: Este script solicita permissao de ADMINISTRADOR e inicia o JARVIS
:: de forma totalmente automatizada (Self-Setup + Optimized Execution)
:: ============================================================================

:: -------------------------------------------------------------------------
:: SOLICITAR ELEVACAO DE PRIVILEGIO (ADM)
:: -------------------------------------------------------------------------
:check_Privileges
NET SESSION >nul 2>&1
if %ERRORLEVEL% == 0 (
    goto :gotAdmin
) else (
    echo.
    echo ========================================================================
    echo   SOLICITANDO PERMISSAO DE ADMINISTRADOR...
    echo ========================================================================
    echo.
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:gotAdmin
pushd "%CD%"
CD /D "%~dp0"

cls
echo.
echo ========================================================================
echo   JARVIS SINGULARITY - SISTEMA DE INICIALIZACAO AUTOMATICA
echo ========================================================================
echo.

:: -------------------------------------------------------------------------
:: VERIFICAR AMBIENTE E DEPENDENCIAS
:: -------------------------------------------------------------------------
echo [1] Verificando integridade e dependencias...
echo   Isso garante que todos os recursos (Vision, Audio, God Mode) estao ativos.
echo.

python setup_manager.py
if %ERRORLEVEL% NEQ 0 (
    if %ERRORLEVEL% NEQ 1 (
         echo.
         echo [!] Erro critico no Setup Manager. Verifique os logs acima.
         pause
         exit /b %ERRORLEVEL%
    )
)

:: -------------------------------------------------------------------------
:: INICIAR JARVIS OTIMIZADO (V2)
:: -------------------------------------------------------------------------
echo.
echo [2] Iniciando Nucleo Otimizado (Singularity V2)...
echo   Carregamento assincrono ativado. HUD abrira em breve...
echo.

:: O setup_manager promove o main_singularity_v2.py para main.py
if exist main.py (
    python main.py
) else if exist main_singularity_v2.py (
    python main_singularity_v2.py
) else (
    python main_singularity.py
)

set JARVIS_EXIT_CODE=%ERRORLEVEL%

echo.
echo ========================================================================
echo   JARVIS ENCERRADO (codigo: %JARVIS_EXIT_CODE%)
echo ========================================================================
echo.

pause
exit /b %JARVIS_EXIT_CODE%
