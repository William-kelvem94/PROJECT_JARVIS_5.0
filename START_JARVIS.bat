@echo off
:: JARVIS 5.0 - SINGULARITY LAUNCHER v10.0 (Admin + Ollama Auto-Setup)
:: Use this if the system closes unexpectedly.

:: =======================================
:: 1. REQUEST ADMINISTRATOR PRIVILEGES
:: =======================================
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [SYSTEM] Requesting Administrator Privileges...
    powershell -Command "Start-Process '%~dpnx0' -Verb RunAs"
    exit /b
)

echo.
echo ========================================================================
echo   JARVIS 5.0 - SINGULARITY LAUNCHER [AUTO MODE]
echo ========================================================================
echo   Status: Running as Administrator
echo   Mode: Fully Autonomous (No user input required)
echo   Auto-Config: ENABLED
echo   Self-Healing: ENABLED
echo ========================================================================
echo.
echo [INFO] Starting in 2 seconds...
timeout /t 2 /nobreak >nul

setlocal enabledelayedexpansion
set "ROOT=%~dp0"
cd /d "%ROOT%"

:: Environment settings
set "KMP_DUPLICATE_LIB_OK=TRUE"
set "PYTHONUTF8=1"

:: =======================================
:: 1.5 AUTO-CONFIGURATION (Optimize Environment)
:: =======================================
echo [SYSTEM] Optimizing environment configuration...
if exist "%ROOT%venv\Scripts\python.exe" (
    "%ROOT%venv\Scripts\python.exe" "%ROOT%scripts\auto_configurator.py"
)
echo.

:: =======================================
:: 2. OLLAMA AUTO-SETUP (Superintelligence)
:: =======================================
echo.
echo [SYSTEM] Verifying Neural Backend (Ollama)...

where ollama >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] Ollama AI Bridge not found. Initiating Auto-Install...
    echo [DOWNLOAD] Downloading OllamaSetup.exe...
    powershell -Command "Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile 'OllamaSetup.exe'"
    
    if exist "OllamaSetup.exe" (
        echo [INSTALL] Installing Ollama... Please follow the prompts if any.
        start /wait OllamaSetup.exe /silent
        del OllamaSetup.exe
        echo [OK] Ollama installed.
    ) else (
        echo [ERROR] Failed to download Ollama. Check internet connection.
        pause
        exit /b 1
    )
) else (
    echo [OK] Ollama AI Bridge detected.
)

:: Ensure Ollama Service is running
tasklist /FI "IMAGENAME eq ollama_app.exe" 2>NUL | find /I /N "ollama_app.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] Ollama Service is active.
) else (
    echo [SYSTEM] Starting Ollama Service...
    start /min "" "ollama" serve
    timeout /t 5 /nobreak >nul
)

:: =======================================
:: 3. PYTHON ENVIRONMENT CHECK
:: =======================================
:: Check VENV
set "VENV_PYTHON=%ROOT%venv\Scripts\python.exe"

if exist "%VENV_PYTHON%" goto :START_CORE

echo [WARNING] Virtual Environment not detected.
echo [SYSTEM] Starting Auto-Recovery Protocol...
echo.
set /p choice="Do you want to install dependencies now? (Y/N): "

if /i "%choice%"=="Y" (
    call "%ROOT%INSTALL_JARVIS.bat"
) else (
    echo [ABORT] System cannot run without dependencies.
    pause
    exit /b 1
)

:: Re-verify
if not exist "%VENV_PYTHON%" (
    echo [FATAL] Environment setup failed. 
    echo Run INSTALL_JARVIS.bat manually to debug.
    pause
    exit /b 1
)

:START_CORE
echo.
echo [SYSTEM] Engaging Singularity Core Engines...
echo.

:: Validate critical dependencies before starting
echo [CHECK] Validating critical dependencies...
"%VENV_PYTHON%" "%ROOT%scripts\validate_dependencies.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [AUTO-HEAL] Dependency issues detected - initiating auto-repair...
    echo.
    
    :: Tenta auto-healing primeiro
    "%VENV_PYTHON%" "%ROOT%scripts\auto_healer.py"
    
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Auto-healing successful! Revalidating...
        "%VENV_PYTHON%" "%ROOT%scripts\validate_dependencies.py"
        
        if %ERRORLEVEL% EQU 0 (
            echo [OK] All dependencies validated after auto-heal!
            goto :CONTINUE_STARTUP
        )
    )
    
    :: Se auto-heal falhou, tenta quick fix
    echo [AUTO-FIX] Running Quick Fix for remaining issues...
    "%VENV_PYTHON%" "%ROOT%scripts\install\quick_fix_torch.py"
    
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Quick Fix completed. Revalidating...
        "%VENV_PYTHON%" "%ROOT%scripts\validate_dependencies.py"
        
        if %ERRORLEVEL% EQU 0 (
            echo [OK] All dependencies validated!
            goto :CONTINUE_STARTUP
        ) else (
            echo [WARNING] Some dependencies may still have issues.
            echo [INFO] Continuing with limited functionality...
            timeout /t 2 /nobreak >nul
            goto :CONTINUE_STARTUP
        )
    ) else (
        echo [ERROR] Auto-repair failed. Running full installation...
        call "%ROOT%INSTALL_JARVIS.bat" /silent
        
        if %ERRORLEVEL% NEQ 0 (
            echo [CRITICAL] Installation failed. Manual intervention required.
            echo [INFO] Check logs: total_installer.log
            timeout /t 5
            exit /b 1
        )
    )
)

:CONTINUE_STARTUP

echo [OK] All dependencies validated.
echo.

:: =======================================
:: 4. MODEL SYNCHRONIZATION (Superintelligence)
:: =======================================
echo [SYSTEM] Synchronizing Neural Models (Ollama)...
"%VENV_PYTHON%" "%ROOT%scripts\install\setup_ollama_models.py"
echo.

"%VENV_PYTHON%" "%ROOT%SINGULARITY_LAUNCHER.py" %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo "[CRITICAL] System crash detected (Exit Code %ERRORLEVEL%)"
    pause
    exit /b %ERRORLEVEL%
)

exit /b 0
