@echo off
setlocal enabledelayedexpansion
REM ============================================================================
REM 🦎 INICIAR ADAPTATIVO - JARVIS Chameleon Launcher
REM ============================================================================
REM Smart launcher that:
REM 1. Checks Python installation
REM 2. Runs adaptive setup (hardware detection + dependency install)
REM 3. Launches JARVIS with appropriate features
REM 4. Handles errors gracefully
REM
REM Author: JARVIS Singularity Team
REM Version: 1.0.0
REM ============================================================================

cls
echo.
echo ============================================================================
echo    🦎 JARVIS CHAMELEON - ADAPTIVE LAUNCHER
echo ============================================================================
echo.

REM ============================================================================
REM Step 1: Check if Python is installed
REM ============================================================================
echo [1/3] Checking Python installation...

python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Python not found!
    echo.
    echo Please install Python 3.8+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo    ✓ Python %PYTHON_VERSION% found
echo.

REM ============================================================================
REM Step 2: Run Adaptive Setup (Hardware Detection + Dependencies)
REM ============================================================================
echo [2/3] Running adaptive setup...
echo    This will detect your hardware and install appropriate dependencies.
echo.

python setup_adaptive.py
set SETUP_EXIT=%ERRORLEVEL%

if !SETUP_EXIT! neq 0 (
    echo.
    echo ⚠️  Setup completed with warnings.
    echo    Some features may not be available.
    echo.
    choice /C YN /M "Continue anyway?"
    if errorlevel 2 (
        echo    Launch cancelled.
        pause
        exit /b !SETUP_EXIT!
    )
)

echo.
echo    ✓ Setup complete
echo.

REM ============================================================================
REM Step 3: Launch JARVIS
REM ============================================================================
echo [3/3] Launching JARVIS Singularity...
echo.
echo ════════════════════════════════════════════════════════════════════════
echo    JARVIS is starting...
echo    Press Ctrl+C to stop.
echo ════════════════════════════════════════════════════════════════════════
echo.

python main_singularity_integrated.py
set JARVIS_EXIT=%ERRORLEVEL%

echo.
echo ════════════════════════════════════════════════════════════════════════
if !JARVIS_EXIT! equ 0 (
    echo    ✅ JARVIS shut down gracefully
) else if !JARVIS_EXIT! equ 130 (
    echo    ⚠️  JARVIS terminated by user ^(Ctrl+C^)
) else (
    echo    ❌ JARVIS exited with error code: !JARVIS_EXIT!
    echo.
    echo    Check logs in data/logs/ for details.
)
echo ════════════════════════════════════════════════════════════════════════
echo.

pause
exit /b !JARVIS_EXIT!