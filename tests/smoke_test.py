import os
import sys
import asyncio
import logging

# Setup environment
os.environ["JARVIS_HEADLESS"] = "1"
os.environ["JARVIS_TEST_MODE"] = "1"  # Disable background threads
sys.path.insert(0, os.getcwd())

from src.core.infrastructure.bootstrapper import SystemBootstrapper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SMOKE_TEST")

async def run_smoke_test():
    logger.info("🔥 Starting Smoke Test...")

    try:
        # Initialize bootstrapper (no app instance)
        bootstrapper = SystemBootstrapper(app_instance=None)

        # Run bootstrap
        instances = await bootstrapper.bootstrap()

        # Verify critical components
        assert "event_bus" in instances, "Event Bus missing"
        assert "ai_agent" in instances, "AI Agent missing"
        assert "system_manifest" in instances, "System Manifest missing"

        # Verify mocked components are NOT present or are skipped
        assert "window_manager" not in instances, "Window Manager should be skipped in headless"

        logger.info("✅ Smoke Test PASSED! System booted successfully.")
        return True

    except Exception as e:
        logger.error(f"❌ Smoke Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    success = asyncio.run(run_smoke_test())
    sys.exit(0 if success else 1)
