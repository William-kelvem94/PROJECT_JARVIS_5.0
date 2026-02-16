#!/usr/bin/env python3
"""
Simple JARVIS startup test
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_jarvis_startup():
    """Test JARVIS startup step by step"""
    print("🚀 JARVIS Startup Test")
    print("=" * 50)

    try:
        print("1. Testing PyQt6...")
        from PyQt6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        print("   ✅ PyQt6 OK")

        print("2. Testing WindowManager...")
        from src.interface.window_manager import get_window_manager
        wm = get_window_manager(app)
        print("   ✅ WindowManager OK")

        print("3. Testing core systems...")
        print("   Testing audio system...")
        try:
            from src.core.audio.enhanced_audio import get_audio_system
            print("   ✅ Audio system import OK")
        except Exception as e:
            print(f"   ⚠️ Audio system failed (non-critical): {e}")
            audio_system = None  # noqa: F841

        print("   Testing vision system...")
        try:
            from src.core.vision.vision_system import get_vision_system
            print("   ✅ Vision system import OK")
        except Exception as e:
            print(f"   ❌ Vision system failed: {e}")
            return 1

        print("   Testing AI agent...")
        try:
            from src.core.intelligence.ai_agent import ai_agent
            print("   ✅ AI Agent import OK")
        except Exception as e:
            print(f"   ❌ AI Agent failed: {e}")
            return 1

        print("4. Testing JarvisSingularity...")
        from main import JarvisSingularity

        # Create instances
        instances = {
            "Window Manager": wm,
            "System Integrator": None,  # Skip for test
            "Audio System": get_audio_system(os.path.join(os.path.dirname(__file__), 'data')),
            "Vision System": get_vision_system(os.path.join(os.path.dirname(__file__), 'data')),
            "AI Agent": ai_agent,
        }

        jarvis = JarvisSingularity(app, instances)
        print("   ✅ JarvisSingularity created")

        print("5. Testing startup...")
        jarvis.start()
        print("   ✅ JARVIS started successfully!")

        print("\n🎉 JARVIS initialization completed successfully!")
        print("The JARVIS core is working. GUI should be visible.")

        # Don't run app.exec() to avoid blocking
        return 0

    except Exception as e:
        print(f"❌ Test failed at step: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_jarvis_startup())