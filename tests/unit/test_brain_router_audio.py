import time

from src.core.intelligence.brain_router import brain_router
from src.core.infrastructure.async_event_bus import event_bus, EventType


def test_brain_router_receives_audio_ready_event():
    # Connect brain_router to the event bus
    brain_router.connect_event_bus(event_bus)

    # Ensure initial state
    brain_router.audio_ready = False

    # Publish AUDIO_READY
    event_bus.publish(EventType.AUDIO_READY, {"available": True, "mock": False})

    time.sleep(0.05)

    assert brain_router.audio_ready is True
