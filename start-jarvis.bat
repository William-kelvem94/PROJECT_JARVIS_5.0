@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

:: ============================================================================
:: JARVIS 5.0 - Bootstrap Universal
:: Instala, configura e inicia TUDO automaticamente
:: ============================================================================

set "SCRIPT_DIR=%~dp0"
set "ROOT=%SCRIPT_DIR%"
set "VENV_DIR=%ROOT%.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "LOGS_DIR=%ROOT%logs"
set "BOOT_LOG=%LOGS_DIR%\boot.log"

if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"
echo [%date% %time%] JARVIS 5.0 bootstrap iniciado > "%BOOT_LOG%"

echo.
echo ================================================================
echo   JARVIS 5.0 - BOOTSTRAP UNIVERSAL
echo   Instalando, configurando e iniciando automaticamente...
echo ================================================================
echo.

:: ============================================================================
:: FASE 1: Python
:: ============================================================================
echo [FASE 1/7] Verificando Python 3.11+...

set "FOUND_PYTHON="

:: Tenta Python 3.11 nos caminhos padrao
for %%P in (
  "%LocalAppData%\Programs\Python\Python311\python.exe"
  "%ProgramFiles%\Python311\python.exe"
  "%ProgramFiles(x86)%\Python311\python.exe"
  "%LocalAppData%\Programs\Python\Python312\python.exe"
  "%ProgramFiles%\Python312\python.exe"
  "%LocalAppData%\Programs\Python\Python313\python.exe"
  "%ProgramFiles%\Python313\python.exe"
) do (
  if exist %%~P if not defined FOUND_PYTHON set "FOUND_PYTHON=%%~P"
)

:: Tenta py launcher
if not defined FOUND_PYTHON (
  where py >nul 2>&1
  if not errorlevel 1 (
    for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "FOUND_PYTHON=%%P"
  )
)

:: Tenta python no PATH
if not defined FOUND_PYTHON (
  where python >nul 2>&1
  if not errorlevel 1 (
    for /f "delims=" %%P in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "FOUND_PYTHON=%%P"
  )
)

if defined FOUND_PYTHON (
  for /f "tokens=2" %%V in ('"%FOUND_PYTHON%" --version 2^>^&1') do set "PYTHON_VERSION=%%V"
  echo [OK] Python %PYTHON_VERSION% encontrado: %FOUND_PYTHON%
) else (
  echo.
  echo [!] Python nao encontrado. Baixando e instalando Python 3.11 automaticamente...
  echo.
  echo [INFO] Download do instalador Python 3.11.9...
  
  set "PYTHON_INSTALLER=%TEMP%\python-3.11.9-amd64.exe"
  powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%PYTHON_INSTALLER%'"
  
  if not exist "%PYTHON_INSTALLER%" (
    echo [ERRO] Falha no download do Python.
    echo [INFO] Baixe manualmente em: https://www.python.org/downloads/windows/
    echo [INFO] Marque "Add Python to PATH" durante a instalacao.
    pause
    exit /b 1
  )
  
  echo [INFO] Instalando Python 3.11.9 (silencioso, adicionando ao PATH)...
  "%PYTHON_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
  
  if errorlevel 1 (
    echo [ERRO] Instalacao do Python falhou.
    pause
    exit /b 1
  )
  
  echo [OK] Python 3.11.9 instalado com sucesso!
  del "%PYTHON_INSTALLER%" 2>nul
  
  :: Aguarda o PATH atualizar
  timeout /t 3 /nobreak >nul
  
  set "FOUND_PYTHON=%LocalAppData%\Programs\Python\Python311\python.exe"
  if not exist "!FOUND_PYTHON!" set "FOUND_PYTHON=%ProgramFiles%\Python311\python.exe"
  
  for /f "tokens=2" %%V in ('"!FOUND_PYTHON!" --version 2^>^&1') do set "PYTHON_VERSION=%%V"
  echo [OK] Python %PYTHON_VERSION% pronto.
)

:: ============================================================================
:: FASE 2: Virtual Environment
:: ============================================================================
echo.
echo [FASE 2/7] Configurando ambiente virtual...

if exist "%PYTHON_EXE%" (
  "%PYTHON_EXE%" --version >nul 2>&1
  if errorlevel 1 (
    echo [INFO] Venv existente corrompida, recriando...
    rmdir /s /q "%VENV_DIR%" 2>nul
  )
)

if not exist "%PYTHON_EXE%" (
  echo [INFO] Criando .venv com %FOUND_PYTHON%...
  "!FOUND_PYTHON!" -m venv "%VENV_DIR%"
  if errorlevel 1 (
    echo [ERRO] Falha ao criar .venv.
    pause
    exit /b 1
  )
  echo [OK] .venv criado.
)

"%PYTHON_EXE%" -m pip install --upgrade pip setuptools wheel >nul 2>&1
echo [OK] pip atualizado.

:: ============================================================================
:: FASE 3: Dependencias Python
:: ============================================================================
echo.
echo [FASE 3/7] Instalando dependencias Python...
echo [INFO] Isso pode demorar 5-15 minutos na primeira vez...
echo.

