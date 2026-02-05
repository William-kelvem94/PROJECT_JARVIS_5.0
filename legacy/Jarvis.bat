@echo off
chcp 65001 >nul
title JARVIS 5.0 - SINGULARITY LAUNCHER
color 0B

cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║         ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗          ║
echo ║         ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝          ║
echo ║         ██║███████║██████╔╝██║   ██║██║███████╗          ║
echo ║    ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║          ║
echo ║    ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║          ║
echo ║     ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝          ║
echo ║                                                            ║
echo ║              S I N G U L A R I T Y   v1.0                 ║
echo ║        Just A Rather Very Intelligent System              ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo [INFO] Iniciando interface visual...
echo.

:: Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python não encontrado!
    echo.
    echo Por favor, instale Python 3.10+ de: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Verificar PyQt6
python -c "import PyQt6" >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] PyQt6 não encontrado!
    echo.
    echo Instalando PyQt6...
    pip install PyQt6
    
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao instalar PyQt6!
        pause
        exit /b 1
    )
)

:: Iniciar GUI
echo [OK] Iniciando JARVIS GUI...
echo.
python gui\main_window.py

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha ao iniciar GUI!
    pause
    exit /b 1
)
