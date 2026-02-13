# ============================================================================
# JARVIS SINGULARITY - Draggable HUD Component
# ============================================================================
# HUD moderno, arrastÃ¡vel, com suporte multi-monitor
# ============================================================================

import json
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                             QGraphicsOpacityEffect, QApplication)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QFont

class DraggableHUD(QWidget):
    """
    HUD arrastÃ¡vel com glassmorphism e animaÃ§Ãµes.
    
    FEATURES:
    - ArrastÃ¡vel com mouse
    - Salva posiÃ§Ã£o entre sessÃµes
    - Suporte multi-monitor
    - AnimaÃ§Ãµes de estado
    - Glassmorphism design
    """
    
    def __init__(self):
        super().__init__()
        
        # =====================================================================
        # WINDOW SETUP
        # =====================================================================
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool  # NÃ£o aparece na taskbar
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Drag support
        self._drag_position = None
        self._is_dragging = False
        
        # =====================================================================
        # LAYOUT
        # =====================================================================
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # ---------------------------------------------------------------------
        # DRAG HANDLE
        # ---------------------------------------------------------------------
        drag_handle = QLabel("â‹®â‹® JARVIS â‹®â‹®")
        drag_handle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drag_handle.setStyleSheet("""
            QLabel {
                color: rgba(100, 200, 255, 0.6);
                font-size: 10px;
                font-weight: bold;
                padding: 5px;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 8px;
                letter-spacing: 2px;
            }
            QLabel:hover {
                color: rgba(100, 200, 255, 1.0);
                background: rgba(0, 0, 0, 0.5);
            }
        """)
        drag_handle.setCursor(Qt.CursorShape.SizeAllCursor)
        layout.addWidget(drag_handle)
        
        # ---------------------------------------------------------------------
        # REACTOR CORE
        # ---------------------------------------------------------------------
        reactor_container = QWidget()
        reactor_layout = QHBoxLayout(reactor_container)
        reactor_layout.setContentsMargins(0, 0, 0, 0)
        reactor_layout.addStretch()
        
        self.reactor = QLabel("â—‰")
        self.reactor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reactor.setStyleSheet("""
            QLabel {
                color: #64C8FF;
                font-size: 80px;
                font-weight: bold;
                text-shadow: 0 0 30px rgba(100, 200, 255, 0.8);
            }
        """)
        reactor_layout.addWidget(self.reactor)
        reactor_layout.addStretch()
        layout.addWidget(reactor_container)
        
        # ---------------------------------------------------------------------
        # STATUS TEXT
        # ---------------------------------------------------------------------
        self.status_label = QLabel("IDLE")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 3px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # ---------------------------------------------------------------------
        # RESPONSE TEXT
        # ---------------------------------------------------------------------
        self.response_label = QLabel("")
        self.response_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.response_label.setWordWrap(True)
        self.response_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 12px;
                padding: 10px;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 8px;
            }
        """)
        self.response_label.setMaximumWidth(400)
        layout.addWidget(self.response_label)
        
        # ---------------------------------------------------------------------
        # CONTAINER PRINCIPAL
        # ---------------------------------------------------------------------
        container = QWidget()
        container.setLayout(layout)
        container.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(10, 20, 40, 0.85),
                    stop:1 rgba(20, 40, 80, 0.85)
                );
                border: 2px solid rgba(100, 200, 255, 0.3);
                border-radius: 20px;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        
        # =====================================================================
        # SIZE & POSITION
        # =====================================================================
        self.setFixedSize(450, 350)
        self._load_position()
        
        # =====================================================================
        # ANIMATIONS
        # =====================================================================
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self._pulse_reactor)
        self.pulse_direction = 1
        self.pulse_value = 1.0
        
        self.update_state("idle")
    
    # =========================================================================
    # DRAG FUNCTIONALITY
    # =========================================================================
    
    def mousePressEvent(self, event):
        """Inicia arrasto"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._is_dragging = True
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Move janela durante arrasto"""
        if self._is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Finaliza arrasto e salva posiÃ§Ã£o"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            self._save_position()
            event.accept()
    
    def _save_position(self):
        """Salva posiÃ§Ã£o atual"""
        try:
            pos_file = Path("data/hud_position.json")
            pos_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(pos_file, 'w') as f:
                json.dump({'x': self.x(), 'y': self.y()}, f)
        except Exception as e:
            print(f"âš ï¸ Erro ao salvar posiÃ§Ã£o: {e}")
    
    def _load_position(self):
        """Carrega posiÃ§Ã£o salva ou centraliza"""
        try:
            pos_file = Path("data/hud_position.json")
            if pos_file.exists():
                with open(pos_file, 'r') as f:
                    pos = json.load(f)
                
                # Verificar se estÃ¡ em tela vÃ¡lida
                screens = QApplication.screens()
                for screen in screens:
                    geom = screen.geometry()
                    if (geom.x() <= pos['x'] <= geom.x() + geom.width() and
                        geom.y() <= pos['y'] <= geom.y() + geom.height()):
                        self.move(pos['x'], pos['y'])
                        return
        except:
            pass
        
        # Fallback: centralizar
        screen = self.screen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
    
    # =========================================================================
    # STATE MANAGEMENT
    # =========================================================================
    
    def update_state(self, state: str):
        """Atualiza estado visual"""
        states = {
            "idle": {"color": "#808080", "text": "IDLE", "pulse": True},
            "listening": {"color": "#00ff88", "text": "LISTENING", "pulse": False},
            "thinking": {"color": "#00d4ff", "text": "THINKING", "pulse": True},
            "speaking": {"color": "#00ff88", "text": "SPEAKING", "pulse": False},
            "error": {"color": "#ff3366", "text": "ERROR", "pulse": True}
        }
        
        config = states.get(state, states["idle"])
        
        # Update reactor
        self.reactor.setStyleSheet(f"""
            QLabel {{
                color: {config['color']};
                font-size: 80px;
                font-weight: bold;
                text-shadow: 0 0 30px {config['color']};
            }}
        """)
        
        # Update status
        self.status_label.setText(config['text'])
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {config['color']};
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 3px;
                padding: 8px;
                text-shadow: 0 0 10px {config['color']};
            }}
        """)
        
        # Animation
        if config['pulse']:
            self.pulse_timer.start(50)
        else:
            self.pulse_timer.stop()
            self.pulse_value = 1.0
    
    def _pulse_reactor(self):
        """AnimaÃ§Ã£o de pulsaÃ§Ã£o"""
        self.pulse_value += 0.02 * self.pulse_direction
        if self.pulse_value >= 1.0 or self.pulse_value <= 0.5:
            self.pulse_direction *= -1
        
        opacity = max(0.5, min(1.0, self.pulse_value))
        self.reactor.setStyleSheet(self.reactor.styleSheet() + f"opacity: {opacity};")
    
    def show_response(self, response: str):
        """Mostra resposta"""
        display = response[:200] + "..." if len(response) > 200 else response
        self.response_label.setText(f"ðŸ’¬ {display}")
    
    def show_error(self, error: str):
        """Mostra erro"""
        self.update_state("error")
        self.response_label.setText(f"âŒ {error}")