:: Instala PyTorch CPU (mais leve, funciona sem GPU)
echo [INFO] Instalando PyTorch (CPU)...
"%PYTHON_EXE%" -m pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision torchaudio >nul 2>&1
if errorlevel 1 (
  echo [WARN] PyTorch CPU falhou, tentando sem index-url...
  "%PYTHON_EXE%" -m pip install torch torchvision torchaudio >nul 2>&1
)
echo [OK] PyTorch instalado.

:: Instala deps base (lista limpa, sem deps mortas)
echo [INFO] Instalando dependencias base...
"%PYTHON_EXE%" -m pip install ^
  fastapi uvicorn[standard] pydantic-settings python-dotenv ^
  loguru aiohttp psutil watchfiles ^
  playwright watchdog ^
  GPUtil mss Pillow pyautogui onnxruntime ^
  mediapipe opencv-python numpy ultralytics ^
  openwakeword webrtcvad-wheels faster-whisper sounddevice ^
  edge-tts pygame ^
  chromadb sentence-transformers faiss-cpu ^
  pycaw screen-brightness-control screeninfo comtypes ^
  pytest pytest-asyncio pytest-mock httpx ^
  >nul 2>&1

if errorlevel 1 (
  echo [WARN] Algumas deps falharam, tentando individualmente...
  for %%D in (
    fastapi uvicorn pydantic-settings python-dotenv
    loguru aiohttp psutil watchfiles
    playwright watchdog
    GPUtil mss Pillow pyautogui onnxruntime
    mediapipe opencv-python numpy ultralytics
    openwakeword webrtcvad-wheels faster-whisper sounddevice
    edge-tts pygame
    chromadb sentence-transformers faiss-cpu
    pycaw screen-brightness-control screeninfo comtypes
    pytest pytest-asyncio pytest-mock httpx
  ) do (
    echo [INFO] Instalando %%D...
    "%PYTHON_EXE%" -m pip install %%D >nul 2>&1
  )
)

echo [OK] Dependencias base instaladas.

:: Instala face_recognition (precisa de dlib)
echo [INFO] Instalando face_recognition (pode demorar)...
"%PYTHON_EXE%" -m pip install https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.24.1-cp311-cp311-win_amd64.whl >nul 2>&1
if errorlevel 1 (
  echo [WARN] Wheel prebuilt do dlib falhou, tentando cmake...
  "%PYTHON_EXE%" -m pip install cmake >nul 2>&1
  "%PYTHON_EXE%" -m pip install dlib >nul 2>&1
)
"%PYTHON_EXE%" -m pip install face_recognition >nul 2>&1
if errorlevel 1 (
  echo [WARN] face_recognition falhou. Reconhecimento facial desabilitado.
) else (
  echo [OK] face_recognition instalado.
)

:: Instala resemblyzer
echo [INFO] Instalando resemblyzer...
"%PYTHON_EXE%" -m pip install webrtcvad-wheels >nul 2>&1
"%PYTHON_EXE%" -m pip install resemblyzer --no-deps >nul 2>&1
if errorlevel 1 (
  echo [WARN] resemblyzer falhou. Identificacao de speaker desabilitada.
) else (
  echo [OK] resemblyzer instalado.
)

:: Validacao rapida
echo [INFO] Validando instalacao...
"%PYTHON_EXE%" -c "import fastapi, uvicorn, torch, loguru, psutil; print('  Core: OK')"
"%PYTHON_EXE%" -c "import faster_whisper; print('  Whisper: OK')" 2>nul || echo   Whisper: NAO INSTALADO
"%PYTHON_EXE%" -c "import mediapipe; print('  MediaPipe: OK')" 2>nul || echo   MediaPipe: NAO INSTALADO
"%PYTHON_EXE%" -c "import sounddevice; print('  SoundDevice: OK')" 2>nul || echo   SoundDevice: NAO INSTALADO

:: ============================================================================
:: FASE 4: Configuracao .env
:: ============================================================================
echo.
echo [FASE 4/7] Configurando ambiente...

if not exist "%ROOT%backend\.env" (
  echo [INFO] Criando backend\.env...
  (
    echo # JARVIS 5.0 - Configuracao automatica
    echo DEBUG_MODE=true
    echo ENABLE_PERCEPTION=true
    echo.
    echo # API Keys (preencha com suas chaves)
    echo GEMINI_API_KEY=
    echo OPENROUTER_API_KEY=
    echo.
    echo # LLM Local
    echo JARVIS_AI_DEVICE=cpu
    echo LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
    echo LM_STUDIO_MODEL=local-model
    echo OLLAMA_ENABLED=false
    echo OLLAMA_URL=http://localhost:11434
    echo OLLAMA_MODEL=llama3.2:3b
    echo.
    echo # Whisper
    echo JARVIS_WHISPER_MODEL=tiny
    echo WHISPER_COMPUTE_TYPE=int8
    echo.
    echo # Obsidian Vault (opcional)
    echo JARVIS_VAULT_ROOT=
  ) > "%ROOT%backend\.env"
  echo [OK] backend\.env criado com ENABLE_PERCEPTION=true.
) else (
  :: Garante que ENABLE_PERCEPTION=true
  findstr /I "ENABLE_PERCEPTION" "%ROOT%backend\.env" >nul 2>&1
  if errorlevel 1 (
    echo ENABLE_PERCEPTION=true>> "%ROOT%backend\.env"
    echo [OK] ENABLE_PERCEPTION=true adicionado ao .env.
  ) else (
    :: Substitui false por true
    powershell -Command "(Get-Content '%ROOT%backend\.env') -replace 'ENABLE_PERCEPTION\s*=\s*false', 'ENABLE_PERCEPTION=true' | Set-Content '%ROOT%backend\.env'"
    echo [OK] ENABLE_PERCEPTION=true garantido no .env.
  )
)

