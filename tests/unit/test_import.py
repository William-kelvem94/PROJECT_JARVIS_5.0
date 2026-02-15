
import sys
import traceback

try:
    from src.core.intelligence.ai_agent import ai_agent
    print("Import Success")
except Exception:
    traceback.print_exc()
