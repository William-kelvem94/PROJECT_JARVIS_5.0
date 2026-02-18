@echo off
setlocal EnableDelayedExpansion

:: ==================================================================================
:: JARVIS 5.0 - Professional Launcher
:: ==================================================================================
:: Sets up environment, verifies dependencies, and launches the core system.
:: ==================================================================================

title JARVIS 5.0 - Singularity
cd /d "%~dp0\..\.."

:: 1. Environment Configuration
:: ----------------------------------------------------------------------------------
chcp 65001 >nul 2>&1
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"
set "CUDA_LAUNCH_BLOCKING=1"
set "VENV_DIR=venv"
set "JARVIS_ENV=production"

:: 2. Virtual Environment Check
:: ----------------------------------------------------------------------------------
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [ERROR] Virtual Environment not found!
    echo [INFO]  Please run 'scripts/install/install_system.py' first.
    pause
    exit /b 1
)

echo [INFO] Activating Neural Environment...
call "%VENV_DIR%\Scripts\activate.bat"

:: 3. Launch System
:: ----------------------------------------------------------------------------------
echo [INFO] Initializing Core Systems...
echo.
set "PYTHONPATH=%CD%"
python main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [CRITICAL] System crashed with error code %ERRORLEVEL%.
    echo [INFO]     Review 'data/logs/jarvis.log' for details.
    pause
)

deactivate
