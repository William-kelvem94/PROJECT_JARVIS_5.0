from PyQt6.QtWidgets import QWidget, QMenu, QApplication
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QAction


class MiniOrb(QWidget):
    """
    Orb flutuante minimalista para controle rápido e feedback visual.
    Substitui o HUD intrusivo quando em modo 'discreto'.
    """

    # Signals
    mode_switch_requested = pyqtSignal(object)  # Request switch to Dashboard/HUD

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
        # Placeholder para animações futuras (QPropertyAnimation)
        pass

    def paintEvent(self, event):
        """Desenha o orb com efeitos visuais"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Cores baseadas no estado
        colors = {
            "idle": QColor(0, 123, 255, 180),  # Azul Stark (transparente)
            "listening": QColor(40, 167, 69, 220),  # Verde
            "thinking": QColor(255, 193, 7, 200),  # Amarelo
            "speaking": QColor(220, 53, 69, 200),  # Vermelho
            "error": QColor(108, 117, 125, 200),  # Cinza
            "studying": QColor(138, 43, 226, 200),  # Roxo (Hiper-Foco)
        }

        color = colors.get(self.state, colors["idle"])

        # Centro do widget
        center = self.rect().center()
        radius = 35

        # Halo externo (Glow)
        glow_color = QColor(color)
        glow_color.setAlpha(50)
        painter.setBrush(QBrush(glow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, radius + 10, radius + 10)

        # Desenha orb principal (Núcleo)
        painter.setBrush(QBrush(color))
        painter.drawEllipse(center, radius, radius)

        # Anel de status (se ativo)
        if self.state in ["listening", "thinking"]:
            pen = QPen(Qt.GlobalColor.white, 2)
            pen.setStyle(Qt.PenStyle.DotLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, radius - 5, radius - 5)

        # Ícone interno baseado no estado
        icons = {
            "idle": "⚡",
            "listening": "🎤",
            "thinking": "🧠",
            "speaking": "🗣️",
            "error": "⚠️",
            "studying": "📚",
        }

        painter.setFont(QFont("Segoe UI Emoji", 20))
        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.drawText(
            self.rect(), Qt.AlignmentFlag.AlignCenter, icons.get(self.state, "âš¡")
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
