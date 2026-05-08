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
  if exist "%ROOT%.env.example" copy "%ROOT%.env.example" "%ROOT%.env" >nul
)

if not defined JARVIS_VAULT_ROOT set "JARVIS_VAULT_ROOT=D:\DOCUMENTOS\GitHub\Will-obsidian"
if not defined OBSIDIAN_VAULT_PATH set "OBSIDIAN_VAULT_PATH=%JARVIS_VAULT_ROOT%"
if not defined JARVIS_KB_PATH set "JARVIS_KB_PATH=%JARVIS_VAULT_ROOT%\JARVIS"

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
