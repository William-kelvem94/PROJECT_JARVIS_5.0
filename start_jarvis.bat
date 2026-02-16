@echo off
setlocal
cd /d "%~dp0"

echo [SYSTEM] Launching JARVIS 5.0 Professional Edition...
call "scripts\launchers\start_jarvis.bat"
if errorlevel 1 (
    echo [ERROR] Launcher returned an error (exit code %ERRORLEVEL%).
    pause
    exit /b %ERRORLEVEL%
)
