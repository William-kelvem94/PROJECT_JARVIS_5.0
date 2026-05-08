@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI\"
cd /d "%ROOT%"
REM ============================================================
REM SCRIPT DE CORREÇÃO RÁPIDA - JARVIS 5.0
REM Corrige problemas críticos de CPU/RAM e LLM offline
REM ============================================================

echo ============================================================
echo   CORREÇÃO CRÍTICA — JARVIS 5.0
echo ============================================================
echo.

REM Verificar se está no diretório correto
if not exist "backend\" (
    echo [ERRO] Diretório backend não encontrado!
    echo Execute este script da raiz do projeto.
    pause
    exit /b 1
)

REM Ativar ambiente virtual
echo [INFO] Ativando ambiente virtual...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo [ERRO] Ambiente virtual não encontrado!
    echo Execute primeiro: setup-venv.bat
    pause
    exit /b 1
)

echo [OK] Venv ativado
echo.

REM Executar script Python de correção
echo [INFO] Executando correções...
python "%SCRIPT_DIR%fix-critical-issues.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Falha ao aplicar correções!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   CORREÇÕES APLICADAS COM SUCESSO!
echo ============================================================
echo.
echo Próximos passos:
echo   1. Reiniciar o backend: scripts/restart-jarvis.bat
echo   2. Verificar health: curl http://localhost:8000/system/capabilities
echo   3. Monitorar CPU/RAM no dashboard
echo.

pause
