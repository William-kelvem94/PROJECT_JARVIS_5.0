import sys
import os
import asyncio
import logging
from unittest.mock import MagicMock
sys.path.append(os.getcwd())
from src.core.infrastructure.async_event_bus import AsyncEventBus, Event, EventType

# Mock dependencies
sys.modules['src.core.audio.voice_controller'] = MagicMock()
sys.modules['src.core.vision.vision_enhancer'] = MagicMock()
sys.modules['src.core.vision.screen_capture'] = MagicMock()
sys.modules['src.core.actions.action_controller'] = MagicMock()
sys.modules['src.core.intelligence.brain_router'] = MagicMock()
sys.modules['src.core.management.performance_optimizer'] = MagicMock()

# Configure Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("VerifyLoop")

async def test_loop():
    print("[START] Starting Audio Loop Verification...")
    
    # 1. Initialize Bus
    bus = AsyncEventBus()
    await bus.start()
    
    # 2. Initialize Agent
    try:
        from src.core.intelligence.ai_agent import AIAgent
        agent = AIAgent(provider="mock")
        agent.connect_event_bus(bus)
        
        # Mock process_command to avoid actual processing
        agent.process_command = MagicMock()
        agent.process_command.return_value = "OK"
        
        print("[OK] AI Agent Initialized")
    except ImportError as e:
        print(f"[FAIL] Failed to import AI Agent: {e}")
        return

    # 3. Simulate Object Payload (from Audio Proxy)
    from types import SimpleNamespace
    payload_obj = SimpleNamespace(text="Hello Jarvis", language="en")
    event_obj = Event(EventType.AUDIO_TRANSCRIPTION, payload_obj)
    
    print("[INFO] Publishing Object Event...")
    await bus.publish(event_obj)
    await asyncio.sleep(0.1)
    
    # Verify
    if agent.process_command.called:
        print("[PASS] Success: Agent processed Object payload!")
        args = agent.process_command.call_args[0]
        print(f"   Received: {args[0]}")
    else:
        print("[FAIL] Failure: Agent did not process Object payload.")
        
    # Reset
    agent.process_command.reset_mock()
    
    # 4. Simulate Dict Payload (Legacy/Direct)
    payload_dict = {"text": "Hello Dictionary", "language": "en"}
    event_dict = Event(EventType.AUDIO_TRANSCRIPTION, payload_dict)
    
    print("[INFO] Publishing Dict Event...")
    await bus.publish(event_dict)
    await asyncio.sleep(0.1)
    
    # Verify
    if agent.process_command.called:
        print("[PASS] Success: Agent processed Dict payload!")
        args = agent.process_command.call_args[0]
        print(f"   Received: {args[0]}")
    else:
        print("[FAIL] Failure: Agent did not process Dict payload.")

    await bus.stop()

if __name__ == "__main__":
    asyncio.run(test_loop())
