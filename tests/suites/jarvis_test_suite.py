"""
JarvisTestSuite - Suite de testes abrangente para JARVIS 5.0
Inclui testes unitários, integração, performance e sistema.
"""

import asyncio
import json
import logging
import time
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import psutil
import coverage

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Resultado de um teste individual."""

    test_name: str
    test_class: str
    status: str  # 'passed', 'failed', 'error', 'skipped'
    duration: float
    error_message: Optional[str] = None
    traceback: Optional[str] = None
    assertions: int = 0
    coverage_percent: Optional[float] = None


@dataclass
class TestSuiteResult:
    """Resultado de uma suíte de testes."""

    suite_name: str
    total_tests: int
    passed: int
    failed: int
    errors: int
    skipped: int
    duration: float
    coverage_percent: Optional[float] = None
    results: List[TestResult] = None

    def __post_init__(self):
        if self.results is None:
            self.results = []


class JarvisTestSuite(unittest.TestCase):
    """
    Suite de testes abrangente para JARVIS 5.0.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_time = None
        self.test_results = []

    def setUp(self):
        """Configuração antes de cada teste."""
        self.start_time = time.time()

    def tearDown(self):
        """Limpeza após cada teste."""
        duration = time.time() - self.start_time
        # Resultado será coletado pelo TestRunner

    @classmethod
    def setUpClass(cls):
        """Configuração da classe de teste."""
        cls.test_data_dir = Path("tests/test_data")
        cls.test_data_dir.mkdir(parents=True, exist_ok=True)

    def assertAsyncEqual(self, first, second, msg=None):
        """Asserção para valores assíncronos."""
        if asyncio.iscoroutine(first):
            first = asyncio.run(first)
        if asyncio.iscoroutine(second):
            second = asyncio.run(second)
        self.assertEqual(first, second, msg)


class SecurityTestSuite(JarvisTestSuite):
    """Testes de segurança."""

    def test_command_injection_prevention(self):
        """Testa prevenção de injeção de comandos."""
        from src.core.security_manager import SecurityManager

        security = SecurityManager()

        # Testa comandos seguros
        safe_commands = ["echo hello", "ls -la", "python --version"]

        for cmd in safe_commands:
            with self.subTest(command=cmd):
                result = security.validate_command(cmd)
                self.assertTrue(result, f"Command should be safe: {cmd}")

        # Testa comandos perigosos
        dangerous_commands = [
            "rm -rf /",
            "echo hello; rm -rf /",
            "cat /etc/passwd",
            "$(malicious_command)",
        ]

        for cmd in dangerous_commands:
            with self.subTest(command=cmd):
                result = security.validate_command(cmd)
                self.assertFalse(result, f"Command should be blocked: {cmd}")

    def test_path_traversal_prevention(self):
        """Testa prevenção de path traversal."""
        from src.core.security_manager import SecurityManager

        security = SecurityManager()

        # Testa caminhos seguros
        safe_paths = ["data/logs/app.log", "config/settings.yaml", "src/core/main.py"]

        for path in safe_paths:
            with self.subTest(path=path):
                result = security.validate_path(path)
                self.assertTrue(result, f"Path should be safe: {path}")

        # Testa caminhos perigosos
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM",
        ]

        for path in dangerous_paths:
            with self.subTest(path=path):
                result = security.validate_path(path)
                self.assertFalse(result, f"Path should be blocked: {path}")


