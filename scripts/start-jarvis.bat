@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI\"

echo.
echo ================================================================
echo   JARVIS 5.0 - OMEGA ADAPTIVE ORCHESTRATOR
echo ================================================================
echo [OMEGA] Raiz do projeto: %ROOT%
echo.

if not exist "%ROOT%scripts\check-prerequisites.bat" (
  echo [ERRO] scripts nao encontrados em %ROOT%
  exit /b 1
)

call "%ROOT%scripts\check-prerequisites.bat"
if errorlevel 1 exit /b 1

call "%ROOT%scripts\detect-hardware.bat"
if errorlevel 1 exit /b 1

if not exist "%ROOT%.env" (
  if exist "%ROOT%.env.example" copy "%ROOT%.env.example" "%ROOT%.env" >nul
)

if not defined JARVIS_VAULT_ROOT set "JARVIS_VAULT_ROOT=D:\DOCUMENTOS\GitHub\Will-obsidian"
if not defined OBSIDIAN_VAULT_PATH set "OBSIDIAN_VAULT_PATH=%JARVIS_VAULT_ROOT%"
if not defined JARVIS_KB_PATH set "JARVIS_KB_PATH=%JARVIS_VAULT_ROOT%\JARVIS"

call "%ROOT%scripts\setup-venv.bat"
if errorlevel 1 exit /b 1

if exist "%ROOT%package.json" (
  where pnpm >nul 2>&1
  if not errorlevel 1 (
    if not exist "%ROOT%node_modules" (
      echo [FRONTEND] Instalando dependencias pnpm...
      pushd "%ROOT%"
      pnpm install --frozen-lockfile
      if errorlevel 1 exit /b 1
      popd
    )
  )
)

call "%ROOT%scripts\launch-backend.bat"
if errorlevel 1 exit /b 1

call "%ROOT%scripts\launch-frontend.bat"
exit /b %errorlevel%
