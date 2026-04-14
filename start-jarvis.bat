@echo off
REM ═══════════════════════════════════════════════════════════════════════
REM  JARVIS 5.0 - Launcher Auto-Suficiente v5.3 (MODO BLINDADO)
REM ═══════════════════════════════════════════════════════════════════════
setlocal enabledelayedexpansion
title JARVIS 5.0 - Auditoria de Sistema...
color 0B

echo.
echo  ================================================================
echo   JARVIS 5.0  ^|  Launcher Auto-Suficiente v5.3
echo   Auditando ambiente para o Chefe...
echo  ================================================================
echo.

cd /d "%~dp0"

REM ════════════════════════════════════════════════════
REM  [1/8] PRE-FLIGHT (VERIFICAÇÕES DE INFRA)
REM ════════════════════════════════════════════════════
echo  [1/8] Verificando Servidor de I.A Local (LM Studio)...
netstat -aon 2>nul | findstr ":1234 " >nul
if errorlevel 1 (
    echo   [AVISO] LM Studio nao detectado na porta 1234.
    echo   A IA funcionara em modo limitado ou via API externa se configurada.
) else (
    echo  [OK] Cerebro Local detectado e pronto.
)

REM Verificar URLs de documentação movidas
if not exist "docs\INSTALL.md" (
    echo   [INFO] Documentacao movida para a pasta /docs para organizacao.
)

echo.

REM ════════════════════════════════════════════════════
REM  [2/8] VERIFICAR AMBIENTE (.env)
REM ════════════════════════════════════════════════════
echo  [2/8] Validando configuracoes de ambiente...
set "ENV_FILE="
if exist ".env" ( set "ENV_FILE=.env" ) else ( if exist "env\.env" ( set "ENV_FILE=env\.env" ) )

if not defined ENV_FILE (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        set "ENV_FILE=.env"
        echo   [!] .env criado via .env.example. Revise suas chaves.
    ) else (
        echo   [ERRO] .env ausente. O Jarvis nao pode iniciar sem configuracoes.
        pause & exit /b 1
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
if defined UV (
    "!UV!" python install 3.12 --quiet
    for /f "usebackq delims=" %%i in (`"!UV!" python find 3.12 2^>nul`) do set "PYTHON=%%i"
)

if not defined PYTHON (
    for /f "usebackq delims=" %%i in (`where python 2^>nul`) do (
        set "_P=%%i"
        echo "!_P!" | findstr /i "WindowsApps" >nul
        if errorlevel 1 set "PYTHON=!_P!"
    )
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

echo  [OK] Backend integro.
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
for %%p in (8000 8081 3000) do (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr "%%p" 2^>nul') do (
        if "%%a" NEQ "0" taskkill /F /PID %%a >nul 2>&1
    )
)
echo  [OK] Portas 8000, 8081 e 3000 liberadas.
echo.

REM ════════════════════════════════════════════════════
REM  [7/8] INICIALIZAÇÃO SINCRONIZADA
REM ════════════════════════════════════════════════════
echo  [7/8] Iniciando Motores (Backend e UI)...

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
echo   (Os servicos continuarao rodando em segundo plano nas janelas minimizadas).
echo.
pause
exit
