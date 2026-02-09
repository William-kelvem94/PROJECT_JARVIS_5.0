@echo off
chcp 65001 >nul
title JARVIS SINGULARITY - HUD LAUNCHER
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
echo ║              S I N G U L A R I T Y   v2.0                 ║
echo ║           HUD Transparente + AI Agent                     ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

:: Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python não encontrado!
    echo.
    echo Instale Python 3.10+ de: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Verificar PyQt6
echo [INFO] Verificando PyQt6...
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
    echo [OK] PyQt6 instalado!
)

:: Iniciar JARVIS Singularity
echo.
echo [OK] Iniciando JARVIS Singularity com HUD...
echo.
python main_singularity.py

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha ao iniciar!
    echo.
    echo Verifique o arquivo jarvis_singularity.log para detalhes.
    pause
    exit /b 1
)
