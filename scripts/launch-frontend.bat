@echo off
REM UTF-8 with BOM
setlocal enabledelayedexpansion

REM ============================================================================
REM JARVIS 5.0 - Frontend Startup Script
REM Inicializa frontend React/Vite com port check
REM Frontend é OPCIONAL - não bloqueia se falhar
REM ============================================================================

if not defined ROOT (
    echo [WARN] ROOT nao definida. Use start-jarvis.bat
    exit /b 0
)

set LOGS_DIR=%ROOT%logs
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"
set LOG_FILE=%LOGS_DIR%\frontend-startup.log

REM Limpar log anterior
if exist "%LOG_FILE%" del "%LOG_FILE%"

echo [%date% %time%] Iniciando JARVIS Frontend... >> "%LOG_FILE%"
echo.

REM Navegar para frontend
cd /d "%ROOT%frontend"
if errorlevel 1 (
    echo [WARN] Frontend nao encontrado em %ROOT%frontend >> "%LOG_FILE%"
    exit /b 0
)

REM Verificar package.json
if not exist "package.json" (
    echo [WARN] package.json nao encontrado. Frontend nao configurado >> "%LOG_FILE%"
    exit /b 0
)

REM Definir PORT (padrão 3000)
if not defined PORT set PORT=3000

REM Verificar gerenciador (pnpm > npm)
for /f "tokens=*" %%i in ('where pnpm 2^>nul') do set PKG_MANAGER=pnpm && goto :pkg_manager_found
for /f "tokens=*" %%i in ('where npm 2^>nul') do set PKG_MANAGER=npm && goto :pkg_manager_found

echo [WARN] Nem pnpm nem npm encontrados >> "%LOG_FILE%"
exit /b 0

:pkg_manager_found
echo [INFO] Usando %PKG_MANAGER% para iniciar frontend >> "%LOG_FILE%"
echo [INFO] PORT: %PORT% >> "%LOG_FILE%"

REM Iniciar frontend em nova janela
echo [INFO] Iniciando frontend em http://127.0.0.1:%PORT% >> "%LOG_FILE%"
if "%PKG_MANAGER%"=="pnpm" (
    start "JARVIS_FRONTEND" cmd /k "pnpm dev --host 127.0.0.1"
) else (
    start "JARVIS_FRONTEND" cmd /k "npm run dev -- --host 127.0.0.1"
)

REM Aguardar port (máximo 60 segundos)
call :wait_port 127.0.0.1 %PORT% 60
if errorlevel 1 (
    echo [WARN] Frontend nao respondeu apos 60 segundos (opcional) >> "%LOG_FILE%"
    exit /b 0
)

echo [SUCCESS] Frontend iniciado com sucesso >> "%LOG_FILE%"
exit /b 0

:wait_port
setlocal
set HOST=%~1
set PORT=%~2
set TIMEOUT=%~3
set ELAPSED=0

:wait_port_loop
if %ELAPSED% geq %TIMEOUT% (
    endlocal
    exit /b 1
)

powershell -NoProfile -Command "try { $t = New-Object System.Net.Sockets.TcpClient; $t.ConnectAsync('%HOST%', %PORT%).Wait(2000); $t.Close(); exit 0 } catch { exit 1 }" 2>nul
if %errorlevel% equ 0 (
    endlocal
    exit /b 0
)

timeout /t 2 /nobreak >nul
set /a ELAPSED=%ELAPSED% + 2
goto wait_port_loop
