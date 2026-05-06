@echo off
REM ============================================================================
REM JARVIS 5.0 - Hardware Detection Script
REM ============================================================================
REM Detecta GPU (NVIDIA, Intel) e configura variaveis de ambiente
REM Versão: 2026-05-06 | Encoding: UTF-8 com BOM

setlocal enabledelayedexpansion
chcp 65001 >nul

REM ============================================================================
REM CONFIGURAÇÕES
REM ============================================================================
set "PROJECT_ROOT=d:\DOCUMENTOS\GitHub\PROJECT_JARVIS_5.0"
set "LOGS_DIR=!PROJECT_ROOT!\logs"
set "LOG_FILE=!LOGS_DIR!\hardware-detection.log"

REM Padrões globais
set "JARVIS_WHISPER_MODEL=tiny"
set "JARVIS_DISABLE_CAMERA=false"
set "DETECTED_DEVICE=none"
set "DETECTED_VRAM=0"

REM Inicializar log
if not exist "!LOGS_DIR!" mkdir "!LOGS_DIR!"
(
    echo ============================================================================
    echo JARVIS 5.0 - Deteccao de Hardware
    echo Data: %date% %time%
    echo ============================================================================
    echo.
) > "!LOG_FILE!"

REM ============================================================================
REM DETECÇÃO NVIDIA
REM ============================================================================
:detect_nvidia
    echo [INFO] Procurando NVIDIA GPU... >> "!LOG_FILE!"
    echo Detectando NVIDIA GPU...

    REM Verificar se nvidia-smi existe
    where /q nvidia-smi
    if !errorlevel! neq 0 (
        echo [INFO] nvidia-smi nao encontrado, pulando NVIDIA >> "!LOG_FILE!"
        goto :detect_intel
    )

    REM Tentar executar nvidia-smi com timeout
    for /f "tokens=1,2" %%A in ('nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2^>nul') do (
        set "GPU_NAME=%%A"
        set "GPU_MEMORY=%%B"
    )

    if "!GPU_NAME!"=="" (
        echo [INFO] Nenhuma NVIDIA GPU encontrada >> "!LOG_FILE!"
        goto :detect_intel
    )

    echo [OK] NVIDIA GPU encontrada: !GPU_NAME! >> "!LOG_FILE!"
    echo [OK] NVIDIA GPU: !GPU_NAME!
    set "DETECTED_DEVICE=nvidia"

    REM Extrair VRAM em MB
    for /f "tokens=1" %%A in ("!GPU_MEMORY!") do (
        set "DETECTED_VRAM=%%A"
    )
    echo [INFO] VRAM: !DETECTED_VRAM! >> "!LOG_FILE!"

    REM Definir modo baseado em VRAM
    REM Se VRAM < 6GB (6144MB), usar BALANCED, senão PERFORMANCE
    setlocal enabledelayedexpansion
    if !DETECTED_VRAM! LSS 6144 (
        set "JARVIS_MODE=BALANCED"
        echo [INFO] VRAM < 6GB detectada, usando modo BALANCED >> "!LOG_FILE!"
    ) else (
        set "JARVIS_MODE=PERFORMANCE"
        echo [INFO] VRAM >= 6GB detectada, usando modo PERFORMANCE >> "!LOG_FILE!"
    )
    endlocal

    set "JARVIS_AI_DEVICE=cuda"
    echo [SUCCESS] NVIDIA GPU configurada para JARVIS >> "!LOG_FILE!"
    goto :set_exports

REM ============================================================================
REM DETECÇÃO INTEL
REM ============================================================================
:detect_intel
    echo [INFO] Procurando Intel GPU (Iris Xe / Arc)... >> "!LOG_FILE!"
    echo Detectando Intel GPU...

    REM Verificar com wmic (Intel devices)
    for /f "tokens=*" %%A in ('wmic path win32_videocontroller get name 2^>nul ^| findstr /i "Intel"') do (
        set "INTEL_GPU=%%A"
    )

    if "!INTEL_GPU!"=="" (
        echo [INFO] Nenhuma Intel GPU encontrada >> "!LOG_FILE!"
        goto :fallback_cpu
    )

    echo [OK] Intel GPU encontrada: !INTEL_GPU! >> "!LOG_FILE!"
    echo [OK] Intel GPU: !INTEL_GPU!
    set "DETECTED_DEVICE=intel"
    set "JARVIS_AI_DEVICE=openvino"
    set "JARVIS_MODE=INTEL_OPT"
    echo [SUCCESS] Intel GPU configurada para JARVIS >> "!LOG_FILE!"
    goto :set_exports

REM ============================================================================
REM FALLBACK CPU
REM ============================================================================
:fallback_cpu
    echo [INFO] Nenhuma GPU detectada, usando CPU >> "!LOG_FILE!"
    echo Usando CPU como processador principal...
    set "DETECTED_DEVICE=cpu"
    set "JARVIS_AI_DEVICE=cpu"
    set "JARVIS_MODE=COMPAT"
    echo [WARN] Sistema configurado para CPU (desempenho limitado) >> "!LOG_FILE!"
    goto :set_exports

REM ============================================================================
REM EXPORTAR VARIÁVEIS DE AMBIENTE
REM ============================================================================
:set_exports
    echo.
    echo [INFO] Definindo variaveis de ambiente... >> "!LOG_FILE!"

    setlocal enabledelayedexpansion

    REM Escrever variáveis em arquivo temporário para uso posterior
    (
        echo set "JARVIS_AI_DEVICE=!JARVIS_AI_DEVICE!"
        echo set "JARVIS_MODE=!JARVIS_MODE!"
        echo set "JARVIS_WHISPER_MODEL=!JARVIS_WHISPER_MODEL!"
        echo set "JARVIS_DISABLE_CAMERA=!JARVIS_DISABLE_CAMERA!"
        echo set "JARVIS_DETECTED_DEVICE=!DETECTED_DEVICE!"
    ) > "!LOGS_DIR!\hardware-env.bat"

    echo [OK] JARVIS_AI_DEVICE=!JARVIS_AI_DEVICE! >> "!LOG_FILE!"
    echo [OK] JARVIS_MODE=!JARVIS_MODE! >> "!LOG_FILE!"
    echo [OK] JARVIS_WHISPER_MODEL=!JARVIS_WHISPER_MODEL! >> "!LOG_FILE!"
    echo [OK] JARVIS_DISABLE_CAMERA=!JARVIS_DISABLE_CAMERA! >> "!LOG_FILE!"
    echo [OK] Variáveis exportadas >> "!LOG_FILE!"

    echo.
    echo ========== Hardware Detection Summary ==========
    echo Dispositivo: !DETECTED_DEVICE!
    echo AI Device: !JARVIS_AI_DEVICE!
    echo Modo: !JARVIS_MODE!
    echo Whisper Model: !JARVIS_WHISPER_MODEL!
    echo ================================================
    echo.

    REM Definir no escopo global (para scripts posteriores)
    endlocal & ^
    set "JARVIS_AI_DEVICE=%JARVIS_AI_DEVICE%" & ^
    set "JARVIS_MODE=%JARVIS_MODE%" & ^
    set "JARVIS_WHISPER_MODEL=%JARVIS_WHISPER_MODEL%" & ^
    set "JARVIS_DISABLE_CAMERA=%JARVIS_DISABLE_CAMERA%"

    echo [SUCCESS] Deteccao de hardware completa >> "!LOG_FILE!"
    echo.

    endlocal
    exit /b 0