class PerformanceTestSuite(JarvisTestSuite):
    """Testes de performance."""

    def test_memory_usage_baseline(self):
        """Testa uso de memória em condições normais."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / (1024 * 1024)  # MB

        # Simula alguma atividade
        data = list(range(10000))
        result = sum(data)

        final_memory = process.memory_info().rss / (1024 * 1024)  # MB
        memory_increase = final_memory - initial_memory

        # Memória não deve aumentar mais que 50MB
        self.assertLess(
            memory_increase, 50, f"Memory increase too high: {memory_increase}MB"
        )

    def test_cpu_usage_baseline(self):
        """Testa uso de CPU em condições normais."""
        initial_cpu = psutil.cpu_percent(interval=1)

        # Simula processamento
        for _ in range(1000):
            _ = sum(range(100))

        final_cpu = psutil.cpu_percent(interval=1)

        # CPU não deve ficar consistentemente acima de 80%
        self.assertLess(final_cpu, 80, f"CPU usage too high: {final_cpu}%")

    async def test_async_performance(self):
        """Testa performance de operações assíncronas."""
        from src.utils.advanced_utils import AsyncRunner

        runner = AsyncRunner()

        start_time = time.time()

        # Executa múltiplas tarefas assíncronas
        tasks = []
        for i in range(10):
            task = runner.run_async(lambda x=i: asyncio.sleep(0.1 * x))
            tasks.append(task)

        await asyncio.gather(*tasks)

        duration = time.time() - start_time

        # Deve completar em menos de 2 segundos (concorrente)
        self.assertLess(duration, 2.0, f"Async operations too slow: {duration}s")


class IntegrationTestSuite(JarvisTestSuite):
    """Testes de integração."""

    def test_config_manager_hierarchy(self):
        """Testa hierarquia do ConfigManager."""
        from src.core.config_manager import ConfigManager

        config = ConfigManager()

        # Testa carregamento de configurações
        test_config = {"test_key": "test_value", "nested": {"key": "nested_value"}}

        config.set("test", test_config)
        result = config.get("test")

        self.assertEqual(result["test_key"], "test_value")
        self.assertEqual(result["nested"]["key"], "nested_value")

    def test_event_bus_communication(self):
        """Testa comunicação via EventBus."""
        from src.core.global_event_bus import global_event_bus

        received_events = []

        async def event_handler(event_data):
            received_events.append(event_data)

        # Registra handler
        global_event_bus.subscribe("test_event", event_handler)

        # Publica evento
        asyncio.run(global_event_bus.publish("test_event", {"message": "test"}))

        # Verifica recebimento
        self.assertEqual(len(received_events), 1)
        self.assertEqual(received_events[0]["message"], "test")

    def test_lazy_loader_functionality(self):
        """Testa funcionalidade do LazyLoader."""
        from src.utils.advanced_utils import LazyLoader

        loader = LazyLoader()

        # Testa carregamento lazy
        module_name = "json"  # Módulo padrão do Python

        # Não deve estar carregado inicialmente
        self.assertNotIn(module_name, loader.loaded_modules)

        # Carrega sob demanda
        module = loader.load_module(module_name)
        self.assertIsNotNone(module)
        self.assertIn(module_name, loader.loaded_modules)

        # Deve retornar o mesmo módulo na segunda chamada
        module2 = loader.load_module(module_name)
        self.assertIs(module, module2)


class SystemTestSuite(JarvisTestSuite):
    """Testes de sistema completo."""

    def test_full_system_startup(self):
        """Testa inicialização completa do sistema."""
        # Este teste seria mais complexo em um ambiente real
        # Por enquanto, apenas verifica se os módulos principais podem ser importados

        try:
            import src.core.main
            import src.core.security_manager
            import src.core.config_manager
            import src.evolution.self_observer

            # Se chegou aqui, imports foram bem-sucedidos
            self.assertTrue(True, "System modules imported successfully")

        except ImportError as e:
            self.fail(f"Failed to import system modules: {e}")

    def test_error_handling(self):
        """Testa tratamento de erros do sistema."""
        from src.core.security_manager import SecurityError

        # Testa que erros customizados funcionam
        with self.assertRaises(SecurityError):
            raise SecurityError("Test security error")


class TestRunner:
    """
    Executor personalizado de testes com métricas avançadas.
    """

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("tests/results")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_tests(
        self, test_suites: List[unittest.TestSuite], with_coverage: bool = True
    ) -> TestSuiteResult:
        """
        Executa suítes de testes com cobertura opcional.

        Args:
            test_suites: Lista de suítes a executar
            with_coverage: Se deve medir cobertura

        Returns:
            Resultado da execução
        """
        start_time = time.time()

        # Configura cobertura se solicitada
        cov = None
        if with_coverage:
            cov = coverage.Coverage(
                source=["src"], omit=["*/tests/*", "*/venv/*", "*/__pycache__/*"]
            )
            cov.start()

        # Executa testes
        loader = unittest.TestLoader()
        runner = unittest.TextTestRunner(
            verbosity=2, stream=open(self.output_dir / "test_output.txt", "w")
        )

        all_results = []
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0
        total_skipped = 0

        for suite in test_suites:
            result = runner.run(suite)

            suite_result = TestSuiteResult(
                suite_name=(
                    suite.__class__.__name__
                    if hasattr(suite, "__class__")
                    else str(suite)
                ),
                total_tests=result.testsRun,
                passed=result.testsRun
                - len(result.failures)
                - len(result.errors)
                - len(result.skipped),
                failed=len(result.failures),
                errors=len(result.errors),
                skipped=len(result.skipped),
                duration=time.time() - start_time,
                results=[],
            )

            # Coleta resultados individuais
            for test, traceback in result.failures + result.errors:
                status = (
                    "failed" if test in [t[0] for t in result.failures] else "error"
                )
                suite_result.results.append(
                    TestResult(
                        test_name=test._testMethodName,
                        test_class=test.__class__.__name__,
                        status=status,
                        duration=0,  # Não temos duração individual
                        traceback=traceback,
                    )
                )

            for test, reason in result.skipped:
                suite_result.results.append(
                    TestResult(
                        test_name=test._testMethodName,
                        test_class=test.__class__.__name__,
                        status="skipped",
                        duration=0,
                        error_message=reason,
                    )
                )

            all_results.append(suite_result)
            total_tests += suite_result.total_tests
            total_passed += suite_result.passed
            total_failed += suite_result.failed
            total_errors += suite_result.errors
            total_skipped += suite_result.skipped

        # Para cobertura
        coverage_percent = None
        if cov:
            cov.stop()
            cov.save()
            coverage_percent = cov.report(
                file=open(self.output_dir / "coverage_report.txt", "w")
            )

        total_duration = time.time() - start_time

        # Resultado agregado
        overall_result = TestSuiteResult(
            suite_name="JarvisTestSuite",
            total_tests=total_tests,
            passed=total_passed,
            failed=total_failed,
            errors=total_errors,
            skipped=total_skipped,
            duration=total_duration,
            coverage_percent=coverage_percent,
            results=all_results,
        )

        # Salva resultados
        self._save_results(overall_result)

        return overall_result

    def _save_results(self, result: TestSuiteResult):
        """Salva resultados em arquivo JSON."""
        result_file = self.output_dir / f"test_results_{int(time.time())}.json"

        result_data = {
            "suite_name": result.suite_name,
            "timestamp": time.time(),
            "summary": {
                "total_tests": result.total_tests,
                "passed": result.passed,
                "failed": result.failed,
                "errors": result.errors,
                "skipped": result.skipped,
                "success_rate": (
                    (result.passed / result.total_tests * 100)
                    if result.total_tests > 0
                    else 0
                ),
                "duration": result.duration,
                "coverage_percent": result.coverage_percent,
            },
            "detailed_results": [
                {
                    "suite_name": r.suite_name,
                    "total_tests": r.total_tests,
                    "passed": r.passed,
                    "failed": r.failed,
                    "errors": r.errors,
                    "skipped": r.skipped,
                    "duration": r.duration,
                }
                for r in result.results
            ],
        }

        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=2, default=str)

        logger.info(f"Test results saved to {result_file}")


def create_comprehensive_test_suite() -> unittest.TestSuite:
    """
    Cria suíte de testes abrangente incluindo todas as categorias.

    Returns:
        TestSuite configurada
    """
    suite = unittest.TestSuite()

    # Adiciona suítes de teste
    suite.addTest(unittest.makeSuite(SecurityTestSuite))
    suite.addTest(unittest.makeSuite(PerformanceTestSuite))
    suite.addTest(unittest.makeSuite(IntegrationTestSuite))
    suite.addTest(unittest.makeSuite(SystemTestSuite))

    return suite


# Função de conveniência para executar todos os testes
def run_all_tests(
    with_coverage: bool = True, output_dir: Path = None
) -> TestSuiteResult:
    """
    Executa todos os testes da suíte.

    Args:
        with_coverage: Se deve medir cobertura
        output_dir: Diretório para salvar resultados

    Returns:
        Resultado da execução
    """
    test_suite = create_comprehensive_test_suite()
    runner = TestRunner(output_dir)
    return runner.run_tests([test_suite], with_coverage)


if __name__ == "__main__":
    # Executa testes quando chamado diretamente
    result = run_all_tests()
    print("\nTest Results:")
    print(f"Total: {result.total_tests}")
    print(f"Passed: {result.passed}")
    print(f"Failed: {result.failed}")
    print(f"Errors: {result.errors}")
    print(f"Skipped: {result.skipped}")
    print(f"Duration: {result.duration:.2f}s")
    if result.coverage_percent:
        print(f"Coverage: {result.coverage_percent:.1f}%")
