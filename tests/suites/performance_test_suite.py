"""
PerformanceTestSuite - Suite de testes de performance para JARVIS 5.0
Inclui testes de carga, stress, endurance e benchmark.
"""

import asyncio
import json
import logging
import time
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import psutil
import statistics

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Métrica de performance individual."""

    name: str
    value: float
    unit: str
    timestamp: float
    metadata: Dict[str, Any] = None


@dataclass
class PerformanceTestResult:
    """Resultado de um teste de performance."""

    test_name: str
    duration: float
    metrics: List[PerformanceMetric]
    success: bool
    error_message: Optional[str] = None
    throughput: Optional[float] = None  # ops/sec
    latency_p50: Optional[float] = None  # ms
    latency_p95: Optional[float] = None  # ms
    latency_p99: Optional[float] = None  # ms
    memory_peak: Optional[float] = None  # MB
    cpu_peak: Optional[float] = None  # %


class PerformanceTestSuite:
    """
    Suite abrangente de testes de performance para JARVIS 5.0.
    """

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("tests/results/performance")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.process = psutil.Process()

    def run_load_test(
        self,
        name: str,
        operation: Callable,
        concurrent_users: int = 10,
        duration_seconds: int = 60,
    ) -> PerformanceTestResult:
        """
        Executa teste de carga com múltiplos usuários concorrentes.

        Args:
            name: Nome do teste
            operation: Função a ser testada (deve ser async ou sync)
            concurrent_users: Número de usuários simultâneos
            duration_seconds: Duração do teste

        Returns:
            Resultado do teste
        """
        start_time = time.time()
        metrics = []
        latencies = []
        errors = []

        # Monitora recursos
        memory_samples = []
        cpu_samples = []

        def monitor_resources():
            while time.time() - start_time < duration_seconds:
                memory_samples.append(self.process.memory_info().rss / (1024 * 1024))
                cpu_samples.append(self.process.cpu_percent())
                time.sleep(1)

        # Inicia monitoramento
        monitor_thread = threading.Thread(target=monitor_resources, daemon=True)
        monitor_thread.start()

        async def run_operation(user_id: int):
            """Executa operação para um usuário."""
            operations_completed = 0
            user_start = time.time()  # noqa: F841

            while time.time() - start_time < duration_seconds:
                op_start = time.time()
                try:
                    if asyncio.iscoroutinefunction(operation):
                        await operation()
                    else:
                        operation()
                    operations_completed += 1
                    latencies.append((time.time() - op_start) * 1000)  # ms
                except Exception as e:
                    errors.append(str(e))

            return operations_completed

        async def run_load_test():
            """Executa o teste de carga."""
            tasks = [run_operation(i) for i in range(concurrent_users)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_operations = sum(r for r in results if isinstance(r, int))
            return total_operations

        # Executa teste
        try:
            total_operations = asyncio.run(run_load_test())
            success = len(errors) == 0
            error_message = f"{len(errors)} errors occurred" if errors else None

            # Calcula métricas
            total_duration = time.time() - start_time
            throughput = total_operations / total_duration if total_duration > 0 else 0

            latency_p50 = statistics.median(latencies) if latencies else None
            latency_p95 = (
                statistics.quantiles(latencies, n=20)[18]
                if len(latencies) >= 20
                else None
            )
            latency_p99 = (
                statistics.quantiles(latencies, n=100)[98]
                if len(latencies) >= 100
                else None
            )

            memory_peak = max(memory_samples) if memory_samples else None
            cpu_peak = max(cpu_samples) if cpu_samples else None

            # Coleta métricas detalhadas
            metrics.extend(
                [
                    PerformanceMetric(
                        "total_operations", total_operations, "ops", start_time
                    ),
                    PerformanceMetric("throughput", throughput, "ops/sec", start_time),
                    PerformanceMetric(
                        "concurrent_users", concurrent_users, "users", start_time
                    ),
                    PerformanceMetric(
                        "test_duration", total_duration, "seconds", start_time
                    ),
                    PerformanceMetric(
                        "errors_count", len(errors), "errors", start_time
                    ),
                ]
            )

            if latency_p50:
                metrics.append(
                    PerformanceMetric("latency_p50", latency_p50, "ms", start_time)
                )
            if latency_p95:
                metrics.append(
                    PerformanceMetric("latency_p95", latency_p95, "ms", start_time)
                )
            if latency_p99:
                metrics.append(
                    PerformanceMetric("latency_p99", latency_p99, "ms", start_time)
                )
            if memory_peak:
                metrics.append(
                    PerformanceMetric("memory_peak", memory_peak, "MB", start_time)
                )
            if cpu_peak:
                metrics.append(PerformanceMetric("cpu_peak", cpu_peak, "%", start_time))

        except Exception as e:
            success = False
            error_message = str(e)
            total_operations = 0
            throughput = 0
            latency_p50 = latency_p95 = latency_p99 = None
            memory_peak = cpu_peak = None

        result = PerformanceTestResult(
            test_name=name,
            duration=time.time() - start_time,
            metrics=metrics,
            success=success,
            error_message=error_message,
            throughput=throughput,
            latency_p50=latency_p50,
            latency_p95=latency_p95,
            latency_p99=latency_p99,
            memory_peak=memory_peak,
            cpu_peak=cpu_peak,
        )

        self._save_result(result)
        return result

    def run_stress_test(
        self,
        name: str,
        operation: Callable,
        max_concurrent: int = 100,
        increment: int = 10,
    ) -> List[PerformanceTestResult]:
        """
        Executa teste de stress aumentando gradualmente a carga.

        Args:
            name: Nome do teste
            operation: Função a ser testada
            max_concurrent: Máximo de usuários concorrentes
            increment: Incremento de usuários por etapa

        Returns:
            Lista de resultados por nível de carga
        """
        results = []

        for concurrent_users in range(increment, max_concurrent + 1, increment):
            logger.info(f"Running stress test with {concurrent_users} concurrent users")

            result = self.run_load_test(
                f"{name}_stress_{concurrent_users}",
                operation,
                concurrent_users,
                duration_seconds=30,  # Teste mais curto para stress
            )

            results.append(result)

            # Para se o sistema falhar
            if not result.success or (result.cpu_peak and result.cpu_peak > 95):
                logger.warning(f"System stressed at {concurrent_users} users")
                break

            # Pequena pausa entre testes
            time.sleep(5)

        return results

    def run_endurance_test(
        self,
        name: str,
        operation: Callable,
        duration_hours: int = 1,
        concurrent_users: int = 5,
    ) -> PerformanceTestResult:
        """
        Executa teste de endurance por período prolongado.

        Args:
            name: Nome do teste
            operation: Função a ser testada
            duration_hours: Duração em horas
            concurrent_users: Usuários concorrentes

        Returns:
            Resultado do teste
        """
        duration_seconds = duration_hours * 3600

        logger.info(f"Starting endurance test for {duration_hours} hours")

        result = self.run_load_test(
            f"{name}_endurance", operation, concurrent_users, duration_seconds
        )

        return result

    def run_memory_leak_test(
        self, name: str, operation: Callable, iterations: int = 1000
    ) -> PerformanceTestResult:
        """
        Testa vazamentos de memória executando operação múltiplas vezes.

        Args:
            name: Nome do teste
            operation: Função a ser testada
            iterations: Número de iterações

        Returns:
            Resultado do teste
        """
        start_time = time.time()
        metrics = []
        memory_samples = []

        try:
            for i in range(iterations):
                if asyncio.iscoroutinefunction(operation):
                    asyncio.run(operation())
                else:
                    operation()

                # Coleta amostra de memória a cada 10 iterações
                if i % 10 == 0:
                    memory_samples.append(
                        self.process.memory_info().rss / (1024 * 1024)
                    )

                # Progress report
                if i % 100 == 0:
                    logger.info(
                        f"Memory leak test: {i}/{iterations} iterations completed"
                    )

            success = True
            error_message = None

            # Análise de vazamento
            if len(memory_samples) >= 2:
                initial_memory = memory_samples[0]
                final_memory = memory_samples[-1]
                memory_growth = final_memory - initial_memory
                growth_rate = memory_growth / len(memory_samples)

                metrics.extend(
                    [
                        PerformanceMetric(
                            "initial_memory", initial_memory, "MB", start_time
                        ),
                        PerformanceMetric(
                            "final_memory", final_memory, "MB", start_time
                        ),
                        PerformanceMetric(
                            "memory_growth", memory_growth, "MB", start_time
                        ),
                        PerformanceMetric(
                            "memory_growth_rate",
                            growth_rate,
                            "MB/iteration",
                            start_time,
                        ),
                    ]
                )

                # Flag se crescimento excessivo
                if growth_rate > 0.1:  # Mais de 0.1MB por iteração
                    success = False
                    error_message = f"Potential memory leak detected: {growth_rate:.3f} MB/iteration"

        except Exception as e:
            success = False
            error_message = str(e)

        result = PerformanceTestResult(
            test_name=name,
            duration=time.time() - start_time,
            metrics=metrics,
            success=success,
            error_message=error_message,
        )

        self._save_result(result)
        return result

    def benchmark_operation(
        self, name: str, operation: Callable, iterations: int = 100
    ) -> PerformanceTestResult:
        """
        Benchmark de uma operação específica.

        Args:
            name: Nome do benchmark
            operation: Função a ser testada
            iterations: Número de iterações

        Returns:
            Resultado do benchmark
        """
        start_time = time.time()
        latencies = []
        memory_samples = []
        cpu_samples = []

        try:
            for i in range(iterations):
                op_start = time.time()

                if asyncio.iscoroutinefunction(operation):
                    asyncio.run(operation())
                else:
                    operation()

                latencies.append((time.time() - op_start) * 1000)

                # Coleta métricas de sistema
                memory_samples.append(self.process.memory_info().rss / (1024 * 1024))
                cpu_samples.append(psutil.cpu_percent())

            # Calcula estatísticas
            avg_latency = statistics.mean(latencies)
            median_latency = statistics.median(latencies)
            p95_latency = (
                statistics.quantiles(latencies, n=20)[18]
                if len(latencies) >= 20
                else None
            )
            p99_latency = (
                statistics.quantiles(latencies, n=100)[98]
                if len(latencies) >= 100
                else None
            )

            throughput = iterations / (time.time() - start_time)
            avg_memory = statistics.mean(memory_samples)
            avg_cpu = statistics.mean(cpu_samples)

            metrics = [
                PerformanceMetric("iterations", iterations, "ops", start_time),
                PerformanceMetric("avg_latency", avg_latency, "ms", start_time),
                PerformanceMetric("median_latency", median_latency, "ms", start_time),
                PerformanceMetric("throughput", throughput, "ops/sec", start_time),
                PerformanceMetric("avg_memory", avg_memory, "MB", start_time),
                PerformanceMetric("avg_cpu", avg_cpu, "%", start_time),
            ]

            if p95_latency:
                metrics.append(
                    PerformanceMetric("p95_latency", p95_latency, "ms", start_time)
                )
            if p99_latency:
                metrics.append(
                    PerformanceMetric("p99_latency", p99_latency, "ms", start_time)
                )

            success = True
            error_message = None

        except Exception as e:
            success = False
            error_message = str(e)
            metrics = []

        result = PerformanceTestResult(
            test_name=name,
            duration=time.time() - start_time,
            metrics=metrics,
            success=success,
            error_message=error_message,
            throughput=throughput if "throughput" in locals() else None,
            latency_p50=median_latency if "median_latency" in locals() else None,
            latency_p95=p95_latency if "p95_latency" in locals() else None,
            latency_p99=p99_latency if "p99_latency" in locals() else None,
            memory_peak=max(memory_samples) if memory_samples else None,
            cpu_peak=max(cpu_samples) if cpu_samples else None,
        )

        self._save_result(result)
        return result

    def _save_result(self, result: PerformanceTestResult):
        """Salva resultado em arquivo JSON."""
        result_file = (
            self.output_dir / f"perf_{result.test_name}_{int(time.time())}.json"
        )

        result_data = {
            "test_name": result.test_name,
            "timestamp": time.time(),
            "duration": result.duration,
            "success": result.success,
            "error_message": result.error_message,
            "throughput": result.throughput,
            "latency_p50": result.latency_p50,
            "latency_p95": result.latency_p95,
            "latency_p99": result.latency_p99,
            "memory_peak": result.memory_peak,
            "cpu_peak": result.cpu_peak,
            "metrics": [
                {
                    "name": m.name,
                    "value": m.value,
                    "unit": m.unit,
                    "timestamp": m.timestamp,
                    "metadata": m.metadata,
                }
                for m in result.metrics
            ],
        }

        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=2, default=str)

        logger.info(f"Performance test result saved to {result_file}")

    def generate_report(self, results: List[PerformanceTestResult]) -> Dict[str, Any]:
        """
        Gera relatório consolidado dos testes de performance.

        Args:
            results: Lista de resultados

        Returns:
            Relatório consolidado
        """
        report = {
            "summary": {
                "total_tests": len(results),
                "successful_tests": len([r for r in results if r.success]),
                "failed_tests": len([r for r in results if not r.success]),
                "avg_duration": (
                    statistics.mean([r.duration for r in results]) if results else 0
                ),
                "total_duration": sum(r.duration for r in results),
            },
            "performance_metrics": {},
            "recommendations": [],
        }

        # Agrega métricas
        all_throughput = [r.throughput for r in results if r.throughput]
        all_latencies_p95 = [r.latency_p95 for r in results if r.latency_p95]
        all_memory_peaks = [r.memory_peak for r in results if r.memory_peak]
        all_cpu_peaks = [r.cpu_peak for r in results if r.cpu_peak]

        if all_throughput:
            report["performance_metrics"]["throughput"] = {
                "avg": statistics.mean(all_throughput),
                "max": max(all_throughput),
                "min": min(all_throughput),
            }

        if all_latencies_p95:
            report["performance_metrics"]["latency_p95"] = {
                "avg": statistics.mean(all_latencies_p95),
                "max": max(all_latencies_p95),
            }

        if all_memory_peaks:
            report["performance_metrics"]["memory_peak"] = {
                "avg": statistics.mean(all_memory_peaks),
                "max": max(all_memory_peaks),
            }

        if all_cpu_peaks:
            report["performance_metrics"]["cpu_peak"] = {
                "avg": statistics.mean(all_cpu_peaks),
                "max": max(all_cpu_peaks),
            }

        # Gera recomendações
        if all_latencies_p95 and statistics.mean(all_latencies_p95) > 1000:
            report["recommendations"].append(
                "High latency detected. Consider optimizing slow operations."
            )

        if all_cpu_peaks and statistics.mean(all_cpu_peaks) > 80:
            report["recommendations"].append(
                "High CPU usage detected. Consider load balancing or optimization."
            )

        if all_memory_peaks and statistics.mean(all_memory_peaks) > 1000:
            report["recommendations"].append(
                "High memory usage detected. Check for memory leaks."
            )

        # Salva relatório
        report_file = self.output_dir / f"performance_report_{int(time.time())}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Performance report saved to {report_file}")
        return report


# Funções de exemplo para teste
async def sample_async_operation():
    """Operação assíncrona de exemplo."""
    await asyncio.sleep(0.01)  # Simula I/O
    return sum(range(100))  # Simula processamento


def sample_sync_operation():
    """Operação síncrona de exemplo."""
    time.sleep(0.01)  # Simula I/O
    return sum(range(100))  # Simula processamento


if __name__ == "__main__":
    # Exemplo de uso
    suite = PerformanceTestSuite()

    # Benchmark simples
    benchmark_result = suite.benchmark_operation(
        "sample_operation_benchmark", sample_sync_operation, iterations=100
    )

    print(f"Benchmark completed: {benchmark_result.success}")
    print(f"Average latency: {benchmark_result.latency_p50:.2f}ms")
    print(f"Throughput: {benchmark_result.throughput:.1f} ops/sec")

    # Teste de carga
    load_result = suite.run_load_test(
        "sample_load_test",
        sample_async_operation,
        concurrent_users=5,
        duration_seconds=10,
    )

    print(f"Load test completed: {load_result.success}")
    print(f"Total operations: {load_result.throughput * load_result.duration:.0f}")
    print(f"Peak memory: {load_result.memory_peak:.1f}MB")
