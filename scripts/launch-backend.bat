@echo off
REM UTF-8 with BOM
setlocal enabledelayedexpansion

REM ============================================================================
REM JARVIS 5.0 - Backend Startup Script
REM Inicializa backend FastAPI/Uvicorn com health check
REM ============================================================================

if not defined ROOT (
    echo [ERROR] ROOT nao definida. Use start-jarvis.bat
    exit /b 1
)

if not defined JARVIS_MODE (
    echo [ERROR] JARVIS_MODE nao definida. Use start.bat
    exit /b 1
)

set LOGS_DIR=%ROOT%logs
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"
set LOG_FILE=%LOGS_DIR%\backend-startup.log

REM Limpar log anterior
if exist "%LOG_FILE%" del "%LOG_FILE%"

echo [%date% %time%] Iniciando JARVIS Backend... >> "%LOG_FILE%"
echo.

REM Navegar para backend
cd /d "%ROOT%backend"
if errorlevel 1 (
    echo [ERROR] Nao foi possivel navegar para %ROOT%backend >> "%LOG_FILE%"
    exit /b 1
)

REM Ativar venv
if not exist "%ROOT%.venv\Scripts\activate.bat" (
    echo [ERROR] venv nao encontrado: %ROOT%.venv\Scripts\activate.bat >> "%LOG_FILE%"
    exit /b 1
)

call "%ROOT%.venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Falha ao ativar venv >> "%LOG_FILE%"
    exit /b 1
)

set "PYTHON_EXE=%ROOT%.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python do venv nao encontrado: %PYTHON_EXE% >> "%LOG_FILE%"
    exit /b 1
)

REM Setar variáveis de ambiente
set JARVIS_AI_DEVICE=!JARVIS_AI_DEVICE:cpu=cpu!
set JARVIS_WHISPER_MODEL=!JARVIS_WHISPER_MODEL:base=base!
set JARVIS_DISABLE_CAMERA=!JARVIS_DISABLE_CAMERA:0=0!

echo [INFO] JARVIS_MODE: !JARVIS_MODE! >> "%LOG_FILE%"
echo [INFO] JARVIS_AI_DEVICE: !JARVIS_AI_DEVICE! >> "%LOG_FILE%"
echo [INFO] JARVIS_WHISPER_MODEL: !JARVIS_WHISPER_MODEL! >> "%LOG_FILE%"
echo [INFO] JARVIS_DISABLE_CAMERA: !JARVIS_DISABLE_CAMERA! >> "%LOG_FILE%"

REM Iniciar backend em nova janela
echo [INFO] Iniciando Uvicorn em http://127.0.0.1:8000 >> "%LOG_FILE%"
start "JARVIS_BACKEND" cmd /k ""%PYTHON_EXE%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --log-level info"

REM Aguardar health check
call :wait_http 127.0.0.1 8000 /health 90
if errorlevel 1 (
    echo [ERROR] Health check falhou apos 90 segundos >> "%LOG_FILE%"
    echo [ERROR] Backend nao respondeu. Verifique a janela JARVIS_BACKEND >> "%LOG_FILE%"
    exit /b 1
)

echo [SUCCESS] Backend iniciado com sucesso >> "%LOG_FILE%"
exit /b 0

:wait_http
setlocal
set HOST=%~1
set PORT=%~2
set ENDPOINT=%~3
set TIMEOUT=%~4
set ELAPSED=0

:wait_http_loop
if %ELAPSED% geq %TIMEOUT% (
    endlocal
    exit /b 1
)

powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://%HOST%:%PORT%%ENDPOINT%' -TimeoutSec 2 -ErrorAction Stop; exit 0 } catch { exit 1 }" 2>nul
if %errorlevel% equ 0 (
    endlocal
    exit /b 0
)

timeout /t 2 /nobreak >nul
set /a ELAPSED=%ELAPSED% + 2
goto wait_http_loop
