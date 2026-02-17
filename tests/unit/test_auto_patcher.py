import os
import json
from pathlib import Path
from unittest.mock import patch

from src.core.evolution.auto_patcher import auto_patcher


def test_attempt_patch_declined_without_permission(tmp_path):
    # Ensure env var not set
    os.environ.pop("JARVIS_ALLOW_SELF_PATCH", None)

    # Create a sample python file
    sample = tmp_path / "sample_bug.py"
    sample.write_text("def add(a, b):\n    return a + b\n")

    insight = {
        "signature": "IndexError: list index out of range",
        "example": {"file": str(sample)},
    }

    ok, msg = auto_patcher.attempt_patch_from_insight(insight)
    assert ok is False
    assert msg == "self-patch-disabled"
    # File must remain unchanged
    assert "return a + b" in sample.read_text(encoding="utf-8")


def test_attempt_patch_applies_when_allowed(tmp_path, monkeypatch):
    # Enable self-patch
    monkeypatch.setenv("JARVIS_ALLOW_SELF_PATCH", "1")

    # Create a sample python file with an obvious bug
    sample = tmp_path / "sample_bug2.py"
    sample.write_text(
        "def greet(name):\n    # missing return\n    print(f'Hello {name}')\n",
        encoding="utf-8",
    )

    insight = {
        "signature": "TypeError: 'NoneType' object is not callable",
        "example": {"file": str(sample)},
    }

    # Mock LLM response to return full-file patched content inside ``` ```
    patched = (
        "```python\n"
        "def greet(name):\n"
        "    return f'Hello {name}'\n"
        "```"
    )

    async def fake_llm(*args, **kwargs):
        return patched

    # Sanity checks that the env var and runtime gate are active
    assert os.getenv("JARVIS_ALLOW_SELF_PATCH") == "1"
    assert auto_patcher.is_allowed() is True

    with patch("src.core.intelligence.ai_agent.ai_agent._call_ollama_async", new=fake_llm):
        ok, msg = auto_patcher.attempt_patch_from_insight(insight)

    assert ok is True, msg
    txt = sample.read_text(encoding="utf-8")
    assert "return f'Hello {name}'" in txt
    # Backup file should exist
    bak_files = list(Path(sample.parent).glob("sample_bug2.py.bak.*"))
    assert len(bak_files) >= 1


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

    # Force the validator to decline the action (no request_id)
    from src.core.evolution.action_validator import ValidationResult

    with patch("src.core.evolution.action_validator.action_validator.validate", return_value=ValidationResult(False, True, "forced-decline")):
        from src.core.evolution.auto_patcher import auto_patcher

        with patch("src.core.intelligence.ai_agent.ai_agent._call_ollama_async", new=fake_llm):
            ok, msg = auto_patcher.attempt_patch_from_insight(insight)

    assert ok is False
    assert msg == "forced-decline"


def test_autopatcher_registers_pending_and_applies_on_approval(monkeypatch, tmp_path):
    # Verify AutoPatcher registers pending approval and ActionApprovalManager executes on approval
    monkeypatch.setenv("JARVIS_ALLOW_SELF_PATCH", "1")

    sample = tmp_path / "sample_protect.py"
    sample.write_text("def a():\n    return 1\n", encoding="utf-8")

    insight = {"signature": "err", "example": {"file": str(sample)}}

    # LLM will return patched file
    patched = "```python\ndef a():\n    return 2\n```"

    async def fake_llm(*args, **kwargs):
        return patched

    # Make validator indicate approval required and supply a request_id
    from src.core.evolution.action_validator import ValidationResult

    fake_validation = ValidationResult(False, True, "approval-needed", request_id="REQ-42")

    with patch("src.core.evolution.action_validator.action_validator.validate", return_value=fake_validation):
        from src.core.evolution.auto_patcher import auto_patcher
        from src.core.evolution.action_approval import action_approval_manager
        from src.core.infrastructure.async_event_bus import get_event_bus, EventType

        # Start event bus and approval manager listener inside same running loop
        bus = get_event_bus()

        import asyncio

        async def _run_flow():
            await bus.start()
            action_approval_manager.start_listening()

            # Call attempt_patch_from_insight in a thread to avoid nested event-loop issues
            loop = asyncio.get_running_loop()
            # Patch AutoPatcher's LLM wrapper to avoid nested event-loop issues
            with patch("src.core.evolution.auto_patcher.AutoPatcher._call_llm_for_patch", return_value=patched):
                ok, msg = await loop.run_in_executor(None, lambda: auto_patcher.attempt_patch_from_insight(insight))

            # Should not apply immediately; should register pending
            assert ok is False
            assert msg == "approval-pending:REQ-42"
            # pending entry must exist
            assert "REQ-42" in action_approval_manager._pending

            # Approve directly (reliable in unit tests)
            action_approval_manager.approve_direct("REQ-42", approved=True, approver="unittest")

            # allow background thread to run
            await asyncio.sleep(0.1)

            # pending should have been removed
            assert "REQ-42" not in action_approval_manager._pending

            # Verify file updated
            txt = sample.read_text(encoding="utf-8")
            assert "return 2" in txt

            await bus.stop()

        asyncio.run(_run_flow())
