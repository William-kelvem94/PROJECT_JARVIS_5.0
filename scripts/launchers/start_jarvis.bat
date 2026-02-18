@echo off
setlocal EnableDelayedExpansion

:: ==================================================================================
:: JARVIS 5.0 - Professional Launcher
:: ==================================================================================
:: Configura o ambiente, verifica dependências e inicia o sistema principal.
:: Encaminha todos os argumentos de linha de comando para o script Python principal.
:: ==================================================================================

title JARVIS 5.0 - Singularity

:: Navega para o diretório raiz do projeto a partir da localização do script
cd /d "%~dp0\..\.."

:: 1. Configuração do Ambiente
:: ----------------------------------------------------------------------------------
:: Define o console para UTF-8 e configura o Python para I/O em UTF-8
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"

:: Para depuração do PyTorch, se necessário
set "CUDA_LAUNCH_BLOCKING=1"

:: Define especificidades do ambiente
set "VENV_DIR=venv"
set "JARVIS_ENV=production"

:: 2. Verificação do Ambiente Virtual
:: ----------------------------------------------------------------------------------
echo [INFO] Procurando pelo ambiente virtual em '%VENV_DIR%'...
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [ERROR] Ambiente Virtual nao encontrado!
    echo [INFO]  Por favor, execute o script de instalacao primeiro.
    pause
    exit /b 1
)

echo [INFO] Ativando Ambiente Neural...
call "%VENV_DIR%\Scripts\activate.bat"

:: 3. Inicialização do Sistema
:: ----------------------------------------------------------------------------------
echo [INFO] Inicializando Sistemas Principais...
set "PYTHONPATH=%CD%"

:: Executa a aplicação principal, encaminhando todos os argumentos do script
python main.py %*

:: 4. Pós-Execução
:: ----------------------------------------------------------------------------------
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [CRITICAL] O sistema travou com o codigo de saida %ERRORLEVEL%.
    echo [INFO]     Revise 'data/logs/errors_critical.log' para detalhes.
    pause
)

:: Desativando o ambiente virtual (boa prática)
if defined VIRTUAL_ENV (
    deactivate
)

endlocal