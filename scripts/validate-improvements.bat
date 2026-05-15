@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI\"
cd /d "%ROOT%"
REM ========================================================================
REM JARVIS 5.0 - Sistema de Validação de Melhorias
REM ========================================================================
REM Este script valida todas as melhorias implementadas em 2026-05-07
REM ========================================================================

setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║     JARVIS 5.0 - Validação de Melhorias (2026-05-07)          ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI\"
set "PYTHON_EXE=%ROOT%.venv\Scripts\python.exe"
set "PASS=0"
set "FAIL=0"
set "WARN=0"

REM Cores (apenas para display, não funcional em todos os terminais)
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "RESET=[0m"

echo ═══════════════════════════════════════════════════════════════════
echo  VERIFICAÇÃO 1: Ambiente Virtual
echo ═══════════════════════════════════════════════════════════════════

if exist "%PYTHON_EXE%" (
    echo ✅ Ambiente virtual encontrado
    set /a PASS+=1
) else (
    echo ❌ Ambiente virtual NÃO encontrado
    echo    Execute: scripts\setup-venv.bat
    set /a FAIL+=1
)

echo.
echo ═══════════════════════════════════════════════════════════════════
echo  VERIFICAÇÃO 2: Dependências Críticas
echo ═══════════════════════════════════════════════════════════════════

if exist "%PYTHON_EXE%" (
    echo Verificando pygame...
    "%PYTHON_EXE%" -c "import pygame; print('✅ pygame instalado')" 2>nul
    if errorlevel 1 (
        echo ❌ pygame NÃO instalado
        set /a FAIL+=1
    ) else (
        set /a PASS+=1
    )
    
    echo Verificando deepfilternet...
    "%PYTHON_EXE%" -c "import df; print('✅ deepfilternet instalado')" 2>nul
    if errorlevel 1 (
        echo ⚠️  deepfilternet NÃO instalado (opcional mas recomendado)
        set /a WARN+=1
    ) else (
        set /a PASS+=1
    )
    
    echo Verificando face_recognition...
    "%PYTHON_EXE%" -c "import face_recognition; print('✅ face_recognition instalado')" 2>nul
    if errorlevel 1 (
        echo ❌ face_recognition NÃO instalado
        set /a FAIL+=1
    ) else (
        set /a PASS+=1
    )
    
    echo Verificando watchdog (para auto-restart)...
    "%PYTHON_EXE%" -c "import watchdog; print('✅ watchdog instalado')" 2>nul
    if errorlevel 1 (
        echo ❌ watchdog NÃO instalado
        set /a FAIL+=1
    ) else (
        set /a PASS+=1
    )
)

echo.
echo ═══════════════════════════════════════════════════════════════════
echo  VERIFICAÇÃO 3: Arquivos Criados
echo ═══════════════════════════════════════════════════════════════════

if exist "%ROOT%backend\app\multi_agent_analysis.py" (
    echo ✅ multi_agent_analysis.py criado
    set /a PASS+=1
) else (
    echo ❌ multi_agent_analysis.py NÃO encontrado
    set /a FAIL+=1
)

if exist "%ROOT%backend\app\auto_restart.py" (
    echo ✅ auto_restart.py criado
    set /a PASS+=1
) else (
    echo ❌ auto_restart.py NÃO encontrado
    set /a FAIL+=1
)

if exist "%ROOT%scripts/restart-jarvis.bat" (
    echo ✅ scripts/restart-jarvis.bat criado
    set /a PASS+=1
) else (
    echo ❌ scripts/restart-jarvis.bat NÃO encontrado
    set /a FAIL+=1
)

if exist "%ROOT%docs\IMPROVEMENTS_2026-05-07.md" (
    echo ✅ Documentação de melhorias criada
    set /a PASS+=1
) else (
    echo ❌ Documentação NÃO encontrada
    set /a FAIL+=1
)

if exist "%ROOT%docs\MULTI_AGENT_SYSTEM.md" (
    echo ✅ Documentação do multi-agent criada
    set /a PASS+=1
) else (
    echo ❌ Documentação do multi-agent NÃO encontrada
    set /a FAIL+=1
)

echo.
echo ═══════════════════════════════════════════════════════════════════
echo  VERIFICAÇÃO 4: Sintaxe dos Arquivos Python
echo ═══════════════════════════════════════════════════════════════════

