"""
Interface - Targeting System
Highlight de elementos antes de clicar
"""

import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class TargetingSystem:
    """Sistema de targeting visual"""
    
    def __init__(self):
        self.qt_available = False
        self.current_target = None
        
        try:
            from PyQt6.QtGui import QPainter, QColor, QPen
            from PyQt6.QtCore import QRect
            self.QPainter = QPainter
            self.QColor = QColor
            self.QPen = QPen
            self.QRect = QRect
            self.qt_available = True
            logger.info("✅ Targeting System disponível")
        except ImportError:
            logger.warning("⚠️ PyQt6 não disponível")
    
    def highlight_element(self, x: int, y: int, width: int, height: int, color: str = "red"):
        """Desenha retângulo em volta do elemento"""
        if not self.qt_available:
            return
        
        self.current_target = (x, y, width, height)
        logger.info(f"🎯 Targeting: ({x}, {y}) {width}x{height}")
        
        # Desenhar retângulo
        # painter = self.QPainter()
        # painter.setPen(self.QPen(self.QColor(color), 3))
        # painter.drawRect(self.QRect(x, y, width, height))
    
    def draw_path(self, start: Tuple[int, int], end: Tuple[int, int]):
        """Desenha linha até elemento"""
        if not self.qt_available:
            return
        
        logger.debug(f"➡️ Path: {start} → {end}")
        
        # Desenhar linha animada
    
    def show_tooltip(self, x: int, y: int, text: str):
        """Mostra tooltip com info do elemento"""
        if not self.qt_available:
            return
        
        logger.debug(f"💬 Tooltip: {text} em ({x}, {y})")
        
        # Mostrar tooltip
    
    def clear(self):
        """Limpa targeting"""
        self.current_target = None


# Instância global
targeting_system = TargetingSystem()
