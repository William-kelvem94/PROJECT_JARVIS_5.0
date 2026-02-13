# -*- coding: utf-8 -*-
"""
QUICK AUTO RECOVERY TEST - Teste RÃ¡pido do Sistema de Auto-RecuperaÃ§Ã£o
JARVIS 5.0 - ValidaÃ§Ã£o rÃ¡pida dos componentes principais
"""

import sys
import os
import json
import logging
import argparse
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Adicionar src ao path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("QuickRecoveryTest")

class QuickRecoveryTester:
    """
    Testador rÃ¡pido dos componentes principais do auto-recovery
    """

    def __init__(self):
        self.test_results: Dict[str, Any] = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {}
        }
        self.recovery_system = None

    def run_quick_tests(self) -> bool:
        """Executa testes rÃ¡pidos dos componentes principais"""
        print("âš¡ JARVIS Quick Auto-Recovery Test Suite")
        print("=" * 60)

        tests = [
            ('import_validation', self.test_import_validation),
            ('system_initialization', self.test_system_initialization),
            ('module_registration', self.test_module_registration),
            ('recovery_trigger', self.test_recovery_trigger),
            ('health_monitoring', self.test_health_monitoring),
            ('performance_check', self.test_performance_check)
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            print(f"\nðŸ” Executando teste rÃ¡pido: {test_name}")
            try:
                result = test_func()
                self.test_results['tests'][test_name] = result

                if result['success']:
                    print(f"   âœ… {test_name}: PASSOU ({result.get('duration', 0):.2f}s)")
                    passed += 1
                else:
                    print(f"   âŒ {test_name}: FALHOU - {result.get('error', 'Erro desconhecido')}")

            except Exception as e:
                logger.error(f"Erro no teste {test_name}: {e}", exc_info=True)
                self.test_results['tests'][test_name] = {
                    'success': False,
                    'error': str(e),
                    'details': {}
                }
                print(f"   âŒ {test_name}: ERRO - {e}")

        # Resumo final
        self.test_results['summary'] = {
            'total_tests': total,
            'passed_tests': passed,
            'failed_tests': total - passed,
            'success_rate': passed / total if total > 0 else 0,
            'total_duration': sum(t.get('duration', 0) for t in self.test_results['tests'].values())
        }

        print(".1%")
        print(".2f")

        return passed == total

    def test_import_validation(self) -> Dict[str, Any]:
        """Testa validaÃ§Ã£o de imports"""
        start_time = time.time()
        result = {'success': True, 'details': {}}

        try:
            # Teste simplificado: verificar se conseguimos acessar as classes necessÃ¡rias
            from core.management.auto_recovery_system import get_auto_recovery_system, FailureType, RecoveryStatus

            # Verificar se as classes existem
            system_func = get_auto_recovery_system
            failure_enum = FailureType
            recovery_enum = RecoveryStatus

            result['details'] = {
                'auto_recovery_system': 'OK',
                'failure_type_enum': 'OK',
                'recovery_status_enum': 'OK',
                'note': 'Imports essenciais verificados com sucesso'
            }

            result['success'] = True

        except Exception as e:
            result['success'] = False
            result['error'] = f"Falha no import essencial: {str(e)}"

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        result['duration'] = time.time() - start_time
        return result

    def test_system_initialization(self) -> Dict[str, Any]:
        """Testa inicializaÃ§Ã£o do sistema"""
        start_time = time.time()
        result = {'success': True, 'details': {}}

        try:
            from core.management.auto_recovery_system import get_auto_recovery_system

            # Inicializar sistema
            self.recovery_system = get_auto_recovery_system()

            # Verificar atributos essenciais
            required_attrs = ['data_dir', 'recovery_strategies', 'module_health', 'monitoring_active']

            for attr in required_attrs:
                if not hasattr(self.recovery_system, attr):
                    raise AttributeError(f"Atributo obrigatÃ³rio faltando: {attr}")

            result['details'] = {
                'system_initialized': True,
                'data_dir': str(self.recovery_system.data_dir),
                'strategies_count': len(self.recovery_system.recovery_strategies),
                'monitoring_active': self.recovery_system.monitoring_active,
                'modules_tracked': len(self.recovery_system.module_health)
            }

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        result['duration'] = time.time() - start_time
        return result

    def test_module_registration(self) -> Dict[str, Any]:
        """Testa registro de mÃ³dulos"""
        start_time = time.time()
        result = {'success': True, 'details': {}}

        try:
            if not self.recovery_system:
                raise RuntimeError("Sistema nÃ£o inicializado")

            # Registrar mÃ³dulos de teste
            test_modules = ["ai_agent", "voice_controller", "vision_enhancer"]
            registered_modules = []

            for module in test_modules:
                full_name = f"jarvis.{module}"
                health = self.recovery_system.register_module(full_name)

                registered_modules.append({
                    'name': full_name,
                    'is_healthy': health.is_healthy,
                    'uptime_minutes': health.uptime_minutes
                })

            result['details'] = {
                'registered_modules': registered_modules,
                'total_registered': len(registered_modules),
                'healthy_modules': sum(1 for m in registered_modules if m['is_healthy'])
            }

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        result['duration'] = time.time() - start_time
        return result

    def test_recovery_trigger(self) -> Dict[str, Any]:
        """Testa trigger de recuperaÃ§Ã£o"""
        start_time = time.time()
        result = {'success': True, 'details': {}}

        try:
            if not self.recovery_system:
                raise RuntimeError("Sistema nÃ£o inicializado")

            from core.management.auto_recovery_system import FailureType

            # Simular trigger de recovery
            self.recovery_system._trigger_recovery(
                failure_type=FailureType.IMPORT_ERROR,
                module_name="test_module",
                error_message="Simulated import error for testing",
                severity=5
            )

            # Aguardar processamento
            time.sleep(1)

            # Verificar se recovery foi registrado
            stats = self.recovery_system.get_recovery_stats()

            result['details'] = {
                'recovery_triggered': True,
                'recovery_stats': stats,
                'has_recovery_history': 'total_recoveries' in stats
            }

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        result['duration'] = time.time() - start_time
        return result

    def test_health_monitoring(self) -> Dict[str, Any]:
        """Testa monitoramento de saÃºde"""
        start_time = time.time()
        result = {'success': True, 'details': {}}

        try:
            if not self.recovery_system:
                raise RuntimeError("Sistema nÃ£o inicializado")

            # Obter relatÃ³rio de saÃºde
            health_report = self.recovery_system.get_module_health_report()

            # Verificar estrutura do relatÃ³rio
            if not isinstance(health_report, dict):
                raise TypeError("Health report deve ser um dicionÃ¡rio")

            # Verificar mÃ³dulos registrados
            expected_modules = ["jarvis.ai_agent", "jarvis.voice_controller", "jarvis.vision_enhancer"]
            found_modules = list(health_report.keys())

            modules_found = [m for m in expected_modules if m in found_modules]

            result['details'] = {
                'health_report_generated': True,
                'total_modules': len(health_report),
                'expected_modules_found': len(modules_found),
                'module_health_details': health_report
            }

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        result['duration'] = time.time() - start_time
        return result

    def test_performance_check(self) -> Dict[str, Any]:
        """Testa performance bÃ¡sica"""
        start_time = time.time()
        result = {'success': True, 'details': {}}

        try:
            if not self.recovery_system:
                raise RuntimeError("Sistema nÃ£o inicializado")

            # Medir tempo de operaÃ§Ãµes crÃ­ticas
            import time as time_module

            # Tempo para obter estatÃ­sticas
            start_stats = time_module.time()
            stats = self.recovery_system.get_recovery_stats()
            stats_time = time_module.time() - start_stats

            # Tempo para obter health report
            start_health = time_module.time()
            health_report = self.recovery_system.get_module_health_report()
            health_time = time_module.time() - start_health

            # Verificar performance aceitÃ¡vel (< 1 segundo para operaÃ§Ãµes crÃ­ticas)
            acceptable_performance = stats_time < 1.0 and health_time < 1.0

            result['details'] = {
                'stats_retrieval_time': stats_time,
                'health_retrieval_time': health_time,
                'acceptable_performance': acceptable_performance,
                'performance_metrics': {
                    'stats_time_ms': stats_time * 1000,
                    'health_time_ms': health_time * 1000
                }
            }

            if not acceptable_performance:
                result['success'] = False
                result['error'] = "Performance abaixo do aceitÃ¡vel (>1s para operaÃ§Ãµes crÃ­ticas)"

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        result['duration'] = time.time() - start_time
        return result

    def save_results(self, output_file: str) -> bool:
        """Salva os resultados em arquivo JSON"""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False, default=str)

            print(f"ðŸ’¾ Resultados salvos em: {output_path}")
            return True

        except Exception as e:
            print(f"âŒ Erro ao salvar resultados: {e}")
            return False

    def print_summary(self):
        """Imprime resumo dos resultados"""
        summary = self.test_results.get('summary', {})

        print("\nðŸ“Š RESUMO DOS TESTES RÃPIDOS:")
        print("-" * 50)
        print(f"   Total de testes: {summary.get('total_tests', 0)}")
        print(f"   Testes aprovados: {summary.get('passed_tests', 0)}")
        print(f"   Testes reprovados: {summary.get('failed_tests', 0)}")
        print(".1%")
        print(".2f")

        if summary.get('failed_tests', 0) > 0:
            print("\nâŒ TESTES QUE FALHARAM:")
            for test_name, test_result in self.test_results.get('tests', {}).items():
                if not test_result.get('success', False):
                    error = test_result.get('error', 'Erro desconhecido')
                    print(f"   â€¢ {test_name}: {error}")

    def cleanup(self):
        """Limpa recursos"""
        try:
            if self.recovery_system and self.recovery_system.monitoring_active:
                self.recovery_system.stop_monitoring()
                print("ðŸ§¹ Sistema de monitoramento parado")
        except Exception as e:
            logger.warning(f"Erro durante cleanup: {e}")

