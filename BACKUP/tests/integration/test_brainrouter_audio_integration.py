import asyncio
from unittest.mock import patch

from src.core.infrastructure.async_event_bus import get_event_bus, EventType
from src.core.intelligence.decision_engine import get_decision_engine
from src.core.intelligence.brain_router import brain_router
from src.core.audio.enhanced_audio import EnhancedAudioSystem


async def _run_integration_flow():
    bus = get_event_bus()
    await bus.start()

    # Capture speak calls from EnhancedAudioSystem
    spoken = []

    audio = EnhancedAudioSystem(event_bus=bus)
    audio.on_speak = lambda text: spoken.append(text)

    # Connect brain_router to the bus (so it can observe AUDIO_READY)
    brain_router.connect_event_bus(bus)

    # Publish that audio subsystem is ready
    bus.publish(EventType.AUDIO_READY, {"available": True, "mock": True})

    # Allow subscriptions to settle
    await asyncio.sleep(0.05)

    engine = get_decision_engine()

    async def fake_call(*args, **kwargs):
        return "Resposta de integração: Olá, Jarvis"

    with patch.object(engine, "_call_llm", new=fake_call):
        res = await engine.decide("Teste integração", context={})
        # allow dispatch
        await asyncio.sleep(0.2)

    await bus.stop()
    return res, spoken


def test_brainrouter_to_audio_integration():
    res, spoken = asyncio.run(_run_integration_flow())
    assert res["final_answer"] == "Resposta de integração: Olá, Jarvis"
    assert spoken, "EnhancedAudioSystem did not receive AUDIO_SPEAK"
    assert spoken[-1] == "Resposta de integração: Olá, Jarvis"
