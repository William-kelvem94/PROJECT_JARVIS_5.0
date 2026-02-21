from src.evolution import evolution_manager
import sys
import asyncio
import os
import signal
import logging
from pathlib import Path

# Ensure project src is on path when running as script
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    # Ensure SafeExecutor will run pytest before applying fixes
    os.environ["JARVIS_SAFE_RUN_TESTS"] = "1"
    # Force minimal Torch threads to reduce CPU/memory pressure
    os.environ["JARVIS_FORCE_TORCH_THREADS"] = "1"

    # Start evolution layer with conservative settings
    await evolution_manager.start(
        observer_interval=600,  # 10 minutes (conservative)
        auto_heal=True,
        initial_scan=True,
        enable_module_generation=False,  # keep module gen off to save resources
        enable_voice_commands=False,  # disable voice to reduce memory pressure
    )

    logger.info("Evolution layer started (safe mode). Press Ctrl+C to stop.")

    # Keep process alive until interrupted
    stop = asyncio.Event()

    def _sigint(_signo, _frame):
        stop.set()

    signal.signal(signal.SIGINT, _sigint)
    signal.signal(signal.SIGTERM, _sigint)

    await stop.wait()

    logger.info("Stopping evolution layer...")
    await evolution_manager.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
