@echo off
REM ═══════════════════════════════════════════════════════════════════════
REM  JARVIS 5.0 - Launcher Auto-Suficiente v5.2
REM  Instala: UV, Python 3.12, Node.js, pnpm, backend deps, playwright,
REM           frontend deps — e entao inicia todos os servicos.
REM ═══════════════════════════════════════════════════════════════════════
setlocal enabledelayedexpansion
title JARVIS 5.0 - Inicializando...
color 0B

echo.
echo  ================================================================
echo   JARVIS 5.0  ^|  Launcher Auto-Suficiente v5.2
echo  ================================================================
echo.

cd /d "%~dp0"

REM ════════════════════════════════════════════════════
REM  [1/8] PRE-FLIGHT (VERIFICAÇÕES LOCAIS)
REM ════════════════════════════════════════════════════
echo  [1/8] Verificando Servidor de I.A Local (LM Studio)...
netstat -aon 2>nul | findstr ":1234 " >nul
if errorlevel 1 (
    echo   [AVISO CRITICO] Servidor LM Studio NAO DETECTADO na porta 1234.
    echo   -------------
    echo   Para o JARVIS 100 por cento Local funcionar, o Cerebro precisa estar online:
    echo   1. Abra o LM Studio.
    echo   2. Carregue o WILL-JARVIS.gguf na memoria.
    echo   3. Inicie o "Local Server" na aba da esquerda.
    echo   -------------
    echo   Pressione qualquer tecla para continuar mesmo assim sem IA Local ativa...
    pause
) else (
    echo  [OK] Cerebro WILL-JARVIS detectado na porta 1234!
)
echo.

REM ════════════════════════════════════════════════════
REM  [2/8] VERIFICAR .env
REM ════════════════════════════════════════════════════
echo  [2/8] Verificando arquivo .env...
set "ENV_FILE="
if exist ".env" set "ENV_FILE=.env"
if not defined ENV_FILE if exist "env\.env" set "ENV_FILE=env\.env"
if not defined ENV_FILE (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul 2>&1
        set "ENV_FILE=.env"
        echo   [AVISO] .env nao encontrado. Criado a partir de .env.example.
        echo   [AVISO] Preencha as chaves de API no arquivo .env antes de usar o JARVIS.
    ) else (
        echo   [ERRO] Nenhum .env ou .env.example encontrado na raiz do projeto.
        pause & exit /b 1
    )
)
echo  [OK] Ambiente: %ENV_FILE%
echo   + Sincronizando .env com o frontend...
copy "%ENV_FILE%" "frontend\.env" >nul 2>&1
echo.

REM ════════════════════════════════════════════════════
REM  [3/8] INSTALAR / LOCALIZAR UV
REM ════════════════════════════════════════════════════
echo  [3/8] Verificando UV (gerenciador de Python)...

set "UV="
REM Verifica UV no PATH
where uv >nul 2>nul
if not errorlevel 1 (
    set "UV=uv"
    goto :UV_OK
)
REM Verifica instalacao local padrao (Windows)
if exist "%LOCALAPPDATA%\uv\bin\uv.exe" (
    set "UV=%LOCALAPPDATA%\uv\bin\uv.exe"
    goto :UV_OK
)
if exist "%APPDATA%\uv\bin\uv.exe" (
    set "UV=%APPDATA%\uv\bin\uv.exe"
    goto :UV_OK
)

REM UV nao encontrado — instalar via PowerShell
echo   + UV nao encontrado. Instalando via PowerShell...
powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex" >nul 2>&1
if exist "%LOCALAPPDATA%\uv\bin\uv.exe" (
    set "UV=%LOCALAPPDATA%\uv\bin\uv.exe"
    goto :UV_OK
)
if exist "%APPDATA%\uv\bin\uv.exe" (
    set "UV=%APPDATA%\uv\bin\uv.exe"
    goto :UV_OK
)

echo   [AVISO] UV nao pode ser instalado automaticamente. Usando pip puro.
set "UV="

:UV_OK
if defined UV (
    echo  [OK] UV: !UV!
) else (
    echo  [OK] Modo: pip puro ^(sem UV^)
)
echo.

REM ════════════════════════════════════════════════════
REM  [4/8] LOCALIZAR / INSTALAR PYTHON 3.12
REM ════════════════════════════════════════════════════
echo  [4/8] Localizando Python 3.12...

