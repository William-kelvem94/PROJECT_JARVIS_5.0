@echo off
chcp 65001 > nul
title 🚀 JARVIS 5.0 - INSTALADOR TOTAL
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                   JARVIS 5.0 - INSTALADOR TOTAL              ║
echo ║               Instala TUDO de uma vez!                      ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo Baixe e instale Python 3.11+ de: https://python.org
    pause
    exit /b 1
)

echo ✅ Python detectado
echo.

:: Pergunta ao usuário
echo ⚠️  ATENÇÃO: Este instalador pode:
echo   1. Instalar Visual C++ Build Tools (~4GB)
echo   2. Instalar TODAS as dependências do JARVIS
echo   3. Demorar 15-30 minutos
echo.

:: Em modo automatizado, aceitamos por padrão ou pedimos confirmação
set /p choice="Deseja continuar? (S/N): "

if /i "%choice%" neq "S" (
    echo ❌ Instalação cancelada
    pause
    exit /b 0
)

echo.
echo 🚀 Iniciando instalação TOTAL...
echo 📝 Log detalhado: total_installer.log
echo.

:: Executa o instalador
python total_installer.py

if errorlevel 1 (
    echo.
    echo ❌ Instalação falhou!
    echo Verifique o arquivo: total_installer.log
    pause
    exit /b 1
)

echo.
echo ✅ Instalação completa!
echo.
echo 📋 Próximos passos:
echo 1. Execute: JARVIS_AUTO.bat
echo 2. Aguarde o JARVIS inicializar
echo 3. Diga "Jarvis" para testar
echo.
pause
