@echo off
:: JARVIS 5.0 - LAUNCHER v9.1 (Resilient)

setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title JARVIS 5.0 - SINULARITY
color 0B

set "ROOT=%~dp0"
cd /d "%ROOT%"

:: Global Guards
set "KMP_DUPLICATE_LIB_OK=TRUE"
set "PYTHONUTF8=1"

:: Verificar VENV (Self-Healing)
set "VENV_PYTHON=%ROOT%venv\Scripts\python.exe"

if exist "%VENV_PYTHON%" goto START_SYSTEM

echo.
echo [ALERTA] Ambiente Virtual (venv) não encontrado.
echo [INFO] JARVIS precisa instalar os componentes no seu PC primeiro.
echo.
set /p choice="Deseja instalar as dependências agora? (S/N): "

if /i "%choice%"=="S" (
    echo [SISTEMA] Iniciando Instalador Universal...
    call "%ROOT%INSTALL_JARVIS.bat"
) else (
    echo [AVISO] O sistema não pode rodar sem as dependências.
    pause
    exit /b 1
)

:: Re-verificar após tentativa de instalação
if not exist "%VENV_PYTHON%" (
    echo [ERRO] Não conseguimos configurar o ambiente. 
    echo Rode o INSTALL_JARVIS.bat manualmente para ver os detalhes.
    pause
    exit /b 1
)

:START_SYSTEM
echo.
echo [SYSTEM] Acionando Núcleo de Singularidade...
echo.

"%VENV_PYTHON%" "%ROOT%SINGULARITY_LAUNCHER.py" %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [CRÍTICO] O sistema parou inesperadamente (Erro %ERRORLEVEL%).
    pause
    exit /b %ERRORLEVEL%
)

exit /b 0
