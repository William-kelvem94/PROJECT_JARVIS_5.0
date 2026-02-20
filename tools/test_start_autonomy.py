import sys
import os
import asyncio
import types
import pytest


import importlib.util

# Patch sys.path for import
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

# Import the conscious_loop function from start_autonomy.py
spec = importlib.util.spec_from_file_location(
    "start_autonomy", os.path.join(os.path.dirname(__file__), "start_autonomy.py")
)
if spec is None or spec.loader is None:
    raise ImportError("Could not load spec or loader for start_autonomy.py")
start_autonomy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(start_autonomy)


@pytest.fixture(autouse=True)
def patch_logging(monkeypatch):
    # Prevent actual logging output during tests
    monkeypatch.setattr(start_autonomy.logger, "info", lambda *a, **k: None)
    monkeypatch.setattr(start_autonomy.logger, "warning", lambda *a, **k: None)
    monkeypatch.setattr(start_autonomy.logger, "error", lambda *a, **k: None)


@pytest.fixture
def mock_brain(monkeypatch):
    class MockBrain:
        def check_connectivity(self):
            return True

    monkeypatch.setattr(start_autonomy, "BrainRouter", MockBrain)
    return MockBrain


@pytest.fixture
def mock_voice(monkeypatch):
    class MockVoice:
        def speak(self, text):
            self.last_spoken = text

    monkeypatch.setattr(start_autonomy, "VoiceController", MockVoice)
    return MockVoice


@pytest.fixture
def mock_agent(monkeypatch):
    class MockAgent:
        safe_mode = False

        def analyze_codebase(self):
            self.analyzed = True

    monkeypatch.setattr(start_autonomy, "AIAgent", MockAgent)
    return MockAgent


@pytest.fixture
def mock_subprocess(monkeypatch):
    class DummyCompleted:
        returncode = 0

    monkeypatch.setattr(
        start_autonomy,
        "subprocess",
        types.SimpleNamespace(run=lambda *a, **k: DummyCompleted()),
    )


@pytest.mark.asyncio
async def test_conscious_loop_normal(
    monkeypatch, mock_brain, mock_voice, mock_agent, mock_subprocess
):
    # Patch asyncio.sleep to break the infinite loop after first iteration
    sleep_calls = []

    async def fake_sleep(secs):
        sleep_calls.append(secs)
        raise KeyboardInterrupt  # Simulate breaking the loop

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    # Run conscious_loop and expect it to exit after one loop
    try:
        await start_autonomy.conscious_loop()
    except KeyboardInterrupt:
        pass
    assert sleep_calls and sleep_calls[0] == 60


@pytest.mark.asyncio
async def test_conscious_loop_no_internet(
    monkeypatch, mock_voice, mock_agent, mock_subprocess
):
    class MockBrainNoNet:
        def check_connectivity(self):
            return False

    monkeypatch.setattr(start_autonomy, "BrainRouter", MockBrainNoNet)

    sleep_called = False

    async def fake_sleep(secs):
        nonlocal sleep_called
        sleep_called = True
        raise KeyboardInterrupt

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    result = None
    try:
        result = await start_autonomy.conscious_loop()
    except KeyboardInterrupt:
        pass

    # In no-connectivity mode, the loop should exit without reaching the sleep
    # call
    assert sleep_called is False
    assert result is None


async def test_conscious_loop_agent_safe_mode(
    monkeypatch, mock_brain, mock_voice, mock_subprocess
):
    class MockAgentSafe:
        safe_mode = True

    monkeypatch.setattr(start_autonomy, "AIAgent", MockAgentSafe)

    # conscious_loop should return early if agent is in safe mode
    result = await start_autonomy.conscious_loop()
    assert result is None


@pytest.mark.asyncio
async def test_conscious_loop_agent_no_analyze(
    monkeypatch, mock_brain, mock_voice, mock_subprocess
):
    # Expect an AttributeError when conscious_loop tries to call the missing
    # analyze_codebase method on the agent.
    with pytest.raises(AttributeError):
        await start_autonomy.conscious_loop()

    async def fake_sleep(secs):
        raise KeyboardInterrupt

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    try:
        await start_autonomy.conscious_loop()
    except KeyboardInterrupt:
        pass
