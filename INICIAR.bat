@echo off
REM ============================================================================
REM JARVIS SINGULARITY - Inicializador Automático
REM ============================================================================
REM Este script organiza, instala e inicia o JARVIS automaticamente
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ========================================================================
echo   JARVIS SINGULARITY - INICIALIZADOR
echo ========================================================================
echo.

REM -------------------------------------------------------------------------
REM VERIFICAR PYTHON
REM -------------------------------------------------------------------------
echo [1] Verificando Python...

where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   ERRO: Python nao encontrado no PATH!
    echo   Instale Python 3.8+ de: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Obter versão do Python
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo   OK: Python %PYTHON_VERSION% encontrado
echo.

REM -------------------------------------------------------------------------
REM EXECUTAR SETUP MANAGER
REM -------------------------------------------------------------------------
echo [2] Executando Setup Manager (organizacao + instalacao)...
echo   Isso pode demorar alguns minutos...
echo.

python setup_manager.py
set SETUP_EXIT_CODE=%ERRORLEVEL%

echo.
echo   Setup Manager finalizado (codigo: %SETUP_EXIT_CODE%)
echo.

REM -------------------------------------------------------------------------
REM VERIFICAR RESULTADO DO SETUP
REM -------------------------------------------------------------------------
if %SETUP_EXIT_CODE% EQU 0 (
    echo   SUCESSO: Setup concluido com sucesso!
) else if %SETUP_EXIT_CODE% EQU 1 (
    echo   AVISO: Setup parcialmente concluido
    echo   Algumas dependencias podem ter falhado
    echo.
    choice /C SN /M "Deseja continuar mesmo assim"
    if !ERRORLEVEL! EQU 2 (
        echo   Abortado pelo usuario
        pause
        exit /b 1
    )
) else (
    echo   ERRO: Setup falhou (codigo: %SETUP_EXIT_CODE%)
    echo   Verifique os erros acima
    echo.
    pause
    exit /b %SETUP_EXIT_CODE%
)

REM -------------------------------------------------------------------------
REM VERIFICAR GOOGLE_API_KEY
REM -------------------------------------------------------------------------
echo.
echo [3] Verificando configuracao...

if "%GOOGLE_API_KEY%"=="" (
    echo   AVISO: GOOGLE_API_KEY nao configurada!
    echo   O JARVIS funcionara em modo local apenas (Ollama)
    echo.
    echo   Para usar Gemini, configure:
    echo   set GOOGLE_API_KEY=sua_chave_aqui
    echo.
    timeout /t 3 >nul
) else (
    echo   OK: GOOGLE_API_KEY configurada
)

REM -------------------------------------------------------------------------
REM INICIAR JARVIS
REM -------------------------------------------------------------------------
echo.
echo [4] Iniciando JARVIS...
echo.
echo ========================================================================
echo   JARVIS ONLINE
echo ========================================================================
echo.

python main.py
set JARVIS_EXIT_CODE=%ERRORLEVEL%

REM -------------------------------------------------------------------------
REM RESULTADO FINAL
REM -------------------------------------------------------------------------
echo.
echo ========================================================================
echo   JARVIS ENCERRADO (codigo: %JARVIS_EXIT_CODE%)
echo ========================================================================
echo.

if %JARVIS_EXIT_CODE% EQU 0 (
    echo   Encerramento normal
) else if %JARVIS_EXIT_CODE% EQU 130 (
    echo   Interrompido pelo usuario (Ctrl+C)
) else (
    echo   Encerramento com erro
    echo   Verifique os logs acima
)

echo.
pause
exit /b %JARVIS_EXIT_CODE%
