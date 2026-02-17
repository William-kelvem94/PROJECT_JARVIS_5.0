import asyncio
from pathlib import Path
from unittest.mock import patch

from src.core.evolution.action_validator import action_validator, ValidationResult
from src.core.infrastructure.async_event_bus import get_event_bus, EventType


def test_auto_approves_safe_python_modification(tmp_path):
    f = tmp_path / "safe_mod.py"
    f.write_text("def ok():\n    return 1\n")

    action = {
        "action_type": "file_modify",
        "target": str(f),
        "proposed_code": "def ok():\n    return 2\n",
    }

    res = action_validator.validate(action)
    assert res.approved is True
    assert res.requires_approval is False


def test_blocks_protected_delete_and_emits_request(monkeypatch):
    # Ensure tests are deterministic regardless of developer env (.env)
    monkeypatch.delenv("JARVIS_AUTO_APPROVE", raising=False)

    bus = get_event_bus()

    async def _run():
        await bus.start()

        captured = []

        async def _h(ev):
            captured.append(ev)

        sub_id = bus.subscribe([EventType.ACTION_APPROVAL_REQUEST], _h)

        action = {"action_type": "file_delete", "target": "main.py"}
        res = action_validator.validate(action)

        # Should require approval and be declined by default
        assert res.approved is False
        assert res.requires_approval is True
        assert res.reason == "protected-path"

        # allow small time for delivery
        await asyncio.sleep(0.05)
        # delivery to subscribers happens asynchronously; assert the event was published
        assert bus.total_events_published >= 1

        bus.unsubscribe(sub_id)
        await bus.stop()

    asyncio.run(_run())


def test_env_auto_approves_protected_path(monkeypatch):
    # When JARVIS_AUTO_APPROVE=1, protected-path actions should be auto-approved
    monkeypatch.setenv("JARVIS_AUTO_APPROVE", "1")
    action = {"action_type": "file_modify", "target": "main.py", "proposed_code": "# noop"}

    res = action_validator.validate(action)
    assert res.approved is True
    assert res.requires_approval is False
    assert res.reason == "auto-approved"


def test_autopatcher_respects_action_validator(monkeypatch, tmp_path):
    # Ensure AutoPatcher will consult ActionValidator and honour a decline
    # Create a dummy file and insight
    sample = tmp_path / "mod.py"
    sample.write_text("def a():\n    return 1\n")

    insight = {"signature": "err", "example": {"file": str(sample)}}

    # Enable self patch env
    monkeypatch.setenv("JARVIS_ALLOW_SELF_PATCH", "1")

    # Mock LLM to return a valid patched file
    patched = "```python\ndef a():\n    return 2\n```"

    async def fake_llm(*args, **kwargs):
        return patched

    # Force the validator to decline the action
    with patch("src.core.evolution.action_validator.action_validator.validate", return_value=ValidationResult(False, True, "forced-decline")):
        from src.core.evolution.auto_patcher import auto_patcher

        with patch("src.core.intelligence.ai_agent.ai_agent._call_ollama_async", new=fake_llm):
            ok, msg = auto_patcher.attempt_patch_from_insight(insight)

    assert ok is False
    assert msg == "forced-decline"
