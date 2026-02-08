@echo off
setlocal enabledelayedexpansion

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::  JARVIS 5.0 - SINGULARITY COMMAND CENTER v9.0
::  MILITARY GRADE - ULTIMATE LAUNCHER WRAPPER
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

chcp 65001 >nul 2>&1
title JARVIS 5.0 - SINGULARITY COMMAND CENTER v9.0
color 0B
mode con: cols=120 lines=40

:: Global Environment Guards
set "KMP_DUPLICATE_LIB_OK=TRUE"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

:: Path Setup
set "ROOT=%~dp0"
cd /d "%ROOT%"

:: Virtual Environment Check
set "VENV_PYTHON=%ROOT%venv\Scripts\python.exe"

if not exist "%VENV_PYTHON%" (
    echo.
    echo [ERROR] Virtual Environment not found at: %VENV_PYTHON%
    echo [ACTION] Please run 'setup_environment.bat' or install requirements manually.
    echo.
    pause
    exit /b 1
)

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: DELEGATE TO SINGULARITY ENGINE
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
echo.
echo [SYSTEM] Engaging Singularity Launcher Engine...
echo.

"%VENV_PYTHON%" "%ROOT%SINGULARITY_LAUNCHER.py" %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [CRITICAL] Singularity Engine reported a non-zero exit code: %ERRORLEVEL%
    echo [RECOVERY] Check logs in data/logs/launcher.log
    echo.
    pause
    exit /b %ERRORLEVEL%
)

exit /b 0
