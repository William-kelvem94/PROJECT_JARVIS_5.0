import sys
import os
import logging
import time

# Setup paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.intelligence.ai_agent import ai_agent
from src.core.vision.ui_detector import ui_detector
from src.core.vision.screen_capture import screen_capture

# Mock logger
logging.basicConfig(level=logging.INFO)

def test_hybrid_vision():
    print("\n[TEST] Testing Hybrid Intelligent Vision Logic...")
    
    # 1. Capture screen
    print("  📸 Capturing screen...")
    capture_path = screen_capture.capture_fullscreen(capture_type='test_vision')
    if not capture_path:
        print("  ❌ Capture failed")
        return False
        
    print(f"  ✅ Captured: {capture_path}")
    
    # 2. Run Hybrid Analysis (Mocking UI detection if needed or letting it run real)
    print("  🧠 Running Hybrid Analysis (Level 1 -> Level 2)...")
    
    # We expect Level 1 to run. Level 2 depends on content.
    # To test escalation, we might need a complex screen or mock the ui_detector.
    
    start_time = time.time()
    result = ai_agent.process_hybrid_vision(capture_path)
    end_time = time.time()
    
    print(f"  ✅ Result: {result}")
    print(f"  ⏱️ Time taken: {end_time - start_time:.2f}s")
    
    if result.get("source") == "local":
        print("  🟢 Decision: Local Filter (No escaltion)")
    elif result.get("source") == "cloud":
        print("  🔵 Decision: Cloud Escalation (Gemini)")
        
    return True

if __name__ == "__main__":
    test_hybrid_vision()
