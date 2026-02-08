@echo off
:: JARVIS 5.0 - LAUNCHER v9.2 (Extreme Compatibility)
:: Se este script fechar sozinho, tente abrir o CMD primeiro e arrastar este arquivo para dentro.

echo [DEBUG] Script iniciado. Pressione qualquer tecla para abrir o JARVIS...
pause

set "ROOT=%~dp0"
cd /d "%ROOT%"

set "KMP_DUPLICATE_LIB_OK=TRUE"
set "PYTHONUTF8=1"

set "VENV_PYTHON=%ROOT%venv\Scripts\python.exe"

if exist "%VENV_PYTHON%" goto START_SYSTEM

echo.
echo [AVISO] venv nao encontrado. Redirecionando para o instalador...
pause
call "%ROOT%INSTALL_JARVIS.bat"

if not exist "%VENV_PYTHON%" (
    echo [ERRO] O ambiente venv nao foi criado. Rode o INSTALL_JARVIS.bat primeiro.
    pause
    exit /b 1
)

:START_SYSTEM
echo.
echo [SISTEMA] Iniciando Singularity Core...
"%VENV_PYTHON%" "%ROOT%SINGULARITY_LAUNCHER.py" %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] O sistema parou com codigo %ERRORLEVEL%.
    pause
)

exit /b 0
