@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI\"
set "VENV_DIR=%ROOT%.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "LOG_DIR=%ROOT%logs"
set "LOG_FILE=%LOG_DIR%\venv-setup.log"
set "REQ_DIR=%ROOT%backend\app"
set "REQ_BASE=%REQ_DIR%\requirements-base.txt"
set "REQ_CPU=%REQ_DIR%\requirements-torch-cpu.txt"
set "REQ_CUDA=%REQ_DIR%\requirements-torch-cu118.txt"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
echo [%date% %time%] Starting JARVIS venv setup > "%LOG_FILE%"

if not defined JARVIS_SYSTEM_PYTHON (
  call "%ROOT%scripts\check-prerequisites.bat"
  if errorlevel 1 exit /b 1
)

if not defined JARVIS_TORCH_PROFILE set "JARVIS_TORCH_PROFILE=cpu"
if not defined JARVIS_AI_DEVICE set "JARVIS_AI_DEVICE=cpu"
if not defined JARVIS_KEEP_BROKEN_VENVS set "JARVIS_KEEP_BROKEN_VENVS=0"

if not "%JARVIS_KEEP_BROKEN_VENVS%"=="1" (
  for /d %%D in ("%ROOT%.venv.broken-*") do (
    echo [VENV] Removing old broken venv backup: %%~nxD
    rmdir /s /q "%%~fD" >> "%LOG_FILE%" 2>&1
  )
  for /d %%D in ("%ROOT%backend\venv.broken-*") do (
    echo [VENV] Removing old backend broken venv backup: %%~nxD
    rmdir /s /q "%%~fD" >> "%LOG_FILE%" 2>&1
  )
)

if "%JARVIS_FORCE_RECREATE_VENV%"=="1" (
  if exist "%VENV_DIR%" (
    for /f "tokens=1-3 delims=/ " %%a in ("%date%") do set "DATE_STAMP=%%c%%b%%a"
    set "BROKEN_DIR=%ROOT%.venv.broken-!DATE_STAMP!-%time::=%"
    set "BROKEN_DIR=!BROKEN_DIR: =0!"
    echo [VENV] Renaming existing venv to !BROKEN_DIR!
    move "%VENV_DIR%" "!BROKEN_DIR!" >> "%LOG_FILE%" 2>&1
  )
)

if exist "%PYTHON_EXE%" (
  "%PYTHON_EXE%" --version >> "%LOG_FILE%" 2>&1
  if errorlevel 1 (
    echo [VENV] Existing venv is broken. Recreate with JARVIS_FORCE_RECREATE_VENV=1.
    exit /b 1
  )
) else (
  echo [VENV] Creating .venv with %JARVIS_SYSTEM_PYTHON%
  "%JARVIS_SYSTEM_PYTHON%" -m venv "%VENV_DIR%" >> "%LOG_FILE%" 2>&1
  if errorlevel 1 (
    echo [ERROR] Failed to create .venv. See %LOG_FILE%
    exit /b 1
  )
)

if not exist "%PYTHON_EXE%" (
  echo [ERROR] Python from .venv not found: %PYTHON_EXE%
  exit /b 1
)

echo [SETUP] Upgrading pip tools...
"%PYTHON_EXE%" -m pip install --upgrade pip setuptools wheel >> "%LOG_FILE%" 2>&1
if errorlevel 1 exit /b 1

if /I "%JARVIS_TORCH_PROFILE%"=="cu118" (
  set "REQ_TORCH=%REQ_CUDA%"
) else (
  set "REQ_TORCH=%REQ_CPU%"
)

echo [SETUP] Installing PyTorch profile: %JARVIS_TORCH_PROFILE%
"%PYTHON_EXE%" -m pip install -r "%REQ_TORCH%" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  echo [ERROR] PyTorch install failed. See %LOG_FILE%
  exit /b 1
)

echo [SETUP] Installing backend base dependencies...
"%PYTHON_EXE%" -m pip install -r "%REQ_BASE%" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  echo [ERROR] Backend requirements install failed. See %LOG_FILE%
  exit /b 1
)

echo [SETUP] Installing pygame for local TTS playback (REQUIRED)...
"%PYTHON_EXE%" -m pip install pygame >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  echo [ERROR] pygame install failed. This is REQUIRED for TTS. See %LOG_FILE%
  exit /b 1
)

echo [SETUP] Installing deepfilternet for noise suppression (REQUIRED)...
"%PYTHON_EXE%" -m pip install deepfilternet >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  echo [ERROR] deepfilternet install failed. This is REQUIRED for voice processing. See %LOG_FILE%
  exit /b 1
)

echo [SETUP] Installing face_recognition with hardware-adapted prebuilt wheels (REQUIRED)...
echo [INFO] Attempting to install dlib prebuilt wheel for Windows...
"%PYTHON_EXE%" -m pip install https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.24.1-cp311-cp311-win_amd64.whl >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  echo [WARN] Prebuilt dlib wheel failed, trying cmake build...
  "%PYTHON_EXE%" -m pip install cmake >> "%LOG_FILE%" 2>&1
  "%PYTHON_EXE%" -m pip install dlib >> "%LOG_FILE%" 2>&1
)

"%PYTHON_EXE%" -m pip install face_recognition >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  echo [ERROR] face_recognition install failed. Face identity Level A is REQUIRED. See %LOG_FILE%
  exit /b 1
)

echo [SETUP] Installing resemblyzer with Windows-safe VAD wheel...
"%PYTHON_EXE%" -m pip install webrtcvad-wheels >> "%LOG_FILE%" 2>&1
"%PYTHON_EXE%" -m pip install resemblyzer --no-deps >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  echo [WARN] resemblyzer install failed. Speaker ID will be disabled. See %LOG_FILE%
)

echo [SETUP] Validating imports...
"%PYTHON_EXE%" -c "import fastapi, uvicorn, torch, chromadb; print('core-ok', torch.__version__)" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  echo [ERROR] Core validation failed. See %LOG_FILE%
  exit /b 1
)

"%PYTHON_EXE%" -c "import webrtcvad; import resemblyzer; print('voice-id-ok')" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  echo [WARN] Speaker ID validation failed, continuing without blocking startup.
)

echo [OK] Virtual environment ready.
echo [INFO] Python: %PYTHON_EXE%
echo [INFO] Device: %JARVIS_AI_DEVICE% / Torch: %JARVIS_TORCH_PROFILE%
exit /b 0
