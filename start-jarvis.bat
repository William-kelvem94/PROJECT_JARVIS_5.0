@echo off
setlocal enabledelayedexpansion
REM JARVIS 5.0 Launcher - Windows LIMPO (ASCII)
REM Rode: .\start-jarvis.bat

cd /d %~dp0

echo ==========================================
echo       JARVIS 5.0 - STARTUP SYSTEM v2.0
echo ==========================================

REM Sanity .env
if not exist env\.env (
    echo [ERROR] Crie env\.env do .env.example com suas chaves!
    pause
    exit /b 1
)

REM Backend VENV
if not exist backend\venv (
    echo [INFO] Criando venv...
    cd backend
    python -m venv venv
