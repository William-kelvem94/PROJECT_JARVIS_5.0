"""
Mouth - Barge-in System
Permite interrupção natural da fala
"""

import logging
import asyncio
from typing import Callable, Optional

logger = logging.getLogger(__name__)

class BargeIn:
    """Sistema de interrupção de fala"""
    
    def __init__(self, tts_engine, vad_callback: Optional[Callable] = None):
        self.tts = tts_engine
        self.vad_callback = vad_callback
        self.speaking = False
        self.interrupted = False
    
    async def speak_with_interrupt(self, text: str) -> bool:
        """Fala com possibilidade de interrupção"""
        self.speaking = True
        self.interrupted = False
        
        # Task 1: TTS falando
        speak_task = asyncio.create_task(self.tts.speak(text, async_mode=True))
        
        # Task 2: Monitorar interrupção
        monitor_task = asyncio.create_task(self._monitor_interruption())
        
        try:
            # Aguardar qualquer uma completar
            done, pending = await asyncio.wait(
                [speak_task, monitor_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancelar tasks pendentes
            for task in pending:
                task.cancel()
            
            if self.interrupted:
                logger.info("🛑 Fala interrompida pelo usuário")
                self.tts.stop()
                return False
            else:
                logger.debug("✅ Fala completa")
                return True
                
        finally:
            self.speaking = False
    
    async def _monitor_interruption(self):
        """Monitora se usuário interrompeu"""
        while self.speaking and not self.interrupted:
            # Verificar VAD
            if self.vad_callback and self.vad_callback():
                logger.info("👂 Voz detectada durante fala")
                self.interrupted = True
                break
            
            await asyncio.sleep(0.1)
    
    def stop_speaking(self):
        """Para fala imediatamente"""
        self.interrupted = True
        self.tts.stop()
