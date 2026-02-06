@echo off
:: ============================================================================
:: JARVIS SINGULARITY - Quick Setup Check
:: ============================================================================
:: Verifica se o sistema esta pronto para executar
:: ============================================================================

setlocal enabledelayedexpansion

echo.
echo ========================================================================
echo   JARVIS - VERIFICADOR RAPIDO DE SETUP
echo ========================================================================
echo.

set "ALL_OK=1"

:: -------------------------------------------------------------------------
:: VERIFICAR PYTHON
:: -------------------------------------------------------------------------
echo [1] Verificando Python...

where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo    [FALHOU] Python nao encontrado
    echo    Solucao: Execute JARVIS_SINGULARITY.bat para instalacao automatica
    set "ALL_OK=0"
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo    [OK] Python !PYTHON_VERSION! instalado
)

:: -------------------------------------------------------------------------
:: VERIFICAR AMBIENTE VIRTUAL
:: -------------------------------------------------------------------------
echo.
echo [2] Verificando ambiente virtual...

if exist "venv\Scripts\python.exe" (
    echo    [OK] Ambiente virtual encontrado
) else (
    echo    [AVISO] Ambiente virtual nao encontrado
    echo    Solucao: Execute JARVIS_SINGULARITY.bat para criar automaticamente
    set "ALL_OK=0"
)

:: -------------------------------------------------------------------------
:: VERIFICAR ARQUIVOS CRITICOS
:: -------------------------------------------------------------------------
echo.
echo [3] Verificando arquivos criticos...

set "FILES_OK=1"

if not exist "main_singularity.py" (
    if not exist "main.py" (
        echo    [FALHOU] Entry point nao encontrado
        set "FILES_OK=0"
        set "ALL_OK=0"
    )
)

if not exist "config.yaml" (
    echo    [FALHOU] config.yaml nao encontrado
    set "FILES_OK=0"
    set "ALL_OK=0"
)

if not exist "requirements_singularity.txt" (
    echo    [FALHOU] requirements_singularity.txt nao encontrado
    set "FILES_OK=0"
    set "ALL_OK=0"
)

if "%FILES_OK%"=="1" (
    echo    [OK] Todos os arquivos criticos presentes
)

:: -------------------------------------------------------------------------
:: VERIFICAR ESTRUTURA
:: -------------------------------------------------------------------------
echo.
echo [4] Verificando estrutura de pastas...

set "DIRS_OK=1"

if not exist "src\core" (
    echo    [FALHOU] src\core nao encontrado
    set "DIRS_OK=0"
    set "ALL_OK=0"
)

if not exist "src\interface" (
    echo    [FALHOU] src\interface nao encontrado
    set "DIRS_OK=0"
    set "ALL_OK=0"
)

if "%DIRS_OK%"=="1" (
    echo    [OK] Estrutura de pastas OK
)

:: -------------------------------------------------------------------------
:: VERIFICAR VALIDADOR
:: -------------------------------------------------------------------------
echo.
echo [5] Executando validador completo...

if exist "validate_project.py" (
    python validate_project.py >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo    [OK] Validacao completa passou
    ) else if !ERRORLEVEL! EQU 1 (
        echo    [AVISO] Validacao parcial (veja detalhes com: python validate_project.py)
    ) else (
        echo    [FALHOU] Validacao completa falhou
        set "ALL_OK=0"
    )
) else (
    echo    [AVISO] validate_project.py nao encontrado
)

:: -------------------------------------------------------------------------
:: RESULTADO FINAL
:: -------------------------------------------------------------------------
echo.
echo ========================================================================

if "%ALL_OK%"=="1" (
    echo   RESULTADO: SISTEMA PRONTO PARA EXECUCAO
    echo ========================================================================
    echo.
    echo   Para iniciar o JARVIS:
    echo   1. Execute: JARVIS_SINGULARITY.bat
    echo   2. OU: python main.py
    echo.
) else (
    echo   RESULTADO: SISTEMA PRECISA DE CONFIGURACAO
    echo ========================================================================
    echo.
    echo   Problemas detectados. Solucoes:
    echo   1. Execute: JARVIS_SINGULARITY.bat (configuracao automatica)
    echo   2. OU execute: python validate_project.py (diagnostico detalhado)
    echo   3. Veja: TROUBLESHOOTING.md para ajuda completa
    echo.
)

pause
exit /b 0
