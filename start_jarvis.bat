@echo off
<<<<<<< Updated upstream
REM JARVIS 5.0 Startup Script

REM Garantir execução na raiz do projeto
cd /d "%~dp0"

echo =============================================
echo   Iniciando JARVIS 5.0...
echo =============================================

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python não encontrado. Instale o Python 3.11+ em https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Instalar ambiente virtual se não existir
if not exist venv\Scripts\activate.bat (
    echo [INFO] Ambiente virtual não encontrado. Criando venv...
    python -m venv venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar venv. Verifique permissões e tente novamente.
        pause
        exit /b 1
    )
)

REM Ativar ambiente virtual
call venv\Scripts\activate.bat

REM Instalar dependências se necessário
if exist requirements.txt (
    echo [INFO] Instalando dependências do requirements.txt...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar dependências. Verifique o requirements.txt.
        pause
        exit /b 1
    )
)

REM Verificar dependências específicas do projeto
python scripts/install/setup_jarvis.py --quick-check
if errorlevel 1 (
    echo [AVISO] Dependências ausentes ou falha na verificação. Executando setup completo...
    python scripts/install/setup_jarvis.py --no-scripts
    if errorlevel 1 (
        echo [ERRO] Setup falhou. Verifique os logs e tente novamente.
        pause
        exit /b 1
    )
)

REM Modo debug
set DEBUG_MODE=
for %%A in (%*) do (
    if /I "%%A"=="--debug" set DEBUG_MODE=1
)

REM Executar JARVIS
if defined DEBUG_MODE (
    echo [INFO] Executando em modo DEBUG...
    python main.py --debug %*
) else (
    python main.py %*
)

REM Mensagem final
if errorlevel 1 (
    echo [ERRO] JARVIS finalizou com erro. Consulte os logs.
    pause
) else (
    echo [SUCESSO] JARVIS finalizado normalmente.
)
=======
setlocal
cd /d "%~dp0"

REM Compatibility shim to centralized launcher
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

call "scripts\launchers\start_jarvis.bat" %*
exit /b %ERRORLEVEL%
>>>>>>> Stashed changes
