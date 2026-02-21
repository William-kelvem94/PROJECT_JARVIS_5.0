import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def run_brain_checks() -> int:
    """Run quick smoke checks for LocalBrain without exiting on import."""
    logging.basicConfig(level=logging.INFO)

    print("--- Testing Imports ---")
    try:
        from src.core.intelligence.local_brain import local_brain

        print("LocalBrain imported.")
    except ImportError as e:
        print(f"Failed to import LocalBrain: {e}")
        raise

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
        print("Skipping generation (model not fully loaded yet).")

    return 0


if __name__ == "__main__":
    run_brain_checks()
