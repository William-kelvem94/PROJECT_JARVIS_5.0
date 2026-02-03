@echo off
chcp 65001 >nul
title PROJECT JARVIS 5.0
REM Launcher profissional para o Jarvis 5.0
REM Encontra Python automaticamente e executa o launcher

echo.
echo ===========================================
echo PROJECT JARVIS 5.0
echo ===========================================
echo.
echo Sistema profissional de captura, processamento
echo e análise inteligente de dados da tela.
echo.
echo ===========================================
echo.

REM Usar caminho completo do Python (já testado e funcionando)
set PYTHON_EXE="C:\Users\willi\AppData\Local\Programs\Python\Python311\python.exe"
echo Usando Python do caminho conhecido
%PYTHON_EXE% --version
echo.

REM Verificar argumentos e executar launcher Python
if "%1"=="check" (
    echo Modo: Verificacao de sistema
    %PYTHON_EXE% launcher.py check
    goto :end
)

if "%1"=="install" (
    echo Modo: Instalacao de dependencias
    %PYTHON_EXE% launcher.py install
    goto :end
)

if "%1"=="run" (
    echo Modo: Execucao direta
    %PYTHON_EXE% launcher.py run
    goto :end
)

if "%1"=="menu" (
    echo Modo: Menu interativo
    %PYTHON_EXE% launcher.py menu
    goto :end
)

REM Modo automático (padrão)
echo Modo: Automatico inteligente
echo.
echo O launcher irá:
echo - Verificar se tudo está configurado
echo - Instalar dependências se necessário
echo - Executar a aplicação automaticamente
echo.

%PYTHON_EXE% launcher.py auto

:end
echo.
echo ===========================================
echo ✅ Processo finalizado
echo ===========================================
echo.
echo DICAS:
echo - Execute sem argumentos para modo automático
echo - Use "LeitorTela.bat check" para verificar sistema
echo - Use "LeitorTela.bat menu" para menu interativo
echo.
pause
