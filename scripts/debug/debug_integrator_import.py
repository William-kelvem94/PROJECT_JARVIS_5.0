
import sys
import traceback
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

print("🔍 Debugging System Integrator Import...")
try:
    import src.core.actions.system_integrator
    print("✅ Import Successful")
except Exception:
    traceback.print_exc()
