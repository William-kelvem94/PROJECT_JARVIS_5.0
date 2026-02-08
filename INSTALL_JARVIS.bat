@echo off
:: JARVIS 5.0 - UNIVERSAL INSTALLER v1.2 (Extreme Compatibility)
:: Se este script fechar sozinho, tente abrir o CMD primeiro e arrastar este arquivo para dentro.

echo [DEBUG] Script iniciado. Pressione qualquer tecla para continuar o setup...
pause

echo.
echo ==========================================================================
echo                 JARVIS 5.0 - PROTOCOLO DE INSTALACAO
echo ==========================================================================
echo.

set "ROOT=%~dp0"
cd /d "%ROOT%"

echo [INFO] Diretorio raiz: %ROOT%

:: Check Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado. Instale o Python 3.11 e marque 'Add to PATH'.
    pause
    exit /b 1
)

:: Create VENV
if exist "%ROOT%venv\Scripts\python.exe" goto SKIP_VENV
echo [INFO] Criando ambiente virtual...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao criar venv.
    pause
    exit /b 1
)
:SKIP_VENV

:: Install
echo [INFO] Instalando dependencias...
"%ROOT%venv\Scripts\python.exe" "%ROOT%scripts\install\total_installer.py"

if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha na instalacao.
    pause
    exit /b 1
)

echo.
echo [OK] Instalacao concluida!
pause
exit /b 0
