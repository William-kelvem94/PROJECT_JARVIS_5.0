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
        self.default_voice = "pt-BR-FranciscaNeural"  # voz feminina natural e elegante

    async def speak(self, text: str, voice: str = None, speed: float = 1.0) -> str:
        """Gera áudio via Edge TTS e retorna o caminho do arquivo MP3."""
        try:
            voice = voice or self.default_voice
            rate = f"+{int((speed-1)*100)}%" if speed >= 1 else f"-{int((1-speed)*100)}%"
            
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            
            # Nome de arquivo baseado em timestamp para evitar conflitos
            filename = self.temp_dir / f"jarvis_{int(time.time() * 1000)}.mp3"
            await communicate.save(str(filename))
            
            logger.info(f"🎤 TTS gerado: {text[:60]}...")
            return str(filename)
            
        except Exception as e:
            logger.error(f"TTS Error: {e}")
            return None

    def cleanup(self):
        """Limpa arquivos temporários antigos (mais de 5 minutos)."""
        now = time.time()
        for f in self.temp_dir.glob("*.mp3"):
            try:
                if (now - f.stat().st_mtime) > 300:
                    f.unlink()
                    logger.debug(f"Removido áudio temporário: {f.name}")
            except Exception as e:
                logger.error(f"Erro ao limpar {f.name}: {e}")

tts_engine = TTSEngine()
