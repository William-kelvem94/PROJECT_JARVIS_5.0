
import sys
import os
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

try:
    from src.core.intelligence.action_executor import ActionExecutor
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

def main():
    print("🤖 Testing Action Executor Wiring...")
    
    executor = ActionExecutor()
    
    # 1. Check Controller Loading
    if executor.action_controller:
        print("✅ Action Controller: LOADED")
    else:
        print("❌ Action Controller: MISSING (Check src.core.actions.action_controller)")
        
    if executor.security_manager:
        print("✅ Security Manager: LOADED")
    else:
        print("⚠️ Security Manager: MISSING (Using Dummy)")

    # 2. Check Advanced System Integrator
    system_integrator = None
    try:
        from src.core.actions.system_integrator import system_integrator as _sys_int
        system_integrator = _sys_int
        if system_integrator:
             print(f"✅ System Integrator: LOADED (Platform: {sys.platform})")
        else:
             print("❌ System Integrator: FAILED instantiation")
    except ImportError:
        print("❌ System Integrator: MODULE NOT FOUND")
        
    # 3. Validation
    if executor.action_controller and system_integrator:
        print("\n✨ MUSCLES & NERVES: FULLY OPERATIONAL")
    else:
        print("\n⚠️ MUSCLES PARALYZED - System cannot interact with PC.")

if __name__ == "__main__":
    main()
