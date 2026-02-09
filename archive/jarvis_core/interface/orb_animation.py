"""
Interface - Orb Animation
Animação central do HUD
"""

import logging
import math
from typing import Optional

logger = logging.getLogger(__name__)

class OrbAnimation:
    """Animação do orb central"""
    
    def __init__(self):
        self.qt_available = False
        self.timer = None
        self.animation_state = "idle"
        self.frame = 0
        
        try:
            from PyQt6.QtCore import QTimer
            self.QTimer = QTimer
            self.qt_available = True
            logger.info("✅ Orb Animation disponível")
        except ImportError:
            logger.warning("⚠️ PyQt6 não disponível")
    
    def animate_idle(self):
        """Respiração suave"""
        if not self.qt_available:
            return
        
        self.animation_state = "idle"
        logger.debug("💙 Animação: Idle (respiração)")
        
        # Implementar animação de respiração
        # Usar QTimer para atualizar frame
    
    def animate_listening(self, amplitude: float = 0.5):
        """Pulsa com voz"""
        if not self.qt_available:
            return
        
        self.animation_state = "listening"
        logger.debug(f"👂 Animação: Listening (amplitude: {amplitude})")
        
        # Pulsar baseado na amplitude
    
    def animate_thinking(self):
        """Gira com partículas"""
        if not self.qt_available:
            return
        
        self.animation_state = "thinking"
        logger.debug("🧠 Animação: Thinking (girando)")
        
        # Rotação com partículas
    
    def animate_speaking(self, audio_level: float = 0.5):
        """Sincronia labial visual"""
        if not self.qt_available:
            return
        
        self.animation_state = "speaking"
        logger.debug(f"🗣️ Animação: Speaking (level: {audio_level})")
        
        # Animar baseado no nível de áudio
    
    def stop(self):
        """Para animação"""
        if self.timer:
            self.timer.stop()
        
        self.animation_state = "idle"


# Instância global
orb_animation = OrbAnimation()
