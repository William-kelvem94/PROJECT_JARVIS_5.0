@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI\"
cd /d "%ROOT%"
REM JARVIS 5.0 - Auto-Fix Agents Validation
REM Verifica se os 4 agentes de auto-correção estão ativos e funcionais
REM Data: 7 de maio de 2026

echo =========================================
echo    JARVIS 5.0 AUTO-FIX AGENTS TEST
echo =========================================
echo.

echo [TEST 1] Verificando agentes ativos...
powershell -Command "(Invoke-RestMethod http://localhost:8000/agents/summary).total_agents"
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Backend não está respondendo!
    echo Execute: start-jarvis.bat
    pause
    exit /b 1
)
echo Esperado: 14 agentes (10 análise + 4 auto-fix)
echo.

echo [TEST 2] Listando todos os agentes...
powershell -Command "Invoke-RestMethod http://localhost:8000/agents/summary | Select-Object -ExpandProperty agents | Where-Object { $_.name -like '*Agent*' } | Select-Object name, running | ConvertTo-Json -Depth 3"
echo.

echo [TEST 3] Verificando agentes de auto-fix especificamente...
powershell -Command "Invoke-RestMethod http://localhost:8000/agents/summary | Select-Object -ExpandProperty agents | Where-Object { $_.name -like '*Fix*' -or $_.name -like '*Dependency*' -or $_.name -like '*Recovery*' -or $_.name -like '*Repair*' } | Select-Object name, type, running | ConvertTo-Json -Depth 3"
echo.

echo [TEST 4] Verificando findings de auto-fix...
powershell -Command "Invoke-RestMethod http://localhost:8000/agents/findings | Select-Object -ExpandProperty findings | Where-Object { $_.title -like '*Auto-Fix*' -or $_.title -like '*Dependência*' -or $_.title -like '*Socket*' -or $_.title -like '*Áudio*' } | ConvertTo-Json -Depth 3"
echo.

echo [TEST 5] Verificando findings críticos...
powershell -Command "(Invoke-RestMethod http://localhost:8000/agents/critical).critical_findings"
echo.

echo [TEST 6] Verificando dependências faltando...
powershell -Command "Invoke-RestMethod http://localhost:8000/agents/findings | Select-Object -ExpandProperty findings | Where-Object { $_.title -like '*Dependência*' } | ConvertTo-Json -Depth 3"
echo.

echo [TEST 7] Verificando recovery de endpoints...
powershell -Command "Invoke-RestMethod http://localhost:8000/agents/findings | Select-Object -ExpandProperty findings | Where-Object { $_.title -like '*Socket*' -or $_.title -like '*Endpoint*' } | ConvertTo-Json -Depth 3"
echo.

echo [TEST 8] Testando endpoint /telemetry/status...
curl -s http://localhost:8000/telemetry/status
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Endpoint com problemas - EndpointRecoveryAgent deve detectar
)
echo.

echo [TEST 9] Verificando status de áudio...
powershell -Command "Invoke-RestMethod http://localhost:8000/agents/findings | Select-Object -ExpandProperty findings | Where-Object { $_.title -like '*Áudio*' -or $_.title -like '*Audio*' } | ConvertTo-Json -Depth 3"
echo.

echo [TEST 10] Verificando health do sistema...
powershell -Command "(Invoke-RestMethod http://localhost:8000/system/capabilities).summary"
echo.

echo =========================================
echo           VALIDAÇÃO COMPLETA
echo =========================================
echo.
echo Próximos passos:
echo.
echo 1. Verificar se total_agents == 14
echo 2. Confirmar agentes de auto-fix running: true
echo 3. Se houver findings críticos, ver recommendation
echo 4. Se dependências faltando, copiar comando fornecido
echo 5. Aguardar 5 minutos e verificar auto-fixes aplicados
echo.
echo Ver documentação completa:
echo - docs\AUTOFIX_AGENTS.md
echo - docs/guides/AUTOFIX_README.md
echo.
pause