if exist "%PYTHON_EXE%" (
    echo Validando multi_agent_analysis.py...
    "%PYTHON_EXE%" -m py_compile backend\app\multi_agent_analysis.py 2>nul
    if errorlevel 1 (
        echo ❌ Erro de sintaxe em multi_agent_analysis.py
        set /a FAIL+=1
    ) else (
        echo ✅ multi_agent_analysis.py OK
        set /a PASS+=1
    )
    
    echo Validando auto_restart.py...
    "%PYTHON_EXE%" -m py_compile backend\app\auto_restart.py 2>nul
    if errorlevel 1 (
        echo ❌ Erro de sintaxe em auto_restart.py
        set /a FAIL+=1
    ) else (
        echo ✅ auto_restart.py OK
        set /a PASS+=1
    )
    
    echo Validando main.py...
    "%PYTHON_EXE%" -m py_compile backend\app\main.py 2>nul
    if errorlevel 1 (
        echo ❌ Erro de sintaxe em main.py
        set /a FAIL+=1
    ) else (
        echo ✅ main.py OK
        set /a PASS+=1
    )
    
    echo Validando routes.py...
    "%PYTHON_EXE%" -m py_compile backend\app\routes.py 2>nul
    if errorlevel 1 (
        echo ❌ Erro de sintaxe em routes.py
        set /a FAIL+=1
    ) else (
        echo ✅ routes.py OK
        set /a PASS+=1
    )
    
    echo Validando system_control.py...
    "%PYTHON_EXE%" -m py_compile backend\app\system_control.py 2>nul
    if errorlevel 1 (
        echo ❌ Erro de sintaxe em system_control.py
        set /a FAIL+=1
    ) else (
        echo ✅ system_control.py OK
        set /a PASS+=1
    )
)

echo.
echo ═══════════════════════════════════════════════════════════════════
echo  VERIFICAÇÃO 5: Scripts de Controle
echo ═══════════════════════════════════════════════════════════════════

if exist "%ROOT%start-jarvis.bat" (
    echo ✅ start-jarvis.bat encontrado
    set /a PASS+=1
) else (
    echo ❌ start-jarvis.bat NÃO encontrado
    set /a FAIL+=1
)

if exist "%ROOT%scripts\setup-venv.bat" (
    echo ✅ setup-venv.bat encontrado
    set /a PASS+=1
) else (
    echo ❌ setup-venv.bat NÃO encontrado
    set /a FAIL+=1
)

echo.
echo ═══════════════════════════════════════════════════════════════════
echo  RESUMO DA VALIDAÇÃO
echo ═══════════════════════════════════════════════════════════════════
echo.
echo   ✅ PASSOU:    %PASS% verificações
echo   ❌ FALHOU:    %FAIL% verificações
echo   ⚠️  AVISOS:    %WARN% verificações
echo.

if %FAIL% GTR 0 (
    echo ═══════════════════════════════════════════════════════════════════
    echo   ❌ VALIDAÇÃO FALHOU - Corrija os problemas antes de continuar
    echo ═══════════════════════════════════════════════════════════════════
    echo.
    echo AÇÕES RECOMENDADAS:
    echo   1. Execute: scripts\setup-venv.bat
    echo   2. Verifique os erros acima
    echo   3. Execute este script novamente
    echo.
    pause
    exit /b 1
) else (
    echo ═══════════════════════════════════════════════════════════════════
    echo   ✅ TODAS AS VERIFICAÇÕES PASSARAM!
    echo ═══════════════════════════════════════════════════════════════════
    echo.
    echo   O JARVIS 5.0 está pronto para uso com todas as melhorias.
    echo.
    echo PRÓXIMOS PASSOS:
    echo   1. Execute: start-jarvis.bat
    echo   2. Acesse: http://localhost:8001 (telemetry)
    echo   3. Teste: http://localhost:8000/agents/summary
    echo.
    if %WARN% GTR 0 (
        echo AVISOS:
        echo   - Há %WARN% dependência(s) opcional(is) não instalada(s)
        echo   - O sistema funcionará, mas com funcionalidade reduzida
        echo   - Para instalar tudo: set JARVIS_INSTALL_FACE_RECOGNITION=1
        echo.
    )
    pause
    exit /b 0
)