set "PYTHON="

REM 3a. Tenta instalar Python 3.12 via UV e achar o caminho
if defined UV (
    "!UV!" python install 3.12 >nul 2>&1
    for /f "usebackq delims=" %%i in (`"!UV!" python find 3.12 2^>nul`) do set "PYTHON=%%i"
    if defined PYTHON (
        echo  [OK] Python 3.12 via UV: !PYTHON!
        goto :PYTHON_OK
    )
)

REM 3b. Tenta encontrar cpython-3.12 no diretorio de instalacao do UV
for /d %%d in ("%APPDATA%\uv\python\cpython-3.12*") do (
    if exist "%%d\python.exe" (
        set "PYTHON=%%d\python.exe"
        echo  [OK] Python 3.12 em UV path: !PYTHON!
        goto :PYTHON_OK
    )
)
for /d %%d in ("%LOCALAPPDATA%\uv\python\cpython-3.12*") do (
    if exist "%%d\python.exe" (
        set "PYTHON=%%d\python.exe"
        echo  [OK] Python 3.12 em UV local path: !PYTHON!
        goto :PYTHON_OK
    )
)

REM 3c. Tenta python global (excluindo Microsoft Store stub)
for /f "usebackq delims=" %%i in (`where python 2^>nul`) do (
    set "_P=%%i"
    echo "!_P!" | findstr /i "WindowsApps" >nul
    if errorlevel 1 (
        set "PYTHON=!_P!"
        echo  [OK] Python global: !PYTHON!
        goto :PYTHON_OK
    )
)

REM 3d. Fallback para py launcher
where py >nul 2>nul
if not errorlevel 1 (
    set "PYTHON=py"
    echo  [OK] Usando py launcher.
    goto :PYTHON_OK
)

echo  [ERRO] Python nao encontrado.
echo  Instale Python 3.12 em https://python.org ou execute: uv python install 3.12
pause & exit /b 1

:PYTHON_OK
echo.

REM ════════════════════════════════════════════════════
REM  [5/8] CONFIGURAR VENV DO BACKEND
REM ════════════════════════════════════════════════════
echo  [5/8] Configurando ambiente virtual do backend...

cd /d "%~dp0backend"

REM Detectar e recriar venv se for Python 3.14 (versao experimental incompativel)
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe --version 2>nul | findstr "3.14" >nul
    if not errorlevel 1 (
        echo   + Venv com Python 3.14 detectado. Recriando com Python 3.12...
        rmdir /s /q venv >nul 2>&1
    )
)

REM Criar venv se nao existir
if not exist "venv\Scripts\activate.bat" (
    echo   + Criando venv...
    "!PYTHON!" -m venv venv
    if errorlevel 1 (
        echo  [ERRO] Falha ao criar ambiente virtual.
        pause & exit /b 1
    )
)

REM Ativar venv
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo  [ERRO] Falha ao ativar ambiente virtual.
    pause & exit /b 1
)

REM Atualizar pip silenciosamente
echo   + Atualizando pip...
python -m pip install --upgrade pip --quiet --no-warn-script-location

REM ── PASSO 1: webrtcvad-wheels (substituto pre-compilado do webrtcvad no Windows)
echo   + [1/3] Instalando webrtcvad-wheels...
python -m pip install webrtcvad-wheels --quiet --no-warn-script-location
if errorlevel 1 (
    echo   [AVISO] webrtcvad-wheels falhou. Resemblyzer pode ter problemas.
)

REM ── PASSO 2: resemblyzer com --no-deps (evita que o pip puxe 'webrtcvad' nativo e tente compilar)
echo   + [2/3] Instalando resemblyzer ^(sem dependencias automaticas^)...
python -m pip install resemblyzer --no-deps --quiet --no-warn-script-location
if errorlevel 1 (
    echo   [AVISO] Falha ao instalar resemblyzer. Identificacao de voz pode nao funcionar.
)

REM ── PASSO 3: demais dependencias do backend
echo   + [3/3] Instalando dependencias do backend ^(pode demorar na primeira vez^)...
python -m pip install -r app\requirements.txt --no-warn-script-location
if errorlevel 1 (
    echo.
    echo  [ERRO] Falha ao instalar dependencias do backend.
    echo  Possiveis causas:
    echo    - Sem internet
    echo    - Alguma lib precisa de compilador C++. Instale:
    echo      https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo.
    pause ^& exit /b 1
)

