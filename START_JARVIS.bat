@echo off
setlocal enabledelayedexpansion

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::  JARVIS 5.0 - SINGULARITY COMMAND CENTER v9.0
::  MILITARY GRADE - ULTIMATE LAUNCHER
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

chcp 65001 >nul 2>&1
title JARVIS 5.0 - SINGULARITY COMMAND CENTER v9.0
color 0B
mode con: cols=120 lines=40

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: GLOBAL ENVIRONMENT
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
set "ROOT=%~dp0"
set "VENV_DIR=%ROOT%venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "LOG_DIR=%ROOT%data\logs"
set "MAX_RETRIES=5"
set "RETRY_COUNT=0"
set "AUTO_REPAIR=1"

:: ML Environment Guards
set "KMP_DUPLICATE_LIB_OK=TRUE"
set "OMP_WAIT_POLICY=PASSIVE"
set "MKL_THREADING_LAYER=INTEL"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: ARGUMENT PARSER
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:parse_args
if "%~1"=="" goto :init
if /i "%~1"=="--repair-pytorch" goto :repair_pytorch
if /i "%~1"=="--safe-mode" set "SAFE_MODE=1"
if /i "%~1"=="--help" goto :show_help
if /i "%~1"=="-h" goto :show_help
shift
goto :parse_args

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: INITIALIZATION
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:init
cd /d "%ROOT%"
cls

echo.
echo ================================================================================
echo                    JARVIS 5.0 - SINGULARITY COMMAND CENTER
echo ================================================================================
echo                          MILITARY GRADE - v9.0
echo ================================================================================
echo.

echo   [SYS] Windows System
echo   [ENV] Python: %VENV_PYTHON%
echo   [ROOT] %ROOT%
echo.

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" 2>nul

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: STAGE 0: DIRECTORY STRUCTURE
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
echo [STAGE 0] Infrastructure Synchronization
echo --------------------------------------------------------------------------------

set "DIRS=data\logs data\faces data\screenshots data\models data\audio\temp data\voice_signatures data\cache data\captures data\exports data\generated_scripts data\memory data\monitoring data\neural_memory data\processed data\temp data\templates data\training_dataset"
for %%D in (%DIRS%) do (
    if not exist "%ROOT%%%D" mkdir "%ROOT%%%D" 2>nul
)
echo   [OK] Directory structure synchronized
echo.

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: STAGE 1: ENVIRONMENT VALIDATION
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
echo [STAGE 1] Environment Validation
echo --------------------------------------------------------------------------------

if not exist "%VENV_PYTHON%" (
    echo   [ERROR] Virtual Environment Missing
    if "%AUTO_REPAIR%"=="1" (
        echo   [AUTO-REPAIR] Running installer...
        python "%ROOT%scripts\install\total_installer.py"
        if !ERRORLEVEL! NEQ 0 (
            echo   [FATAL] Failed to create virtual environment
            pause
            exit /b 1
        )
    ) else (
        echo   [ACTION] Run: python scripts\install\total_installer.py
        pause
        exit /b 1
    )
)

echo   [OK] Python Environment: %VENV_PYTHON%
echo.

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: STAGE 2: DEPENDENCY GUARDS
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
echo [STAGE 2] Neural Engine Dependency Guards
echo --------------------------------------------------------------------------------

:: Check NumPy version
"%VENV_PYTHON%" -c "import numpy; exit(0 if int(numpy.__version__.split('.')[0]) < 2 else 1)" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo   [WARN] NumPy 2.x detected - downgrading to 1.26.4...
    "%VENV_PYTHON%" -m pip install "numpy==1.26.4" --force-reinstall --quiet
    echo   [OK] NumPy fixed
)

:: Check for crash flag
if exist "%LOG_DIR%\jarvis_crash.flag" (
    echo   [WARN] Previous crash detected
    del "%LOG_DIR%\jarvis_crash.flag" >nul 2>&1
)

echo   [OK] Dependencies validated
echo.

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: STAGE 3: PRE-FLIGHT VALIDATION
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
echo [STAGE 3] Pre-Flight System Check
echo --------------------------------------------------------------------------------

if exist "%ROOT%scripts\install\pre_flight_check.py" (
    "%VENV_PYTHON%" "%ROOT%scripts\install\pre_flight_check.py"
    if !ERRORLEVEL! NEQ 0 (
        echo   [ERROR] Pre-flight validation failed
        if "%AUTO_REPAIR%"=="1" (
            echo   [AUTO-REPAIR] Attempting repair...
            "%VENV_PYTHON%" "%ROOT%scripts\install\total_installer.py" --repair
        ) else (
            pause
            exit /b 1
        )
    )
) else (
    echo   [WARN] Pre-flight script not found - skipping
)

