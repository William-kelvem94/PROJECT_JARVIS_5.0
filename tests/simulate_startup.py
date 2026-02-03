
import sys
import os
import logging
import traceback
import importlib

# Setup paths - Add PROJECT ROOT to path to allow 'from src...' imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Redirect stdout/stderr to file
log_file = open('tests/simulation_result.log', 'w', encoding='utf-8')
sys.stdout = log_file
sys.stderr = log_file

def test_module(module_name, class_name=None):
    print(f"\n[TESTING] {module_name}...")
    try:
        mod = importlib.import_module(module_name)
        print(f"  ✅ Import successful: {module_name}")
        
        if class_name:
            cls = getattr(mod, class_name)
            if hasattr(mod, class_name.lower()): # Check for global instance (e.g. gesture_controller)
                instance = getattr(mod, class_name.lower())
                print(f"  ✅ Global instance found: {class_name.lower()}")
            else:
                print(f"  ℹ️ Instantiating {class_name}...")
                instance = cls()
                print(f"  ✅ Instantiation successful: {class_name}")
            return True
    except Exception as e:
        print(f"  ❌ FAILED: {module_name}")
        print(f"  Error: {str(e)}")
        traceback.print_exc()
        return False

def run_simulation():
    print("==========================================")
    print("   JARVIS 5.0 - FULL SYSTEM SIMULATION    ")
    print("==========================================")
    
    failures = []

    # 1. Core Utils
    if not test_module('utils.config', 'Config'): failures.append('utils.config')
    
    # 2. Database
    if not test_module('database.models', 'DatabaseManager'): failures.append('database.models')
    
    # 3. Hardware Manager
    if not test_module('core.hardware_manager', 'HardwareManager'): failures.append('core.hardware_manager')

    # 4. Neural Memory (Critical)
    if not test_module('core.neural_memory', 'NeuralMemory'): failures.append('core.neural_memory')

    # 5. Controllers (The sources of recent crashes)
    if not test_module('core.action_controller', 'ActionController'): failures.append('core.action_controller')
    
    # Gesture Controller (MediaPipe issue)
    if not test_module('core.gesture_controller', 'GestureController'): failures.append('core.gesture_controller')
    
    # Voice Controller (Common crash point)
    if not test_module('core.voice_controller', 'VoiceController'): failures.append('core.voice_controller')

    # Camera Controller (CV2/FaceRec)
    if not test_module('core.camera_controller', 'CameraController'): failures.append('core.camera_controller')

    # UI Detector (YOLO)
    if not test_module('core.ui_detector', 'UIDetector'): failures.append('core.ui_detector')

    # 6. AI Agent (Orchestrator)
    if not test_module('core.ai_agent', 'AIAgent'): failures.append('core.ai_agent')

    print("\n==========================================")
    if failures:
        print(f"❌ SIMULATION COMPLETED WITH {len(failures)} FAILURES.")
        print("Failed Modules:", ", ".join(failures))
        sys.exit(1)
    else:
        print("✅ SIMULATION COMPLETED SUCCESSFULLY! All Core Systems Operational.")
        sys.exit(0)

if __name__ == "__main__":
    run_simulation()
