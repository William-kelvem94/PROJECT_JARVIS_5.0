@echo off
REM ═══════════════════════════════════════════════════════════════════════
REM  JARVIS 5.0 - Launcher Auto-Suficiente v5.5 (BRAINROUTER READY)
REM ═══════════════════════════════════════════════════════════════════════
setlocal enabledelayedexpansion
title JARVIS 5.0 - Auditoria de Sistema...
color 0B

echo.
echo  ================================================================
echo   JARVIS 5.0  ^|  Launcher Auto-Suficiente v5.5
echo   Auditando ambiente para o Chefe...
echo  ================================================================
echo.

cd /d "%~dp0"

REM ════════════════════════════════════════════════════
REM  [1/8] PRE-FLIGHT (VERIFICAÇÕES DE INFRAESTRUTURA IA)
REM ═══════════════════════════════════════════════════════════════════════
echo  [1/8] Verificando Roteamento Cognitivo Local (LM Studio)...
netstat -aon 2>nul | findstr ":1234 " >nul
if errorlevel 1 (
    echo   [AVISO] LM Studio nao detectado na porta 1234.
    echo   [INFO] O JARVIS usara o motor de Cloud Fallback (API externa^) por padrao.
) else (
    echo  [OK] Roteamento de Cerebro Local detectado e disponivel.
)

REM ════════════════════════════════════════════════════
REM  [1.5/8] DETECÇÃO DE HARDWARE (DESKTOP VS LAPTOP)
REM ════════════════════════════════════════════════════
echo.
echo  [1.5/8] Analisando Perfil de Hardware e Roteamento de Memoria...
set "HARDWARE_PROFILE=LAPTOP"
wmic path win32_VideoController get name | findstr /i "NVIDIA" >nul
if %errorlevel%==0 (
    set "HARDWARE_PROFILE=DESKTOP"
    echo  [INFO] GPU NVIDIA Detectada ^(GTX 1050 Ti ou similar^).
    echo  [INFO] Perfil configurado para aceleracao de IA Local ^(CUDA^).
) else (
    echo  [INFO] GPU NVIDIA nao detectada.
    echo  [INFO] Perfil configurado para Notebook ^(Processamento CPU Seguro / API Cloud^).
)
echo.

REM ════════════════════════════════════════════════════
REM  [2/8] VERIFICAR AMBIENTE (.env INTELIGENTE)
REM ════════════════════════════════════════════════════
echo  [2/8] Validando configuracoes de ambiente e senhas de API...
set "ENV_FILE="
if exist ".env" ( set "ENV_FILE=.env" ) else ( if exist "env\.env" ( set "ENV_FILE=env\.env" ) )

if not defined ENV_FILE (
    if "%HARDWARE_PROFILE%"=="DESKTOP" (
        if exist "env\.env.desktop.example" (
            copy "env\.env.desktop.example" ".env" >nul
            set "ENV_FILE=.env"
            echo   [!] .env gerado automaticamente para DESKTOP. Revise suas chaves de API.
        )
    ) else (
        if exist "env\.env.laptop.example" (
            copy "env\.env.laptop.example" ".env" >nul
            set "ENV_FILE=.env"
            echo   [!] .env gerado automaticamente para NOTEBOOK. Revise suas chaves de API.
        )
    )
    
    if not exist ".env" (
        if exist ".env.example" (
            copy ".env.example" ".env" >nul
            set "ENV_FILE=.env"
            echo   [!] .env padrao criado.
        ) else (
            echo   [ERRO] Nenhum template .env encontrado. O Jarvis nao pode iniciar.
            pause & exit /b 1
        )
    )
)
echo  [OK] Arquivo de ambiente: %ENV_FILE%
copy "%ENV_FILE%" "frontend\.env" >nul 2>&1
echo.

REM ════════════════════════════════════════════════════
REM  [3/8] UV & PYTHON 3.12 (A ESTRUTURA MESTRA)
REM ════════════════════════════════════════════════════
echo  [3/8] Orquestrando Motor Python...
set "UV="
where uv >nul 2>nul && set "UV=uv"
if not defined UV if exist "%LOCALAPPDATA%\uv\bin\uv.exe" set "UV=%LOCALAPPDATA%\uv\bin\uv.exe"

set "PYTHON="
set "PYLAUNCHER="
if defined UV (
    "!UV!" python install 3.12 --quiet
    for /f "usebackq delims=" %%i in (`"!UV!" python find 3.12 2^>nul`) do set "PYTHON=%%i"
)

