@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI\"
set "LOGS_DIR=%ROOT%logs"
set "LOG_FILE=%LOGS_DIR%\hardware-detection.log"
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"

set "MODE=COMPAT"
set "DEVICE=cpu"
set "TORCH_PROFILE=cpu"
set "WHISPER_MODEL=tiny"
set "DISABLE_CAMERA=false"
set "GPU_NAME="

where nvidia-smi >nul 2>&1
if not errorlevel 1 (
  for /f "tokens=* delims=" %%G in ('nvidia-smi --query-gpu=name --format=csv^,noheader 2^>nul') do if not defined GPU_NAME set "GPU_NAME=%%G"
  echo !GPU_NAME! | findstr /I "1050 1050 Ti 1050Ti" >nul
  if not errorlevel 1 (
    set "MODE=NVIDIA_LOW_VRAM"
    set "DEVICE=cuda"
    set "TORCH_PROFILE=cu118"
    set "WHISPER_MODEL=tiny"
  ) else (
    set "MODE=NVIDIA"
    set "DEVICE=cuda"
    set "TORCH_PROFILE=cu118"
    set "WHISPER_MODEL=base"
  )
) else (
  for /f "tokens=* delims=" %%G in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "try { (Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name) -join '; ' } catch { '' }" 2^>nul') do set "GPU_NAME=%%G"
  echo !GPU_NAME! | findstr /I "Intel Iris Intel(R) Iris Intel Arc" >nul
  if not errorlevel 1 (
    set "MODE=INTEL_CPU_SAFE"
    set "DEVICE=cpu"
    set "TORCH_PROFILE=cpu"
    set "WHISPER_MODEL=tiny"
  )
)

echo [HW] Mode=!MODE! Device=!DEVICE! Torch=!TORCH_PROFILE! GPU=!GPU_NAME!
echo [%date% %time%] Mode=!MODE! Device=!DEVICE! Torch=!TORCH_PROFILE! GPU=!GPU_NAME! > "%LOG_FILE%"

endlocal & (
  set "JARVIS_MODE=%MODE%"
  set "JARVIS_AI_DEVICE=%DEVICE%"
  set "JARVIS_TORCH_PROFILE=%TORCH_PROFILE%"
  set "JARVIS_WHISPER_MODEL=%WHISPER_MODEL%"
  set "JARVIS_DISABLE_CAMERA=%DISABLE_CAMERA%"
  set "JARVIS_GPU_NAME=%GPU_NAME%"
)
exit /b 0
