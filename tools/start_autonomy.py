
import sys
import os
import asyncio
import logging
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from src.core.intelligence.brain_router import BrainRouter
from src.core.audio.voice_controller import VoiceController
from src.core.intelligence.ai_agent import AIAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Autonomy")

async def conscious_loop():
    logger.info("🧠 Initializing Consciousness...")
    
    # 1. Connect Brain
    brain = BrainRouter()
    if not brain.check_connectivity():
        logger.warning("⚠️ No internet. Autonomy degraded to LOCAL.")
    
    # 2. Connect Voice
    voice = VoiceController()
    voice.speak("Consciousness Initialized. I am listening.")
    
    # 3. Connect Agent
    agent = AIAgent() # Standalone Agent
    if agent.safe_mode:
        logger.error("❌ Agent is in SAFE MODE.")
        return
    
    logger.info("✨ Autonomy Loop Active.")
    while True:
        # Simulate 'Thinking' or 'Processing' if idle
        # In full version this is event-driven.
        await asyncio.sleep(5)
        logger.debug("Thinking...")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(conscious_loop())
