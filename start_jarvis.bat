@echo off
REM JARVIS 5.0 Startup Script

echo Starting JARVIS 5.0...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    exit /b 1
)

REM Check dependencies
python setup_jarvis.py --quick-check

REM Start JARVIS
python main.py %*
