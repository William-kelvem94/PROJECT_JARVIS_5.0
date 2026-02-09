
import sys
import os
import logging

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logging.basicConfig(level=logging.INFO)

print("--- Testing Imports ---")
try:
    from src.core.intelligence.local_brain import local_brain
    print("LocalBrain imported.")
except ImportError as e:
    print(f"Failed to import LocalBrain: {e}")
    sys.exit(1)

print("\n--- Testing Load ---")
try:
    print("Calling load()... (This triggers download if first time)")
    local_brain.load()
    if local_brain.is_loaded:
        print("Success: Brain Loaded.")
    else:
        print("Failed: Brain not loaded (maybe missing dependencies?)")
except Exception as e:
    print(f"CRASH during load: {e}")

print("\n--- Testing Generation ---")
if local_brain.is_loaded:
    try:
        response = local_brain.generate_response("Hello, who are you?", "You are a test assistant.")
        print(f"Response: {response}")
    except Exception as e:
        print(f"CRASH during generation: {e}")
else:
    print("Skipping generation test.")
