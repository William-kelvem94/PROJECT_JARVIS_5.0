@echo off
setlocal enabledelayedexpansion

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: JARVIS SINGULARITY - ULTIMATE COMMAND CENTER v8.0 (MILITARY GRADE)
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: UI: High-Density Panel | Core: Robust Modular Self-Healing
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

chcp 65001 >nul 2>&1
title 🚀 JARVIS 5.0 - SINGULARITY ULTIMATE CENTER
color 0B

:: Global Constants
set "ROOT=%~dp0"
set "VENV_DIR=%ROOT%venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "MAX_RETRIES=5"
set "RETRY_COUNT=0"
set "LOG_DIR=%ROOT%data\logs"

:: Critical ML Environment Guards
set "KMP_DUPLICATE_LIB_OK=TRUE"
set "OMP_WAIT_POLICY=PASSIVE"
set "MKL_THREADING_LAYER=INTEL"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

:: UI Theme Colors (ANSI)
set "CYAN=[96m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "WHITE=[97m"
set "RESET=[0m"

cd /d "%ROOT%"

:: Argument Handling
if /i "%~1"=="--repair-pytorch" goto :repair_pytorch
if /i "%~1"=="--safe-mode" set "JARVIS_SAFE_MODE=1"

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: INITIALIZATION SEQUENCE
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:header
cls
call :show_technical_header

:: STAGE 0: ARCHITECTURAL INTEGRITY
echo [%time%] %WHITE%STAGE 0: Infrastructure Sync%RESET%
call :ensure_directories

:: STAGE 1: ENVIRONMENT VALIDATION
echo [%time%] %WHITE%STAGE 1: Environment Integrity Check...%RESET%
if not exist "%VENV_PYTHON%" (
    call :handle_missing_venv || exit /b 1
)

:: STAGE 2: LIBRARY GUARDS (NumPy / DLLs)
echo [%time%] %WHITE%STAGE 2: Synchronizing Neural Engine Guards...%RESET%
call :check_numpy_version
call :check_crash_flag

:: STAGE 3: PRE-FLIGHT SYSTEM CHECK (🆕 P0 VALIDATION)
echo [%time%] %WHITE%STAGE 3: Executing Pre-flight Protocol...%RESET%
if exist "%VENV_PYTHON%" (
    "%VENV_PYTHON%" scripts\install\pre_flight_check.py
    if %ERRORLEVEL% NEQ 0 (
    echo.
    echo %RED%[CRITICAL] Pre-flight validation failed.%RESET%
    echo Please check the error messages above.
    pause
    exit /b 1
)

:: STAGE 4: MAIN EXECUTION PULSE
echo.
echo %GREEN%========================================================================%RESET%
echo    %GREEN%JARVIS ONLINE%RESET% - Launching Multi-Threaded Singularity Core
echo %GREEN%========================================================================%RESET%
echo.

REM Toast Notification (Try-catch in PS)
powershell -Command "try { New-BurntToastNotification -Text 'JARVIS', 'Singularity Core Initialized' } catch {}" >nul 2>&1

:launch_loop
    set /a RETRY_COUNT+=1
    echo [%time%] %WHITE%SYSTEM PULSE%RESET% (Attempt !RETRY_COUNT!/%MAX_RETRIES%)
    
    :: Start process with high priority if admin available
    "%VENV_PYTHON%" main.py %*
    set "EXIT_VAL=%ERRORLEVEL%"
    
    if %EXIT_VAL% EQU 0 (
        echo.
        echo %GREEN%[STABLE]%RESET% JARVIS shut down normally. All systems preserved.
        pause
        exit /b 0
    )
    
    if %EXIT_VAL% EQU 130 (
        echo.
        echo %YELLOW%[HALTED]%RESET% Manual interruption detected.
        pause
        exit /b 0
    )
    
    :: CRASH DETECTION
    call :handle_execution_error !EXIT_VAL!
    
    if !RETRY_COUNT! LEQ %MAX_RETRIES% (
        echo %YELLOW%[RECOVERY]%RESET% Attempting hot-restart in 5 seconds...
        timeout /t 5 /nobreak >nul
        goto :launch_loop
    ) else (
        echo.
        echo %RED%[FATAL] Error threshold reached.%RESET%
        echo %CYAN%[ACTION]%RESET% Run START_JARVIS.bat --repair-pytorch
        echo.
        pause
        exit /b %EXIT_VAL%
    )

goto :eof

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: REPAIR & MAINTENANCE FUNCTIONS
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:repair_pytorch
cls
echo ╔══════════════════════════════════════════════════════════════╗
echo ║          🔧  JARVIS EMERGENCY REPAIR: PYTORCH              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo [%time%] Initiating deep repair sequence for c10.dll issues...
echo.

where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python global not found in PATH for repair.
    pause
    exit /b 1
)

echo [1/3] Purging existing installations...
"%VENV_PYTHON%" -m pip uninstall torch torchvision torchaudio numpy -y

echo [2/3] Installing stabilized production versions (NumPy 1.26.4 + Torch)...
"%VENV_PYTHON%" -m pip install "numpy==1.26.4" "torch==2.0.1" "torchvision==0.15.2" --index-url https://download.pytorch.org/whl/cu118

echo [3/3] Verifying library integrity...
"%VENV_PYTHON%" -c "import torch; import numpy; print('✓ Torch Integrity:', torch.__version__); print('✓ NumPy Integrity:', numpy.__version__)"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo %GREEN%✅ REPAIR SUCCESSFUL!%RESET% Restarting system...
    timeout /t 5
    goto :header
) else (
    echo.
    echo %RED%❌ REPAIR FAILED.%RESET% Check internet and permissions.
    pause
    exit /b 1
)

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: UTILITY FUNCTIONS
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:show_technical_header
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║              JARVIS 5.0 - SINGULARITY ULTIMATE CENTER (v8.0)           ║
echo ║────────────────────────────────────────────────────────────────────────║
REM High Density System Info (via PowerShell)
set "PS_CMD=$os = Get-CimInstance Win32_OperatingSystem; $cpu = Get-CimInstance Win32_Processor; $memTotal = [math]::Round($os.TotalVisibleMemorySize/1024/1024, 1); $memFree = [math]::Round($os.FreePhysicalMemory/1024/1024, 1); try { $pyV = (& '%VENV_PYTHON%' --version 2>&1).Split(' ')[1] } catch { $pyV = 'Not Found' }; Write-Host '  OS: ' -NoNewline; Write-Host $os.Caption -ForegroundColor Cyan -NoNewline; Write-Host ' (Build ' -NoNewline; Write-Host $os.BuildNumber -NoNewline; Write-Host ') | Python: ' -NoNewline; Write-Host $pyV -ForegroundColor Green"
powershell -command "%PS_CMD%"

