@echo off
REM JARVIS 5.0 - Auto-Fix Agents Validation
REM Verifica se os 4 agentes de auto-correção estão ativos e funcionais
REM Data: 7 de maio de 2026

echo =========================================
echo    JARVIS 5.0 AUTO-FIX AGENTS TEST
echo =========================================
echo.

echo [TEST 1] Verificando agentes ativos...
curl -s http://localhost:8000/agents/summary | jq ".total_agents"
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Backend não está respondendo!
    echo Execute: start-jarvis.bat
    pause
    exit /b 1
)
echo Esperado: 14 agentes (10 análise + 4 auto-fix)
echo.

echo [TEST 2] Listando todos os agentes...
curl -s http://localhost:8000/agents/summary | jq ".agents[] | select(.name | contains(\"Agent\")) | {name: .name, running: .running}"
echo.

echo [TEST 3] Verificando agentes de auto-fix especificamente...
curl -s http://localhost:8000/agents/summary | jq ".agents[] | select(.name | contains(\"Fix\") or contains(\"Dependency\") or contains(\"Recovery\") or contains(\"Repair\")) | {name: .name, type: .type, running: .running}"
echo.

echo [TEST 4] Verificando findings de auto-fix...
curl -s http://localhost:8000/agents/findings | jq ".findings[] | select(.title | contains(\"Auto-Fix\") or contains(\"Dependência\") or contains(\"Socket\") or contains(\"Áudio\"))"
echo.

echo [TEST 5] Verificando findings críticos...
curl -s http://localhost:8000/agents/critical | jq ".critical_findings"
echo.

echo [TEST 6] Verificando dependências faltando...
curl -s http://localhost:8000/agents/findings | jq ".findings[] | select(.title | contains(\"Dependência\"))"
echo.

echo [TEST 7] Verificando recovery de endpoints...
curl -s http://localhost:8000/agents/findings | jq ".findings[] | select(.title | contains(\"Socket\") or contains(\"Endpoint\"))"
echo.

echo [TEST 8] Testando endpoint /telemetry/status...
curl -s http://localhost:8000/telemetry/status
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Endpoint com problemas - EndpointRecoveryAgent deve detectar
)
echo.

echo [TEST 9] Verificando status de áudio...
curl -s http://localhost:8000/agents/findings | jq ".findings[] | select(.title | contains(\"Áudio\") or contains(\"Audio\"))"
echo.

echo [TEST 10] Verificando health do sistema...
curl -s http://localhost:8000/system/capabilities | jq ".summary"
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
echo - AUTOFIX_README.md
echo.
pause