:: Cria .env do frontend se nao existir
if not exist "%ROOT%frontend\.env.local" (
  if exist "%ROOT%frontend\.env.example" (
    copy "%ROOT%frontend\.env.example" "%ROOT%frontend\.env.local" >nul
    echo [OK] frontend\.env.local criado.
  )
)

:: ============================================================================
:: FASE 5: Playwright (browser automation)
:: ============================================================================
echo.
echo [FASE 5/7] Instalando navegadores do Playwright...
"%PYTHON_EXE%" -m playwright install --with-deps chromium >nul 2>&1
if errorlevel 1 (
  echo [WARN] Playwright browsers falhou. Browser automation desabilitado.
) else (
  echo [OK] Playwright pronto.
)

:: ============================================================================
:: FASE 6: Frontend (Node.js)
:: ============================================================================
echo.
echo [FASE 6/7] Verificando Node.js e frontend...

set "NODE_FOUND="
where node >nul 2>&1
if not errorlevel 1 (
  set "NODE_FOUND=1"
  for /f "tokens=*" %%i in ('node --version 2^>^&1') do echo [OK] Node.js: %%i
)

if not defined NODE_FOUND (
  echo [!] Node.js nao encontrado.
  echo [INFO] Baixe em: https://nodejs.org/ (LTS recomendado)
  echo [INFO] O frontend nao sera iniciado, mas o backend funcionara.
  echo.
) else (
  :: Verifica/instala pnpm
  where pnpm >nul 2>&1
  if errorlevel 1 (
    where corepack >nul 2>&1
    if not errorlevel 1 (
      echo [INFO] Habilitando pnpm via corepack...
      corepack enable >nul 2>&1
      corepack prepare pnpm@latest --activate >nul 2>&1
    )
  )
  
  where pnpm >nul 2>&1
  if not errorlevel 1 (
    for /f "tokens=*" %%i in ('pnpm --version 2^>^&1') do echo [OK] pnpm: %%i
  ) else (
    where npm >nul 2>&1
    if not errorlevel 1 (
      echo [INFO] Instalando pnpm via npm...
      npm install -g pnpm >nul 2>&1
    )
  )
  
  :: Instala deps do frontend
  if exist "%ROOT%frontend\package.json" (
    echo [INFO] Instalando dependencias do frontend...
    pushd "%ROOT%frontend"
    where pnpm >nul 2>&1
    if not errorlevel 1 (
      pnpm install >nul 2>&1
    ) else (
      npm install >nul 2>&1
    )
    popd
    echo [OK] Frontend deps instaladas.
  )
)

:: ============================================================================
:: FASE 7: Iniciar JARVIS
:: ============================================================================
echo.
echo [FASE 7/7] Iniciando JARVIS 5.0...
echo.
echo ================================================================
echo.

:: Inicia backend
echo [BACKEND] Iniciando FastAPI em http://localhost:8000
echo [BACKEND] Documentacao: http://localhost:8000/docs
echo.

start "JARVIS Backend" cmd /k "cd /d "%ROOT%backend" && "%PYTHON_EXE%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

:: Aguarda backend subir
echo [INFO] Aguardando backend inicializar...
timeout /t 5 /nobreak >nul

:: Testa se backend esta respondendo
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:8000/health' -TimeoutSec 5 -ErrorAction Stop; if ($r.StatusCode -eq 200) { Write-Host '[OK] Backend respondendo!' } } catch { Write-Host '[WARN] Backend ainda nao respondeu, mas pode estar iniciando...' }"

:: Inicia frontend se Node.js disponivel
if defined NODE_FOUND (
  echo.
  echo [FRONTEND] Iniciando Next.js em http://localhost:3000
  echo.
  start "JARVIS Frontend" cmd /k "cd /d "%ROOT%frontend" && pnpm dev"
)

echo.
echo ================================================================
echo   JARVIS 5.0 INICIADO!
echo.
echo   Backend:    http://localhost:8000
echo   Docs API:   http://localhost:8000/docs
echo   Frontend:   http://localhost:3000
echo   Telemetria: http://localhost:8001
echo.
echo   Para parar: feche as janelas do terminal
echo ================================================================
echo.
echo [OK] Bootstrap concluido. >> "%BOOT_LOG%"

endlocal
pause
