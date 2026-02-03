@echo off
chcp 65001 >nul
title Teste Direto - Leitor de Tela

echo.
echo 🧪 TESTE DIRETO - LEITOR DE TELA
echo ===========================================
echo.

echo 📋 Procurando Python...

REM Tentar caminhos comuns do Python
set PYTHON_EXE=
if exist "C:\Python311\python.exe" set PYTHON_EXE=C:\Python311\python.exe
if exist "C:\Python310\python.exe" set PYTHON_EXE=C:\Python310\python.exe
if exist "C:\Python39\python.exe" set PYTHON_EXE=C:\Python39\python.exe
if exist "C:\Program Files\Python311\python.exe" set PYTHON_EXE="C:\Program Files\Python311\python.exe"
if exist "C:\Program Files\Python310\python.exe" set PYTHON_EXE="C:\Program Files\Python310\python.exe"
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe" set PYTHON_EXE="C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe"

REM Tentar python no PATH
if not defined PYTHON_EXE (
    python --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_EXE=python
    )
)

if not defined PYTHON_EXE (
    echo ❌ Python não encontrado!
    echo.
    echo 🔧 Instale Python de: https://python.org
    pause
    exit /b 1
)

echo ✅ Python encontrado: %PYTHON_EXE%
%PYTHON_EXE% --version
echo.

echo 📋 Testando aplicação diretamente...
echo (Isto irá mostrar exatamente onde está o erro)
echo.

%PYTHON_EXE% main.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Aplicação falhou! Código de erro: %errorlevel%
    echo.
    echo 🔧 Verifique as mensagens de erro acima.
) else (
    echo.
    echo ✅ Aplicação executada com sucesso!
)

echo.
pause
