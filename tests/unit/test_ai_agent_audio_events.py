import asyncio
import time
from unittest.mock import Mock

import pytest

from src.core.intelligence.ai_agent import AIAgent
from src.core.infrastructure.async_event_bus import event_bus, EventType


def test_ai_agent_handles_audio_ready_and_transcription(monkeypatch):
    agent = AIAgent()

    # Replace process_command with a fast coroutine to capture calls
    called = []

    async def fake_process_command(cmd):
        called.append(cmd)
        return "OK"

    agent.process_command = fake_process_command

    # Connect to the global event bus
    agent.connect_event_bus(event_bus)

    # Publish AUDIO_READY
    event_bus.publish(EventType.AUDIO_READY, {"available": True, "mock": False})

    # Give the bus a moment to dispatch
    time.sleep(0.1)

    assert agent.audio_ready is True

    # Publish transcription
    event_bus.publish(EventType.AUDIO_TRANSCRIPTION, {"text": "Olá Jarvis"})

    # Wait for async handler to schedule process_command
    time.sleep(0.2)

    assert called and called[0] == "Olá Jarvis"
