import asyncio
import edge_tts
from pathlib import Path
from loguru import logger
import os
import time

class TTSEngine:
    def __init__(self):
        self.temp_dir = Path("temp_audio")
        self.temp_dir.mkdir(exist_ok=True)
        self.default_voice = "pt-BR-FranciscaNeural"

    async def speak(self, text: str, voice: str = None) -> str | None:
        try:
            voice = voice or self.default_voice
            communicate = edge_tts.Communicate(text, voice)
            # Nome de arquivo baseado em timestamp para evitar conflitos
            filename = self.temp_dir / f"jarvis_{int(time.time() * 1000)}.mp3"
            await communicate.save(str(filename))
            logger.info(f"🎤 TTS: {text[:70]}...")
            return str(filename)
        except Exception as e:
            logger.error(f"TTS Error: {e}")
            return None

    def cleanup(self):
        """Limpa arquivos temporários antigos (mais de 5 minutos)."""
        now = time.time()
        for f in list(self.temp_dir.glob("*.mp3")):
            try:
                if (now - f.stat().st_mtime) > 300:
                    f.unlink(missing_ok=True)
                    logger.debug(f"Removido áudio temporário: {f.name}")
            except Exception as e:
                logger.error(f"Erro ao limpar {f.name}: {e}")

tts_engine = TTSEngine()
