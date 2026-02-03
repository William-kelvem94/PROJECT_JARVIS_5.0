@echo off
setlocal
title JARVIS 5.0 - STARTING...

:: Verificar privilegios de Admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] Privilegios de Administrador confirmados.
) else (
    echo [AVISO] Solicitando permissao de Administrador...
    powershell -Command "Start-Process '%~dpnx0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"

:LOOP
cls
echo ==========================================================
echo    J.A.R.V.I.S.  5.0  -  STARK  EVOLUTION  INITIATIVE
echo ==========================================================
echo.
echo [1] Iniciando Sistema Neural...
echo [2] Verificando Sensores (Visao/Voz)...
echo [3] Conectando ao Nucleo Gemini...
echo.

:: Executar Jarvis
py main.py

if %errorlevel% neq 0 (
    echo.
    echo [CRITICO] O sistema falhou ou foi fechado.
    echo.
    echo Pressione qualquer tecla para reiniciar...
    pause >nul
    goto LOOP
)
