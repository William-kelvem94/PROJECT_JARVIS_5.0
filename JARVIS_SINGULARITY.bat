@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: JARVIS SINGULARITY - AUTONOMOUS LAUNCHER
:: ============================================================================
:: Sistema de inicializacao totalmente autonomo com:
:: - Auto-deteccao e instalacao de Python
:: - Auto-configuracao de ambiente virtual
:: - Auto-instalacao de dependencias
:: - Auto-configuracao de API keys
:: - Auto-start e auto-restart em caso de falha
:: ============================================================================

:: -------------------------------------------------------------------------
:: CONFIGURACOES
:: -------------------------------------------------------------------------
set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%venv"
set "LOG_FILE=%PROJECT_DIR%jarvis_launcher.log"
set "PYTHON_MIN_VERSION=3.10"
set "MAX_RETRIES=3"
set "RETRY_COUNT=0"

:: Limpar log anterior
if exist "%LOG_FILE%" del "%LOG_FILE%"

:: -------------------------------------------------------------------------
:: SOLICITAR ELEVACAO DE PRIVILEGIO (ADM)
:: -------------------------------------------------------------------------
:check_Privileges
NET SESSION >nul 2>&1
if %ERRORLEVEL% == 0 (
    goto :gotAdmin
) else (
    echo.
    echo ========================================================================
    echo   SOLICITANDO PERMISSAO DE ADMINISTRADOR...
    echo ========================================================================
    echo.
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:gotAdmin
pushd "%CD%"
CD /D "%~dp0"

cls
call :log_message "================================================================================"
call :log_message "  JARVIS SINGULARITY - AUTONOMOUS LAUNCHER v2.0"
call :log_message "================================================================================"
call :log_message ""

:: -------------------------------------------------------------------------
:: ETAPA 1: VERIFICAR/INSTALAR PYTHON
:: -------------------------------------------------------------------------
call :log_message "[1/7] Verificando Python..."

:: Verificar se Python esta instalado
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    call :log_message "    Python nao encontrado. Tentando instalacao automatica..."
    call :install_python
    if !ERRORLEVEL! NEQ 0 (
        call :log_error "Falha ao instalar Python automaticamente"
        call :log_message "Por favor, instale Python %PYTHON_MIN_VERSION%+ manualmente:"
        call :log_message "https://www.python.org/downloads/"
        pause
        exit /b 1
    )
) else (
    :: Obter versao do Python
    for /f "tokens=2 delims= " %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    call :log_message "    Python !PYTHON_VERSION! encontrado"
)

:: -------------------------------------------------------------------------
:: ETAPA 2: CRIAR/ATIVAR AMBIENTE VIRTUAL
:: -------------------------------------------------------------------------
call :log_message ""
call :log_message "[2/7] Configurando ambiente virtual..."

if not exist "%VENV_DIR%" (
    call :log_message "    Criando ambiente virtual..."
    python -m venv "%VENV_DIR%"
    if !ERRORLEVEL! NEQ 0 (
        call :log_error "Falha ao criar ambiente virtual"
        pause
        exit /b 1
    )
    call :log_message "    Ambiente virtual criado com sucesso"
) else (
    call :log_message "    Ambiente virtual existente encontrado"
)

:: Ativar ambiente virtual
call :log_message "    Ativando ambiente virtual..."
call "%VENV_DIR%\Scripts\activate.bat"

:: -------------------------------------------------------------------------
:: ETAPA 3: ATUALIZAR PIP
:: -------------------------------------------------------------------------
call :log_message ""
call :log_message "[3/7] Atualizando pip..."
python -m pip install --upgrade pip >nul 2>&1
call :log_message "    Pip atualizado"

:: -------------------------------------------------------------------------
:: ETAPA 4: VERIFICAR E INSTALAR DEPENDENCIAS
:: -------------------------------------------------------------------------
call :log_message ""
call :log_message "[4/7] Verificando dependencias..."

if not exist "requirements_singularity.txt" (
    call :log_error "requirements_singularity.txt nao encontrado!"
    pause
    exit /b 1
)

:: Verificar se precisa instalar dependencias
python -c "import PyQt6" >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    call :log_message "    Instalando dependencias (isso pode demorar varios minutos)..."
    python setup_manager.py
    if !ERRORLEVEL! NEQ 0 (
        if !ERRORLEVEL! NEQ 1 (
            call :log_error "Erro ao instalar dependencias"
            call :log_message "    Tentando instalacao alternativa..."
            python -m pip install -r requirements_singularity.txt
            if !ERRORLEVEL! NEQ 0 (
                call :log_error "Falha na instalacao de dependencias"
                pause
                exit /b 1
            )
        )
    )
    call :log_message "    Dependencias instaladas"
) else (
    call :log_message "    Dependencias ja instaladas"
)

