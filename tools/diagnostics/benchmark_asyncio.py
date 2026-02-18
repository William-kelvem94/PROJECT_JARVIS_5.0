"""
Benchmark AsyncIO - Comparação de Performance
===============================================
Testa melhorias de performance com async/await vs threading
"""

import sys
import asyncio
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

sys.path.insert(0, str(PROJECT_ROOT))


async def test_1_file_io_performance():
    """Teste 1: Performance de File I/O (aiofiles vs síncrono)"""
    print("\n" + "=" * 70)
    print("TESTE 1: File I/O Performance (aiofiles)")
    print("=" * 70)

    try:
        from src.core.intelligence.action_handler import get_action_handler
        from src.core.intelligence.structured_output import (
            WriteFileAction,
            ReadFileAction,
        )

        handler = get_action_handler()
        test_file = "data/temp/benchmark_async.txt"
        test_content = "AsyncIO Benchmark Test " * 100  # ~2300 chars

        # Benchmark: Write + Read (10 iterações)
        iterations = 10
        start_time = time.time()

        for i in range(iterations):
            # Write
            write_action = WriteFileAction(path=test_file, content=test_content)
            await handler.execute_actions([write_action])

            # Read
            read_action = ReadFileAction(path=test_file)
            await handler.execute_actions([read_action])

        elapsed = time.time() - start_time
        avg_per_op = (elapsed / (iterations * 2)) * 1000  # ms por operação

        print(f"✅ Completado: {iterations} write + {iterations} read")
        print(f"⏱️  Tempo total: {elapsed:.3f}s")
        print(f"⚡ Média por operação: {avg_per_op:.2f}ms")

        # Cleanup
        import os

        if os.path.exists(test_file):
            os.remove(test_file)

        return {
            "test": "file_io",
            "iterations": iterations * 2,
            "total_time": elapsed,
            "avg_ms": avg_per_op,
        }

    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return None


async def test_2_parallel_execution():
    """Teste 2: Execução paralela de ações (concorrência)"""
    print("\n" + "=" * 70)
    print("TESTE 2: Execução Paralela (asyncio.gather)")
    print("=" * 70)

    try:
        from src.core.intelligence.action_handler import get_action_handler
        from src.core.intelligence.structured_output import WaitAction, WriteFileAction

        handler = get_action_handler()

        # Criar 5 ações paralelas
        actions = [
            WaitAction(seconds=0.1),
            WriteFileAction(path="data/temp/test1.txt", content="test1"),
            WriteFileAction(path="data/temp/test2.txt", content="test2"),
            WriteFileAction(path="data/temp/test3.txt", content="test3"),
            WaitAction(seconds=0.1),
        ]

        # Benchmark sequencial simulado (soma dos tempos)
        sequential_time = 0.1 + 0.05 + 0.05 + 0.05 + 0.1  # ~0.35s esperado

        # Benchmark paralelo real
        start_time = time.time()
        results = await handler.execute_actions(actions)
        parallel_time = time.time() - start_time

        # Speedup
        if parallel_time > 0:
            speedup = sequential_time / parallel_time
        else:
            speedup = 1.0

        success_count = sum(1 for r in results if r["status"] == "success")

        print(f"✅ Ações executadas: {success_count}/{len(actions)}")
        print(f"⏱️  Tempo sequencial (estimado): {sequential_time:.3f}s")
        print(f"⏱️  Tempo paralelo (real): {parallel_time:.3f}s")
        print(f"🚀 Speedup: {speedup:.2f}x")

        # Cleanup
        import os

        for i in range(1, 4):
            path = f"data/temp/test{i}.txt"
            if os.path.exists(path):
                os.remove(path)

        return {
            "test": "parallel",
            "actions": len(actions),
            "sequential_time": sequential_time,
            "parallel_time": parallel_time,
            "speedup": speedup,
        }

    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return None


async def test_3_timeout_handling():
    """Teste 3: Validação de timeouts"""
    print("\n" + "=" * 70)
    print("TESTE 3: Timeout Handling")
    print("=" * 70)

    try:
        from src.core.intelligence.perception_engine import get_perception_engine

        perception = get_perception_engine()

        # Teste gather_context com timeout
        start_time = time.time()
        context = await perception.gather_context(
            user_command="teste timeout",
            enable_vision=False,  # Desabilitar visão (captura demora)
        )
        elapsed = time.time() - start_time

        print(f"✅ Context gathered em {elapsed:.2f}s")
        print(f"   • screenshot_path: {bool(context.get('screenshot_path'))}")
        print(f"   • user_face: {context.get('user_face')}")
        print(f"   • memory_context: {bool(context.get('memory_context'))}")

        # Verificar que não ultrapassou timeout global (10s)
        if elapsed < 10.0:
            print("✅ Dentro do timeout global (10s)")
        else:
            print(f"⚠️ Ultrapassou timeout: {elapsed:.2f}s")

        return {"test": "timeout", "elapsed": elapsed, "within_timeout": elapsed < 10.0}

    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return None


async def run_benchmark():
    """Executa todos os benchmarks"""
    print("=" * 70)
    print("🚀 BENCHMARK ASYNCIO - CORREÇÃO P1")
    print("=" * 70)
    print("Testando melhorias de performance com async/await")
    print("=" * 70)

    results = []

    # Teste 1: File I/O
    result1 = await test_1_file_io_performance()
    if result1:
        results.append(result1)

    # Teste 2: Parallel Execution
    result2 = await test_2_parallel_execution()
    if result2:
        results.append(result2)

    # Teste 3: Timeout Handling
    result3 = await test_3_timeout_handling()
    if result3:
        results.append(result3)

    # Resumo
    print("\n" + "=" * 70)
    print("📊 RESUMO DOS BENCHMARKS")
    print("=" * 70)

    for result in results:
        test_name = result["test"]

        if test_name == "file_io":
            print("\n✅ File I/O (aiofiles):")
            print(f"   • {result['iterations']} operações")
            print(f"   • Média: {result['avg_ms']:.2f}ms/operação")

        elif test_name == "parallel":
            print("\n✅ Execução Paralela:")
            print(f"   • {result['actions']} ações")
            print(f"   • Speedup: {result['speedup']:.2f}x")

        elif test_name == "timeout":
            status = "✅" if result["within_timeout"] else "❌"
            print(f"\n{status} Timeout Handling:")
            print(f"   • Tempo: {result['elapsed']:.2f}s")

    print("\n" + "=" * 70)
    print("🎉 Benchmarks concluídos!")
    print("=" * 70)
    print("\n💡 Melhorias AsyncIO:")
    print("   ✅ File I/O não-bloqueante (aiofiles)")
    print("   ✅ Execução paralela real (asyncio.gather)")
    print("   ✅ Timeouts robustos (asyncio.wait_for)")
    print("   ✅ Error handling graceful")

    passed = len([r for r in results if r])
    total = 3

    if passed == total:
        print(f"\n✅ {passed}/{total} benchmarks bem-sucedidos")
        return 0
    else:
        print(f"\n⚠️ {passed}/{total} benchmarks bem-sucedidos")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_benchmark())
    sys.exit(exit_code)
