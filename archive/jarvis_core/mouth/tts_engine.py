"""
Mouth - TTS Engine
Text-to-Speech com Edge-TTS e XTTS
"""

import logging
import asyncio
from pathlib import Path
from typing import Optional
import pygame

logger = logging.getLogger(__name__)

class TTSEngine:
    """Motor de Text-to-Speech"""
    
    def __init__(self, engine: str = "edge", voice: str = "pt-BR-FranciscaNeural"):
        self.engine = engine
        self.voice = voice
        self.temp_dir = Path("data/temp")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar pygame mixer
        try:
            pygame.mixer.init()
            self.mixer_ready = True
        except:
            logger.warning("⚠️ Pygame mixer não disponível")
            self.mixer_ready = False
        
        logger.info(f"✅ TTS Engine: {engine} ({voice})")
    
    async def speak(self, text: str, async_mode: bool = False) -> bool:
        """Fala texto"""
        if self.engine == "edge":
            return await self._speak_edge(text, async_mode)
        elif self.engine == "xtts":
            return await self._speak_xtts(text, async_mode)
        else:
            logger.error(f"❌ Engine desconhecido: {self.engine}")
            return False
    
    async def _speak_edge(self, text: str, async_mode: bool) -> bool:
        """Edge-TTS (Microsoft)"""
        try:
            import edge_tts
            
            output_file = self.temp_dir / "tts_output.mp3"
            
            # Gerar áudio
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(str(output_file))
            
            # Reproduzir
            if self.mixer_ready:
                pygame.mixer.music.load(str(output_file))
                pygame.mixer.music.play()
                
                if not async_mode:
                    # Aguardar terminar
                    while pygame.mixer.music.get_busy():
                        await asyncio.sleep(0.1)
                
                return True
            else:
                logger.warning("⚠️ Mixer não disponível. Áudio salvo em: {output_file}")
                return False
                
        except ImportError:
            logger.error("❌ edge-tts não instalado")
            return False
        except Exception as e:
            logger.error(f"❌ Erro no TTS: {e}")
            return False
    
    async def _speak_xtts(self, text: str, async_mode: bool) -> bool:
        """XTTS-v2 (Coqui)"""
        try:
            from TTS.api import TTS
            
            # Lazy loading do modelo
            if not hasattr(self, '_xtts_model'):
                logger.info("📥 Carregando XTTS-v2...")
                self._xtts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            
            output_file = self.temp_dir / "tts_output.wav"
            
            # Gerar áudio
            self._xtts_model.tts_to_file(
                text=text,
                file_path=str(output_file),
                language="pt"
            )
            
            # Reproduzir
            if self.mixer_ready:
                pygame.mixer.music.load(str(output_file))
                pygame.mixer.music.play()
                
                if not async_mode:
                    while pygame.mixer.music.get_busy():
                        await asyncio.sleep(0.1)
                
                return True
            else:
                return False
                
        except ImportError:
            logger.error("❌ TTS (Coqui) não instalado")
            return False
        except Exception as e:
            logger.error(f"❌ Erro no XTTS: {e}")
            return False
    
    def stop(self):
        """Para reprodução"""
        if self.mixer_ready:
            pygame.mixer.music.stop()
    
    def is_speaking(self) -> bool:
        """Verifica se está falando"""
        if self.mixer_ready:
            return pygame.mixer.music.get_busy()
        return False


# Instância global
tts_engine = None

def get_tts(engine: str = "edge", voice: str = "pt-BR-FranciscaNeural") -> TTSEngine:
    """Retorna instância do TTS"""
    global tts_engine
    
    if not tts_engine:
        tts_engine = TTSEngine(engine, voice)
    
    return tts_engine
