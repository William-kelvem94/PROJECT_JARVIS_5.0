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

"%VENV_PYTHON%" "%ROOT%SINGULARITY_LAUNCHER.py" %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [CRITICAL] System crash detected (Exit Code %ERRORLEVEL%).
    pause
    exit /b %ERRORLEVEL%
)

exit /b 0
