#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Modern Enhanced HUD
==================================================
Features:
- Draggable and resizable
- Glassmorphism design with smooth animations
- Multi-monitor support with position persistence
- Fluid 60 FPS animations
- Responsive to different screen sizes
- Keyboard shortcuts
- Modern Iron Man inspired aesthetics
"""

import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QGraphicsOpacityEffect, QApplication, QPushButton, QSizeGrip
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QPointF,
    QSize, pyqtSignal, QParallelAnimationGroup, QSequentialAnimationGroup,
    QRectF
)
from PyQt6.QtGui import (
    QFont, QPainter, QColor, QPen, QBrush, QLinearGradient,
    QRadialGradient, QKeySequence, QShortcut, QPolygonF, QPainterPath,
    QRegion, QIcon, QAction, QColorTransform, QImage, QTransform
)
import math
import time
import random


class ModernReactorCore(QWidget):
    """
    Animated reactor core with smooth pulsing effects
    60 FPS animations with multiple layers
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        
        # Animation state
        self.pulse_value = 0
        self.rotation = 0
        self.status = "idle"
        
        # Orbital Data
        self.sync_val = 0.0
        self.nucleo_val = 0.0
        
        # Color schemes for different states - Elite HSL punchy colors
        self.colors = {
            "idle": QColor(0, 180, 255, 180),      # Electric Cyan
            "listening": QColor(0, 255, 150, 200), # Neon Emerald
            "thinking": QColor(130, 0, 255, 200),  # Deep Purple
            "speaking": QColor(255, 100, 0, 200),  # Pulsing Orange
            "error": QColor(255, 0, 80, 220),      # Cyber Red
            "success": QColor(0, 255, 100, 200),   # Bright Green
            # Emotion Mappings (Localized/Refined)
            "happy": QColor(255, 220, 0, 200),    # Golden
            "sad": QColor(100, 150, 255, 180),    # Soft Blue
            "angry": QColor(255, 30, 0, 230),     # Aggressive Red
            "surprise": QColor(255, 0, 255, 200), # Magenta
            "fear": QColor(80, 0, 80, 200),       # Dark Purple
        }
        
        self.current_color = self.colors["idle"]
        
        # 60 FPS animation timer
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._animate)
        self.animation_timer.start(16)  # ~60 FPS
        
    def _animate(self):
        """Smooth animation loop"""
        self.pulse_value = (self.pulse_value + 2) % 360
        self.rotation = (self.rotation + 2) % 360  # Faster rotation
        self.update()
        
    def set_status(self, status: str):
        """Update reactor status with smooth color transition"""
        self.status = status
        target_color = self.colors.get(status, self.colors["idle"])
        
        # Smooth color transition (can be animated further)
        self.current_color = target_color
        self.update()
        
    def set_data(self, sync=None, nucleo=None):
        """Update orbital data rings"""
        if sync is not None: self.sync_val = sync
        if nucleo is not None: self.nucleo_val = nucleo
        self.update()

    def paintEvent(self, event):
        """Paint the Stark Arc - Integrated Data Reactor"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        
        # Base scale - adaptive but compact
        base_size = min(width, height)
        scale = base_size / 200.0
        
        pulse_factor = (math.sin(math.radians(self.pulse_value)) + 1) / 2
        
        # 0. OUTER ORBITAL DATA RINGS (Sync & Nucleo)
        # SINCRO RING (Deep Blue/Cyan)
        ring_sync_r = 95 * scale
        painter.setPen(QPen(QColor(0, 180, 255, 30), 2 * scale))
        painter.drawEllipse(int(center_x - ring_sync_r), int(center_y - ring_sync_r), 
                            int(ring_sync_r * 2), int(ring_sync_r * 2))
        
        painter.setPen(QPen(QColor(0, 180, 255, 200), 3 * scale))
        span_sync = -int(self.sync_val * 3.6 * 16)
        painter.drawArc(int(center_x - ring_sync_r), int(center_y - ring_sync_r), 
                        int(ring_sync_r * 2), int(ring_sync_r * 2), 90 * 16, span_sync)
        
        # NUCLEO RING (Inner to Sync)
        ring_nuc_r = 85 * scale
        painter.setPen(QPen(QColor(0, 255, 150, 20), 2 * scale))
        painter.drawEllipse(int(center_x - ring_nuc_r), int(center_y - ring_nuc_r), 
                            int(ring_nuc_r * 2), int(ring_nuc_r * 2))
        
        painter.setPen(QPen(QColor(0, 255, 150, 180), 3 * scale))
        span_nuc = -int(self.nucleo_val * 3.6 * 16)
        painter.drawArc(int(center_x - ring_nuc_r), int(center_y - ring_nuc_r), 
                        int(ring_nuc_r * 2), int(ring_nuc_r * 2), 90 * 16, span_nuc)

        # 1. DEEP GLOW
        glow_radius = (75 + (pulse_factor * 15)) * scale
        glow_gradient = QRadialGradient(center_x, center_y, glow_radius)
        glow_color = QColor(self.current_color)
        glow_color.setAlpha(40 + int(pulse_factor * 40))
        glow_gradient.setColorAt(0, glow_color)
        glow_gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(glow_gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(center_x - glow_radius), int(center_y - glow_radius), 
                            int(glow_radius * 2), int(glow_radius * 2))
        
        # 2. ROTATING SHARDS (Technological detail)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        shard_r = 60 * scale
        painter.setPen(QPen(self.current_color, 4 * scale))
        for i in range(4):
            start = (self.rotation + i * 90) * 16
            span = 30 * 16
            painter.drawArc(int(center_x - shard_r), int(center_y - shard_r), 
                            int(shard_r * 2), int(shard_r * 2), start, span)
            
        # 3. CENTRAL CORE (Intense)
        core_r = (30 + (pulse_factor * 5)) * scale
        core_grad = QRadialGradient(center_x, center_y, core_r)
        core_grad.setColorAt(0, Qt.GlobalColor.white)
        core_grad.setColorAt(0.3, self.current_color)
        core_grad.setColorAt(1, QColor(0,0,0,0))
        painter.setBrush(core_grad)
        painter.drawEllipse(int(center_x - core_r), int(center_y - core_r), 
                            int(core_r * 2), int(core_r * 2))

class EliteCircularGauge(QWidget):
    """Modern circular gauge for system metrics"""
    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.setMinimumSize(60, 60)
        self.value = 0.0
        self.label = label
        self.color = QColor(100, 200, 255, 200)

    def set_value(self, val):
        self.value = val
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        side = min(w, h) - 10
        rect = QRectF((w - side) / 2, (h - side) / 2, side, side)
        
        # Background ring
        painter.setPen(QPen(QColor(100, 200, 255, 30), 2))
        painter.drawEllipse(rect)
        
        # Value arc
        painter.setPen(QPen(self.color, 3))
        span_angle = -int(self.value * 3.6 * 16)
        painter.drawArc(rect, 90 * 16, span_angle)
        
        # Label
        painter.setPen(QPen(QColor(100, 200, 255, 180), 1))
        font_size = max(6, int(side / 8))
        painter.setFont(QFont("Segoe UI", font_size, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{int(self.value)}%\n{self.label}")

class ModernTelemetryWidget(QWidget):
    """
    Holographic telemetry display for Neural & Emotional states
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(100)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 5, 15, 5)
        self.layout.setSpacing(20)
        
        # We handle sync/nucleo in the Reactor now, but keep this for emotion
        self.emotion_container = QWidget()
        em_layout = QVBoxLayout(self.emotion_container)
        
        # Minimalist Data Feed
        lbl = QLabel("ESTRUTURA NEURAL")
        lbl.setStyleSheet("color: rgba(0, 180, 255, 0.6); font-size: 7px; font-weight: bold; letter-spacing: 2px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.emotion_val = QLabel("NEUTRO")
        self.emotion_val.setStyleSheet("color: white; font-size: 10px; font-family: 'Consolas'; font-weight: bold; border: 1px solid rgba(0, 180, 255, 0.2); border-radius: 4px; padding: 4px;")
        self.emotion_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        em_layout.addWidget(lbl)
        em_layout.addWidget(self.emotion_val)
        
        self.layout.addStretch()
        self.layout.addWidget(self.emotion_container)
        self.layout.addStretch()

    def update_stats(self, sync=None, emotion=None, cpu=None, pulse=None):
        if emotion:
            em_map = {"NEUTRAL": "NEUTRO", "HAPPY": "FELIZ", "SAD": "TRISTE", 
                      "ANGRY": "BRAVO", "SURPRISE": "SURPRESA", "FEAR": "MEDO"}
            self.emotion_val.setText(em_map.get(emotion.upper(), emotion.upper()))


class ModernWaveformWidget(QWidget):
    """Animated waveform visualizer for voice/processing simulation"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.phase = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(30)
        
    def _animate(self):
        self.phase += 0.2
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        painter.setPen(QPen(QColor(0, 180, 255, 100), 1))
        
        points = QPolygonF()
        for x in range(0, w, 2):
            # Complex wave simulation
            y = h/2 + math.sin(x*0.05 + self.phase) * 10 * math.sin(x*0.01)
            points.append(QPointF(x, y))
            
        painter.drawPolyline(points)
        # Add glow line
        painter.setPen(QPen(QColor(0, 180, 255, 200), 1))
        painter.drawPolyline(points.translated(0, 1))

class HUDEventTicker(QWidget):
    """Scrolling ticker for system events - Compact Edition"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(2)
        
        self.events = []
        self.labels = []
        for _ in range(5):
            lbl = QLabel("")
            lbl.setStyleSheet("color: rgba(100, 200, 255, 0.5); font-size: 8px; font-family: 'Consolas';")
            self.layout.addWidget(lbl)
            self.labels.append(lbl)

    def add_event(self, text):
        timestamp = time.strftime("%H:%M:%S")
        self.events.insert(0, f"[{timestamp}] {text}")
        if len(self.events) > 5:
            self.events.pop()
        
        for i, event in enumerate(self.events):
            self.labels[i].setText(event)
            # Fade out older events
            opacity = 1.0 - (i * 0.18)
            self.labels[i].setStyleSheet(f"color: rgba(100, 200, 255, {opacity}); font-size: 9px; font-family: 'Consolas';")

class ModernHUD(QMainWindow):
    """
    Modern, draggable, fluid HUD for JARVIS
    
    Features:
    - Glassmorphism design
    - Smooth 60 FPS animations
    - Draggable with mouse
    - Multi-monitor support
    - Position persistence
    - Keyboard shortcuts
    - Responsive design
    """
    
    # Signals for thread-safe communication
    status_changed = pyqtSignal(str)
    response_ready = pyqtSignal(str)
    telemetry_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        
        # Configuration
        self.config_file = Path.home() / ".jarvis" / "hud_config.json"
        self.config_file.parent.mkdir(exist_ok=True)
        
        # Window setup
        self._setup_window()
        
        # UI Components
        self._setup_ui()
        
        # Load saved position
        self._load_position()
        
        # Setup keyboard shortcuts
        self._setup_shortcuts()
        
        # Connect signals
        self.status_changed.connect(self._on_status_changed)
        self.response_ready.connect(self._on_response_ready)
        self.telemetry_updated.connect(self._on_telemetry_updated)
        
        # Drag support
        self._drag_position = None
        self._is_dragging = False
        
        # Elite Animations
        self.scan_y = 0
        self.scan_dir = 1
        self.hex_opacity = 0.1
        
        # Status & Response State
        self.status = "idle"
        self.full_response = ""
        self.current_display_text = ""
        
        # Neural Typewriter timer
        self.type_timer = QTimer()
        self.type_timer.timeout.connect(self._update_typewriter)
        
        # STABLE 3D STATE
        self.perspective_angle = 12 # Deg (more subtle/stable)
        self.particles = []
        for _ in range(20):
            self.particles.append({
                'x': random.randint(0, 1000), 'y': random.randint(0, 1000),
                'speed': random.uniform(0.3, 1.2), 'size': random.uniform(1, 2)
            })
            
        self.nodes = [] # Neural synced nodes
        for _ in range(8):
            self.nodes.append({
                'pos': QPointF(random.uniform(0.2, 0.8), random.uniform(0.3, 0.7)),
                'pulse': random.uniform(0, 6.28),
                'conn': random.sample(range(8), 2)
            })
        
        # 60 FPS update loop for visual effects
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.update)
        self.ui_timer.start(16) 
        
    def showEvent(self, event):
        """Fade in animation and bounds check on show"""
        super().showEvent(event)
        
        # 1. ENSURE WITHIN BOUNDS
        screen = QApplication.primaryScreen().availableGeometry()
        if not screen.contains(self.geometry()):
            # Move to a safe location if it was off-screen (e.g. monitor disconnected)
            self.move(screen.right() - self.width() - 20, screen.bottom() - self.height() - 20)
            
        # 2. FADE IN ANIMATION
        self.setWindowOpacity(0.0)
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(800)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(0.95) # Premium transparent look
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_anim.start()
        
    def _setup_window(self):
        """Configure window properties"""
        self.setWindowTitle("J.A.R.V.I.S. Singularity")
        
        # Frameless with transparency
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        
        # Ensure it doesn't take focus but stays on top
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # Default size based on screen (Responsive & Safe)
        screen = QApplication.primaryScreen().availableGeometry()
        
        # Proportional sizing - NEVER exceeds screen limits
        # We aim for ~20% width and ~60% height
        safe_width = int(screen.width() * 0.20)
        safe_height = int(screen.height() * 0.60)
        
        # Strict Clamp: Don't let it be taller/wider than the screen available space
        width = min(safe_width, screen.width() - 40)
        height = min(safe_height, screen.height() - 40)
        
        # Minimum usable size
        width = max(300, width)
        height = max(500, height)
        
        self.resize(width, height)
        
    def _setup_ui(self):
        """Build the Stark OS Responsive Interface"""
        central = QWidget()
        self.setCentralWidget(central)
        central.setObjectName("main_panel")
        
        # High-Fidelity Glassmorphism Style
        central.setStyleSheet("""
            QWidget#main_panel {
                background: qradialgradient(
                    cx:0.5, cy:0.2, radius:1.2,
                    fx:0.5, fy:0,
                    stop:0 rgba(10, 25, 45, 230),
                    stop:0.7 rgba(5, 10, 20, 245),
                    stop:1 rgba(0, 0, 0, 250)
                );
                border: 1px solid rgba(0, 180, 255, 0.2);
                border-radius: 15px;
            }
            QLabel {
                background: transparent;
                color: #00B4FF;
                font-family: 'Segoe UI Semibold', 'Outfit', Arial;
            }
        """)
        
        # Main Layout (Structured & Responsive)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 1. HEADER (Title & Stats)
        header = QHBoxLayout()
        title_lbl = QLabel("J.A.R.V.I.S. // STARK-OS v10.0")
        title_lbl.setStyleSheet("font-size: 10px; letter-spacing: 5px; color: rgba(0, 180, 255, 0.7);")
        header.addWidget(title_lbl)
        header.addStretch()
        layout.addLayout(header)
        
        # 2. CORE REACTOR (Dynamic Center)
        self.reactor = ModernReactorCore()
        layout.addWidget(self.reactor, 3)
        
        # 3. RESPONSE AREA (Neural Typewriter)
        self.response_label = QLabel("PROTOCOLO DE INTERFACE STARK-OS ATIVO...")
        self.response_label.setWordWrap(True)
        self.response_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.response_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9); 
            font-size: 11px; 
            padding: 10px; 
            background: rgba(0, 180, 255, 0.05);
            border-left: 2px solid #00B4FF;
        """)
        self.response_label.setMinimumHeight(80)
        layout.addWidget(self.response_label)
        
        # 4. TELEMETRY & FEED
        self.telemetry = ModernTelemetryWidget()
        layout.addWidget(self.telemetry)
        
        self.ticker = HUDEventTicker()
        layout.addWidget(self.ticker)
        
        # 5. FOOTER (Status)
        self.status_label = QLabel("NÚCLEO ESTÁVEL")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #00B4FF; font-family: 'Consolas'; font-size: 10px; font-weight: bold; letter-spacing: 3px;")
        layout.addWidget(self.status_label)
        
        # Size grip
        self.size_grip = QSizeGrip(central)
        self.size_grip.setFixedSize(20, 20)
        self.size_grip.setStyleSheet("background: rgba(0, 180, 255, 0.1); border-radius: 10px;")
        
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Ctrl+H to toggle visibility
        toggle_shortcut = QShortcut(QKeySequence("Ctrl+H"), self)
        toggle_shortcut.activated.connect(self._toggle_visibility)
        
        # Escape to close
        escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        escape_shortcut.activated.connect(self.close)
        
    def _toggle_visibility(self):
        """Toggle HUD visibility"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            
    def _load_position(self):
        """Load saved window position"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    x = config.get('x', 100)
                    y = config.get('y', 100)
                    width = config.get('width', 400)
                    height = config.get('height', 600)
                    
                    self.setGeometry(x, y, width, height)
            except Exception as e:
                print(f"Failed to load HUD position: {e}")
                
    def _save_position(self):
        """Save current window position"""
        try:
            config = {
                'x': self.x(),
                'y': self.y(),
                'width': self.width(),
                'height': self.height()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Failed to save HUD position: {e}")
            
    def mousePressEvent(self, event):
        """Start dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """Handle dragging"""
        if self._is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        """Stop dragging and handle screen snapping"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            
            # SCREEN SNAPPING LOGIC
            screen = QApplication.primaryScreen().availableGeometry()
            pos = self.pos()
            snap_margin = 30
            
            new_x, new_y = pos.x(), pos.y()
            
            # Horizontal snapping
            if abs(pos.x() - screen.left()) < snap_margin:
                new_x = screen.left()
            elif abs((pos.x() + self.width()) - screen.right()) < snap_margin:
                new_x = screen.right() - self.width()
                
            # Vertical snapping
            if abs(pos.y() - screen.top()) < snap_margin:
                new_y = screen.top()
            elif abs((pos.y() + self.height()) - screen.bottom()) < snap_margin:
                new_y = screen.bottom() - self.height()
                
            if new_x != pos.x() or new_y != pos.y():
                self.move(new_x, new_y)
                
            self._save_position()
            event.accept()
            
    def paintEvent(self, event):
        """Stable 3D Perspective Rendering for JARVIS"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # 1. APPLY SUBTLE STABLE 3D TRANSFORM
        transform = QTransform()
        transform.translate(cx, cy)
        transform.rotate(self.perspective_angle, Qt.Axis.YAxis)
        transform.translate(-cx, -cy)
        painter.setTransform(transform)
        
        # 2. DRAW PREMIUM STARK-FRAME (Chamfered Glass)
        # Use a path for strict clipping and aesthetics
        path = QPainterPath()
        m, c = 10, 30
        path.moveTo(m + c, m)
        path.lineTo(w - m - c, m)
        path.lineTo(w - m, m + c)
        path.lineTo(w - m, h - m - c)
        path.lineTo(w - m - c, h - m)
        path.lineTo(m + c, h - m)
        path.lineTo(m, h - m - c)
        path.lineTo(m, m + c)
        path.closeSubpath()
        
        # Clip to ensure zero overflow within the widget
        painter.setClipPath(path)
        
        # Glass Backdrop
        painter.fillPath(path, QBrush(QColor(10, 20, 35, 230)))
        
        # Neon Border (1px Elite)
        painter.setPen(QPen(QColor(0, 180, 255, 180), 1))
        painter.drawPath(path)
        
        # 3. BACKGROUND EFFECTS (Hex Grid & Scanlines)
        self._draw_hex_grid(painter)
        self._draw_scanning_laser(painter)
        
        # 4. NEURAL NODE MAP (Subtle depth)
        self._draw_neural_nodes(painter)
        
        # 5. DATA PARTICLES
        self._draw_particles(painter)

    def _clamp_to_screen(self):
        """Strictly ensures the HUD stays within the available Windows desktop area"""
        screen = QApplication.primaryScreen().availableGeometry()
        geo = self.geometry()
        
        # Maintain 10px padding from screen edges
        new_x = max(screen.left() + 10, min(geo.x(), screen.right() - geo.width() - 10))
        new_y = max(screen.top() + 10, min(geo.y(), screen.bottom() - geo.height() - 10))
        
        if new_x != geo.x() or new_y != geo.y():
            self.move(new_x, new_y)

    def moveEvent(self, event):
        """Monitor movement and prevent accidental overflow"""
        super().moveEvent(event)
        if not self._is_dragging:
            self._clamp_to_screen()
    
    def _draw_neural_nodes(self, painter):
        """Thinking synapse map (Optimized/Subtle)"""
        w, h = self.width(), self.height()
        t = time.time()
        for node in self.nodes:
            p = QPointF(node['pos'].x() * w, node['pos'].y() * h)
            # Pulse
            alpha = int(100 + 100 * math.sin(t * 2 + node['pulse']))
            painter.setBrush(QColor(0, 180, 255, max(0, min(255, alpha))))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(p, 2, 2)
            
    def _draw_particles(self, painter):
        """Micro greebles"""
        w, h = self.width(), self.height()
        for p in self.particles:
            p['y'] -= p['speed']
            if p['y'] < 0: p['y'] = 1000
            px, py = (p['x']/1000)*w, (p['y']/1000)*h
            painter.setBrush(QColor(0, 180, 255, 60))
            painter.drawRect(int(px), int(py), int(p['size']), int(p['size']))

    def _on_telemetry_updated(self, data: dict):
        """Update telemetry based on system signals"""
        sync = data.get("sync", "0%")
        cpu = data.get("cpu", 0)
        emotion = data.get("emotion", "NEUTRAL")
        
        # Update Reactor
        try:
            sync_val = float(str(sync).replace('%',''))
            self.reactor.set_data(sync=sync_val, nucleo=cpu)
        except: pass
        
        # Update Telemetry & Feed
        self.telemetry.update_stats(sync=sync, emotion=emotion, cpu=cpu)
        
        if emotion:
            self.reactor.set_status(emotion.lower())
        
        self.update()

    def log_event(self, message: str):
        """Add a short system message to the event ticker"""
        if hasattr(self, 'ticker'):
            self.ticker.add_event(message)

    def _draw_hex_grid(self, painter):
        """Draws a subtle pulsating hexagonal grid overlay"""
        painter.save()
        hex_size = 30
        h = hex_size * math.sqrt(3) / 2
        painter.setPen(QPen(QColor(100, 200, 255, int(40 * (math.sin(time.time()*2)+1.5))), 0.5))
        
        for row in range(-1, self.height() // int(h) + 1):
            for col in range(-1, self.width() // int(hex_size * 1.5) + 1):
                x = col * hex_size * 1.5
                y = row * h * 2 + (col % 2) * h
                
                # Draw hexagon (simplified for performance)
                poly = QPolygonF()
                for i in range(6):
                    angle = math.radians(60 * i)
                    poly.append(QPointF(x + hex_size * math.cos(angle), y + hex_size * math.sin(angle)))
                painter.drawPolygon(poly)
        painter.restore()

    def _draw_scanning_laser(self, painter):
        """Draws a moving horizontal laser line with glow"""
        self.scan_y += 3 * self.scan_dir
        if self.scan_y > self.height() or self.scan_y < 0:
            self.scan_dir *= -1
            
        laser_color = QColor(100, 200, 255, 150)
        gradient = QLinearGradient(0, self.scan_y - 10, 0, self.scan_y + 10)
        gradient.setColorAt(0, QColor(0, 0, 0, 0))
        gradient.setColorAt(0.5, laser_color)
        gradient.setColorAt(1, QColor(0, 0, 0, 0))
        
        painter.fillRect(5, self.scan_y - 10, self.width() - 10, 20, QBrush(gradient))
        painter.setPen(QPen(laser_color, 1))
        painter.drawLine(10, self.scan_y, self.width() - 10, self.scan_y)

    def resizeEvent(self, event):
        """Handle resize"""
        super().resizeEvent(event)
        # Position size grip at bottom right
        self.size_grip.move(
            self.width() - self.size_grip.width() - 5,
            self.height() - self.size_grip.height() - 5
        )
        self._save_position()

    def _on_status_changed(self, status: str):
        """Handle status change (thread-safe) with PT-BR translation"""
        self.status = status.lower()
        
        # Omni-HUD PT-BR Technical Mapping
        status_map = {
            "idle": "NÚCLEO ESTÁVEL",
            "listening": "CAPTAÇÃO BIOMÉTRICA ATIVA",
            "thinking": "PROCESSAMENTO FRACTAL EM CURSO",
            "speaking": "REPRODUÇÃO DE FLUXO NEURAL",
            "error": "FALHA CRÍTICA DE PROTOCOLO",
            "success": "SINCRO CONCLUÍDA"
        }
        
        display_status = status_map.get(self.status, status.upper())
        self.status_label.setText(display_status)
        self.update() # Trigger 3D render update
        
    def _on_response_ready(self, text: str):
        """Handle new response with typewriter effect"""
        self.full_response = text
        self.current_display_text = ""
        self.response_label.setText("")
        self.type_timer.start(20) # 20ms per char
        
        # Fade in container
        effect = QGraphicsOpacityEffect()
        self.response_label.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(400)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        animation.start()

    def _update_typewriter(self):
        """Animated character by character reveal"""
        if len(self.current_display_text) < len(self.full_response):
            # Reveal next 2 chars for snappiness
            next_chars = self.full_response[len(self.current_display_text):len(self.current_display_text)+2]
            self.current_display_text += next_chars
            self.response_label.setText(self.current_display_text)
        else:
            self.type_timer.stop()
        
    # Public API (thread-safe via signals)
    def update_state(self, state: str):
        """Update HUD state (can be called from any thread)"""
        self.status_changed.emit(state)
        
    def show_response(self, text: str):
        """Show response text (can be called from any thread)"""
        self.response_ready.emit(text)
        
    def _on_telemetry_updated(self, data: dict):
        """Update 3D state based on system telemetry"""
        sync = data.get("sync", "0%")
        cpu = data.get("cpu", 0)
        emotion = data.get("emotion", "NEUTRAL")
        
        # Map telemetry to 3D effects
        try:
            sync_val = float(str(sync).replace('%',''))
            # Speed up particles and perspective if sync is high
            self.perspective_angle = 15 + (sync_val / 20.0)
            for p in self.particles: 
                p['speed'] = 0.5 + (cpu / 50.0)
        except: pass
        
        # Repaint request
        self.update()

    def update_telemetry(self, stats: dict):
        """Update telemetry stats (can be called from any thread)"""
        self.telemetry_updated.emit(stats)
        
    def log_event(self, message: str):
        """Add a short system message to the event ticker"""
        if hasattr(self, 'ticker'):
            self.ticker.add_event(message)

    def closeEvent(self, event):
        """Save position before closing"""
        self._save_position()
        super().closeEvent(event)


# Alias for compatibility
JarvisHUD = ModernHUD


# Test the HUD
if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    hud = ModernHUD()
    hud.show()
    
    # Test animations
    def test_states():
        import time
        states = ["idle", "listening", "thinking", "speaking", "success", "error", "idle"]
        responses = [
            "Systems online and ready",
            "Listening for your command...",
            "Processing your request...",
            "Here's what I found for you.",
            "Task completed successfully!",
            "Error: Unable to process",
            "Standing by..."
        ]
        
        for state, response in zip(states, responses):
            hud.update_state(state)
            hud.show_response(response)
            QApplication.processEvents()
            time.sleep(2)
    
    # Run test after 1 second
    QTimer.singleShot(1000, test_states)
    
    sys.exit(app.exec())
