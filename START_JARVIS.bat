@echo off
:: ============================================================================
::  JARVIS 5.0 - SINGULARITY COMMAND CENTER v9.3
::  STARK INDUSTRIES - MILITARY GRADE SYSTEM
:: ============================================================================

setlocal enabledelayedexpansion
set "ROOT=%~dp0"
cd /d "%ROOT%"

:: Estetica de Inicializacao
color 0B
echo.
echo  ##########################################################################
echo  #                                                                        #
echo  #                 JARVIS 5.0 - SINGULARITY CORE ONLINE                   #
echo  #                    STARK INDUSTRIES - LEVEL 9 ACCESS                   #
echo  #                                                                        #
echo  ##########################################################################
echo.

:: Variaveis de Ambiente Stark
set "KMP_DUPLICATE_LIB_OK=TRUE"
set "PYTHONUTF8=1"

:: Verificacao de Seguranca (VENV)
set "VENV_PYTHON=%ROOT%venv\Scripts\python.exe"

if exist "%VENV_PYTHON%" goto :ENGAGE_SINGULARITY

echo [WARNING] Nucleo de Ambiente Virtual nao detectado.
echo [SYSTEM] Iniciando Protocolo de Auto-Recuperacao...
echo.
set /p opt="Deseja iniciar a instalacao automatica agora? (S/N): "

if /i "%opt%"=="S" (
    call "%ROOT%INSTALL_JARVIS.bat"
) else (
    echo [ABORT] Shutdown preventivo acionado. Dependencias ausentes.
    pause
    exit /b 1
)

:: Validacao Final apos Instalacao
if not exist "%VENV_PYTHON%" (
    echo [FATAL] Falha críitica ao configurar o ambiente.
    echo Execute o INSTALL_JARVIS.bat individualmente.
    pause
    exit /b 1
)

:ENGAGE_SINGULARITY
echo [SYSTEM] Acionando Motores de Singularidade...
echo.

"%VENV_PYTHON%" "%ROOT%SINGULARITY_LAUNCHER.py" %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [CRITICAL] Erro de sistema detectado (Code %ERRORLEVEL%).
    pause
    exit /b %ERRORLEVEL%
)

exit /b 0
