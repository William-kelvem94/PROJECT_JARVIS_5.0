@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI\"
set "LOGS_DIR=%ROOT%logs"
set "LOG_FILE=%LOGS_DIR%\hardware-detection.log"
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"

set "JARVIS_MODE=COMPAT"
set "JARVIS_AI_DEVICE=cpu"
set "JARVIS_WHISPER_MODEL=tiny"
set "JARVIS_DISABLE_CAMERA=false"

where nvidia-smi >nul 2>&1
if not errorlevel 1 (
  set "JARVIS_AI_DEVICE=cuda"
  set "JARVIS_MODE=PERFORMANCE"
) else (
  wmic path win32_VideoController get name 2>nul | findstr /I "Intel Iris Intel Arc" >nul
  if not errorlevel 1 (
    set "JARVIS_AI_DEVICE=openvino"
    set "JARVIS_MODE=INTEL_OPT"
    set "JARVIS_DISABLE_CAMERA=true"
  )
)

echo [HW] Mode=%JARVIS_MODE% Device=%JARVIS_AI_DEVICE%
exit /b 0
