import asyncio
import time

from types import SimpleNamespace

from src.core.config.system_manifest import system_manifest
from src.core.audio.enhanced_audio import get_audio_system
from src.core.infrastructure.async_event_bus import get_event_bus, EventType


def test_get_audio_system_returns_proxy_when_multiproc_enabled(monkeypatch):
    # Ensure multiprocess mode for audio
    orig = system_manifest.audio.multiprocessing_enabled
    system_manifest.audio.multiprocessing_enabled = True

    # Use in-process event bus (no child process required for this unit test)
    event_bus = get_event_bus()

    audio = get_audio_system(event_bus=event_bus)

    # Should be proxy instance exposing start_listening and on_transcription
    assert hasattr(audio, "start_listening")
    assert callable(audio.start_listening)
    assert hasattr(audio, "on_transcription")

    # Simulate a transcription event on the bus and ensure proxy forwards it
    received = []

    def cb(obj):
        received.append(obj.text)

    audio.on_transcription = cb

    # Publish a transcription event (simulate child)
    event_bus.publish(EventType.AUDIO_TRANSCRIPTION, {"text": "hello world"})

    # Allow async event loop in tests (subscribe handlers run asynchronously)
    time.sleep(0.1)

    assert received and received[0] == "hello world"

    # restore
    system_manifest.audio.multiprocessing_enabled = orig
