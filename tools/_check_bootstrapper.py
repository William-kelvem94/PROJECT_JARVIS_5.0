
import sys
import os
sys.path.insert(0, os.getcwd())
import logging

# Setup basic logging to stdout
logging.basicConfig(level=logging.INFO)

try:
    print("Testing SystemBootstrapper Import...")
    from src.core.infrastructure.bootstrapper import SystemBootstrapper
    print("✅ Imported SystemBootstrapper")
    
    print("Testing SystemBootstrapper Instantiation...")
    bs = SystemBootstrapper()
    print("✅ Instantiated SystemBootstrapper")
    
    print("Testing Bootstrap Method Existence...")
    if hasattr(bs, 'bootstrap'):
        print("✅ bootstrap method exists")
    else:
        print("❌ bootstrap method MISSING")

except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
