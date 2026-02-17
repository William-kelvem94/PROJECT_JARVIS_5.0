import sys
import os
import logging
import pytest

# Ensure src is importable during tests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_local_brain_import():
    """Smoke test: module import should not crash test collection."""
    try:
        from src.core.intelligence.local_brain import local_brain
    except ImportError as exc:
        pytest.fail(f"Failed to import LocalBrain: {exc}")

    assert local_brain is not None


def test_local_brain_async_load_flag():
    """Loading can be triggered without raising exceptions."""
    from src.core.intelligence.local_brain import local_brain

    if not hasattr(local_brain, "load_async"):
        pytest.skip("LocalBrain implementation does not expose load_async")

    try:
        if not getattr(local_brain, "_is_loaded", False):
            local_brain.load_async()
        assert hasattr(local_brain, "_is_loading")
    except Exception as exc:
        pytest.fail(f"LocalBrain async load trigger failed: {exc}")


def test_local_brain_generate_response_smoke():
    """If model is already loaded, generation should return text."""
    from src.core.intelligence.local_brain import local_brain

    if not getattr(local_brain, "_is_loaded", False) or not getattr(
        local_brain, "pipe", None
    ):
        pytest.skip("Model not fully loaded; skipping generation smoke test")

    response = local_brain.generate_response("Hello!")
    assert isinstance(response, str)
