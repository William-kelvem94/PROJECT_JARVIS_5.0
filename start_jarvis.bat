@echo off
REM JARVIS 5.0 Startup Script

REM Ensure we are in the project root
cd /d "%~dp0"

echo Starting JARVIS 5.0...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    exit /b 1
)

REM Check dependencies
python scripts/install/setup_jarvis.py --quick-check
if errorlevel 1 (
    echo Dependencies missing or check failed. Running full setup...
    REM Use --no-scripts to prevent overwriting this script while running
    python scripts/install/setup_jarvis.py --no-scripts
    if errorlevel 1 (
        echo Error: Setup failed. Please check the logs and try again.
        pause
        exit /b 1
    )
)

REM Start JARVIS
python main.py %*
