#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS HUD - Interface Transparente Estilo Iron Man
Overlay click-through com reator pulsante

This file now serves as a compatibility wrapper for the ModernHUD
For the enhanced version, see modern_hud.py
"""

import sys
import math
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont

# Import the modern HUD as default
try:
    from .modern_hud import ModernHUD as JarvisHUD
    from .modern_hud import ArcReactorWidget as ReactorWidget
    print("âœ… Using enhanced Modern HUD")
except ImportError:
    print("âš ï¸ Modern HUD not available, using legacy HUD")
    
    # Legacy HUD implementation follows...
    class ReactorWidget(QWidget):
        """Widget do Reator Arc - NÃºcleo Visual do JARVIS"""
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.pulse = 0
            self.growing = True
            self.status_color = QColor(0, 255, 255, 200)  # Ciano
            self.status_text = "ONLINE"
            
            # AnimaÃ§Ã£o suave (60 FPS)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.animate)
            self.timer.start(16)  # ~60 FPS

        def animate(self):
            """AnimaÃ§Ã£o de pulsaÃ§Ã£o do reator"""
            if self.growing:
                self.pulse += 1
                if self.pulse >= 20:
                    self.growing = False
            else:
                self.pulse -= 1
                if self.pulse <= 0:
                    self.growing = True
            self.update()

        def set_status(self, status):
            """
            Atualiza status visual do reator
            
            Args:
                status: 'listening', 'thinking', 'speaking', 'error', 'idle'
            """
            if status == "listening":
                self.status_color = QColor(0, 255, 0, 200)  # Verde
                self.status_text = "LISTENING"
            elif status == "thinking":
                self.status_color = QColor(0, 0, 255, 200)  # Azul
                self.status_text = "THINKING"
            elif status == "speaking":
                self.status_color = QColor(255, 165, 0, 200)  # Laranja
                self.status_text = "SPEAKING"
            elif status == "error":
                self.status_color = QColor(255, 0, 0, 200)  # Vermelho
                self.status_text = "ERROR"
            elif status == "idle":
                self.status_color = QColor(0, 255, 255, 200)  # Ciano
                self.status_text = "IDLE"
            else:
                self.status_color = QColor(0, 255, 255, 200)
                self.status_text = "ONLINE"
            
            self.update()

        def set_response(self, text):
            """Atualiza o texto da resposta no HUD"""
            self.response_text = text
            self.update()

        def paintEvent(self, event):
            """Desenha o reator na tela"""
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Centro do reator (canto inferior direito)
            center_x = self.width() - 150
            center_y = self.height() - 150
            
            # Desenhar o Reator (Anel Externo Pulsante)
            painter.setPen(QPen(self.status_color, 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            radius = 50 + (self.pulse * 0.5)
            painter.drawEllipse(
                int(center_x - radius),
                int(center_y - radius),
                int(radius * 2),
                int(radius * 2)
            )
            
            # Anel IntermediÃ¡rio
            painter.setPen(QPen(self.status_color, 2))
            inner_radius = 35
            painter.drawEllipse(
                int(center_x - inner_radius),
                int(center_y - inner_radius),
                int(inner_radius * 2),
                int(inner_radius * 2)
            )
            
            # NÃºcleo SÃ³lido
            painter.setBrush(QBrush(self.status_color))
            painter.drawEllipse(
                int(center_x - 10),
                int(center_y - 10),
                20,
                20
            )
            
            # Texto de Status
            painter.setPen(QPen(self.status_color, 2))
            painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
            painter.drawText(
                int(center_x - 60),
                int(center_y + 80),
                self.status_text
            )

            # Texto da Resposta (Se houver)
            if hasattr(self, 'response_text') and self.response_text:
                painter.setPen(QPen(QColor(0, 255, 255, 220), 1))
                painter.setFont(QFont("Consolas", 14, QFont.Weight.Normal))
                
                # Caixa de texto centralizada na parte inferior
                rect_x = 100
                rect_y = self.height() - 250
                rect_w = self.width() - 350
                rect_h = 100
                
                painter.drawText(
                    rect_x, rect_y, rect_w, rect_h,
                    Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
                    self.response_text
                )


    class JarvisHUD(QMainWindow):
        """HUD Principal - Overlay Transparente"""
        
        # Sinais para comunicaÃ§Ã£o thread-safe
        status_changed = pyqtSignal(str)
        response_ready = pyqtSignal(str)
        
        def __init__(self):
            super().__init__()
            
            # ConfiguraÃ§Ã£o de TransparÃªncia Total e Click-Through
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint | 
                Qt.WindowType.WindowStaysOnTopHint | 
                Qt.WindowType.Tool
            )
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)  # Click-through!
            
            # Tela cheia
            screen = QApplication.primaryScreen().geometry()
            self.setGeometry(0, 0, screen.width(), screen.height())
            
            # Widget do reator
            self.reactor = ReactorWidget(self)
            self.reactor.resize(screen.width(), screen.height())
            
            # Conectar sinais
            self.status_changed.connect(self.reactor.set_status)
            self.response_ready.connect(self.reactor.set_response)
            
            self.show()

        def update_state(self, state_text):
            """Atualiza estado do HUD (thread-safe)"""
            self.status_changed.emit(state_text)

        def show_response(self, text):
            """Exibe texto de resposta no HUD (thread-safe)"""
            self.response_ready.emit(text)


# Para testar sozinho: python src/interface/hud.py
if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = JarvisHUD()
    
    # Teste de animaÃ§Ã£o
    import time
    states = ["listening", "thinking", "speaking", "idle"]
    
    def cycle_states():
        for state in states:
            hud.update_state(state)
            QApplication.processEvents()
            time.sleep(2)
    
    # Timer para testar estados
    test_timer = QTimer()
    test_timer.timeout.connect(cycle_states)
    test_timer.start(8000)
    
    sys.exit(app.exec())
