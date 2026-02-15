# -*- coding: utf-8 -*-
"""
CORE INTEGRATION TEST - Teste Real de Integração do Sistema
JARVIS 5.0 - Validação completa dos módulos core e sua integração
"""

import sys
import os
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Adicionar o diretório raiz ao Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CoreIntegrationTester:
    """Testador completo da integração dos módulos core"""

    def __init__(self):
        self.results: Dict[str, Any] = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {}
        }

    def run_all_tests(self) -> bool:
        """Executa todos os testes de integração"""
        print("🚀 JARVIS Core Integration Test Suite")
        print("=" * 60)

        tests = [
            ('imports', self.test_imports),
            ('orchestrator', self.test_orchestrator),
            ('security', self.test_security_manager),
            ('iot', self.test_iot_manager),
            ('initialization', self.test_full_initialization),
            ('health_checks', self.test_health_checks)
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            print(f"\n🔍 Executando teste: {test_name}")
            try:
                result = test_func()
                self.results['tests'][test_name] = result

                if result['success']:
                    print(f"   ✅ {test_name}: PASSOU")
                    passed += 1
                else:
                    print(f"   ❌ {test_name}: FALHOU - {result.get('error', 'Erro desconhecido')}")

            except Exception as e:
                logger.error(f"Erro no teste {test_name}: {e}", exc_info=True)
                self.results['tests'][test_name] = {
                    'success': False,
                    'error': str(e),
                    'details': {}
                }
                print(f"   ❌ {test_name}: ERRO - {e}")

        # Resumo final
        self.results['summary'] = {
            'total_tests': total,
            'passed_tests': passed,
            'failed_tests': total - passed,
            'success_rate': passed / total if total > 0 else 0
        }

        print(f"\n📊 RESULTADO FINAL: {passed}/{total} testes passaram ({self.results['summary']['success_rate']:.1%})")

        return passed == total

    def test_imports(self) -> Dict[str, Any]:
        """Testa todos os imports críticos do core"""
        result = {'success': True, 'details': {}}

        critical_modules = [
            "src.core.management.orchestrator",
            "src.core.security.security_manager",
            "src.core.iot.iot_manager",
            "src.core.management.fallback_system",
            "src.core.management.shutdown_manager",
            "src.core.intelligence.context_sanitizer",
            "src.core.audio.voice_filter",
            "src.core.vision.vision_system",
            "src.core.audio.voice_controller",
            "src.core.intelligence.ai_agent",
            "src.core.actions.action_controller"
        ]

        successful_imports = 0

        for module in critical_modules:
            try:
                __import__(module)
                result['details'][module] = {'status': 'success'}
                successful_imports += 1
            except Exception as e:
                result['details'][module] = {'status': 'failed', 'error': str(e)}
                result['success'] = False

        result['summary'] = f"{successful_imports}/{len(critical_modules)} imports bem-sucedidos"
        return result

    def test_orchestrator(self) -> Dict[str, Any]:
        """Testa o StarkOrchestrator"""
        result = {'success': True, 'details': {}}

        try:
            from src.core.management.orchestrator import StarkOrchestrator

            # Mock JarvisCore
            class MockJarvisCore:
                def __init__(self):
                    self.shutdown_manager = None
                    self.ai_agent = None
                    self.window_manager = None

            mock_jarvis = MockJarvisCore()
            orchestrator = StarkOrchestrator(mock_jarvis)

            # Testar métodos básicos
            health = orchestrator.get_system_health()
            info = orchestrator.get_system_info()

            result['details'] = {
                'health_check': health,
                'system_info': info,
                'components_count': info.get('components_count', 0),
                'is_ready': info.get('is_ready', False)
            }

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        return result

    def test_security_manager(self) -> Dict[str, Any]:
        """Testa o SecurityManager"""
        result = {'success': True, 'details': {}}

        try:
            from src.core.security.security_manager import SecurityManager

            security = SecurityManager()

            # Testar validações básicas
            test_paths = [
                "/home/user/documents",
                "C:\\Users\\user\\Documents",
                "/tmp/test"
            ]

            test_urls = [
                "https://google.com/search",
                "https://github.com/user/repo",
                "http://localhost:5000"
            ]

            path_results = {}
            url_results = {}

            for path in test_paths:
                try:
                    path_results[path] = security.validate_path_access(path)
                except Exception as e:
                    path_results[path] = f"Error: {e}"

            for url in test_urls:
                try:
                    url_results[url] = security.validate_web_request(url)
                except Exception as e:
                    url_results[url] = f"Error: {e}"

            result['details'] = {
                'path_validations': path_results,
                'url_validations': url_results
            }

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        return result

    def test_iot_manager(self) -> Dict[str, Any]:
        """Testa o IOTManager"""
        result = {'success': True, 'details': {}}

        try:
            from src.core.iot.iot_manager import IOTManager

            iot = IOTManager()

            result['details'] = {
                'is_configured': iot.is_configured,
                'ha_url': getattr(iot, 'ha_url', None),
                'ha_token_configured': bool(getattr(iot, 'ha_token', None))
            }

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        return result

    def test_full_initialization(self) -> Dict[str, Any]:
        """Testa a inicialização completa do sistema"""
        result = {'success': True, 'details': {}}

        try:
            from src.core.management.orchestrator import StarkOrchestrator

            # Mock JarvisCore
            class MockJarvisCore:
                def __init__(self):
                    self.shutdown_manager = None
                    self.ai_agent = None
                    self.window_manager = None

            mock_jarvis = MockJarvisCore()
            orchestrator = StarkOrchestrator(mock_jarvis)

            # Executar inicialização
            orchestrator.initialize_stark_system()

            # Verificar estado final
            final_health = orchestrator.get_system_health()
            final_info = orchestrator.get_system_info()

            result['details'] = {
                'initialization_completed': True,
                'final_health': final_health,
                'final_info': final_info,
                'system_healthy': final_info.get('system_healthy', False),
                'is_ready': final_info.get('is_ready', False)
            }

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        return result

    def test_health_checks(self) -> Dict[str, Any]:
        """Testa os health checks de todos os módulos"""
        result = {'success': True, 'details': {}}

        try:
            from src.core.management.orchestrator import StarkOrchestrator

            # Mock JarvisCore
            class MockJarvisCore:
                def __init__(self):
                    self.shutdown_manager = None
                    self.ai_agent = None
                    self.window_manager = None

            mock_jarvis = MockJarvisCore()
            orchestrator = StarkOrchestrator(mock_jarvis)

            # Testar health check de módulos específicos
            modules_to_check = ['vision', 'audio', 'intelligence', 'actions', 'security', 'iot', 'infrastructure']

            health_results = {}
            for module in modules_to_check:
                try:
                    status = orchestrator.get_module_status(module)
                    health_results[module] = status
                except Exception as e:
                    health_results[module] = f"Error: {e}"
                    result['success'] = False

            result['details'] = {
                'module_health': health_results,
                'offline_modules': [m for m, s in health_results.items() if s == 'OFFLINE']
            }

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        return result

    def save_results(self, output_file: str) -> bool:
        """Salva os resultados em arquivo JSON"""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)

            print(f"💾 Resultados salvos em: {output_path}")
            return True

        except Exception as e:
            print(f"❌ Erro ao salvar resultados: {e}")
            return False

    def print_summary(self):
        """Imprime resumo dos resultados"""
        summary = self.results.get('summary', {})

        print("\n📊 RESUMO DOS TESTES:")
        print("-" * 40)
        print(f"   Total de testes: {summary.get('total_tests', 0)}")
        print(f"   Testes aprovados: {summary.get('passed_tests', 0)}")
        print(f"   Testes reprovados: {summary.get('failed_tests', 0)}")
        print(".1%")

        if summary.get('failed_tests', 0) > 0:
            print("\n❌ TESTES QUE FALHARAM:")
            for test_name, test_result in self.results.get('tests', {}).items():
                if not test_result.get('success', False):
                    error = test_result.get('error', 'Erro desconhecido')
                    print(f"   • {test_name}: {error}")

def run_integration_test(output_file: Optional[str] = None, verbose: bool = False) -> bool:
    """
    Executa teste completo de integração do core

    Args:
        output_file: Arquivo para salvar resultados (opcional)
        verbose: Modo verboso

    Returns:
        True se todos os testes passaram
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    tester = CoreIntegrationTester()
    success = tester.run_all_tests()

    tester.print_summary()

    if output_file:
        tester.save_results(output_file)

    return success

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Core Integration Test - JARVIS 5.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

# Executar todos os testes
python tests/test_core_integration.py

# Salvar resultados em arquivo
python tests/test_core_integration.py --output results.json

# Modo verboso
python tests/test_core_integration.py --verbose

# Executar apenas testes específicos
python tests/test_core_integration.py --tests imports orchestrator
        """
    )

    parser.add_argument('--output', '-o', help='Arquivo para salvar resultados dos testes')
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verboso com debug')
    parser.add_argument('--tests', nargs='*', help='Executar apenas testes específicos')

    args = parser.parse_args()

    success = run_integration_test(args.output, args.verbose)

    if success:
        print("\n🎉 Todos os testes de integração passaram!")
        sys.exit(0)
    else:
        print("\n❌ Alguns testes falharam. Verifique os logs acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()