@echo off
:: ============================================================================
::  JARVIS 5.0 - STARK INDUSTRIES UNIVERSAL INSTALLER v1.3
::  SYSTEM STATUS: MILITARY GRADE DEPLOYMENT PROTOCOL
:: ============================================================================

set "ROOT=%~dp0"
cd /d "%ROOT%"

:: Estetica Stark
color 0E
echo.
echo  ##########################################################################
echo  #                                                                        #
echo  #             JARVIS 5.0 - PROTOCOLO DE INSTALACAO UNIVERSAL             #
echo  #                    STARK INDUSTRIES - SECURE DEPLOY                    #
echo  #                                                                        #
echo  ##########################################################################
echo.

:: 1. Verificacao de Requisitos
echo [SYSTEM] Verificando integridade do ambiente...
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python nao detectado no Windows.
    echo [ACTION] Instale o Python 3.11 e marque a opcao "ADD TO PATH".
    echo.
    pause
    exit /b 1
)

:: 2. Iniciando Ambiente Virtual
if exist "%ROOT%venv\Scripts\python.exe" (
    echo [SYSTEM] Ambiente Virtual (VENV) ja sincronizado.
    goto :INSTALL_DEPS
)

echo [SYSTEM] Criando Nucleo de Ambiente Virtual (VENV)...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Falha na criacao do VENV. Verifique permissoes de sistema.
    pause
    exit /b 1
)

:INSTALL_DEPS
:: 3. Instalacao de Dependencias
echo [SYSTEM] Iniciando Sincronizacao de Bibliotecas Neurais...
echo [WARN] Este processo demanda alto consumo de rede e processamento.
echo.

if not exist "%ROOT%scripts\install\total_installer.py" (
    echo [ERROR] Modulo de instalacao total_installer.py nao localizado.
    pause
    exit /b 1
)

"%ROOT%venv\Scripts\python.exe" "%ROOT%scripts\install\total_installer.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [CRITICAL] Falha na sincronizacao do sistema.
    echo Verifique sua conexao e execute novamente.
    pause
    exit /b 1
)

echo.
echo ##########################################################################
echo #             SISTEMA SINCRONIZADO: JARVIS ESTA ONLINE                   #
echo ##########################################################################
echo.
pause
exit /b 0
