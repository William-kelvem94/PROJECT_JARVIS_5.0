
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.utils.config import config
    print("Config imported success")
except Exception:
    import traceback
    traceback.print_exc()
