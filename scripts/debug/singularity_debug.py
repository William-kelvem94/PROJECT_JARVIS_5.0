import sys
import io
import os
from pathlib import Path
import logging

PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT / "src"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DEBUG")

print("🚀 INICIANDO DIAGNÓSTICO PROFUNDO...")

try:
    print("Step 1: Importing PyQt6...")
    from PyQt6.QtWidgets import QApplication
    print("Step 2: Creating QApplication...")
    app = QApplication(sys.argv)
    
    print("Step 3: Importing Window Manager...")
    from interface.window_manager import get_window_manager
    print("Step 4: Initializing Window Manager...")
    wm = get_window_manager(app)
    
    print("Step 5: Importing Vision System...")
    from core.vision_system import get_vision_system
    print("Step 6: Initializing Vision System...")
    vs = get_vision_system(PROJECT_ROOT / "data")
    
    print("Step 7: Importing Audio System...")
    from core.enhanced_audio import get_audio_system
    print("Step 8: Initializing Audio System...")
    asys = get_audio_system(PROJECT_ROOT / "data")
    
    print("Step 9: Importing Integrator...")
    from core.system_integrator import get_system_integrator
    print("Step 10: Initializing Integrator...")
    si = get_system_integrator()
    
    print("✅ TODO INICIALIZADO COM SUCESSO!")
    
except Exception as e:
    print(f"❌ FALHA NO DIAGNÓSTICO: {e}")
    import traceback
    traceback.print_exc()
except BaseException as e:
    print(f"🚨 CRITICAL SYSTEM ERROR: {e}")