set "PS_CMD2=$os = Get-CimInstance Win32_OperatingSystem; $cpu = Get-CimInstance Win32_Processor; $memTotal = [math]::Round($os.TotalVisibleMemorySize/1024/1024, 1); $memFree = [math]::Round($os.FreePhysicalMemory/1024/1024, 1); Write-Host '  RAM: ' -NoNewline; Write-Host $memTotal 'GB total' -NoNewline; Write-Host ' (' -NoNewline; Write-Host $memFree 'GB free' -ForegroundColor Yellow -NoNewline; Write-Host ') | CPU: ' -NoNewline; Write-Host $cpu.Name -ForegroundColor Cyan"
powershell -command "%PS_CMD2%"

where nvidia-smi >nul 2>&1 && (
    for /f "usebackq tokens=*" %%A in (`powershell "$gpu=nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits; Write-Host \"  GPU: $($gpu)\" -ForegroundColor Green"`) do echo %%A
) || (
    echo   GPU: Memory optimizations active (CPU Mode)
)
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.
goto :eof

:ensure_directories
for %%D in (
    "data\logs"
    "data\faces"
    "data\screenshots"
    "data\models"
    "data\audio\temp"
    "data\voice_signatures"
    "data\cache"
    "data\captures"
    "data\exports"
    "data\generated_scripts"
    "data\memory"
    "data\monitoring"
    "data\neural_memory"
    "data\processed"
    "data\temp"
    "data\templates"
    "data\training_dataset"
) do (
    if not exist "%ROOT%%%~D" mkdir "%ROOT%%%~D" 2>nul
)
goto :eof

:handle_missing_venv
echo [ERROR] Virtual Environment missing or corrupted.
echo [ACTION] Invoking Total Installer sequence...
python scripts\install\total_installer.py
if %ERRORLEVEL% NEQ 0 (
    echo [FATAL] Setup failed.
    pause
    exit /b 1
)
goto :eof

:check_numpy_version
"%VENV_PYTHON%" -c "import numpy; exit(0 if int(numpy.__version__.split('.')[0]) < 2 else 1)" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo %YELLOW%[CONFLICT]%RESET% NumPy 2.x detected. Downgrading to stable 1.26.4...
    "%VENV_PYTHON%" -m pip install "numpy==1.26.4" --force-reinstall --quiet
)
goto :eof

:check_crash_flag
if exist "%LOG_DIR%\jarvis_crash.flag" (
    echo.
    echo %YELLOW%╔══════════════════════════════════════════════════════════════╗%RESET%
    echo %YELLOW%║           ⚠️  PREVIOUS SESSION CRASH DETECTED             ║%RESET%
    echo %YELLOW%║  Action: Run START_JARVIS.bat --repair-pytorch         ║%RESET%
    echo %YELLOW%╚══════════════════════════════════════════════════════════════╝%RESET%
    echo.
    del "%LOG_DIR%\jarvis_crash.flag" >nul 2>&1
)
goto :eof

:handle_execution_error
set "ERR_CODE=%1"
echo %date% %time% - Crash Code %ERR_CODE% > "%LOG_DIR%\jarvis_crash.flag"
echo.
echo %RED%[‼] CRITICAL FAIL DETECTED (Code %ERR_CODE%)%RESET%
goto :eof
