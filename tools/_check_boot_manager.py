
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    print("Importing BootManager...")
    from src.core.infrastructure.boot_manager import BootManager
    print("✅ Success: Imported BootManager")
except Exception as e:
    print(f"❌ Fail: {e}")
    import traceback
    traceback.print_exc()