REM ── Instalar browsers do Playwright
echo   + Instalando Playwright ^(Chromium^)...
python -m playwright install chromium --with-deps >nul 2>&1
if errorlevel 1 (
    echo   [AVISO] Playwright/Chromium nao instalado. Funcoes de browser desativadas.
)

echo  [OK] Backend pronto.
echo.
cd /d "%~dp0"

REM ════════════════════════════════════════════════════
REM  [6/8] VERIFICAR NODE.JS E pnpm
REM ════════════════════════════════════════════════════
echo  [6/8] Verificando Node.js e pnpm...

where node >nul 2>nul
if errorlevel 1 (
    echo  [ERRO] Node.js nao encontrado.
    echo  Instale em https://nodejs.org ^(versao LTS recomendada^)
    pause & exit /b 1
)

for /f "usebackq delims=" %%v in (`node --version 2^>nul`) do set "NODE_VER=%%v"
echo  [OK] Node.js: !NODE_VER!

REM Garantir pnpm instalado
where pnpm >nul 2>nul
if errorlevel 1 (
    echo   + pnpm nao encontrado. Instalando via npm...
    call npm install -g pnpm >nul 2>&1
    if errorlevel 1 (
        echo   [AVISO] Falha ao instalar pnpm. Usando npm como fallback.
        set "PKG_MANAGER=npm"
    ) else (
        set "PKG_MANAGER=pnpm"
    )
) else (
    set "PKG_MANAGER=pnpm"
)
echo  [OK] Gerenciador de pacotes: !PKG_MANAGER!
echo.

REM ════════════════════════════════════════════════════
REM  [7/8] INSTALAR DEPENDENCIAS DO FRONTEND
REM ════════════════════════════════════════════════════
echo  [7/8] Instalando dependencias do frontend...

cd /d "%~dp0frontend"

if not exist "node_modules" (
    echo   + Instalando pacotes ^(pode demorar na primeira vez^)...
    if "!PKG_MANAGER!"=="pnpm" (
        call pnpm install
    ) else (
        call npm install
    )
    if errorlevel 1 (
        echo  [ERRO] Falha ao instalar dependencias do frontend.
        pause & exit /b 1
    )
) else (
    echo   + node_modules ja existe. Verificando atualizacoes...
    if "!PKG_MANAGER!"=="pnpm" (
        call pnpm install --silent
    ) else (
        call npm install --silent
    )
)

echo  [OK] Frontend pronto.
echo.
cd /d "%~dp0"

REM ════════════════════════════════════════════════════
REM  [8/8] INICIAR SERVICOS
REM ════════════════════════════════════════════════════
echo  [8/8] Liberando portas e iniciando servicos...

REM Liberar portas
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000 "') do (
    if "%%a" NEQ "0" taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8081 "') do (
    if "%%a" NEQ "0" taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":3000 "') do (
    if "%%a" NEQ "0" taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

REM ── Backend API (FastAPI porta 8000)
start "JARVIS Backend :8000" /d "%~dp0backend" cmd /k ^
    "color 0B && title [API] JARVIS Backend :8000 && call venv\Scripts\activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

REM ── Agent Worker (LiveKit porta interna 8081)
start "JARVIS Agent Worker" /d "%~dp0backend" cmd /k ^
    "color 0D && title [Worker] JARVIS Agents && call venv\Scripts\activate && python dev_watch_worker.py"

timeout /t 3 /nobreak >nul

REM ── Frontend Next.js (porta 3000)
if exist "%~dp0frontend\.next" rmdir /s /q "%~dp0frontend\.next" >nul 2>&1
start "JARVIS Frontend :3000" /d "%~dp0frontend" cmd /k ^
    "color 07 && title [UI] JARVIS Frontend :3000 && !PKG_MANAGER! run dev"

REM ── Aguardar boot
title JARVIS 5.0 - Running
echo.
echo  ================================================================
echo   JARVIS 5.0 INICIADO - Aguarde ~20s para boot completo
echo  ================================================================
echo   API    ^>  http://localhost:8000/docs
echo   UI     ^>  http://localhost:3000
echo   Worker ^>  porta interna 8081
echo  ================================================================
echo   Feche as janelas individuais para parar cada servico.
echo   Feche ESTA janela somente apos todos os servicos estarem OK.
echo  ================================================================
echo.
pause
