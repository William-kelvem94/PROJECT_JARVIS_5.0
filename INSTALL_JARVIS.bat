@echo off
:: JARVIS 5.0 - UNIVERSAL INSTALLER v1.1 (Ultra Resilient)
:: Este script é otimizado para não fechar sozinho em caso de erro.

chcp 65001 >nul 2>&1
title JARVIS 5.0 - UNIVERSAL INSTALLER
color 0E

echo.
echo  ==========================================================================
echo                 JARVIS 5.0 - PROTOCOLO DE INSTALAÇÃO UNIVERSAL
echo  ==========================================================================
echo.

:: Detectar ROOT de forma segura
set "ROOT=%~dp0"
cd /d "%ROOT%"

:: 1. Verificar Python (Busca robusta)
echo [SISTEMA] Verificando requisitos de sistema...
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python não foi encontrado no seu Windows.
    echo.
    echo [AÇÃO] 1. Baixe o Python 3.11 em python.org
    echo [AÇÃO] 2. Marque a opção "ADD PYTHON TO PATH" na instalação.
    echo.
    pause
    exit /b 1
)

:: 2. Criar VENV
if exist "%ROOT%venv\Scripts\python.exe" (
    echo [SISTEMA] Ambiente Virtual (venv) já detectado.
    goto SKIP_VENV
)

echo [SISTEMA] Criando Ambiente Virtual (venv)...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao criar o venv. Verifique se o Python está instalado corretamente.
    pause
    exit /b 1
)
echo [OK] Ambiente Virtual criado em %ROOT%venv
:SKIP_VENV

:: 3. Executar Total Installer
echo [SISTEMA] Iniciando instalação de dependências...
echo [AVISO] Isso abrirá o instalador Python interno.
echo.

if not exist "%ROOT%scripts\install\total_installer.py" (
    echo [ERRO] Arquivo scripts\install\total_installer.py não encontrado!
    echo [ROOT] %ROOT%
    pause
    exit /b 1
)

"%ROOT%venv\Scripts\python.exe" "%ROOT%scripts\install\total_installer.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] A instalação das bibliotecas falhou. 
    echo Verifique se você tem internet e tente novamente.
    pause
    exit /b 1
)

echo.
echo ==========================================================================
echo    INSTALAÇÃO CONCLUÍDA: JARVIS 5.0 pronto para uso!
echo ==========================================================================
echo.
pause
exit /b 0
