@echo off
chcp 65001 > nul
title 🚀 JARVIS 5.0 - SINGULARITY
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                JARVIS 5.0 - SINGULARITY                      ║
echo ║             Starting Integrated AI Systems...                ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Set environment variables
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

:: Ensure we are in the project root
cd /d "%~dp0"

:: Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found!
    echo Please run JARVIS_AUTO.bat first to install dependencies.
    pause
    exit /b 1
)

echo 🤖 Jarvis is waking up...
echo 📝 Logs: data/logs/jarvis_singularity.log
echo.

:: Launch main.py
venv\Scripts\python.exe main.py

if errorlevel 1 (
    echo.
    echo ❌ JARVIS crashed or was stopped with errors.
    pause
)
