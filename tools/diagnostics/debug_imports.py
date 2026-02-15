
import sys
import os
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

modules_to_test = [
    "src.core.intelligence.stark_nexus",
    "src.core.intelligence.action_executor",
    "src.learning.learning_engine",
    "src.core.intelligence.analisador_contexto",
    "src.core.management.device_manager",
    "src.core.management.orchestrator"
]

for module in modules_to_test:
    print(f"\nScanning: {module} ...")
    try:
        __import__(module)
        print(f"✅ Success: {module}")
    except Exception as e:
        print(f"❌ Failed: {module}")
        traceback.print_exc()
