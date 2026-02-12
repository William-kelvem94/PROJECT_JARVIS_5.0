import sys
import math
import logging
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient

from src.interface.ui_signals import ui_signals
from src.utils.config import config

logger = logging.getLogger(__name__)

class ArcReactorWidget(QWidget):
    """
    O Coração do JARVIS: Um Arc Reactor animado via QPainter.
    Pulsante, rotativo e responsivo ao estado do sistema.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(250, 250)
        self.angle = 0
        self.pulse = 0
        self.is_listening = False
        self.boot_mode = False
        self.status_text = "INITIALIZING..."
        
        # Cores Stark
        self.color_cyan = QColor(0, 255, 255, 200)      # Neon Principal
        self.color_orange = QColor(255, 140, 0, 200)   # Modo Escuta
        self.color_boot = QColor(255, 215, 0, 200)     # Modo Boot (Dourado Stark)
        self.color_glow = QColor(0, 255, 255, 50)       # Brilho
        
        # Timer de Animação (60 FPS para fluidez total)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(16)

    def _animate(self):
        # Rotação dinâmica: Boot (6x) > Listening (3x) > Idle (1.5x)
        speed = 6 if self.boot_mode else (3 if self.is_listening else 1.5)
        self.angle = (self.angle + speed) % 360
        self.pulse = (self.pulse + 0.05) % (2 * math.pi)
        if self.isVisible():
            self.update()

    def set_boot_state(self, is_booting: bool):
        self.boot_mode = is_booting
        self.update()

    @pyqtSlot(bool)
    def set_listening(self, state: bool):
        self.is_listening = state
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        center = QPoint(width // 2, height // 2)
        base_radius = 80
        
        # Calcular fator de pulsação (respirando)
        pulse_factor = 1.0 + 0.05 * math.sin(self.pulse)
        radius = base_radius * pulse_factor
        
        if self.boot_mode:
            color = self.color_boot
        else:
            color = self.color_orange if self.is_listening else self.color_cyan
        
        # 1. Glow Central
        # Fix: Ensure center is QPointF and radius is float
        from PyQt6.QtCore import QPointF
        gradient = QRadialGradient(QPointF(center), float(radius))
        glow_color = color.lighter(150)
        glow_color.setAlpha(80)
        gradient.setColorAt(0, glow_color)
        gradient.setColorAt(1, QColor(0,0,0,0))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, int(radius * 1.2), int(radius * 1.2))
        
        # 2. Anéis do Reator
        pen = QPen(color, 3)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Anel Externo Segmentado
        for i in range(0, 360, 45):
            painter.drawArc(
                int(center.x() - radius), 
                int(center.y() - radius), 
                int(radius * 2), 
                int(radius * 2), 
                int((i + self.angle) * 16), 
                int(30 * 16)
            )

        # Anel Interno Pulsante
        inner_radius = radius * 0.7
        painter.drawEllipse(center, int(inner_radius), int(inner_radius))
        
        # 3. Núcleo de Energia (Triângulos/Segmentos centrais)
        painter.save()
        painter.translate(center)
        painter.rotate(-self.angle * 2)
        
        core_pen = QPen(color, 5)
        painter.setPen(core_pen)
        for i in range(3):
            painter.rotate(120)
            painter.drawLine(0, -int(inner_radius*0.8), 0, -int(inner_radius*0.4))
        painter.restore()

        # 4. Texto de Status (Tecnológico)
        painter.setPen(color)
        painter.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        painter.drawText(
            self.rect(), 
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, 
            self.status_text
        )

class ModernHUD(QMainWindow):
    """
    Janela Principal do HUD: Transparente e Always-on-top.
    """
    
    status_changed = pyqtSignal(str) # Signal for status updates

    def __init__(self):
        super().__init__()
        
        # Configurações de Janela Futurista
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Central Widget
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.reactor = ArcReactorWidget()
        self.layout.addWidget(self.reactor)
        self.setCentralWidget(self.central_widget)
        
        # Posicionamento Inicial (Canto Superior Direito)
        self.resize(300, 300)
        self._set_default_position()
        
        # Conexão de Sinais
        ui_signals.update_status.connect(self.update_status)
        ui_signals.update_listening_state.connect(self.reactor.set_listening)
        ui_signals.update_boot_stage.connect(self.update_boot_ui)
        
        # Thread-safe internal signals
        self._state_signal.connect(self._handle_state_update)
        self._log_signal.connect(self._handle_log_event)
        
        logger.info("💎 Modern HUD Stark Edition inicializado.")

    # Internal Signals for thread-safe cross-thread calls
    _state_signal = pyqtSignal(str)
    _log_signal = pyqtSignal(str)

    # API Compatibility with FallbackHUD
    def update_state(self, state: str):
        """Thread-safe state update"""
        self._state_signal.emit(state)

    def log_event(self, message: str):
        """Thread-safe log event"""
        self._log_signal.emit(message)

    def show_response(self, text: str):
        """Thread-safe response display (using log for now)"""
        self._log_signal.emit(f"AI: {text}")

    @pyqtSlot(str)
    def _handle_state_update(self, state: str):
        if state == "loading_model":
            self.reactor.status_text = "LOADING CLOUD..."
            self.reactor.update()
        elif state == "listening":
            self.reactor.set_listening(True)
        elif state == "idle":
            self.reactor.set_listening(False)
            self.reactor.status_text = "ONLINE"
            self.reactor.update()

    @pyqtSlot(str)
    def _handle_log_event(self, message: str):
        # Temporary: route log events to status text for visibility
        self.reactor.status_text = message.upper()[:20] # Truncate to fit
        self.reactor.update()

    def _set_default_position(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.width() - 20, 20)

    @pyqtSlot(str, int)
    def update_boot_ui(self, message: str, progress: int):
        """Atualiza o visual durante o carregamento pesado"""
        self.reactor.boot_mode = True
        self.reactor.status_text = f"{message.upper()} {progress}%"
        
        # Se terminou, volta ao normal
        if progress >= 100:
            self.reactor.boot_mode = False
            self.reactor.status_text = "SYSTEM ONLINE"
            # Pequeno delay para garantir que o usuário veja o final
            QTimer.singleShot(2000, lambda: self.update_status("SISTEMA ONLINE"))
        
        self.reactor.update()

    @pyqtSlot(str)
    def update_status(self, text: str):
        self.reactor.status_text = text.upper()
        if self.isVisible():
            self.reactor.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = ModernHUD()
    hud.show()
    sys.exit(app.exec())
