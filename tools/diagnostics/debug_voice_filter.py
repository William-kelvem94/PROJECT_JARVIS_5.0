
import sys
import os
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    print("Attempting to import AtomicVoiceFilter...")
    from src.core.audio.voice_filter import AtomicVoiceFilter
    print("Import successful.")
    
    print("Checking attributes...")
    print(f"TECH_BLOCKLIST: {len(AtomicVoiceFilter.TECH_BLOCKLIST)} items")
    print("Attributes check successful.")
    
except Exception:
    traceback.print_exc()
