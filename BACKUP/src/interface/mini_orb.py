from PyQt6.QtWidgets import QWidget, QMenu, QApplication
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QAction


class MiniOrb(QWidget):
    """
    Orb flutuante minimalista para controle rápido e feedback visual.
    Substitui o HUD intrusivo quando em modo 'discreto'.
    """

    # Signals
    # Request switch to Dashboard/HUD
    mode_switch_requested = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_orb()
        self.setup_animations()

    def setup_orb(self):
        # Janela sempre no topo, sem bordas, ferramenta
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        # Transparente
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(100, 100)

        # Posição inicial (canto superior direito por padrão, mas salvo depois)
        # self.move(100, 100)

        # Estado visual
        self.state = "idle"  # idle, listening, thinking, speaking, error
        self.drag_position = None

        # Menu de contexto
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def setup_animations(self):
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QVariantAnimation, QTimer

        # Animação de Pulsar (Glow)
        self._glow_radius = 0
        self.pulse_anim = QVariantAnimation(self)
        self.pulse_anim.setStartValue(0)
        self.pulse_anim.setEndValue(20)
        self.pulse_anim.setDuration(2000)
        self.pulse_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.pulse_anim.setLoopCount(-1)
        self.pulse_anim.valueChanged.connect(self._update_glow)
        self.pulse_anim.start()

        # Rotação para estados ativos
        self._rotation = 0
        self.rot_timer = QTimer(self)
        self.rot_timer.timeout.connect(self._rotate)
        self.rot_timer.start(30)

    def _update_glow(self, value):
        self._glow_radius = value
        self.update()

    def _rotate(self):
        if self.state in ["thinking", "listening", "studying"]:
            speed = 5 if self.state == "thinking" else 2
            self._rotation = (self._rotation + speed) % 360
            self.update()

    def paintEvent(self, event):
        """Desenha o orb com efeitos visuais Stark 3.0"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Cores baseadas no estado (Sincronizadas com JarvisTheme)
        from src.interface.theme import JarvisTheme
        
        colors = {
            "idle": JarvisTheme.PRIMARY_CYAN,
            "listening": JarvisTheme.SECONDARY_ORANGE,
            "thinking": JarvisTheme.ACCENT_GOLD,
            "speaking": JarvisTheme.ERROR_RED,
            "error": QColor(100, 100, 100),
            "studying": JarvisTheme.SECONDARY_PURPLE,
        }

        base_color = colors.get(self.state, colors["idle"])
        center = self.rect().center()
        radius = 32

        # 1. Glow AURA (Efeito Glassmorphism Dinâmico)
        from PyQt6.QtGui import QRadialGradient
        from PyQt6.QtCore import QPointF
        
        gradient = QRadialGradient(QPointF(center), radius + self._glow_radius + 10)
        glow_c = QColor(base_color)
        glow_c.setAlpha(int(80 - self._glow_radius * 2))
        gradient.setColorAt(0, glow_c)
        gradient.setColorAt(1, QColor(0, 0, 0, 0))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, radius + self._glow_radius + 10, radius + self._glow_radius + 10)

        # 2. Anel de Rotação (Apenas em estados ativos)
        if self.state in ["listening", "thinking", "studying"]:
            pen = QPen(base_color, 2)
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            
            painter.save()
            painter.translate(center)
            painter.rotate(self._rotation)
            painter.drawEllipse(QPointF(0, 0), radius + 4, radius + 4)
            painter.restore()

        # 3. Núcleo do Orb (Gradiente Stark)
        core_grad = QRadialGradient(QPointF(center), radius)
        core_grad.setColorAt(0, base_color.lighter(130))
        core_grad.setColorAt(0.8, base_color)
        core_grad.setColorAt(1, base_color.darker(150))
        
        painter.setBrush(QBrush(core_grad))
        painter.setPen(QPen(base_color.lighter(150), 1))
        painter.drawEllipse(center, radius, radius)

        # 4. Ícone Central com Glow
        icons = {
            "idle": "⚡",
            "listening": "🎤",
            "thinking": "🧠",
            "speaking": "🗣️",
            "error": "⚠️",
            "studying": "📚",
        }

        icon_text = icons.get(self.state, "⚡")
        painter.setFont(QFont("Segoe UI Emoji", 18))
        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.drawText(
            self.rect(), Qt.AlignmentFlag.AlignCenter, icon_text
        )

    def mousePressEvent(self, event):
        """Inicia arrasto"""
        if event.button() == Qt.MouseButton.LeftButton:
            # PyQt6: use globalPosition() -> QPointF, convert to QPoint
            self.drag_position = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        """Arrasta o orb - permite movimento entre monitores"""
        if self.drag_position is not None:
            # Calcular nova posição usando coordenadas globais
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.move(new_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Finaliza arrasto"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = None
            event.accept()

        # Se foi clique rápido (sem arrasto significativo), alterna listening
        # (Lógica simplificada aqui, idealmente mediria tempo/distância)

    def show_context_menu(self, pos):
        """Menu de contexto com ações rápidas"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #050a10; color: #fff; border: 1px solid #00c3ff; }
            QMenu::item:selected { background-color: #00c3ff; color: #000; }
        """)

        toggle_listen = QAction("🎤 Alternar Escuta", self)
        # Conectar ações reais depois
        menu.addAction(toggle_listen)

        menu.addSeparator()

        from src.interface.window_manager import InterfaceMode

        dash_action = QAction("🎛️ Abrir Painel", self)
        dash_action.triggered.connect(
            lambda: self.mode_switch_requested.emit(InterfaceMode.DASHBOARD)
        )
        menu.addAction(dash_action)

        hud_action = QAction("🎯 Abrir HUD", self)
        hud_action.triggered.connect(
            lambda: self.mode_switch_requested.emit(InterfaceMode.HUD_OVERLAY)
        )
        menu.addAction(hud_action)

        menu.addSeparator()

        quit_action = QAction("🚪 Sair", self)
        app = QApplication.instance()
        if app:
            quit_action.triggered.connect(app.quit)
        menu.addAction(quit_action)

        menu.exec(self.mapToGlobal(pos))

    def set_state(self, state: str):
        """Muda estado visual do orb"""
        self.state = state
        self.update()

    def set_studying(self, topic: str, state: bool):
        """Define estado de estudo"""
        if state:
            self.state = "studying"
            self.setToolTip(f"Estudando: {topic}")
        else:
            self.state = "idle"
            self.setToolTip("JARVIS Mini Orb")
        self.update()
