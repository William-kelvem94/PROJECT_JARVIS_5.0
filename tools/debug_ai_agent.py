
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.core.intelligence.ai_agent import ai_agent
    print("AI Agent imported success")
except Exception:
    import traceback
    traceback.print_exc()
