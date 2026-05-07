@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI\"
set "LOGS_DIR=%ROOT%logs"
set "LOG_FILE=%LOGS_DIR%\prerequisites-check.log"
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"

echo [%date% %time%] Checking prerequisites > "%LOG_FILE%"

where python >nul 2>&1
if errorlevel 1 (
  echo [ERRO] Python nao encontrado
  exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo [OK] Python: %PYTHON_VERSION%

where node >nul 2>&1
if errorlevel 1 (
  echo [WARN] Node.js nao encontrado
) else (
  for /f "tokens=*" %%i in ('node --version 2^>^&1') do echo [OK] Node.js: %%i
)

where pnpm >nul 2>&1
if errorlevel 1 (
  where npm >nul 2>&1
  if errorlevel 1 (
    echo [WARN] pnpm/npm nao encontrados
  ) else (
    for /f "tokens=*" %%i in ('npm --version 2^>^&1') do echo [OK] npm: %%i
  )
) else (
  for /f "tokens=*" %%i in ('pnpm --version 2^>^&1') do echo [OK] pnpm: %%i
)

exit /b 0
