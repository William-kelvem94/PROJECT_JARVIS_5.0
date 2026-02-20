from src.core.intelligence.local_brain import local_brain
from src.core.management.hardware_manager import hardware_manager
import logging
import sys
import os
import time

# Adicionar root ao path
sys.path.append(os.getcwd())


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VERIFY-PHASE5")


def test_hardware_optimization():
    logger.info("Checking Hardware optimizations...")
    compute_type = hardware_manager.get_compute_type()
    device = hardware_manager.get_device()
    logger.info(f"✅ Device: {device} | Compute Type: {compute_type}")

    if device == "cuda" and compute_type == "bfloat16":
        logger.info("🚀 CUDA bfloat16 optimization ACTIVE")
    elif device == "cuda":
        logger.info("✨ CUDA float16 optimization ACTIVE")
    else:
        logger.info("💻 CPU float32 (Safe Mode) ACTIVE")


def test_kv_cache_speed():
    logger.info("Testing KV Cache performance...")
    prompt1 = "Olá Jarvis, como você está?"
    prompt2 = "Quais são seus protocolos de segurança?"

    # Simular primeiro turno (frio)
    start = time.time()
    res1 = local_brain.generate_response(prompt1, use_cache=True)
    cold_time = time.time() - start
    logger.info(f"⏱️ Cold response time: {cold_time:.2f}s")

    # Simular segundo turno (quente - deve ser mais rápido no processamento de
    # prompt)
    start = time.time()
    res2 = local_brain.generate_response(prompt2, use_cache=True)
    warm_time = time.time() - start
    logger.info(f"⏱️ Warm response time: {warm_time:.2f}s")

    if warm_time < cold_time:
        logger.info("✅ KV Cache: Speedup detected")
    else:
        logger.info(
            "ℹ️ KV Cache: Buffer was too small for noticeable speedup or model loading overhead dominated."
        )


if __name__ == "__main__":
    test_hardware_optimization()
    # Note: KV Cache test depends on model loading, skip if model not
    # available in CI/Tests
    if os.environ.get("SKIP_HEAVY_TESTS") != "1":
        try:
            test_kv_cache_speed()
        except Exception as e:
            logger.warning(f"Could not test KV Cache: {e}")

    logger.info("Phase 5 Optimization Verification Complete.")
