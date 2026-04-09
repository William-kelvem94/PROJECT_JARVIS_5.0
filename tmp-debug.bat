@echo off
cd /d "%~dp0"
echo DEBUG1
cd frontend
pnpm install
echo DEBUG2
pause
