import os
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from .autonomous_brain import AutonomousBrain
from .api import start_telemetry_server
from .kb_loader import load_kb
from .perception import perception_manager
from .perception.voice_engine import add_callback as add_voice_callback, start as start_voice_engine
from .routes import router as main_router
from .system_bridge import router as system_bridge_router
from .voice_websocket import router as voice_router
from .dependencies import get_sentinel_parser, get_sentinel
from .psyche.device_awareness import DeviceAwareness
from .psyche.dream_cycle import DreamCycle
from .psyche.gap_analyzer import GapAnalyzer
from .multi_agent_analysis import start_multi_agent_analysis, stop_multi_agent_analysis, get_orchestrator
from .auto_restart import enable_auto_restart, disable_auto_restart

# Store background tasks to prevent garbage collection
_background_tasks: set[asyncio.Task] = set()

# --- Omega Protocol Singletons ---
# Psyche/Brain
device_awareness = DeviceAwareness()
dream_cycle = DreamCycle(
    logs_path="logs/interactions.log",
    obsidian_kb_path=os.environ.get(
        "JARVIS_KB_PATH",
        os.path.join(os.environ.get("JARVIS_VAULT_ROOT", r"D:\DOCUMENTOS\GitHub\Will-obsidian"), "JARVIS")
    ),
    holodeck_queue_path="data/holodeck_queue.txt"
)
gap_analyzer = GapAnalyzer()
autonomous_brain = AutonomousBrain()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing JARVIS 5.0 Omega Core...")

    try:
        add_voice_callback(perception_manager._on_voice_event)
    except Exception as e:
        logger.warning(f"Falha ao registrar callback de voz: {e}")

    try:
        start_voice_engine()
    except Exception as e:
        logger.warning(f"Falha ao iniciar o Voice Engine: {e}")

    # Start Telemetry Dashboard
    try:
        start_telemetry_server()
        logger.info("Telemetry Dashboard started successfully on port 8001")
    except Exception as e:
        logger.warning(f"Não foi possível iniciar o Telemetry Dashboard: {e}")

    # 1. Start Autonomous Thinking Loop
    autonomous_brain.start_background_thinking()

    # 2. Initialize Psyche Awareness
    initial_state = device_awareness.get_system_state()
    logger.info(f"Initial Psyche State: {initial_state}")

    # 3. Schedule KB sync, Dream Cycle, Gap Analysis and Resource Governor
    _background_tasks.add(asyncio.create_task(load_kb()))
    _background_tasks.add(asyncio.create_task(run_psyche_cycles()))
    _background_tasks.add(asyncio.create_task(device_awareness.resource_governor_loop(callback_fn=handle_governor_action)))

    # 4. Start Multi-Agent Analysis System
    try:
        start_multi_agent_analysis()
        logger.info("Multi-Agent Analysis System started successfully")
        
        # Register Auto-Fix Agents
        from .autofix_agents import register_autofix_agents
        register_autofix_agents()
        logger.info("Auto-Fix Agents registered successfully")
    except Exception as e:
        logger.warning(f"Failed to start Multi-Agent Analysis: {e}")

    # 5. Enable Auto-Restart on Improvements (if enabled via env var)
    if os.getenv("JARVIS_AUTO_RESTART", "0") == "1":
        try:
            enable_auto_restart()
            logger.info("Auto-Restart System enabled")
        except Exception as e:
            logger.warning(f"Failed to enable Auto-Restart: {e}")

    yield

    logger.info("Shutting down JARVIS 5.0 Omega Core...")
    autonomous_brain.stop()
    
    # Stop Multi-Agent Analysis
    try:
        stop_multi_agent_analysis()
    except Exception as e:
        logger.warning(f"Error stopping Multi-Agent Analysis: {e}")
    
    # Disable Auto-Restart
    try:
        disable_auto_restart()
    except Exception as e:
        logger.warning(f"Error disabling Auto-Restart: {e}")

    # Cancel background tasks
    for task in _background_tasks:
        task.cancel()
    _background_tasks.clear()

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

def _get_cors_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ORIGINS")
    if raw_origins:
        return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000").strip()
    origins = [frontend_url] if frontend_url else []
    if "http://localhost:3000" not in origins:
        origins.append("http://localhost:3000")
    if "http://127.0.0.1:3000" not in origins:
        origins.append("http://127.0.0.1:3000")
    return origins


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router)
app.include_router(system_bridge_router)
app.include_router(voice_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
