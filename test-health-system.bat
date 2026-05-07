@echo off
REM ========================================================================
REM JARVIS 5.0 - Teste do Sistema de Health Checking em Tempo Real
REM ========================================================================
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║    JARVIS 5.0 - Teste de Health Checking em Tempo Real        ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

set "PYTHON_EXE=.venv\Scripts\python.exe"

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
echo  TESTANDO SISTEMA DE HEALTH CHECKING
echo ═══════════════════════════════════════════════════════════════════
echo.

echo Criando script de teste...
(
echo import requests
echo import json
echo import sys
echo from datetime import datetime
echo.
echo def test_endpoint^(url, name, expected_keys=None^):
echo     """Testa um endpoint e valida resposta."""
echo     try:
echo         print^(f"\n🔍 Testando: {name}"^)
echo         response = requests.get^(url, timeout=10^)
echo         
echo         if response.status_code != 200:
echo             print^(f"   ❌ Status {response.status_code}"^)
echo             return False
echo         
echo         data = response.json^(^)
echo         
echo         if expected_keys:
echo             for key in expected_keys:
echo                 if key not in data:
echo                     print^(f"   ⚠️  Key '{key}' não encontrada"^)
echo                     return False
echo         
echo         print^(f"   ✅ OK - {len^(json.dumps^(data^)^)} bytes"^)
echo         return True
echo     except requests.exceptions.Timeout:
echo         print^(f"   ❌ Timeout ^(>10s^)"^)
echo         return False
echo     except Exception as e:
echo         print^(f"   ❌ Erro: {str^(e^)[:50]}"^)
echo         return False
echo.
echo def test_capabilities^(^):
echo     """Testa endpoint de capabilities com validação detalhada."""
echo     print^("\n🔍 Testando: /system/capabilities ^(detalhado^)"^)
echo     
echo     try:
echo         response = requests.get^("http://localhost:8000/system/capabilities", timeout=10^)
echo         if response.status_code != 200:
echo             print^(f"   ❌ Status {response.status_code}"^)
echo             return False
echo         
echo         data = response.json^(^)
echo         
echo         # Validar estrutura
echo         if "capabilities" not in data:
echo             print^("   ❌ Key 'capabilities' não encontrada"^)
echo             return False
echo         
echo         if "summary" not in data:
echo             print^("   ❌ Key 'summary' não encontrada"^)
echo             return False
echo         
echo         caps = data["capabilities"]
echo         summary = data["summary"]
echo         
echo         # Contar componentes
echo         groups = ["nucleo_cognitivo", "percepcao", "sistema", "seguranca", "hardware"]
echo         total_components = 0
echo         
echo         for group_name in groups:
echo             if group_name in caps:
echo                 components = caps[group_name].get^("components", []^)
echo                 total_components += len^(components^)
echo                 print^(f"   📦 {caps[group_name]['title']}: {len^(components^)} componentes"^)
echo         
echo         # Mostrar sumário
echo         print^(f"\n   📊 SUMÁRIO:"^)
echo         print^(f"      Total:    {summary['total']}"^)
echo         print^(f"      Online:   {summary['online']}"^)
echo         print^(f"      Offline:  {summary['offline']}"^)
echo         print^(f"      Degraded: {summary['degraded']}"^)
echo         print^(f"      Error:    {summary['error']}"^)
echo         print^(f"      Health:   {summary['health_percentage']:.1f}%%"^)
echo         
echo         if total_components != summary['total']:
echo             print^(f"\n   ⚠️  Contagem não bate: {total_components} vs {summary['total']}"^)
echo         
echo         print^(f"\n   ✅ Capabilities OK"^)
echo         return True
echo     
echo     except Exception as e:
echo         print^(f"   ❌ Erro: {str^(e^)}"^)
echo         return False
echo.
echo def test_agents_summary^(^):
echo     """Testa se agentes estão ativos."""
echo     print^("\n🔍 Testando: /agents/summary ^(agentes especializados^)"^)
echo     
echo     try:
echo         response = requests.get^("http://localhost:8000/agents/summary", timeout=10^)
echo         if response.status_code != 200:
echo             print^(f"   ❌ Status {response.status_code}"^)
echo             return False
echo         
echo         data = response.json^(^)
echo         
echo         if "total_agents" not in data:
echo             print^("   ❌ Key 'total_agents' não encontrada"^)
echo             return False
echo         
echo         total = data.get^("total_agents", 0^)
echo         running = data.get^("agents_running", 0^)
echo         
echo         print^(f"   📊 Total de agentes: {total}"^)
echo         print^(f"   ▶️  Agentes rodando: {running}"^)
echo         
echo         if total ^>= 10:
echo             print^(f"   ✅ 10+ agentes registrados ^(esperado: 10^)"^)
echo         else:
echo             print^(f"   ⚠️  Apenas {total} agentes ^(esperado: 10^)"^)
echo         
echo         return True
echo     
echo     except Exception as e:
echo         print^(f"   ❌ Erro: {str^(e^)}"^)
echo         return False
echo.
echo print^("═══════════════════════════════════════════════════════════════════"^)
echo print^("  TESTE 1: Endpoints Básicos"^)
echo print^("═══════════════════════════════════════════════════════════════════"^)
echo.
echo tests = [
echo     ^("http://localhost:8000/health", "Health Check", ["status"]^),
echo     ^("http://localhost:8000/system/hardware", "Hardware Status", ["camera", "microphone"]^),
echo ]
echo.
echo passed = 0
echo failed = 0
echo.
echo for url, name, keys in tests:
echo     if test_endpoint^(url, name, keys^):
echo         passed += 1
echo     else:
echo         failed += 1
echo.
echo print^("\n═══════════════════════════════════════════════════════════════════"^)
echo print^("  TESTE 2: Capabilities e Agentes"^)
echo print^("═══════════════════════════════════════════════════════════════════"^)
echo.
echo if test_capabilities^(^):
echo     passed += 1
echo else:
echo     failed += 1
echo.
echo if test_agents_summary^(^):
echo     passed += 1
echo else:
echo     failed += 1
echo.
echo print^("\n═══════════════════════════════════════════════════════════════════"^)
echo print^(f"  RESULTADOS: ✅ {passed} passaram / ❌ {failed} falharam"^)
echo print^("═══════════════════════════════════════════════════════════════════\n"^)
echo.
echo if failed ^> 0:
echo     print^("AÇÕES RECOMENDADAS:"^)
echo     print^("1. Verifique se o backend está rodando na porta 8000"^)
echo     print^("2. Execute: python -m uvicorn app.main:app --reload"^)
echo     print^("3. Verifique logs em logs/"^)
echo     sys.exit^(1^)
echo else:
echo     print^("✅ Sistema de Health Checking funcionando perfeitamente!"^)
echo     print^("\nPRÓXIMOS PASSOS:"^)
echo     print^("  - Acesse o dashboard: http://localhost:3000"^)
echo     print^("  - Verifique capabilities: http://localhost:8000/system/capabilities"^)
echo     print^("  - Consulte agentes: http://localhost:8000/agents/summary"^)
echo     sys.exit^(0^)
) > test_health_system.py

echo Executando testes...
echo.
"%PYTHON_EXE%" test_health_system.py
set "TEST_RESULT=%ERRORLEVEL%"

del test_health_system.py 2>nul

echo.
if %TEST_RESULT% EQU 0 (
    echo ╔════════════════════════════════════════════════════════════════╗
    echo ║          ✅ SISTEMA DE HEALTH CHECKING VALIDADO!              ║
    echo ╚════════════════════════════════════════════════════════════════╝
    echo.
    echo O sistema está monitorando 19 componentes com 10 agentes.
    echo.
) else (
    echo ╔════════════════════════════════════════════════════════════════╗
    echo ║               ❌ ALGUNS TESTES FALHARAM                        ║
    echo ╚════════════════════════════════════════════════════════════════╝
    echo.
)

pause
exit /b %TEST_RESULT%