if not defined PYTHON (
    for /f "usebackq delims=" %%i in (`where py 2^>nul`) do (
        set "_P=%%i"
        echo "!_P!" | findstr /i "WindowsApps" >nul
        if errorlevel 1 if not defined PYLAUNCHER set "PYLAUNCHER=!_P!"
    )
)

if not defined PYTHON if defined PYLAUNCHER (
    set "PYTHON=%PYLAUNCHER%"
)

if not defined PYTHON (
    for /f "usebackq delims=" %%i in (`where python 2^>nul`) do (
        set "_P=%%i"
        echo "!_P!" | findstr /i "WindowsApps" >nul
        if errorlevel 1 set "PYTHON=!_P!"
    )
)

if not defined PYTHON if exist "%~dp0backend\venv\Scripts\python.exe" (
    set "PYTHON=%~dp0backend\venv\Scripts\python.exe"
)

if not defined PYTHON (
    echo  [ERRO] Python 3.12 nao localizado.
    pause & exit /b 1
)
echo  [OK] Python: !PYTHON!
echo.

REM ════════════════════════════════════════════════════
REM  [4/8] BACKEND VENV & DEPS (STRESS TEST)
REM ════════════════════════════════════════════════════
echo  [4/8] Auditando Backend (venv e dependencias)...
cd /d "%~dp0backend"
if not exist "venv\Scripts\activate.bat" (
    echo   + Inicializando novo ambiente virtual...
    "!PYTHON!" -m venv venv
)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
echo   + Validando integridade das bibliotecas...
python -m pip install -r app\requirements.txt --quiet
if errorlevel 1 (
    echo   [!] Erro nas dependencias. Tentando correcao automatica...
    python -m pip install -r app\requirements.txt
)
echo   + Verificando dependencias essenciais do BrainRouter (Google GenAI/OpenAI/Httpx)...
python -m pip install google-genai openai httpx --quiet

echo  [OK] Backend integro.

REM VERIFICAÇÃO DE CUDA PARA DESKTOP
if "%HARDWARE_PROFILE%"=="DESKTOP" (
    echo   + Verificando suporte CUDA do PyTorch...
    python -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>nul
    if errorlevel 1 (
        echo   [AVISO] PyTorch nao esta otimizado para sua GPU NVIDIA!
        echo   [INFO] Instalando CUDA automaticamente para nao travar o i3...
        cd /d "%~dp0"
        call scripts\install_pytorch_cuda.bat
        cd /d "%~dp0backend"
    ) else (
        echo  [OK] Motores da Placa de Video ativados.
    )
)
echo.

REM ════════════════════════════════════════════════════
REM  [5/8] NODE & FRONTEND (pnpm check)
REM ════════════════════════════════════════════════════
echo  [5/8] Validando ecossistema Frontend...
cd /d "%~dp0"
set "PKG=npm"
where pnpm >nul 2>nul && set "PKG=pnpm"

cd frontend
if not exist "node_modules" (
    echo   + Instalando node_modules pela primeira vez...
    call !PKG! install
) else (
    echo   + Node_modules detectado. Verificando consistencia...
    call !PKG! install --silent
)
echo  [OK] Frontend pronto.
echo.

REM ════════════════════════════════════════════════════
REM  [6/8] LIMPEZA DE PORTAS (BLINDAGEM)
REM ════════════════════════════════════════════════════
echo  [6/8] Blindando Portas (Limpando processos antigos)...
for %%p in (8000 3000) do (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr "%%p" 2^>nul') do (
        if "%%a" NEQ "0" taskkill /F /PID %%a >nul 2>&1
    )
)
echo  [OK] Portas 8000 e 3000 liberadas.
echo.

REM ════════════════════════════════════════════════════
REM  [7/8] INICIALIZAÇÃO SINCRONIZADA
REM ════════════════════════════════════════════════════
echo  [7/8] Iniciando Motores Hibridos (Local/Rede/Cloud)...

cd /d "%~dp0backend"
start "JARVIS_BACKEND" /min cmd /k "call venv\Scripts\activate && uvicorn app.main:app --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

cd /d "%~dp0frontend"
if exist ".next" rmdir /s /q ".next"
start "JARVIS_FRONTEND" /min cmd /k "color 07 && !PKG! run dev"

echo.
echo  ================================================================
echo   AUDITORIA CONCLUIDA COM SUCESSO!
echo  ================================================================
echo   Backend: http://localhost:8000
echo   Frontend: http://localhost:3000
echo  ================================================================
echo.
echo   Pressione qualquer tecla para encerrar este launcher principal.
echo   ^(Os servicos continuarao rodando em segundo plano nas janelas minimizadas^).
echo.
pause
exit
