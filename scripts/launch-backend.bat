@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

if not defined ROOT (
  echo [ERROR] ROOT nao definida. Use start-jarvis.bat
  exit /b 1
)

if not defined JARVIS_MODE set "JARVIS_MODE=COMPAT"
if not defined JARVIS_AI_DEVICE set "JARVIS_AI_DEVICE=cpu"
if not defined JARVIS_WHISPER_MODEL set "JARVIS_WHISPER_MODEL=tiny"
if not defined JARVIS_DISABLE_CAMERA set "JARVIS_DISABLE_CAMERA=false"

set "LOGS_DIR=%ROOT%logs"
set "LOG_FILE=%LOGS_DIR%\backend-startup.log"
set "PYTHON_EXE=%ROOT%.venv\Scripts\python.exe"
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"

echo [%date% %time%] Starting JARVIS backend > "%LOG_FILE%"
echo [INFO] Mode=%JARVIS_MODE% Device=%JARVIS_AI_DEVICE% Whisper=%JARVIS_WHISPER_MODEL% >> "%LOG_FILE%"

if not exist "%PYTHON_EXE%" (
  echo [ERROR] Python da venv nao encontrado: %PYTHON_EXE%
  exit /b 1
)

pushd "%ROOT%backend"
if errorlevel 1 exit /b 1

call :wait_http 127.0.0.1 8000 /health 2
if not errorlevel 1 (
  echo [OK] Backend ja esta online.
  popd
  exit /b 0
)

echo [BACKEND] Starting http://127.0.0.1:8000
start "JARVIS_BACKEND" /B cmd /c ""%PYTHON_EXE%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --log-level info >> "%LOG_FILE%" 2>&1"

popd
call :wait_http 127.0.0.1 8000 /health 120
if errorlevel 1 (
  echo [ERROR] Backend nao respondeu em http://127.0.0.1:8000/health
  echo [ERROR] Backend health timeout >> "%LOG_FILE%"
  exit /b 1
)

echo [OK] Backend online.
echo [OK] Backend online >> "%LOG_FILE%"
exit /b 0

:wait_http
setlocal EnableExtensions EnableDelayedExpansion
set "HOST=%~1"
set "PORT=%~2"
set "ENDPOINT=%~3"
set "TIMEOUT=%~4"
set /a ELAPSED=0

:wait_http_loop
if !ELAPSED! geq !TIMEOUT! (
  endlocal
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -UseBasicParsing -Uri 'http://%HOST%:%PORT%%ENDPOINT%' -TimeoutSec 2 -ErrorAction Stop | Out-Null; exit 0 } catch { exit 1 }" >nul 2>nul
if !errorlevel! equ 0 (
  endlocal
  exit /b 0
)

timeout /t 2 /nobreak >nul
set /a ELAPSED+=2
goto wait_http_loop
