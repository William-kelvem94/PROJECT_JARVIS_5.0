"""
Wake Word Detection Module
Inspired by llm-guy/jarvis - Listens for wake words like "Jarvis" to activate the assistant
"""

import os
import time
import threading
from typing import Optional, Callable, List
from pathlib import Path

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("Warning: speech_recognition not available")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    print("Warning: pyttsx3 not available")


class WakeWordDetector:
    """
    Wake word detection system for voice activation
    Features:
    - Multiple wake words support
    - Timeout and auto-reset
    - Conversation mode management
    - Privacy-focused (optional offline mode)
    """
    
    def __init__(
        self,
        wake_words: List[str] = None,
        timeout: float = 30.0,
        confidence_threshold: float = 0.6,
        offline_mode: bool = False
    ):
        """
        Initialize wake word detector.
        
        Args:
            wake_words: List of wake words (default: ["jarvis", "hey jarvis"])
            timeout: Seconds of inactivity before reset (default: 30)
            confidence_threshold: Minimum confidence for detection
            offline_mode: Use offline speech recognition
        """
        self.wake_words = wake_words or ["jarvis", "hey jarvis", "oi jarvis"]
        self.timeout = timeout
        self.confidence_threshold = confidence_threshold
        self.offline_mode = offline_mode
        
        # State management
        self.is_active = False
        self.is_listening = False
        self.last_activity = time.time()
        
        # Initialize components
        self.recognizer = None
        self.tts_engine = None
        
        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            # Adjust for better wake word detection
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
        
        if PYTTSX3_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 175)
                self.tts_engine.setProperty('volume', 0.9)
            except:
                self.tts_engine = None
        
        # Callback for when activated
        self.on_activated: Optional[Callable] = None
        self.on_deactivated: Optional[Callable] = None
        
        print(f"[WakeWord] Initialized with wake words: {self.wake_words}")
        print(f"[WakeWord] Timeout: {timeout}s, Offline: {offline_mode}")
    
    def _contains_wake_word(self, text: str) -> bool:
        """Check if text contains any wake word."""
        text_lower = text.lower().strip()
        for wake_word in self.wake_words:
            if wake_word.lower() in text_lower:
                return True
        return False
    
    def _speak(self, text: str):
        """Speak text if TTS available."""
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except:
                print(f"[WakeWord] {text}")
        else:
            print(f"[WakeWord] {text}")
    
    def listen_for_wake_word(self) -> bool:
        """
        Listen for wake word in audio stream.
        Returns True if wake word detected.
        """
        if not self.recognizer:
            print("[WakeWord] ERROR: Speech recognizer not available")
            return False
        
        try:
            with sr.Microphone() as source:
                # Quick ambient noise adjustment
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                
                print("[WakeWord] Listening for wake word...")
                # Short timeout for wake word detection
                audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=3)
                
                # Recognize speech
                try:
                    if self.offline_mode:
                        # Try offline recognition if available
                        text = self._recognize_offline(audio)
                    else:
                        # Use Google Speech Recognition
                        text = self.recognizer.recognize_google(audio, language='pt-BR')
                    
                    if text:
                        print(f"[WakeWord] Heard: {text}")
                        return self._contains_wake_word(text)
                    
                except sr.UnknownValueError:
                    pass  # Could not understand audio
                except sr.RequestError as e:
                    print(f"[WakeWord] Recognition error: {e}")
                    # Fallback to English if Portuguese fails
                    try:
                        text = self.recognizer.recognize_google(audio, language='en-US')
                        if text:
                            print(f"[WakeWord] Heard (EN): {text}")
                            return self._contains_wake_word(text)
                    except:
                        pass
        
        except sr.WaitTimeoutError:
            pass  # Normal timeout, continue listening
        except Exception as e:
            print(f"[WakeWord] Error: {e}")
        
        return False
    
    def _recognize_offline(self, audio) -> Optional[str]:
        """
        Recognize speech offline if VOSK available.
        
        Note: This is a placeholder implementation. To enable offline recognition:
        1. Install VOSK: pip install vosk
        2. Download a VOSK model from https://alphacephei.com/vosk/models
        3. Set VOSK_MODEL_PATH environment variable
        4. Implement VOSK recognition logic here
        
        Returns:
            Recognized text or None if not implemented
        """
        # Placeholder for offline recognition
        # Would require VOSK or similar offline STT
        return None
    
    def activate(self):
        """Activate the assistant."""
        if not self.is_active:
            self.is_active = True
            self.last_activity = time.time()
            print("[WakeWord] ✓ Activated!")
            self._speak("Sim, estou aqui!")
            
            if self.on_activated:
                self.on_activated()
    
    def deactivate(self):
        """Deactivate the assistant."""
        if self.is_active:
            self.is_active = False
            print("[WakeWord] ✗ Deactivated (timeout or command)")
            
            if self.on_deactivated:
                self.on_deactivated()
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = time.time()
    
    def check_timeout(self):
        """Check if timeout has been reached."""
        if self.is_active:
            elapsed = time.time() - self.last_activity
            if elapsed > self.timeout:
                print(f"[WakeWord] Timeout reached ({elapsed:.1f}s > {self.timeout}s)")
                self.deactivate()
                return True
        return False
    
    def listen_for_command(self, timeout: float = 5.0) -> Optional[str]:
        """
        Listen for a command after activation.
        
        Args:
            timeout: Maximum time to wait for command
            
        Returns:
            Recognized command text or None
        """
        if not self.is_active:
            return None
        
        if not self.recognizer:
            return None
        
        try:
            with sr.Microphone() as source:
                print("[WakeWord] Listening for command...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=10.0
                )
                
                # Recognize command
                try:
                    text = self.recognizer.recognize_google(audio, language='pt-BR')
                    print(f"[WakeWord] Command: {text}")
                    self.update_activity()
                    return text
                except sr.UnknownValueError:
                    print("[WakeWord] Could not understand command")
                    return None
                except sr.RequestError as e:
                    print(f"[WakeWord] Recognition error: {e}")
                    return None
        
        except sr.WaitTimeoutError:
            print("[WakeWord] Command timeout")
            return None
        except Exception as e:
            print(f"[WakeWord] Error listening for command: {e}")
            return None
    
    def run_loop(self, command_handler: Callable[[str], bool]):
        """
        Run the main wake word detection loop.
        
        Args:
            command_handler: Function to handle recognized commands
                           Should return False to stop the loop
        """
        print("\n" + "="*60)
        print("🎤 WAKE WORD DETECTION ACTIVE")
        print("="*60)
        print(f"Wake words: {', '.join(self.wake_words)}")
        print(f"Timeout: {self.timeout} seconds")
        print("Speak a wake word to activate...")
        print("="*60 + "\n")
        
        self.is_listening = True
        
        try:
            while self.is_listening:
                # Check for timeout if active
                if self.is_active:
                    if self.check_timeout():
                        print("[WakeWord] Waiting for wake word...")
                        continue
                
                # If not active, listen for wake word
                if not self.is_active:
                    if self.listen_for_wake_word():
                        self.activate()
                else:
                    # If active, listen for commands
                    command = self.listen_for_command()
                    if command:
                        # Check for exit commands
                        exit_words = ["sair", "tchau", "bye", "exit", "quit", "desligar"]
                        if any(word in command.lower() for word in exit_words):
                            self._speak("Até logo!")
                            return
                        
                        # Handle command
                        try:
                            should_continue = command_handler(command)
                            if not should_continue:
                                return
                        except Exception as e:
                            print(f"[WakeWord] Error handling command: {e}")
                    
                    # Small delay between command listening
                    time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\n[WakeWord] Interrupted by user")
        finally:
            self.is_listening = False
            if self.is_active:
                self.deactivate()
            print("[WakeWord] Shutdown complete")
    
    def stop(self):
        """Stop the wake word detector."""
        self.is_listening = False
        if self.is_active:
            self.deactivate()


# Example usage
if __name__ == "__main__":
    def handle_command(command: str) -> bool:
        """Example command handler."""
        print(f"\n>>> Processing: {command}")
        
        # Simple command responses
        if "hora" in command or "time" in command:
            import datetime
            now = datetime.datetime.now().strftime("%H:%M")
            print(f"São {now}")
        elif "nome" in command or "name" in command:
            print("Meu nome é JARVIS!")
        else:
            print("Comando recebido e processado.")
        
        # Continue listening
        return True
    
    # Create detector
    detector = WakeWordDetector(
        wake_words=["jarvis", "hey jarvis", "oi jarvis"],
        timeout=30.0
    )
    
    # Run the loop
    detector.run_loop(handle_command)
