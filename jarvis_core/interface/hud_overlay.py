"""
Interface - HUD Overlay
Interface holográfica transparente
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

class HUDOverlay:
    """Overlay transparente estilo Iron Man"""
    
    def __init__(self, transparency: float = 0.9):
        self.transparency = transparency
        self.window = None
        self.qt_available = False
        
        try:
            from PyQt6.QtWidgets import QMainWindow, QApplication
            from PyQt6.QtCore import Qt
            from PyQt6.QtGui import QColor
            
            self.qt_available = True
            logger.info("✅ PyQt6 disponível")
            
            # Criar aplicação Qt (se não existir)
            import sys
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
            else:
                self.app = QApplication.instance()
            
            # Criar janela
            self.window = QMainWindow()
            self._setup_window()
            
        except ImportError:
            logger.warning("⚠️ PyQt6 não instalado. HUD desabilitado.")
    
    def _setup_window(self):
        """Configura janela transparente"""
        if not self.window:
            return
        
        from PyQt6.QtCore import Qt
        
        # Configurar flags
        self.window.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Transparência
        self.window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Tamanho fullscreen
        self.window.showFullScreen()
        
        # Pass-through (mouse atravessa)
        self.window.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        logger.info("✅ HUD configurado")
    
    def show(self):
        """Mostra HUD"""
        if self.window:
            self.window.show()
            logger.info("👁️ HUD visível")
    
    def hide(self):
        """Esconde HUD"""
        if self.window:
            self.window.hide()
            logger.info("🙈 HUD oculto")
    
    def set_passthrough(self, enabled: bool):
        """Ativa/desativa pass-through"""
        if not self.window:
            return
        
        from PyQt6.QtCore import Qt
        
        if enabled:
            self.window.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        else:
            self.window.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)


# Instância global
hud_overlay = None

def get_hud(transparency: float = 0.9) -> Optional[HUDOverlay]:
    """Retorna instância do HUD"""
    global hud_overlay
    
    if not hud_overlay:
        hud_overlay = HUDOverlay(transparency)
    
    return hud_overlay if hud_overlay.qt_available else None
