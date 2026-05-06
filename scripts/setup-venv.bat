@echo off
SETLOCAL EnableExtensions EnableDelayedExpansion

REM ============================================================
REM JARVIS 5.0 - Virtual Environment Setup Script
REM Setup and configure Python virtual environment with dependencies
REM ============================================================

REM ─────────────────────────────────────────────────────────────
REM 1. INITIALIZATION & PATH SETUP
REM ─────────────────────────────────────────────────────────────
cd /d "%~dp0.."
SET "ROOT=%~dp0..\"
SET "VENV_DIR=%ROOT%.venv"
SET "VENV_ACT=%VENV_DIR%\Scripts\activate.bat"
SET "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
SET "LOG_DIR=%ROOT%logs"
SET "LOG_FILE=%LOG_DIR%\venv-setup.log"
SET "BACK_DIR=%ROOT%backend"
SET "REQ_FILE=%BACK_DIR%\app\requirements.txt"

REM Create logs directory if it doesn't exist
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Initialize log file
echo [%date% %time%] Starting JARVIS 5.0 venv setup... > "%LOG_FILE%"
echo Root directory: %ROOT% >> "%LOG_FILE%"

REM ─────────────────────────────────────────────────────────────
REM 2. VENV CREATION (if not exists)
REM ─────────────────────────────────────────────────────────────
if exist "%VENV_ACT%" (
    echo [INFO] Virtual environment already exists at %VENV_DIR%
    echo [INFO] Virtual environment already exists at %VENV_DIR% >> "%LOG_FILE%"
) else (
    echo [SETUP] Creating virtual environment...
    echo [SETUP] Creating virtual environment... >> "%LOG_FILE%"
    python -m venv "%VENV_DIR%" >> "%LOG_FILE%" 2>&1
    if !ERRORLEVEL! NEQ 0 (
        echo [ERROR] Failed to create virtual environment
        echo [ERROR] Failed to create virtual environment >> "%LOG_FILE%"
        exit /b 1
    )
)

REM ─────────────────────────────────────────────────────────────
REM 3. ACTIVATE VENV
REM ─────────────────────────────────────────────────────────────
echo [SETUP] Activating virtual environment...
call "%VENV_ACT%"
if !ERRORLEVEL! NEQ 0 (
    echo [ERROR] Failed to activate virtual environment
    echo [ERROR] Failed to activate virtual environment >> "%LOG_FILE%"
    exit /b 1
)

REM ─────────────────────────────────────────────────────────────
REM 4. UPGRADE PIP, SETUPTOOLS, WHEEL
REM ─────────────────────────────────────────────────────────────
echo [SETUP] Upgrading pip, setuptools, wheel...
%PYTHON_EXE% -m pip install --upgrade pip setuptools wheel --quiet >> "%LOG_FILE%" 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo [WARNING] Failed to upgrade pip tools. Continuing...
    echo [WARNING] Failed to upgrade pip tools >> "%LOG_FILE%"
)

REM ─────────────────────────────────────────────────────────────
REM 5. INSTALL WEBRTCVAD-WHEELS (Windows dependency for resemblyzer)
REM ─────────────────────────────────────────────────────────────
echo [SETUP] Installing webrtcvad-wheels (Windows compatibility)...
%PYTHON_EXE% -m pip install webrtcvad-wheels --quiet >> "%LOG_FILE%" 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo [WARNING] Failed to install webrtcvad-wheels
    echo [WARNING] Failed to install webrtcvad-wheels >> "%LOG_FILE%"
)

REM ─────────────────────────────────────────────────────────────
REM 6. INSTALL RESEMBLYZER (no-deps to avoid C++ compilation)
REM ─────────────────────────────────────────────────────────────
echo [SETUP] Installing resemblyzer (--no-deps)...
%PYTHON_EXE% -m pip install resemblyzer --no-deps --quiet >> "%LOG_FILE%" 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo [WARNING] Failed to install resemblyzer
    echo [WARNING] Failed to install resemblyzer >> "%LOG_FILE%"
)

REM ─────────────────────────────────────────────────────────────
REM 7. INSTALL PYTORCH (based on JARVIS_AI_DEVICE)
REM ─────────────────────────────────────────────────────────────
if not defined JARVIS_AI_DEVICE (
    SET "JARVIS_AI_DEVICE=cpu"
)

if "!JARVIS_AI_DEVICE!"=="cuda" (
    echo [SETUP] Installing PyTorch with CUDA 12.1 support...
    %PYTHON_EXE% -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --quiet >> "%LOG_FILE%" 2>&1
) else if "!JARVIS_AI_DEVICE!"=="openvino" (
    echo [SETUP] Installing PyTorch CPU (OpenVINO fallback)...
    %PYTHON_EXE% -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --quiet >> "%LOG_FILE%" 2>&1
) else (
    echo [SETUP] Installing PyTorch CPU...
    %PYTHON_EXE% -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --quiet >> "%LOG_FILE%" 2>&1
)

if !ERRORLEVEL! NEQ 0 (
    echo [ERROR] Failed to install PyTorch
    echo [ERROR] Failed to install PyTorch >> "%LOG_FILE%"
    exit /b 1
)

REM ─────────────────────────────────────────────────────────────
REM 8. INSTALL REQUIREMENTS.TXT
REM ─────────────────────────────────────────────────────────────
if not exist "%REQ_FILE%" (
    echo [ERROR] Requirements file not found: %REQ_FILE%
    echo [ERROR] Requirements file not found: %REQ_FILE% >> "%LOG_FILE%"
    exit /b 1
)

echo [SETUP] Installing requirements from %REQ_FILE%...
%PYTHON_EXE% -m pip install -r "%REQ_FILE%" --ignore-requires-python --quiet >> "%LOG_FILE%" 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo [ERROR] Failed to install requirements
    echo [ERROR] Failed to install requirements >> "%LOG_FILE%"
    exit /b 1
)

REM ─────────────────────────────────────────────────────────────
REM 9. VALIDATION - Test critical imports
REM ─────────────────────────────────────────────────────────────
echo [SETUP] Validating critical imports...
%PYTHON_EXE% -c "import fastapi, uvicorn, torch; print('Validation OK')" >> "%LOG_FILE%" 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo [ERROR] Validation failed - critical imports missing
    echo [ERROR] Validation failed - critical imports missing >> "%LOG_FILE%"
    exit /b 1
)

REM ─────────────────────────────────────────────────────────────
REM 10. SUCCESS
REM ─────────────────────────────────────────────────────────────
echo [OK] Virtual environment setup completed successfully!
echo [OK] Virtual environment setup completed successfully! >> "%LOG_FILE%"
echo [INFO] Device: !JARVIS_AI_DEVICE! >> "%LOG_FILE%"
echo [INFO] Setup completed at %date% %time% >> "%LOG_FILE%"

exit /b 0
