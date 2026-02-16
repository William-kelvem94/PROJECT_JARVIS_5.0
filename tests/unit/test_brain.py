<<<<<<< Updated upstream
import sys
import os
import logging

<<<<<<< HEAD
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
=======
import logging

import pytest
>>>>>>> Stashed changes
=======
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
>>>>>>> dev-new-version

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

<<<<<<< HEAD
<<<<<<< Updated upstream
print('--- Testing Imports ---')
=======
print("--- Testing Imports ---")
>>>>>>> dev-new-version
try:
    from src.core.intelligence.local_brain import local_brain

    print("LocalBrain imported.")
except ImportError as e:
    print(f"Failed to import LocalBrain: {e}")
    sys.exit(1)

print("\n--- Testing Load ---")
if not local_brain._is_loaded:
    print("Triggering async load...")
    local_brain.load_async()
    if local_brain._is_loading:
        print("Load thread started successfully.")
    else:
        print("Warning: Load thread did not start.")
else:
    print("LocalBrain already loaded.")

print("\n--- Testing Generation (Mock) ---")
if local_brain._is_loaded and local_brain.pipe:
    try:
        response = local_brain.generate_response("Hello!")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Generation failed: {e}")
else:
<<<<<<< HEAD
    print('Skipping generation (model not fully loaded yet).')
=======
=======
    print("Skipping generation (model not fully loaded yet).")
>>>>>>> dev-new-version

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
>>>>>>> Stashed changes


def test_local_brain_generate_response_smoke():
    """If model is already loaded, generation should return text."""
    from src.core.intelligence.local_brain import local_brain

    if not getattr(local_brain, "_is_loaded", False) or not getattr(
        local_brain, "pipe", None
    ):
        pytest.skip("Model not fully loaded; skipping generation smoke test")

    response = local_brain.generate_response("Hello!")
    assert isinstance(response, str)
