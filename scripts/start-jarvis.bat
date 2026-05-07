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

if not exist "%ROOT%.venv\Scripts\activate.bat" (
  echo [VENV] Ambiente virtual ausente. Criando...
  python -m venv "%ROOT%.venv"
  if errorlevel 1 exit /b 1
)

call "%ROOT%.venv\Scripts\activate.bat"
if errorlevel 1 exit /b 1

if not exist "%ROOT%.venv\Scripts\python.exe" (
  echo [ERRO] Python do venv nao encontrado.
  exit /b 1
)

call "%ROOT%scripts\launch-backend.bat"
if errorlevel 1 exit /b 1

call "%ROOT%scripts\launch-frontend.bat"
exit /b 0
