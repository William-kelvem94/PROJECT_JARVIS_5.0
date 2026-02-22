import logging
from typing import Optional
import speech_recognition as sr
from ..utils.config import config

logger = logging.getLogger("JARVIS-LISTENER")

class Listener:
    """The Ears of JARVIS. Listens for speech and converts to text."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.language = config.get("language", "pt-BR")
        
        # Enhanced Sensitivity Settings
        self.recognizer.pause_threshold = 1.0  # Seconds of silence before a phrase is considered complete
        self.recognizer.energy_threshold = 300 # Minimum audio energy to consider for recording
        self.recognizer.dynamic_energy_threshold = True
        
        # Adjust for ambient noise on start with more precision
        with self.microphone as source:
            logger.info("Calibrating microphone for ambient noise (Precision Mode)...")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)

    def listen(self) -> Optional[str]:
        """Listens to the microphone with extended capture limits."""
        with self.microphone as source:
            logger.info("Listening...")
            try:
                # Increased timeout and phrase limit to catch full sentences
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                text = self.recognizer.recognize_google(audio, language=self.language)
                logger.info(f"Yous said: {text}")
                return text
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                logger.debug("Could not understand audio.")
                return None
            except Exception as e:
                logger.error(f"Listener error: {e}")
                return None

# Global Instance
listener = Listener()
