import logging
import asyncio
import os
import tempfile
import pygame
import pyttsx3
from ..utils.config import config

logger = logging.getLogger("JARVIS-SPEAKER")

class Speaker:
    """The Voice of JARVIS. Premium (Edge) with local fallback (pyttsx3)."""
    
    def __init__(self):
        self.voice = config.get("tts_voice", "pt-BR-AntonioNeural")
        # Initialize fallback
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 170)
        
        # Pygame for mp3 playback
        pygame.mixer.init()

    def speak(self, text: str):
        """Speaks the provided text."""
        logger.info(f"Speaking: {text}")
        
        # Try Premium Edge TTS (online)
        if config.get("voice_enabled"):
            try:
                asyncio.run(self._speak_edge(text))
            except Exception as e:
                logger.warning(f"Edge TTS failed, using fallback: {e}")
                self._speak_fallback(text)
        else:
            print(f"[JARVIS]: {text}")

    async def _speak_edge(self, text: str):
        import edge_tts
        
        communicate = edge_tts.Communicate(text, self.voice)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            await communicate.save(tmp.name)
            tmp_path = tmp.name
        
        try:
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
            pygame.mixer.music.unload()
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def _speak_fallback(self, text: str):
        self.engine.say(text)
        self.engine.runAndWait()

# Global Instance
speaker = Speaker()
