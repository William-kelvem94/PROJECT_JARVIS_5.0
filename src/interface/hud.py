"""
JARVIS HUD - Interface Transparente Estilo Iron Man
Overlay click-through com reator pulsante
"""

import sys
import math
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont

class ReactorWidget(QWidget):
    """Widget do Reator Arc - Núcleo Visual do JARVIS"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pulse = 0
        self.growing = True
        self.status_color = QColor(0, 255, 255, 200)  # Ciano
        self.status_text = "ONLINE"
        
        # Animação suave (60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # ~60 FPS

    def animate(self):
        """Animação de pulsação do reator"""
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

    def paintEvent(self, event):
        """Desenha o reator na tela"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Centro da tela (canto inferior direito)
        center_x = self.width() - 100
        center_y = self.height() - 100
        
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
        
        # Anel Intermediário
        painter.setPen(QPen(self.status_color, 2))
        inner_radius = 35
        painter.drawEllipse(
            int(center_x - inner_radius),
            int(center_y - inner_radius),
            int(inner_radius * 2),
            int(inner_radius * 2)
        )
        
        # Núcleo Sólido
        painter.setBrush(QBrush(self.status_color))
        painter.drawEllipse(
            int(center_x - 10),
            int(center_y - 10),
            20,
            20
        )
        
        # Texto de Status
        painter.setPen(QPen(self.status_color, 1))
        painter.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        painter.drawText(
            int(center_x - 50),
            int(center_y + 80),
            self.status_text
        )


class JarvisHUD(QMainWindow):
    """HUD Principal - Overlay Transparente"""
    
    # Sinais para comunicação thread-safe
    status_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # Configuração de Transparência Total e Click-Through
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
        
        # Conectar sinal
        self.status_changed.connect(self.reactor.set_status)
        
        self.show()

    def update_state(self, state_text):
        """
        Atualiza estado do HUD (thread-safe)
        
        Args:
            state_text: 'listening', 'thinking', 'speaking', 'error', 'idle'
        """
        self.status_changed.emit(state_text)


# Para testar sozinho: python src/interface/hud.py
if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = JarvisHUD()
    
    # Teste de animação
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