echo   [OK] Pre-flight checks passed
echo.

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: STAGE 4: LAUNCH SEQUENCE
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
echo.
echo ================================================================================
echo                        JARVIS SINGULARITY CORE ONLINE
echo ================================================================================
echo      Multi-Threaded Neural Engine  -  Self-Healing Architecture
echo ================================================================================
echo.

echo   [RESOURCES] Initializing system resources...
echo.

:: Toast notification (silent fail)
powershell -NoProfile -Command "try { New-BurntToastNotification -Text 'JARVIS 5.0', 'Singularity Core Initializing...' -ErrorAction SilentlyContinue } catch {}" >nul 2>&1

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: MAIN EXECUTION LOOP
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:launch_loop
set /a RETRY_COUNT+=1
echo [%TIME%] SYSTEM PULSE (Attempt !RETRY_COUNT!/%MAX_RETRIES%)

"%VENV_PYTHON%" main.py %*
set "EXIT_CODE=%ERRORLEVEL%"

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: EXIT CODE HANDLER
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
if %EXIT_CODE% EQU 0 (
    echo.
    echo ================================================================================
    echo                            GRACEFUL SHUTDOWN
    echo ================================================================================
    echo   [OK] System shut down normally
    timeout /t 3
    exit /b 0
)

if %EXIT_CODE% EQU 130 (
    echo.
    echo ================================================================================
    echo                          MANUAL INTERRUPTION
    echo ================================================================================
    echo   [OK] User-initiated shutdown
    timeout /t 3
    exit /b 0
)

:: CRASH DETECTED
echo %date% %time% - Crash Code %EXIT_CODE% > "%LOG_DIR%\jarvis_crash.flag"
echo.
echo   [ERROR] System crash detected - Exit Code %EXIT_CODE%

if "%AUTO_REPAIR%"=="1" (
    echo   [AUTO-REPAIR] Analyzing crash...
    "%VENV_PYTHON%" -c "import numpy; exit(0 if int(numpy.__version__.split('.')[0]) < 2 else 1)" 2>nul
    if !ERRORLEVEL! NEQ 0 (
        echo   [AUTO-REPAIR] Fixing NumPy conflict...
        "%VENV_PYTHON%" -m pip install "numpy==1.26.4" --force-reinstall --quiet
    )
)

if !RETRY_COUNT! LEQ %MAX_RETRIES% (
    echo   [RECOVERY] Hot-restart in 5 seconds...
    timeout /t 5 /nobreak >nul
    goto :launch_loop
) else (
    echo.
    echo ================================================================================
    echo                       FATAL ERROR - MAX RETRIES EXCEEDED
    echo ================================================================================
    echo   [CRITICAL] System stability compromised after %MAX_RETRIES% attempts
    echo   [SOLUTION] Run: START_JARVIS.bat --repair-pytorch
    echo.
    pause
    exit /b %EXIT_CODE%
)

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: REPAIR FUNCTION
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:repair_pytorch
cls
echo.
echo ================================================================================
echo                  EMERGENCY REPAIR: PYTORCH ECOSYSTEM
echo ================================================================================
echo.

if not exist "%VENV_PYTHON%" (
    echo   [ERROR] Python environment not found
    pause
    exit /b 1
)

echo   [1/4] Purging corrupted installations...
"%VENV_PYTHON%" -m pip uninstall torch torchvision torchaudio numpy -y

echo   [2/4] Installing stabilized NumPy 1.26.4...
"%VENV_PYTHON%" -m pip install "numpy==1.26.4" --force-reinstall

echo   [3/4] Installing PyTorch CPU (stable)...
"%VENV_PYTHON%" -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo   [4/4] Verifying integrity...
"%VENV_PYTHON%" -c "import torch; import numpy; print('Success: Torch', torch.__version__, '- NumPy', numpy.__version__)"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================================================
    echo                          REPAIR SUCCESSFUL
    echo ================================================================================
    echo   [SUCCESS] Neural engine restored to operational state
    echo.
    timeout /t 3
    goto :init
) else (
    echo.
    echo ================================================================================
    echo                            REPAIR FAILED
    echo ================================================================================
    echo   [ERROR] Check internet connection and permissions
    echo.
    pause
    exit /b 1
)

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: HELP MENU
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:show_help
cls
echo.
echo ================================================================================
echo                    JARVIS 5.0 - SINGULARITY COMMAND CENTER
echo ================================================================================
echo.
echo USAGE:
echo   START_JARVIS.bat [OPTIONS]
echo.
echo OPTIONS:
echo   --help, -h           Show this help message
echo   --repair-pytorch     Emergency repair for PyTorch/NumPy issues
echo   --safe-mode          Start with minimal features
echo.
echo EXAMPLES:
echo   # Normal startup
echo   START_JARVIS.bat
echo.
echo   # Repair corrupted dependencies
echo   START_JARVIS.bat --repair-pytorch
echo.
echo ================================================================================
echo.
pause
exit /b 0
