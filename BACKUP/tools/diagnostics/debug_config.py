import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    print("Config imported success")
except Exception:
    import traceback

    traceback.print_exc()
