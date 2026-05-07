@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI\"
set "LOGS_DIR=%ROOT%logs"
set "LOG_FILE=%LOGS_DIR%\prerequisites-check.log"
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"

echo [%date% %time%] Checking prerequisites > "%LOG_FILE%"

set "FOUND_PYTHON="

for %%P in (
  "%LocalAppData%\Programs\Python\Python311\python.exe"
  "%ProgramFiles%\Python311\python.exe"
  "%ProgramFiles(x86)%\Python311\python.exe"
) do (
  if exist %%~P if not defined FOUND_PYTHON set "FOUND_PYTHON=%%~P"
)

if not defined FOUND_PYTHON (
  where py >nul 2>&1
  if not errorlevel 1 (
    for /f "delims=" %%P in ('py -3.11 -c "import sys; print(sys.executable)" 2^>nul') do set "FOUND_PYTHON=%%P"
  )
)

if not defined FOUND_PYTHON (
  where python >nul 2>&1
  if not errorlevel 1 (
    for /f "delims=" %%P in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "FOUND_PYTHON=%%P"
  )
)

if not defined FOUND_PYTHON (
  echo [ERRO] Python 3.11 nao encontrado.
  echo [INFO] Instale o Python oficial 3.11.x de https://www.python.org/downloads/windows/
  exit /b 1
)

for /f "tokens=2" %%V in ('"%FOUND_PYTHON%" --version 2^>^&1') do set "PYTHON_VERSION=%%V"
echo [OK] Python: %PYTHON_VERSION% em %FOUND_PYTHON%
echo [OK] Python: %PYTHON_VERSION% em %FOUND_PYTHON% >> "%LOG_FILE%"

echo %PYTHON_VERSION% | findstr /B "3.11." >nul
if errorlevel 1 (
  echo [ERRO] Python %PYTHON_VERSION% encontrado, mas o Jarvis requer Python 3.11.x.
  exit /b 1
)

where node >nul 2>&1
if errorlevel 1 (
  echo [WARN] Node.js nao encontrado. O frontend nao sera iniciado automaticamente.
) else (
  for /f "tokens=*" %%i in ('node --version 2^>^&1') do echo [OK] Node.js: %%i
)

where pnpm >nul 2>&1
if errorlevel 1 (
  where corepack >nul 2>&1
  if not errorlevel 1 (
    echo [SETUP] Habilitando pnpm via corepack...
    corepack enable >nul 2>&1
    corepack prepare pnpm@9.15.9 --activate >nul 2>&1
  )
)

where pnpm >nul 2>&1
if errorlevel 1 (
  where npm >nul 2>&1
  if errorlevel 1 (
    echo [WARN] pnpm/npm nao encontrados.
  ) else (
    for /f "tokens=*" %%i in ('npm --version 2^>^&1') do echo [OK] npm: %%i
  )
) else (
  for /f "tokens=*" %%i in ('pnpm --version 2^>^&1') do echo [OK] pnpm: %%i
)

endlocal & set "JARVIS_SYSTEM_PYTHON=%FOUND_PYTHON%" & set "JARVIS_SYSTEM_PYTHON_VERSION=%PYTHON_VERSION%"
exit /b 0
