@echo off
setlocal enabledelayedexpansion

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::  JARVIS 5.0 - UNIVERSAL INSTALLER v1.0
::  MILITARY GRADE - AUTOMATED DEPLOYMENT
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

chcp 65001 >nul 2>&1
title JARVIS 5.0 - UNIVERSAL INSTALLER
color 0E
mode con: cols=100 lines=30

echo.
echo  ==========================================================================
echo                 JARVIS 5.0 - PROTOCOLO DE INSTALAÇÃO UNIVERSAL
echo  ==========================================================================
echo.

:: Detectar ROOT
set "ROOT=%~dp0"
cd /d "%ROOT%"

:: 1. Verificar Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python não detectado no PATH do Windows.
    echo [AÇÃO] Por favor, instale o Python 3.10+ (Marque "Add to PATH").
    pause
    exit /b 1
)

:: 2. Criar VENV se não existir
if not exist "%ROOT%venv" (
    echo [SISTEMA] Criando Ambiente Virtual (venv)...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERRO] Falha ao criar venv.
        pause
        exit /b 1
    )
    echo [OK] Ambiente Virtual criado.
) else (
    echo [SISTEMA] Ambiente Virtual já existe.
)

:: 3. Executar Total Installer
echo [SISTEMA] Iniciando instalação de dependências críticas...
echo [AVISO] Isso pode levar alguns minutos (1-5 min)...
echo.

"%ROOT%venv\Scripts\python.exe" "%ROOT%scripts\install\total_installer.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] A instalação falhou. Verifique o log: scripts\install\total_installer.log
    pause
    exit /b 1
)

echo.
echo ==========================================================================
echo    INSTALAÇÃO CONCLUÍDA: JARVIS 5.0 está pronto para o combate!
echo    Use START_JARVIS.bat para iniciar o sistema.
echo ==========================================================================
echo.
pause
exit /b 0
