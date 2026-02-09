@echo off
:: JARVIS 5.0 - UNIVERSAL INSTALLER v1.4 (Pure ASCII Mode)
:: Use this if the system closes unexpectedly.

:: Check for silent mode
if "%~1"=="/silent" (
    echo [INFO] Running in SILENT/AUTO mode...
    set SILENT_MODE=1
) else (
    echo [DEBUG] Script started. Press ENTER to begin setup...
    pause
    set SILENT_MODE=0
)

echo.
echo ==========================================================================
echo                 JARVIS 5.0 - INSTALLATION PROTOCOL
echo ==========================================================================
echo.

set "ROOT=%~dp0"
cd /d "%ROOT%"

echo [INFO] Project Root: %ROOT%

:: 1. Check Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found in PATH. 
    echo Please install Python 3.11 and check "Add to PATH".
    if "%SILENT_MODE%"=="0" pause
    exit /b 1
)

:: 2. Create VENV
if exist "%ROOT%venv\Scripts\python.exe" (
    echo [INFO] VENV already exists.
    goto :INSTALL_DEPS
)

echo [INFO] Creating Virtual Environment (VENV)...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to create VENV.
    if "%SILENT_MODE%"=="0" pause
    exit /b 1
)

:INSTALL_DEPS
:: 3. Run Total Installer
echo [INFO] Syncing neural libraries...
echo [WARN] This may take several minutes.
echo.

if not exist "%ROOT%scripts\install\total_installer.py" (
    echo [ERROR] total_installer.py not found at:
    echo %ROOT%scripts\install\total_installer.py
    if "%SILENT_MODE%"=="0" pause
    exit /b 1
)

"%ROOT%venv\Scripts\python.exe" "%ROOT%scripts\install\total_installer.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [CRITICAL] Installation failed. 
    echo Check scripts\install\total_installer.log for details.
    if "%SILENT_MODE%"=="0" pause
    exit /b 1
)

echo.
echo ==========================================================================
echo    SYSTEM SYNCED: JARVIS IS ONLINE
echo ==========================================================================
echo.
if "%SILENT_MODE%"=="0" pause
exit /b 0
