@echo off
REM ============================================================================
REM JARVIS SINGULARITY - Launcher
REM ============================================================================
REM Inicia o JARVIS Singularity com arquitetura QThread
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ========================================================================
echo   JARVIS SINGULARITY - LAUNCHER
echo ========================================================================
echo.

REM -------------------------------------------------------------------------
REM VERIFICAR PYTHON
REM -------------------------------------------------------------------------
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   ERRO: Python nao encontrado no PATH!
    echo   Instale Python 3.8+ de: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM -------------------------------------------------------------------------
REM VERIFICAR GOOGLE_API_KEY (OPCIONAL)
REM -------------------------------------------------------------------------
if "%GOOGLE_API_KEY%"=="" (
    echo   AVISO: GOOGLE_API_KEY nao configurada
    echo   O JARVIS funcionara em modo local apenas (Ollama)
    echo.
    echo   Para usar Gemini, configure antes de executar:
    echo   set GOOGLE_API_KEY=sua_chave_aqui
    echo.
    timeout /t 2 >nul
)

REM -------------------------------------------------------------------------
REM INICIAR JARVIS SINGULARITY
REM -------------------------------------------------------------------------
echo   Iniciando JARVIS Singularity...
echo.

py main_singularity.py

set EXIT_CODE=%ERRORLEVEL%

REM -------------------------------------------------------------------------
REM RESULTADO
REM -------------------------------------------------------------------------
echo.
echo ========================================================================
if %EXIT_CODE% EQU 0 (
    echo   JARVIS encerrado normalmente
) else if %EXIT_CODE% EQU 130 (
    echo   Interrompido pelo usuario (Ctrl+C)
) else (
    echo   JARVIS encerrado com erro (codigo: %EXIT_CODE%^)
    echo   Verifique os logs acima
)
echo ========================================================================
echo.

pause
exit /b %EXIT_CODE%
