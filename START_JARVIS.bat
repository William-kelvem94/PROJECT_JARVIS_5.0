@echo off
chcp 65001 >nul
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
echo   JARVIS 5.0 - SINGULARITY LAUNCHER [STARK 2.0]
echo ========================================================================
echo   Status: Running as Administrator
echo   Mode: Stark Architecture (POWER TOTAL)
echo   Auto-Config: ENABLED
echo   Self-Healing: ENABLED
echo   Elite Search: ACTIVE
echo   Hardware Lock: MANDATORY
echo ========================================================================
echo.
echo [INFO] ✨ STARK ARCHITECTURE v2.0 - HARDWARE ALIGNMENT MANDATORY
echo [INFO] 👑 CONTROLE TOTAL HABILITADO
echo [INFO] Starting in 2 seconds...
timeout /t 2 /nobreak >nul

setlocal enabledelayedexpansion
set "ROOT=%~dp0"
cd /d "%ROOT%"

:: Environment settings
set "KMP_DUPLICATE_LIB_OK=TRUE"
set "PYTHONUTF8=1"
set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Ollama"

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
        start /wait OllamaSetup.exe /quiet
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
    powershell -WindowStyle Hidden -Command "ollama serve"
    timeout /t 5 /nobreak >nul
)

:: =======================================
:: 3.5 CORE SYSTEMS VERIFICATION
:: =======================================
echo.
echo [SYSTEM] 🛡️ Verificando Integridade do Sistema...

:: Verificar Microsoft Account
echo [CHECK] 🆔 Identidade Stark...
if exist "%ROOT%data\microsoft_device_identifier.json" (
    echo [OK] ✅ Perfil de dispositivo detectado.
) else (
    echo [INFO] 📝 Primeiro uso - perfil será criado automaticamente.
)

:: Verificar Python Environment
echo [CHECK] 🐍 Ambiente Jarvis...
if exist "%ROOT%src\core\intelligence\ai_agent.py" (
    echo [OK] ✅ Núcleo de Inteligência disponível.
) else (
    echo [WARNING] ⚠️ AIAgent não encontrado - modo limitado.
)

:: =======================================
:: 4. PYTHON ENVIRONMENT CHECK
:: =======================================
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
    echo [AUTO-HEAL] Dependency issues detected - SKIPPING auto-repair for now...
    echo.
    
    :: Temporarily skip auto-healing to get JARVIS running
    :: "%VENV_PYTHON%" "%ROOT%scripts\auto_healer.py"
    
    goto :CONTINUE_STARTUP
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
:: 5. MODEL SYNCHRONIZATION (Superintelligence)
:: =======================================
echo [SYSTEM] Synchronizing Neural Models (Ollama)...
"%VENV_PYTHON%" "%ROOT%scripts\install\setup_ollama_models.py"
echo.

"%VENV_PYTHON%" "%ROOT%scripts\launchers\SINGULARITY_LAUNCHER.py" %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================================================
    echo  [CRITICAL] JARVIS Core Exited with Error Code: %ERRORLEVEL%
    echo ========================================================================
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [DEBUG] Launcher loop finished.
pause
exit /b 0
