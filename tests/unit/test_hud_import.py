from PyQt6.QtWidgets import QApplication
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestScript")

try:
    print("Initializing QApplication...")
    app = QApplication(sys.argv)
    
    print("Importing window_manager...")
    from src.interface.window_manager import get_window_manager, InterfaceMode
    
    print("Getting window manager instance...")
    wm = get_window_manager(app)
    
    print("Attempting to initialize HUD via switch_mode...")
    wm.switch_mode(InterfaceMode.HUD_OVERLAY)
    
    if wm._hud:
        print(f"HUD initialized: {type(wm._hud)}")
        if "FallbackHUD" in str(type(wm._hud)):
            print("FAILURE: System fell back to FallbackHUD!")
            # Inspect why
            # Note: window_manager logs the error, check console output
        else:
            print("SUCCESS: ModernHUD initialized.")
    else:
        print("FAILURE: No HUD instance created.")
    
except Exception as e:
    print(f"CRITICAL FAILURE: {e}")
    import traceback
    with open("hud_error.log", "w") as f:
        traceback.print_exc(file=f)
    print("Traceback written to hud_error.log")
