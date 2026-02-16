@echo off
setlocal
cd /d "%~dp0"

echo [SYSTEM] Redirecting to Professional Launcher...
call "scripts\launchers\start_jarvis.bat"
if errorlevel 1 (
    echo [ERROR] Script "scripts\launchers\start_jarvis.bat" returned an error (exit code %ERRORLEVEL%).
    exit /b %ERRORLEVEL%
)
