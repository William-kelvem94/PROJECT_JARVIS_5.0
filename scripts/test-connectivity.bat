@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI\"
cd /d "%ROOT%"
REM ========================================================================
REM JARVIS 5.0 - Teste de Conectividade dos Endpoints
REM ========================================================================
REM Este script testa todos os endpoints críticos do JARVIS
REM ========================================================================

setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║     JARVIS 5.0 - Teste de Conectividade de Endpoints          ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

set "PYTHON_EXE=%ROOT%.venv\Scripts\python.exe"
set "PASS=0"
set "FAIL=0"

if not exist "%PYTHON_EXE%" (
    echo ❌ Ambiente virtual não encontrado
    echo    Execute: scripts\setup-venv.bat
    pause
    exit /b 1
)

echo Instalando requests (se necessário)...
"%PYTHON_EXE%" -m pip install requests --quiet 2>nul

echo.
echo ═══════════════════════════════════════════════════════════════════
echo  TESTANDO ENDPOINTS DO BACKEND (porta 8000)
echo ═══════════════════════════════════════════════════════════════════
echo.

echo Criando script de teste...
(
echo import requests
echo import json
echo import sys
echo.
echo def test_endpoint^(url, name^):
echo     try:
echo         response = requests.get^(url, timeout=10^)
echo         if response.status_code == 200:
echo             print^(f"✅ {name}: OK ^(status {response.status_code}^)"^)
echo             return True
echo         else:
echo             print^(f"⚠️  {name}: Status {response.status_code}"^)
echo             return False
echo     except requests.exceptions.ConnectionError:
echo         print^(f"❌ {name}: Conexão recusada ^(servidor offline?^)"^)
echo         return False
echo     except requests.exceptions.Timeout:
echo         print^(f"❌ {name}: Timeout ^(>10s^)"^)
echo         return False
echo     except Exception as e:
echo         print^(f"❌ {name}: {str^(e^)}"^)
echo         return False
echo.
echo endpoints = [
echo     ^("http://localhost:8000/health", "Health Check"^),
echo     ^("http://localhost:8000/telemetry/status", "Telemetry Status"^),
echo     ^("http://localhost:8000/telemetry/api/status", "Telemetry API Status"^),
echo     ^("http://localhost:8000/agents/summary", "Multi-Agent Summary"^),
echo     ^("http://localhost:8000/agents/findings", "Multi-Agent Findings"^),
echo     ^("http://localhost:8000/agents/critical", "Multi-Agent Critical"^),
echo ]
echo.
echo print^("Testando endpoints do backend..."^)
echo passed = 0
echo failed = 0
echo.
echo for url, name in endpoints:
echo     if test_endpoint^(url, name^):
echo         passed += 1
echo     else:
echo         failed += 1
echo.
echo print^(f"\n═══════════════════════════════════════════════"^)
echo print^(f"Resultados: ✅ {passed} passaram / ❌ {failed} falharam"^)
echo print^(f"═══════════════════════════════════════════════\n"^)
echo.
echo if failed ^> 0:
echo     print^("AÇÕES RECOMENDADAS:"^)
echo     print^("1. Verifique se o backend está rodando: python -m uvicorn app.main:app --reload"^)
echo     print^("2. Verifique os logs em logs/"^)
echo     print^("3. Execute scripts/validate-improvements.bat para verificar dependências"^)
echo     sys.exit^(1^)
echo else:
echo     print^("✅ Todos os endpoints estão funcionando corretamente!"^)
echo     sys.exit^(0^)
) > test_connectivity.py

echo Executando testes...
echo.
"%PYTHON_EXE%" test_connectivity.py
set "TEST_RESULT=%ERRORLEVEL%"

del test_connectivity.py 2>nul

echo.
if %TEST_RESULT% EQU 0 (
    echo ╔════════════════════════════════════════════════════════════════╗
    echo ║               ✅ TODOS OS TESTES PASSARAM!                     ║
    echo ╚════════════════════════════════════════════════════════════════╝
    echo.
    echo O sistema está pronto para uso.
    echo.
    echo PRÓXIMOS PASSOS:
    echo   - Acesse o frontend: http://localhost:3000
    echo   - Verifique telemetria: http://localhost:8001
    echo   - Consulte agentes: http://localhost:8000/agents/summary
    echo.
) else (
    echo ╔════════════════════════════════════════════════════════════════╗
    echo ║               ❌ ALGUNS TESTES FALHARAM                        ║
    echo ╚════════════════════════════════════════════════════════════════╝
    echo.
    echo Verifique os problemas acima antes de prosseguir.
    echo.
)

pause
exit /b %TEST_RESULT%
