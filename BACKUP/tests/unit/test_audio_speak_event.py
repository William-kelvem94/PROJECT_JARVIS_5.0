import asyncio
from unittest.mock import patch, MagicMock

from src.core.infrastructure.async_event_bus import get_event_bus, EventType
from src.core.intelligence.decision_engine import DecisionEngine, get_decision_engine


async def _run_decide_and_capture():
    captured = []

    async def _handler(event):
        captured.append(event.data.get("text"))

    bus = get_event_bus()
    # Start the event bus dispatcher for the test
    await bus.start()

    sub_id = bus.subscribe([EventType.AUDIO_SPEAK], _handler)

    # Sanity: manual publish should be delivered
    bus.publish(EventType.AUDIO_SPEAK, {"text": "manual test"})
    await asyncio.sleep(0.5)
    assert "manual test" in captured

    engine = get_decision_engine()

    # Patch _call_llm to avoid external calls and return a known response
    async def fake_call(*args, **kwargs):
        return "Resposta de teste para fala"

    with patch.object(engine, "_call_llm", new=fake_call):
        # Also wrap bus.publish to assert it's called for AUDIO_SPEAK
        orig_publish = bus.publish

        def publish_wrapper(event_type, data=None, **kwargs):
            publish_wrapper.calls.append((event_type, data))
            return orig_publish(event_type, data, **kwargs)

        publish_wrapper.calls = []

        with patch.object(bus, "publish", new=publish_wrapper):
            res = await engine.decide("Teste de fala", context={})

            # Allow small time for event dispatch
            await asyncio.sleep(0.2)

    # Cleanup
    bus.unsubscribe(sub_id)
    await bus.stop()

    return res, captured, publish_wrapper.calls


def test_decision_engine_publishes_audio_speak_event():
    res, captured, calls = asyncio.run(_run_decide_and_capture())
    assert res["final_answer"] == "Resposta de teste para fala"
    # Ensure publish was invoked for AUDIO_SPEAK
    assert any(c[0].value == EventType.AUDIO_SPEAK.value for c in calls)
    # If bus dispatched the event, captured should contain the message as well
    assert (not captured) or (
        captured and captured[-1] == "Resposta de teste para fala"
    )