:: -------------------------------------------------------------------------
:: ETAPA 5: VALIDAR ESTRUTURA DO PROJETO
:: -------------------------------------------------------------------------
call :log_message ""
call :log_message "[5/7] Validando estrutura do projeto..."

call :validate_structure
if !ERRORLEVEL! NEQ 0 (
    call :log_error "Estrutura do projeto invalida"
    pause
    exit /b 1
)

:: -------------------------------------------------------------------------
:: ETAPA 6: CONFIGURAR API KEYS (SE NECESSARIO)
:: -------------------------------------------------------------------------
call :log_message ""
call :log_message "[6/7] Verificando configuracao..."

if "%GOOGLE_API_KEY%"=="" (
    call :log_message "    API Key nao configurada. Sistema funcionara em modo local."
    call :log_message "    Para melhor desempenho, configure GOOGLE_API_KEY no config.yaml"
) else (
    call :log_message "    API Key configurada"
)

:: -------------------------------------------------------------------------
:: ETAPA 7: INICIAR JARVIS COM AUTO-RESTART
:: -------------------------------------------------------------------------
call :log_message ""
call :log_message "[7/7] Iniciando JARVIS Singularity..."
call :log_message ""
call :log_message "================================================================================"
call :log_message "  JARVIS ONLINE - Sistema Operacional"
call :log_message "================================================================================"
call :log_message ""

:start_jarvis
if exist main.py (
    python main.py
) else if exist main_singularity.py (
    python main_singularity.py
) else (
    call :log_error "Entry point nao encontrado!"
    pause
    exit /b 1
)

set JARVIS_EXIT_CODE=%ERRORLEVEL%

:: -------------------------------------------------------------------------
:: TRATAMENTO DE ERRO E AUTO-RESTART
:: -------------------------------------------------------------------------
call :log_message ""
call :log_message "================================================================================"
call :log_message "  JARVIS ENCERRADO (codigo: %JARVIS_EXIT_CODE%)"
call :log_message "================================================================================"

if %JARVIS_EXIT_CODE% EQU 0 (
    call :log_message "  Encerramento normal"
    goto :end_launcher
) else if %JARVIS_EXIT_CODE% EQU 130 (
    call :log_message "  Interrompido pelo usuario (Ctrl+C)"
    goto :end_launcher
) else (
    set /a RETRY_COUNT+=1
    if !RETRY_COUNT! LEQ %MAX_RETRIES% (
        call :log_message "  Erro detectado. Tentativa !RETRY_COUNT! de %MAX_RETRIES%..."
        call :log_message "  Reiniciando em 5 segundos..."
        timeout /t 5 >nul
        goto :start_jarvis
    ) else (
        call :log_error "Numero maximo de tentativas excedido"
        call :log_message "  Verifique os logs em: %LOG_FILE%"
    )
)

:end_launcher
call :log_message ""
pause
exit /b %JARVIS_EXIT_CODE%

:: ============================================================================
:: FUNCOES AUXILIARES
:: ============================================================================

:log_message
echo %~1
echo %~1 >> "%LOG_FILE%"
goto :eof

:log_error
echo    [ERRO] %~1
echo    [ERRO] %~1 >> "%LOG_FILE%"
goto :eof

:install_python
:: Tentar instalar Python via winget
where winget >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    call :log_message "    Instalando Python via winget..."
    :: Install Python 3.10 or later - let winget choose the latest stable
    winget install Python.Python.3.10 --silent
    if !ERRORLEVEL! EQU 0 (
        call :log_message "    Python instalado com sucesso"
        :: Refresh PATH - let Windows find Python automatically
        call refreshenv >nul 2>&1
        exit /b 0
    )
)

:: Tentar via chocolatey
where choco >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    call :log_message "    Instalando Python via chocolatey..."
    choco install python --version=3.10 -y
    if !ERRORLEVEL! EQU 0 (
        call :log_message "    Python instalado com sucesso"
        exit /b 0
    )
)

:: Se chegou aqui, falhou
exit /b 1

:validate_structure
:: Verificar arquivos criticos
set "VALIDATION_FAILED=0"

if not exist "src\core\ai_agent.py" (
    call :log_error "    src\core\ai_agent.py nao encontrado"
    set "VALIDATION_FAILED=1"
)

if not exist "src\interface\ai_worker.py" (
    call :log_error "    src\interface\ai_worker.py nao encontrado"
    set "VALIDATION_FAILED=1"
)

if not exist "config.yaml" (
    call :log_error "    config.yaml nao encontrado"
    set "VALIDATION_FAILED=1"
)

if "%VALIDATION_FAILED%"=="1" (
    exit /b 1
)

call :log_message "    Estrutura validada com sucesso"
exit /b 0
