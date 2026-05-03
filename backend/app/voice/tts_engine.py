import asyncio
import edge_tts
from pathlib import Path
from loguru import logger
import os
import time

try:
    import pygame
    pygame.mixer.init()
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
    logger.warning("pygame não instalado. Áudio local desativado. Instale com: pip install pygame")

class TTSEngine:
    def __init__(self):
        self.temp_dir = Path("temp_audio")
        self.temp_dir.mkdir(exist_ok=True)
        # Masculino, técnico, estilo JARVIS
        self.default_voice = "pt-BR-AntônioNeural"

    async def speak(self, text: str, voice: str = None, play_local: bool = True) -> str | None:
        try:
            voice = voice or self.default_voice
            communicate = edge_tts.Communicate(text, voice)
            filename = self.temp_dir / f"jarvis_{int(time.time() * 1000)}.mp3"
            await communicate.save(str(filename))
            logger.info(f"🎤 TTS Gerado: {text[:70]}...")
            
            if play_local and HAS_PYGAME:
                self.play_audio(str(filename))
                
            return str(filename)
        except Exception as e:
            logger.error(f"TTS Error: {e}")
            return None

    def play_audio(self, file_path: str):
        """Reproduz o arquivo de áudio de forma bloqueante para sincronia ou background dependendo da thread."""
        if not HAS_PYGAME: return
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            logger.error(f"Erro ao tocar áudio local: {e}")

    def cleanup(self):
        """Limpa arquivos temporários antigos (mais de 5 minutos)."""
        now = time.time()
        for f in list(self.temp_dir.glob("*.mp3")):
            try:
                if (now - f.stat().st_mtime) > 300:
                    # Garantir que o mixer soltou o arquivo antes de deletar
                    if HAS_PYGAME and pygame.mixer.music.get_busy():
                        continue
                    f.unlink(missing_ok=True)
            except Exception as e:
                pass

tts_engine = TTSEngine()
