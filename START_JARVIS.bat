@echo off
:: JARVIS 5.0 - SINULARITY LAUNCHER v9.4 (Pure ASCII Mode)
:: Use this if the system closes unexpectedly.

echo [DEBUG] Launcher started. Press any key to engage JARVIS...
pause

setlocal enabledelayedexpansion
set "ROOT=%~dp0"
cd /d "%ROOT%"

:: Environment settings
set "KMP_DUPLICATE_LIB_OK=TRUE"
set "PYTHONUTF8=1"

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
    echo [WARNING] Some critical dependencies are missing!
    echo.
    set /p install_choice="Do you want to install missing dependencies now? (Y/N): "
    
    if /i "%install_choice%"=="Y" (
        echo [SYSTEM] Installing missing dependencies...
        "%VENV_PYTHON%" -m pip install onnxruntime==1.17.0 --quiet
        "%VENV_PYTHON%" -m pip install -r "%ROOT%requirements.txt" --quiet
        echo [OK] Dependencies installed. Revalidating...
        "%VENV_PYTHON%" "%ROOT%scripts\validate_dependencies.py"
        
        if %ERRORLEVEL% NEQ 0 (
            echo [ERROR] Some dependencies still missing. Please run INSTALL_JARVIS.bat
            pause
            exit /b 1
        )
    ) else (
        echo [ABORT] Cannot start without critical dependencies.
        pause
        exit /b 1
    )
)

echo [OK] All dependencies validated.
echo.

"%VENV_PYTHON%" "%ROOT%SINGULARITY_LAUNCHER.py" %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo "[CRITICAL] System crash detected (Exit Code %ERRORLEVEL%)"
    pause
    exit /b %ERRORLEVEL%
)

exit /b 0