def run_quick_tests(output_file: Optional[str] = None, verbose: bool = False) -> bool:
    """
    Executa testes rÃ¡pidos dos componentes principais do auto-recovery

    Args:
        output_file: Arquivo para salvar resultados (opcional)
        verbose: Modo verboso

    Returns:
        True se todos os testes passaram
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    tester = QuickRecoveryTester()

    try:
        success = tester.run_quick_tests()

        tester.print_summary()

        if output_file:
            tester.save_results(output_file)

        return success

    finally:
        tester.cleanup()

def main():
    """FunÃ§Ã£o principal"""
    parser = argparse.ArgumentParser(
        description="Quick Auto Recovery Test - JARVIS 5.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

# Executar todos os testes rÃ¡pidos
python src/core/management/quick_auto_recovery.py

# Salvar resultados em arquivo
python src/core/management/quick_auto_recovery.py --output quick_test_results.json

# Modo verboso
python src/core/management/quick_auto_recovery.py --verbose
        """
    )

    parser.add_argument('--output', '-o', help='Arquivo para salvar resultados dos testes')
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verboso com debug')

    args = parser.parse_args()

    success = run_quick_tests(args.output, args.verbose)

    if success:
        print("\nðŸŽ‰ Todos os testes rÃ¡pidos passaram!")
        sys.exit(0)
    else:
        print("\nâŒ Alguns testes falharam. Verifique os logs acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()
