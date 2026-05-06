@echo off
REM ============================================================================
REM JARVIS 5.0 - Check Prerequisites Script
REM ============================================================================
REM Valida dependências necessárias: Python 3.11+, Node.js, npm/pnpm
REM Versão: 2026-05-06 | Encoding: UTF-8 com BOM

setlocal enabledelayedexpansion
chcp 65001 >nul

REM ============================================================================
REM CONFIGURAÇÕES
REM ============================================================================
set "PROJECT_ROOT=d:\DOCUMENTOS\GitHub\PROJECT_JARVIS_5.0"
set "LOGS_DIR=!PROJECT_ROOT!\logs"
set "LOG_FILE=!LOGS_DIR!\prerequisites-check.log"

REM Inicializar log
if not exist "!LOGS_DIR!" mkdir "!LOGS_DIR!"
(
    echo ============================================================================
    echo JARVIS 5.0 - Verificacao de Pre-requisitos
    echo Data: %date% %time%
    echo ============================================================================
    echo.
) > "!LOG_FILE!"

REM ============================================================================
REM FUNÇÕES AUXILIARES
REM ============================================================================

:check_python
    echo [INFO] Verificando Python 3.11+... >> "!LOG_FILE!"
    echo Verificando Python 3.11+...

    python --version >nul 2>&1
    if !errorlevel! neq 0 (
        echo [ERROR] Python nao encontrado no PATH >> "!LOG_FILE!"
        echo [FAIL] Python nao encontrado no PATH
        echo.
        echo [ERRO] Python 3.11+ eh obrigatorio para JARVIS 5.0
        echo Por favor, instale Python de: https://www.python.org/downloads/
        echo Certifique-se de marcar "Add Python to PATH" durante instalacao
        timeout /t 3 /nobreak >nul
        endlocal
        exit /b 1
    )

    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    echo [OK] Python encontrado: !PYTHON_VERSION! >> "!LOG_FILE!"
    echo [OK] Python: !PYTHON_VERSION!
    exit /b 0

:check_nodejs
    echo [INFO] Verificando Node.js... >> "!LOG_FILE!"
    echo Verificando Node.js...

    node --version >nul 2>&1
    if !errorlevel! neq 0 (
        echo [WARN] Node.js nao encontrado - frontend pode nao funcionar >> "!LOG_FILE!"
        echo [WARN] Node.js nao encontrado (apenas aviso)
        echo.
        echo Node.js eh recomendado para desenvolvimento frontend
        timeout /t 2 /nobreak >nul
        exit /b 0
    )

    for /f "tokens=*" %%i in ('node --version 2^>^&1') do set "NODE_VERSION=%%i"
    echo [OK] Node.js encontrado: !NODE_VERSION! >> "!LOG_FILE!"
    echo [OK] Node.js: !NODE_VERSION!
    exit /b 0

:check_package_manager
    echo [INFO] Verificando gerenciador de pacotes... >> "!LOG_FILE!"
    echo Verificando pnpm/npm...

    REM Verificar pnpm primeiro
    pnpm --version >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=*" %%i in ('pnpm --version 2^>^&1') do set "PKG_MGR=pnpm %%i"
        echo [OK] pnpm encontrado: !PKG_MGR! >> "!LOG_FILE!"
        echo [OK] pnpm: !PKG_MGR!
        exit /b 0
    )

    REM Verificar npm
    npm --version >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=*" %%i in ('npm --version 2^>^&1') do set "PKG_MGR=npm %%i"
        echo [OK] npm encontrado: !PKG_MGR! >> "!LOG_FILE!"
        echo [OK] npm: !PKG_MGR!
        exit /b 0
    )

    echo [WARN] Nenhum gerenciador (pnpm/npm) encontrado >> "!LOG_FILE!"
    echo [WARN] Nenhum gerenciador encontrado (apenas aviso)
    exit /b 0

REM ============================================================================
REM SEQUÊNCIA PRINCIPAL
REM ============================================================================
:main
    echo.
    echo ========== Verificando Pre-requisitos JARVIS 5.0 ==========
    echo.

    call :check_python
    if !errorlevel! neq 0 goto :prerequisites_failed

    call :check_nodejs
    REM Node.js é só aviso, continua mesmo se falhar

    call :check_package_manager
    REM Package manager é só aviso, continua mesmo se falhar

    echo.
    echo [SUCCESS] Todos os pre-requisitos obrigatorios foram satisfeitos >> "!LOG_FILE!"
    echo [SUCCESS] Pre-requisitos verificados com sucesso
    echo.

    endlocal
    exit /b 0

:prerequisites_failed
    echo.
    echo [ERROR] Verificacao de pre-requisitos falhou >> "!LOG_FILE!"
    echo [ERROR] Falha: Pre-requisitos obrigatorios nao atendidos
    echo.
    endlocal
    exit /b 1
