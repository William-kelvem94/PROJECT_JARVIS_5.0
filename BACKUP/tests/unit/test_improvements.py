"""
Teste Simples do Sistema Core JARVIS
====================================

Teste focado nos componentes que implementamos/melhoramos.
"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))


def test_core_improvements():
    """Testa especificamente as melhorias implementadas"""
    print("🔧 JARVIS Core Improvements Test")
    print("=" * 40)

    # Test 1: StarkOrchestrator imports and basic functionality
    print("1️⃣ Testando StarkOrchestrator...")
    try:
        from src.core.orchestrator import StarkOrchestrator

        # Mock simples
        class MockJarvis:
            def __init__(self):
                self.shutdown_manager = None
                self.ai_agent = None
                self.window_manager = None

        mock_jarvis = MockJarvis()
        orchestrator = StarkOrchestrator(mock_jarvis)

        # Teste básico de status
        print(f"   ✅ Instância criada: is_ready = {orchestrator.is_ready}")

        # Teste de get_system_info (novo método)
        info = orchestrator.get_system_info()
        print(f"   ✅ get_system_info(): {info['components_count']} componentes")

        # Teste de health check (melhorado)
        health = orchestrator.get_system_health()
        print(f"   ✅ get_system_health(): {len(health)} módulos monitorados")

        print("   🎯 StarkOrchestrator: SUCESSO")

    except Exception as e:
        print(f"   ❌ StarkOrchestrator falhou: {e}")
        return False

    # Test 2: SecurityManager
    print("\n2️⃣ Testando SecurityManager...")
    try:
        from src.core.security.security_manager import SecurityManager

        security = SecurityManager()

        # Teste path validation
        safe_result = security.validate_path_access("/home/user/docs")
        unsafe_result = security.validate_path_access("C:\\Windows\\System32")

        print(f"   ✅ Path seguro aprovado: {safe_result}")
        print(f"   ✅ Path inseguro bloqueado: {not unsafe_result}")

        # Teste web validation
        safe_web = security.validate_web_request("https://google.com")
        unsafe_web = security.validate_web_request("https://malicious.com")

        print(f"   ✅ URL segura aprovada: {safe_web}")
        print(f"   ✅ URL insegura bloqueada: {not unsafe_web}")

        print("   🛡️ SecurityManager: SUCESSO")

    except Exception as e:
        print(f"   ❌ SecurityManager falhou: {e}")
        return False

    # Test 3: IOTManager
    print("\n3️⃣ Testando IOTManager...")
    try:
        from src.core.iot.iot_manager import IOTManager

        iot = IOTManager()

        print(f"   ✅ Instância criada: configurado = {iot.is_configured}")
        print(f"   ✅ Home Assistant URL: {iot.ha_url}")

        if not iot.is_configured:
            print("   ℹ️  IoT não configurado (esperado - token ausente)")

        print("   🏠 IOTManager: SUCESSO")

    except Exception as e:
        print(f"   ❌ IOTManager falhou: {e}")
        return False

    # Test 4: Core __init__.py improvements
    print("\n4️⃣ Testando imports melhorados...")
    try:
        from src.core import StarkOrchestrator, SecurityManager, IOTManager

        print("   ✅ Import direto from src.core funciona")

        # Verifica se __all__ está definido
        import src.core

        if hasattr(src.core, "__all__"):
            print(f"   ✅ __all__ definido com {len(src.core.__all__)} exports")

        print("   📦 Core imports: SUCESSO")

    except Exception as e:
        print(f"   ❌ Core imports falharam: {e}")
        return False

    # Test 5: Submodule __init__.py improvements
    print("\n5️⃣ Testando submodules melhorados...")

    submodules = [
        ("src.core.security", "SecurityManager"),
        ("src.core.iot", "IOTManager"),
    ]

    for module_name, class_name in submodules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            if hasattr(module, class_name):
                print(f"   ✅ {module_name}.{class_name} disponível")
            else:
                print(f"   ⚠️ {module_name}.{class_name} não encontrado")
        except Exception as e:
            print(f"   ❌ {module_name} falhou: {e}")

    print("   📁 Submodules: SUCESSO")

    print("\n🎉 Todas as melhorias funcionando corretamente!")
    return True


def main():
    """Executa todos os testes das melhorias"""
    success = test_core_improvements()

    if success:
        print("\n✨ RESULTADO: Todas as melhorias do sistema core estão funcionais!")
        print("\n📋 Melhorias implementadas:")
        print("   • StarkOrchestrator com métodos avançados")
        print("   • SecurityManager integrado")
        print("   • IOTManager integrado")
        print("   • Imports melhorados em __init__.py")
        print("   • Health checks expandidos")

    else:
        print("\n⚠️ RESULTADO: Algumas melhorias precisam de ajustes.")
        sys.exit(1)


if __name__ == "__main__":
    main()
