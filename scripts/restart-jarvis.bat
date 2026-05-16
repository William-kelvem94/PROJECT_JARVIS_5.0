@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI\"
cd /d "%ROOT%"
REM ========================================================================
REM JARVIS 5.0 - Manual Restart Script
REM ========================================================================
REM Use este script para reiniciar o JARVIS manualmente quando necessário
REM ========================================================================

setlocal EnableExtensions
chcp 65001 >nul

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║           JARVIS 5.0 - Sistema de Reinício Manual             ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI\"

echo [1/4] Parando processos do JARVIS...
REM Para processos Python do backend (filtra por diretório do projeto)
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| find "PID:"') do (
    wmic process where "ProcessId=%%i" get CommandLine 2>nul | findstr /i "JARVIS" >nul 2>nul
    if not errorlevel 1 taskkill /F /PID %%i 2>nul
)

REM Para processos Node do frontend (filtra por diretório do projeto)
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq node.exe" /FO LIST ^| find "PID:"') do (
    wmic process where "ProcessId=%%i" get CommandLine 2>nul | findstr /i "JARVIS" >nul 2>nul
    if not errorlevel 1 taskkill /F /PID %%i 2>nul
)

echo [2/4] Aguardando limpeza de recursos...
timeout /t 3 /nobreak >nul

echo [3/4] Verificando ambiente virtual...
if not exist "%ROOT%.venv\Scripts\python.exe" (
    echo [AVISO] Ambiente virtual não encontrado. Execute setup-venv.bat primeiro.
    pause
    exit /b 1
)

echo [4/4] Reiniciando JARVIS...
start "JARVIS Restart" cmd /k "cd /d %ROOT% && call start-jarvis.bat"

echo.
echo ✅ JARVIS reiniciado com sucesso!
echo.
echo Verifique a nova janela para o status do sistema.
echo.
timeout /t 5
exit /b 0
