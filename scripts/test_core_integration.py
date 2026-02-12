"""
Demonstração do Sistema Core JARVIS
===================================

Script para demonstrar o funcionamento dos módulos principais
e testar a integração entre os components do sistema.
"""

import sys
import logging
from pathlib import Path

# Adicionar o diretório raiz ao Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_core_integration():
    """Testa a integração dos módulos core"""
    print("🚀 JARVIS Core Integration Test")
    print("=" * 50)
    
    try:
        # Mock de JarvisCore para teste
        class MockJarvisCore:
            def __init__(self):
                self.shutdown_manager = None
                self.ai_agent = None
                self.window_manager = None
        
        # 1. Testar imports
        print("📦 Testando imports...")
        try:
            from src.core import StarkOrchestrator, SecurityManager, IOTManager
            print("✅ Imports principais funcionando")
        except Exception as e:
            print(f"❌ Erro nos imports: {e}")
            return False
        
        # 2. Testar StarkOrchestrator
        print("\n🎛️ Testando StarkOrchestrator...")
        try:
            mock_jarvis = MockJarvisCore()
            orchestrator = StarkOrchestrator(mock_jarvis)
            
            # Teste de health check
            health = orchestrator.get_system_health()
            print(f"   📊 System Health: {health}")
            
            # Teste de informações do sistema
            info = orchestrator.get_system_info()
            print(f"   💻 System Info: Components={info['components_count']}, Ready={info['is_ready']}")
            
            print("✅ StarkOrchestrator funcionando")
        except Exception as e:
            print(f"❌ Erro no StarkOrchestrator: {e}")
            return False
        
        # 3. Testar SecurityManager
        print("\n🔒 Testando SecurityManager...")
        try:
            security = SecurityManager()
            
            # Teste de validação de paths
            safe_path = "/home/user/documents"
            unsafe_path = "C:\\Windows\\System32"
            
            print(f"   🛡️ Path '{safe_path}' é seguro: {security.validate_path_access(safe_path)}")
            print(f"   🛡️ Path '{unsafe_path}' é seguro: {security.validate_path_access(unsafe_path)}")
            
            # Teste de validação web
            safe_url = "https://google.com/search"
            unsafe_url = "https://malicious-site.com"
            
            print(f"   🌐 URL '{safe_url}' é segura: {security.validate_web_request(safe_url)}")
            print(f"   🌐 URL '{unsafe_url}' é segura: {security.validate_web_request(unsafe_url)}")
            
            print("✅ SecurityManager funcionando")
        except Exception as e:
            print(f"❌ Erro no SecurityManager: {e}")
            return False
        
        # 4. Testar IOTManager
        print("\n🏠 Testando IOTManager...")
        try:
            iot = IOTManager()
            print(f"   🔧 IoT configurado: {iot.is_configured}")
            print(f"   🌐 Home Assistant URL: {iot.ha_url}")
            
            if not iot.is_configured:
                print("   ℹ️  Para configurar IoT, adicione 'iot.ha_token' ao ai_config.yaml")
            
            print("✅ IOTManager funcionando")
        except Exception as e:
            print(f"❌ Erro no IOTManager: {e}")
            return False
        
        # 5. Testar inicialização completa
        print("\n🚀 Testando inicialização completa...")
        try:
            orchestrator.initialize_stark_system()
            
            final_health = orchestrator.get_system_health()
            final_info = orchestrator.get_system_info()
            
            print(f"   📈 Componentes registrados: {final_info['registered_components']}")
            print(f"   💚 Sistema saudável: {final_info['system_healthy']}")
            print(f"   🎯 Sistema pronto: {final_info['is_ready']}")
            
            print("✅ Inicialização completa funcionando")
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
        
        print("\n🎉 Todos os testes passaram! Core system integrado com sucesso.")
        return True
        
    except Exception as e:
        logger.error(f"Erro geral no teste: {e}", exc_info=True)
        return False

def test_imports():
    """Testa todos os imports do core"""
    print("🔍 Testando imports individuais...")
    
    modules_to_test = [
        "src.core.orchestrator",
        "src.core.security.security_manager", 
        "src.core.iot.iot_manager",
        "src.core.management.fallback_system",
        "src.core.management.shutdown_manager",
    ]
    
    successful_imports = 0
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"   ✅ {module}")
            successful_imports += 1
        except Exception as e:
            print(f"   ❌ {module}: {e}")
    
    print(f"\n📊 Imports bem-sucedidos: {successful_imports}/{len(modules_to_test)}")
    return successful_imports == len(modules_to_test)

def main():
    """Função principal para executar todos os testes"""
    print("JARVIS Core System Testing Suite")
    print("=" * 50)
    
    # Teste 1: Imports
    imports_ok = test_imports()
    
    # Teste 2: Integração
    if imports_ok:
        integration_ok = test_core_integration()
        
        if integration_ok:
            print("\n🎊 Todos os testes foram bem-sucedidos!")
            print("O sistema core está funcionando corretamente.")
        else:
            print("\n⚠️ Alguns testes de integração falharam.")
            sys.exit(1)
    else:
        print("\n❌ Falhas nos imports. Verifique as dependências.")
        sys.exit(1)

if __name__ == "__main__":
    main()