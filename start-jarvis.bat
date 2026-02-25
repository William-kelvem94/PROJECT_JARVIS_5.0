@echo off
REM Batch script to launch backend and frontend for Jarvis project on Windows.
REM Usage: double-click this file or run from a command prompt.

REM ensure we are in the repository root
cd /d %~dp0

REM -- prepare backend environment if needed --
if not exist backend\venv\Scripts\activate.bat (
    echo Creating Python virtual environment...
    python -m venv backend\venv
    call backend\venv\Scripts\activate.bat
    echo Installing Python dependencies...
    pip install --upgrade pip
    pip install -r backend\app\requirements.txt
    deactivate
)

REM load environment variables from env\.env into current process
for /f "usebackq tokens=1,2 delims==" %%A in ("%~dp0env\.env") do (
    if not "%%A"=="#" set "%%A=%%B"
)

REM start backend in new window (env vars inherited)
start "Jarvis Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && echo Starting backend... && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM start frontend in new window (env vars inherited)
start "Jarvis Frontend" cmd /k "cd /d %~dp0frontend && echo Starting frontend... && npx pnpm dev"

echo Launched backend and frontend. Check the two new windows for logs.
pause