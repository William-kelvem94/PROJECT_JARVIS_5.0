@echo off
REM JARVIS 5.0 - Start Minimal
REM Atalho leve: ativa venv e executa o main.py sem instalar dependências

:: Ir para a raiz do projeto (este arquivo fica em scripts\launchers)
cd /d "%~dp0\..\.."

:: Forçar terminal UTF-8
chcp 65001 >nul
set PYTHONUTF8=1

echo [INFO] Iniciando JARVIS (modo minimal)...

:: Ativar venv se existir
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

:: Marcar modo minimal para o processo Python
set JARVIS_MINIMAL=1
:: Executar Jarvis em headless minimal
python main.py %*

REM Fim
