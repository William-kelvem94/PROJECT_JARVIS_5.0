@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI\"
set "LOGS_DIR=%ROOT%logs"
set "BOOT_LOG=%LOGS_DIR%\boot.log"

if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"
echo [%date% %time%] Starting JARVIS boot > "%BOOT_LOG%"

echo.
echo ================================================================
echo   JARVIS 5.0 - OMEGA ADAPTIVE ORCHESTRATOR
echo ================================================================
echo [OMEGA] Raiz do projeto: %ROOT%
echo [OMEGA] Raiz do projeto: %ROOT%>>"%BOOT_LOG%"
echo.

if not exist "%ROOT%scripts\check-prerequisites.bat" (
  echo [ERRO] scripts nao encontrados em %ROOT%
  exit /b 1
)

call "%ROOT%scripts\check-prerequisites.bat"
if errorlevel 1 (
  echo [ERRO] Prerequisitos falharam. Veja %ROOT%logs\prerequisites-check.log
  echo [ERRO] Prerequisitos falharam. Veja %ROOT%logs\prerequisites-check.log>>"%BOOT_LOG%"
  exit /b 1
)

call "%ROOT%scripts\detect-hardware.bat"
if errorlevel 1 (
  echo [ERRO] Detectacao de hardware falhou.
  echo [ERRO] Detectacao de hardware falhou.>>"%BOOT_LOG%"
  exit /b 1
)

if not exist "%ROOT%.env" (
  if exist "%ROOT%.env.example" (
    echo [CONFIG] Criando .env a partir de .env.example
    copy "%ROOT%.env.example" "%ROOT%.env" >nul
  ) else (
    echo [ERRO] .env.example nao encontrado. Crie .env manualmente.
    exit /b 1
  )
)

echo [CONFIG] Carregando variaveis de ambiente de .env
for /f "usebackq tokens=1,* delims==" %%a in ("%ROOT%.env") do (
  set "line=%%a"
  if not "!line:~0,1!"=="#" if not "!line!"=="" set "%%a=%%b"
)

call "%ROOT%scripts\setup-venv.bat"
if errorlevel 1 (
  echo [ERRO] Setup da venv falhou. Veja %ROOT%logs\venv-setup.log
  echo [ERRO] Setup da venv falhou. Veja %ROOT%logs\venv-setup.log>>"%BOOT_LOG%"
  exit /b 1
)

if exist "%ROOT%frontend\package.json" (
  where pnpm >nul 2>&1
  if not errorlevel 1 (
    if not exist "%ROOT%frontend\node_modules" (
      echo [FRONTEND] Instalando dependencias do frontend...
      pushd "%ROOT%frontend"
      pnpm install --frozen-lockfile
      if errorlevel 1 (
        popd
        exit /b 1
      )
      popd
    )
  )
)

call "%ROOT%scripts\launch-backend.bat"
if errorlevel 1 (
  echo [ERRO] Backend nao iniciou. Veja %ROOT%logs\backend-startup.log
  echo [ERRO] Backend nao iniciou. Veja %ROOT%logs\backend-startup.log>>"%BOOT_LOG%"
  exit /b 1
)

call "%ROOT%scripts\launch-frontend.bat"
if errorlevel 1 (
  echo [WARN] Frontend nao iniciou, mas o backend ficou online.
  echo [WARN] Frontend nao iniciou, mas o backend ficou online.>>"%BOOT_LOG%"
)
echo [OK] JARVIS boot concluido.
echo [OK] JARVIS boot concluido.>>"%BOOT_LOG%"
exit /b %errorlevel%
