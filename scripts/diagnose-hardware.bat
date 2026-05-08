@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI\"
cd /d "%ROOT%"
REM JARVIS 5.0 - Diagnostic for Hardware Issues
REM Verifica especificamente: voz, fala, audicao, visao (camera e tela)
REM Data: 7 de maio de 2026

echo =========================================
echo    JARVIS 5.0 HARDWARE DIAGNOSTIC
echo =========================================
echo.
echo Verificando: voz, fala, audicao, visao
echo.

echo [1/6] Verificando backend ativo...
curl -s http://localhost:8000/health > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Backend nao esta respondendo!
    echo Execute: start-jarvis.bat
    pause
    exit /b 1
)
echo [OK] Backend ativo
echo.

echo [2/6] Verificando hardware status...
curl -s http://localhost:8000/system/hardware
echo.

echo [3/6] Testando dependencias Python...
.\.venv\Scripts\python.exe -c "try: import pygame; print('[OK] pygame instalado')\nexcept: print('[ERRO] pygame ausente - execute: pip install pygame')"

.\.venv\Scripts\python.exe -c "try: import sounddevice; print('[OK] sounddevice instalado')\nexcept: print('[ERRO] sounddevice ausente - execute: pip install sounddevice')"

.\.venv\Scripts\python.exe -c "try: import pycaw; print('[OK] pycaw instalado')\nexcept: print('[ERRO] pycaw ausente - execute: pip install pycaw comtypes')"

.\.venv\Scripts\python.exe -c "try: import face_recognition; print('[OK] face_recognition instalado')\nexcept: print('[ERRO] face_recognition ausente - execute: pip install dlib-prebuilt face_recognition')"

.\.venv\Scripts\python.exe -c "try: import mss; print('[OK] mss instalado')\nexcept: print('[ERRO] mss ausente - execute: pip install mss')"
echo.

echo [4/6] Testando dispositivos de audio...
.\.venv\Scripts\python.exe -c "import sounddevice as sd; devices = sd.query_devices(); print(f'[INFO] {len(devices)} dispositivos encontrados'); has_input = any(d['max_input_channels'] > 0 for d in devices); has_output = any(d['max_output_channels'] > 0 for d in devices); print(f'[INFO] Entrada (microfone): {\"SIM\" if has_input else \"NAO\"}'); print(f'[INFO] Saida (alto-falante): {\"SIM\" if has_output else \"NAO\"}')"
echo.

echo [5/6] Verificando findings dos agentes...
curl -s http://localhost:8000/agents/findings | jq ".findings[] | select(.title | contains(\"Camera\") or contains(\"Microfone\") or contains(\"Audio\") or contains(\"Tela\"))"
echo.

echo [6/6] Verificando capabilities completo...
curl -s http://localhost:8000/system/capabilities | jq "{camera: .capabilities.hardware.components[0], microphone: .capabilities.hardware.components[1], screen_mirror: .capabilities.hardware.components[2], audio: .capabilities.percepcao.components[3]}"
echo.

echo =========================================
echo           DIAGNOSTICO COMPLETO
echo =========================================
echo.
echo PROXIMOS PASSOS:
echo.
echo 1. Se "pygame ausente":
echo    .venv\Scripts\pip.exe install pygame
echo.
echo 2. Se "sounddevice ausente":
echo    .venv\Scripts\pip.exe install sounddevice
echo.
echo 3. Se "pycaw ausente":
echo    .venv\Scripts\pip.exe install pycaw comtypes
echo.
echo 4. Se "face_recognition ausente":
echo    .venv\Scripts\pip.exe install dlib-prebuilt face_recognition
echo.
echo 5. Se "Camera offline":
echo    - Verificar se camera esta conectada
echo    - Verificar permissoes do Windows (Configuracoes ^> Privacidade ^> Camera)
echo.
echo 6. Se "Microphone offline":
echo    - Verificar se microfone esta conectado
echo    - Verificar permissoes do Windows (Configuracoes ^> Privacidade ^> Microfone)
echo.
echo 7. Se "screen_mirror offline":
echo    .venv\Scripts\pip.exe install mss
echo.
echo Ver documentacao completa:
echo - docs\SOLUTIONS_FOR_REPORTED_ISSUES.md
echo - docs/guides/AUTOFIX_README.md
echo.
pause
