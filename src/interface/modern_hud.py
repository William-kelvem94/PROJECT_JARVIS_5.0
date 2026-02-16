import sys
import math
import logging
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient

from src.interface.ui_signals import ui_signals
from src.interface.theme import JarvisTheme
from src.utils.config import config

logger = logging.getLogger(__name__)

class ArcReactorWidget(QWidget):
    """
    O CoraÃ§Ã£o do JARVIS: Um Arc Reactor animado via QPainter.
    Pulsante, rotativo e responsivo ao estado do sistema.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(250, 250)
        self.angle = 0
        self.pulse = 0
        self.spark_angle = 0
        self.is_listening = False
        self.boot_mode = False
        self.is_studying = False
        self.status_text = "INITIALIZING..."
        
        # Cores do Tema Unificado
        self.color_cyan = JarvisTheme.get_color_with_alpha(JarvisTheme.PRIMARY_CYAN, JarvisTheme.ALPHA_HIGH)
        self.color_orange = JarvisTheme.get_color_with_alpha(JarvisTheme.SECONDARY_ORANGE, JarvisTheme.ALPHA_HIGH)
        self.color_boot = JarvisTheme.get_color_with_alpha(JarvisTheme.ACCENT_GOLD, JarvisTheme.ALPHA_HIGH)
        self.color_study = QColor(138, 43, 226, 200) # BlueViolet para Hiper-Foco
        self.color_glow = JarvisTheme.get_color_with_alpha(JarvisTheme.PRIMARY_CYAN, JarvisTheme.ALPHA_GLOW)
        
        # Timer de AnimaÃ§Ã£o (60 FPS para fluidez total)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(16)

    def _animate(self):
        # Rotação dinâmica: Boot (6x) > Listening (3x) > Idle (1.5x)
        speed = 6 if self.boot_mode else (3 if self.is_listening else 1.5)
        self.angle = (self.angle + speed) % 360
        self.pulse = (self.pulse + 0.05) % (2 * math.pi)
        self.spark_angle = (self.spark_angle + (speed * 4 if self.is_studying else speed)) % 360
        if self.isVisible():
            self.update()

    def set_boot_state(self, is_booting: bool):
        self.boot_mode = is_booting
        self.update()

    @pyqtSlot(bool)
    def set_listening(self, state: bool):
        self.is_listening = state
        self.update()

    @pyqtSlot(str, bool)
    def set_studying(self, topic: str, state: bool):
        self.is_studying = state
        if state:
            self.status_text = f"STUDYING: {topic.upper()}"
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        center = QPoint(width // 2, height // 2)
        base_radius = 80
        
        # Calcular fator de pulsaÃ§Ã£o (respirando)
        pulse_factor = 1.0 + 0.05 * math.sin(self.pulse)
        radius = base_radius * pulse_factor
        
        if self.boot_mode:
            color = self.color_boot
        elif self.is_studying:
            color = self.color_study
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
        
        # 2. AnÃ©is do Reator
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
        
        # 3. NÃºcleo de Energia (TriÃ¢ngulos/Segmentos centrais)
        painter.save()
        painter.translate(center)
        painter.rotate(-self.angle * 2)
        
        core_pen = QPen(color, 5)
        painter.setPen(core_pen)
        for i in range(3):
            painter.rotate(120)
            painter.drawLine(0, -int(inner_radius*0.8), 0, -int(inner_radius*0.4))
        painter.restore()

        # 3.1 Neural Sparks (Partículas orbitais)
        if self.is_studying or self.is_listening:
            painter.setPen(QPen(Qt.GlobalColor.white, 2))
            painter.setBrush(QBrush(Qt.GlobalColor.white))
            
            spark_radius = inner_radius * 0.9
            num_sparks = 4 if self.is_studying else 2
            
            for i in range(num_sparks):
                s_angle = math.radians(self.spark_angle + (i * 360 / num_sparks))
                sx = center.x() + spark_radius * math.cos(s_angle)
                sy = center.y() + spark_radius * math.sin(s_angle)
                painter.drawEllipse(QPoint(int(sx), int(sy)), 2, 2)

        # 4. Texto de Status (TecnolÃ³gico)
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
        
        # ConfiguraÃ§Ãµes de Janela Futurista
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Central Widget
        self.central_widget = QWidget()
        self._main_layout = QVBoxLayout(self.central_widget)
        self.reactor = ArcReactorWidget()
        self._main_layout.addWidget(self.reactor)
        self.setCentralWidget(self.central_widget)
        
        # Menu de Contexto
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Posicionamento Inicial (Canto Superior Direito)
        self.resize(300, 300)
        self._set_default_position()
        
        # ConexÃ£o de Sinais
        ui_signals.update_status.connect(self.update_status)
        ui_signals.update_listening_state.connect(self.reactor.set_listening)
        ui_signals.update_boot_stage.connect(self.update_boot_ui)
        ui_signals.update_learning_status.connect(self.reactor.set_studying)
        
        # Thread-safe internal signals
        self._state_signal.connect(self._handle_state_update)
        self._log_signal.connect(self._handle_log_event)
        
        logger.info("ðŸ’Ž Modern HUD Stark Edition inicializado.")

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
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.geometry()
            self.move(geometry.width() - self.width() - 20, 20)
        else:
            self.move(100, 100)

    @pyqtSlot(str, int)
    def update_boot_ui(self, message: str, progress: int):
        """Atualiza o visual durante o carregamento pesado"""
        self.reactor.boot_mode = True
        self.reactor.status_text = f"{message.upper()} {progress}%"
        
        # Se terminou, volta ao normal
        if progress >= 100:
            self.reactor.boot_mode = False
            self.reactor.status_text = "SYSTEM ONLINE"
            # Pequeno delay para garantir que o usuÃ¡rio veja o final
            QTimer.singleShot(2000, lambda: self.update_status("SISTEMA ONLINE"))
        
        self.reactor.update()

    @pyqtSlot(str)
    def update_status(self, text: str):
        self.reactor.status_text = text.upper()
        if self.isVisible():
            self.reactor.update()

    def mousePressEvent(self, event):
        """Inicia arrasto do HUD"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            # Garantir que a janela fique no topo durante o arrasto
            self.raise_()

    def mouseMoveEvent(self, event):
        """Arrasta o HUD - permite movimento entre monitores"""
        if hasattr(self, 'drag_pos') and self.drag_pos is not None:
            # Calcular nova posição usando coordenadas globais
            new_pos = event.globalPosition().toPoint() - self.drag_pos
            self.move(new_pos)
            event.accept()

            self.drag_pos = None
            event.accept()

    def show_context_menu(self, pos):
        """Menu de contexto Stark no HUD"""
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction
        
        menu = QMenu(self)
        # Estilo Stark para o Menu
        menu.setStyleSheet("""
            QMenu { background-color: #050a10; color: #fff; border: 1px solid #00c3ff; padding: 5px; }
            QMenu::item { padding: 5px 20px; }
            QMenu::item:selected { background-color: rgba(0, 195, 255, 50); color: #00c3ff; border: 1px solid #00c3ff; border-radius: 4px; }
            QMenu::separator { height: 1px; background: #1f293a; margin: 5px 0; }
        """)
        
        # Ações
        dashboard_action = QAction("🎛️ Abrir Painel de Controle", self)
        dashboard_action.triggered.connect(self._request_dashboard)
        menu.addAction(dashboard_action)

        orb_action = QAction("💫 Alternar para Mini Orb", self)
        orb_action.triggered.connect(self._request_orb)
        menu.addAction(orb_action)
        
        menu.addSeparator()
        
        hide_action = QAction("🙈 Ocultar HUD", self)
        hide_action.triggered.connect(self.hide)
        menu.addAction(hide_action)
        
        menu.addSeparator()

        restart_action = QAction("🔄 Reiniciar Protocolos", self)
        restart_action.triggered.connect(self._restart_protocols)
        menu.addAction(restart_action)
        
        quit_action = QAction("❌ Desativar Sistema", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)
        
        menu.exec(self.mapToGlobal(pos))

    def _request_dashboard(self):
        """Solicita abertura do Dashboard via Signal Hub ou WindowManager"""
        # Como não temos acesso direto ao WM aqui, usamos um hack simples:
        # Tenta encontrar a janela principal ou emitir um sinal global
        try:
            from src.interface.ui_signals import ui_signals
            # Emitir sinal customizado se existisse, ou usar log para trigger
            # Melhor abordagem: WindowManager deve escutar eventos.
            # Por enquanto, vamos fechar o HUD e abrir o dashboard se possível.
            # A arquitetura ideal é o WindowManager gerenciar isso.
<<<<<<< Updated upstream
            pass 
        except: pass
        
=======
            pass
        except Exception:
            pass

>>>>>>> Stashed changes
        # Alternativa: Tentar acessar o WindowManager global se disponível
        try:
            from src.interface.window_manager import get_window_manager, InterfaceMode
            wm = get_window_manager()
            wm.switch_mode(InterfaceMode.DASHBOARD)
        except Exception:
            logger.warning("Falha ao contactar WindowManager do HUD")

    def _request_orb(self):
        try:
            from src.interface.window_manager import get_window_manager, InterfaceMode
            wm = get_window_manager()
            wm.switch_mode(InterfaceMode.ORB)
<<<<<<< Updated upstream
        except: pass
=======
        except Exception:
            pass
>>>>>>> Stashed changes

    def _restart_protocols(self):
        """Simula reinício visual"""
        self.reactor.boot_mode = True
        self.reactor.status_text = "REBOOTING..."
        self.reactor.update()
        QTimer.singleShot(3000, lambda: self.update_boot_ui("SYSTEM READY", 100))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = ModernHUD()
    hud.show()
    sys.exit(app.exec())
