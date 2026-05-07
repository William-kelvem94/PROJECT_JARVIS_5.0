import os
import asyncio
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger

from .autonomous_brain import AutonomousBrain
from .routes import router as main_router
from .system_bridge import router as system_bridge_router
from .voice_websocket import router as voice_router
from .security.sentinel_core import SentinelSecurity
from .security.sentinel_parser import SentinelParser
from .psyche.device_awareness import DeviceAwareness
from .psyche.dream_cycle import DreamCycle
from .psyche.gap_analyzer import GapAnalyzer

# --- Omega Protocol Singletons ---
# Security
sentinel_parser = SentinelParser()
sentinel = SentinelSecurity()

# Psyche/Brain
device_awareness = DeviceAwareness()
dream_cycle = DreamCycle(
    logs_path="logs/interactions.log",
    obsidian_kb_path=os.environ.get(
        "JARVIS_KB_PATH",
        os.path.join(os.path.dirname(__file__), "..", "..", "data", "kb_local", "JARVIS", "KnowledgeBase")
    ),
    holodeck_queue_path="data/holodeck_queue.txt"
)
gap_analyzer = GapAnalyzer()
autonomous_brain = AutonomousBrain()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing JARVIS 5.0 Omega Core...")

    # 1. Start Autonomous Thinking Loop
    autonomous_brain.start_background_thinking()

    # 2. Initialize Psyche Awareness
    initial_state = device_awareness.get_system_state()
    logger.info(f"Initial Psyche State: {initial_state}")

    # 3. Schedule Dream Cycle, Gap Analysis and Resource Governor
    asyncio.create_task(run_psyche_cycles())
    asyncio.create_task(device_awareness.resource_governor_loop(callback_fn=handle_governor_action))

    yield

    logger.info("Shutting down JARVIS 5.0 Omega Core...")
    autonomous_brain.stop()

async def run_psyche_cycles():
    """Background loop for subconscious processing."""
    while True:
        try:
            # Dream Cycle: Evolution of Knowledge Base
            dream_cycle.process_dreams()

            # Gap Analysis: Detecting missing info (triggered by brain/logs)
            logger.debug("Psyche heartbeat: DreamCycle and GapAnalyzer active.")

            await asyncio.sleep(3600) # Run every hour
        except Exception as e:
            logger.error(f"Error in psyche background cycles: {e}")
            await asyncio.sleep(60)

async def handle_governor_action(action: str, state: str):
    """Callback for the Resource Governor to adapt JARVIS's operational mode."""
    logger.info(f"Adapting system behavior: {action} due to {state} state.")
    # Here we would integrate with the SmartRouter or ModelManager
    # Example:
    # if action == "MIGRATE_TO_LIGHTWEIGHT_API":
    #     smart_router.set_mode("eco")
    # elif action == "MAX_LOCAL_PERFORMANCE":
    #     smart_router.set_mode("performance")
    pass

app = FastAPI(lifespan=lifespan)

app.include_router(main_router)
app.include_router(system_bridge_router)
app.include_router(voice_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
