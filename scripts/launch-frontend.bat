@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

if not defined ROOT (
  echo [WARN] ROOT nao definida. Use start-jarvis.bat
  exit /b 0
)

set "LOGS_DIR=%ROOT%logs"
set "LOG_FILE=%LOGS_DIR%\frontend-startup.log"
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"
echo [%date% %time%] Starting JARVIS frontend > "%LOG_FILE%"

if not exist "%ROOT%frontend\package.json" (
  echo [WARN] Frontend nao encontrado.
  exit /b 0
)

if not defined PORT set "PORT=3000"

where pnpm >nul 2>&1
if not errorlevel 1 (
  set "PKG_MANAGER=pnpm"
) else (
  where npm >nul 2>&1
  if errorlevel 1 (
    echo [WARN] pnpm/npm nao encontrados.
    exit /b 0
  )
  set "PKG_MANAGER=npm"
)

pushd "%ROOT%frontend"
if errorlevel 1 exit /b 0

echo [FRONTEND] Starting http://127.0.0.1:%PORT%
if "%PKG_MANAGER%"=="pnpm" (
  start "JARVIS_FRONTEND" /B cmd /c "pnpm dev --hostname 127.0.0.1 >> "%LOG_FILE%" 2>&1"
) else (
  start "JARVIS_FRONTEND" /B cmd /c "npm run dev -- --hostname 127.0.0.1 >> "%LOG_FILE%" 2>&1"
)

popd
call :wait_port 127.0.0.1 %PORT% 90
if errorlevel 1 (
  echo [WARN] Frontend nao respondeu em 90s. Backend continua ativo.
  echo [WARN] Frontend timeout >> "%LOG_FILE%"
  exit /b 0
)

echo [OK] Frontend online.
echo [OK] Frontend online >> "%LOG_FILE%"
exit /b 0

:wait_port
setlocal EnableExtensions EnableDelayedExpansion
set "HOST=%~1"
set "PORT=%~2"
set "TIMEOUT=%~3"
set /a ELAPSED=0

:wait_port_loop
if !ELAPSED! geq !TIMEOUT! (
  endlocal
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $t = [Net.Sockets.TcpClient]::new(); $ok = $t.ConnectAsync('%HOST%', %PORT%).Wait(2000); $t.Close(); if ($ok) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>nul
if !errorlevel! equ 0 (
  endlocal
  exit /b 0
)

timeout /t 2 /nobreak >nul
set /a ELAPSED+=2
goto wait_port_loop
