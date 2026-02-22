import sys
import threading
import logging
import argparse
import time
from pathlib import Path

# Fix for standard output encoding
if sys.platform == 'win32':
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

# Configuration and Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger("JARVIS-CORE")

class JarvisSingularity:
    """
    JARVIS 5.0 - Unified Singularity Core
    The ultimate entry point for the Stark 'Completão' Vision.
    """
    
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="JARVIS 5.0 - Singularity Core")
        self.parser.add_argument("--headless", action="store_true", help="Start without GUI")
        self.parser.add_argument("--debug", action="store_true", help="Enable debug logging")
        self.parser.add_argument("--safe", action="store_true", help="Start in safe mode")
        self.args = self.parser.parse_args()
        
        if self.args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            
        self.is_running = True
        self.boot_manager = None
        self.ui_mode = not self.args.headless
        
    def bootstrap(self):
        """Orchestrates the complete system boot sequence."""
        print("\n" + "="*60)
        print("  🧬 JARVIS 5.0 - SINGULARITY CORE INITIALIZER")
        print("  Vision: Stark 'Completão' | Version: 5.0.1")
        print("="*60 + "\n")
        
        try:
            # 1. Initialize professional BootManager
            from src.core.infrastructure.boot_manager import boot_manager
            self.boot_manager = boot_manager
            
            # Setup GUI requirement in boot manifest
            if not self.ui_mode:
                # Disable GUI-related modules if headless
                if "window_manager" in self.boot_manager.modules:
                    self.boot_manager.modules["window_manager"].required = False
            
            # 2. Execute Boot Sequence
            logger.info("🚀 Starting Neural Boot Sequence...")
            success = self.boot_manager.start_boot(blocking=True)
            
            if not success:
                logger.critical("❌ Critical failure during Singularity Boot.")
                sys.exit(1)
                
            # 3. Post-Boot Integration
            self._integrate_systems()
            
            # 4. Proactive Briefing
            self._start_briefing()
            
            # 5. Launch Interfaces
            self._launch_interfaces()
            
        except Exception as e:
            logger.critical(f"💥 Fatal Crash during bootstrap: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def _integrate_systems(self):
        """Connects instances from BootManager to local references."""
        self.ai_agent = self.boot_manager.get_instance("ai_agent")
        self.speaker = self.boot_manager.get_instance("audio_system")
        self.window_manager = self.boot_manager.get_instance("window_manager")
        self.app = self.boot_manager.get_instance("qt_application")
        
        logger.info("✅ Systems integrated into Singularity Core.")

    def _start_briefing(self):
        """Generates and speaks the Stark 'Completão' Briefing."""
        try:
            from src.core.briefing_manager import briefing_manager
            briefing = briefing_manager.generate_startup_briefing()
            print(f"\n[JARVIS]: {briefing}")
            if self.speaker:
                # Run speech in thread to not block UI
                threading.Thread(target=self.speaker.speak, args=(briefing,), daemon=True).start()
        except Exception as e:
            logger.warning(f"Briefing failed: {e}")

    def _launch_interfaces(self):
        """Starts Voice, Text and GUI event loops."""
        # A. Voice Loop Thread
        threading.Thread(target=self._voice_loop, daemon=True, name="VoiceLoop").start()
        
        # B. Text Loop Thread
        threading.Thread(target=self._text_loop, daemon=True, name="TextLoop").start()
        
        # C. GUI Main Loop (Must be in Main Thread)
        if self.ui_mode and self.app:
            logger.info("✨ Launching Visual HUD & Dashboard...")
            sys.exit(self.app.exec())
        else:
            logger.info("🔌 Headless mode active. Running core in terminal.")
            while self.is_running:
                time.sleep(1)

    def _text_loop(self):
        """Interactive Terminal for JARVIS."""
        print("\n--- STARK CONSOLE ACCESS GRANTED ---")
        while self.is_running:
            try:
                user_input = input("\n[USER]: ").strip()
                if not user_input: continue
                
                if user_input.lower() in ["exit", "sair", "shutdown"]:
                    self.shutdown()
                    break
                
                response = self.ai_agent.process(user_input) if self.ai_agent else "Core offline."
                print(f"\n[JARVIS]: {response}")
                if self.speaker:
                    self.speaker.speak(response)
                    
            except EOFError:
                break
            except Exception as e:
                logger.error(f"Console error: {e}")

    def _voice_loop(self):
        """Background listener for vocal commands."""
        # Using the listener fromperception if available
        try:
            from src.perception.listener import listener
            while self.is_running:
                voice_text = listener.listen()
                if voice_text:
                    logger.info(f"🎤 Voice Heard: {voice_text}")
                    response = self.ai_agent.process(voice_text)
                    print(f"\n[JARVIS]: {response}")
                    if self.speaker:
                        self.speaker.speak(response)
        except Exception as e:
            logger.error(f"Voice loop failed: {e}")

    def shutdown(self):
        """Graceful system termination."""
        print("\n🛑 Initiating Shutdown Protocol...")
        self.is_running = False
        if self.speaker:
            self.speaker.speak("Desativando protocolos. Até logo, senhor.")
        time.sleep(1)
        if self.app:
            self.app.quit()
        sys.exit(0)

if __name__ == "__main__":
    jarvis = JarvisSingularity()
    jarvis.bootstrap()

