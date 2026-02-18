import asyncio
from unittest.mock import patch

from src.core.intelligence.ai_agent import AIAgent
from src.core.infrastructure.async_event_bus import Event, EventType


def test_agent_is_born_blind_and_updates_on_vision_ready_event():
    agent = AIAgent()

    # Inicialmente cego
    assert hasattr(agent, "vision_ready")
    assert agent.vision_ready is False
    assert agent.vision_mock_mode is False

    # Simular evento VISION_READY (mock = True)
    evt = Event(type=EventType.VISION_READY, data={"available": True, "mock": True})

    asyncio.run(agent._on_vision_ready(evt))

    assert agent.vision_ready is True
    assert agent.vision_mock_mode is True


def test_process_command_skips_screenshot_until_vision_ready():
    async def inner():
        agent = AIAgent()

        # Substituir _call_ollama_async para evitar chamadas externas
        async def fake_ollama(*_args, **_kwargs):
            _ = (_args, _kwargs)
            return "OK"

        # Dummy screen capture que falha se chamada (não deve ser chamada
        # enquanto agent.vision_ready == False)
        class DummyCaptureShouldNotCall:
            def capture_fullscreen(self, *args, **kwargs):
                _ = (args, kwargs)
                raise AssertionError(
                    "capture_fullscreen must NOT be called when vision is not ready"
                )

        with patch.object(agent, "_call_ollama_async", fake_ollama):
            with patch.object(agent, "screen_capture", DummyCaptureShouldNotCall()):
                agent.vision_ready = False
                res = await agent.process_command("Qual é o texto na tela?")
                assert isinstance(res, str)
                assert res == "OK"

            # Agora habilitar visão e usar um capture que registra chamadas
            class DummyCaptureRecord:
                def __init__(self):
                    self.called = False

                def capture_fullscreen(self, *args, **kwargs):
                    self.called = True
                    _ = (args, kwargs)
                    return None

            agent.vision_ready = True
            recorder = DummyCaptureRecord()
            with patch.object(agent, "screen_capture", recorder):
                res2 = await agent.process_command("Verifique a tela")
                assert res2 == "OK"
                assert recorder.called is True

    asyncio.run(inner())
