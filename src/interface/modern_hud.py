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
        self.rotation_inner = 0
        self.rotation_mid = 0
        self.rotation_outer = 0
        self.plasma_phase = 0
        
        # Color palettes (Stark 2.0)
        self.palettes = {
            "stable": QColor(0, 242, 255),    # Stark Cyan
            "thinking": QColor(188, 0, 255),  # Neural Purple
            "alert": QColor(255, 170, 0),     # Warning Amber
            "critical": QColor(255, 0, 60),   # Critical Red
            "listening": QColor(0, 255, 150)  # Biometric Green
        }
        self.current_color = self.palettes["stable"]
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(16) # 60 FPS
        
    def _animate(self):
        # Update animation phases
        self.pulse_value = (self.pulse_value + 2) % 360
        self.rotation_inner -= 1.5   # Counter-clockwise
        self.rotation_mid += 0.8     # Clockwise
        self.rotation_outer -= 0.4   # Slow Counter-clockwise
        self.plasma_phase += 0.1
        self.update()

    def set_status(self, status: str):
        self.status = status.lower()
        target = self.palettes.get(self.status, self.palettes["stable"])
        # Simple color snap for now
        self.current_color = target

    def set_data(self, sync=None, nucleo=None):
        if sync is not None: self.sync_val = sync
        if nucleo is not None: self.nucleo_val = nucleo

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        base_size = min(w, h)
        scale = base_size / 220.0
        
        pulse_factor = (math.sin(math.radians(self.pulse_value)) + 1) / 2
        
        # 1. ATMOSPHERIC OUTER GLOW
        outer_glow = QRadialGradient(cx, cy, 110 * scale)
        c = QColor(self.current_color)
        c.setAlpha(int(20 + 15 * pulse_factor))
        outer_glow.setColorAt(0, c)
        outer_glow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(outer_glow)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(cx - 110 * scale), int(cy - 110 * scale), 
                            int(220 * scale), int(220 * scale))

        # 2. TRIPLE ORBITAL DATA RINGS
        # OUTER SYNC RING (Segmented)
        self._draw_segmented_ring(painter, cx, cy, 95 * scale, self.rotation_outer, 12, 15, QColor(self.current_color.red(), self.current_color.green(), self.current_color.blue(), 60))
        self._draw_arc_data(painter, cx, cy, 95 * scale, self.sync_val, QColor(self.current_color), 3 * scale)

        # MID PROCESSING RING (Hex-like dots)
        self._draw_dotted_ring(painter, cx, cy, 80 * scale, self.rotation_mid, 24, QColor(self.current_color.red(), self.current_color.green(), self.current_color.blue(), 80))

        # INNER NUCLEO RING (Smooth glow)
        self._draw_arc_data(painter, cx, cy, 65 * scale, self.nucleo_val, QColor(0, 255, 150, 200), 2 * scale)

        # 3. ROTATING POWER SHARDS
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.rotation_inner)
        for i in range(3):
            painter.rotate(120)
            shard_path = QPainterPath()
            shard_path.moveTo(0, -50 * scale)
            shard_path.lineTo(10 * scale, -40 * scale)
            shard_path.lineTo(0, -35 * scale)
            shard_path.lineTo(-10 * scale, -40 * scale)
            shard_path.closeSubpath()
            
            c_shard = QColor(self.current_color)
            c_shard.setAlpha(180)
            painter.setBrush(c_shard)
            painter.setPen(QPen(Qt.GlobalColor.white, 1, Qt.PenStyle.SolidLine))
            painter.drawPath(shard_path)
        painter.restore()

        # 4. PLASMA PLASMA PLASMA CORE
        core_r = (35 + (5 * pulse_factor)) * scale
        plasma = QRadialGradient(cx, cy, core_r)
        
        # Dynamic plasma shift
        off1 = (math.sin(self.plasma_phase) + 1) / 2 * 0.2
        plasma.setColorAt(0, Qt.GlobalColor.white)
        plasma.setColorAt(0.3 + off1, self.current_color)
        plasma.setColorAt(0.8, QColor(self.current_color.red()//2, self.current_color.green()//2, self.current_color.blue()//2, 100))
        plasma.setColorAt(1, QColor(0, 0, 0, 0))
        
        painter.setBrush(plasma)
        painter.drawEllipse(int(cx - core_r), int(cy - core_r), int(core_r * 2), int(core_r * 2))

        # 5. CORE STATUS LABEL
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        font = QFont("Consolas", int(8 * scale), QFont.Weight.Bold)
        painter.setFont(font)
        status_txt = f"C-LOAD: {int(self.nucleo_val)}%"
        painter.drawText(QRectF(cx - 50*scale, cy + 50*scale, 100*scale, 20*scale), Qt.AlignmentFlag.AlignCenter, status_txt)

    def _draw_segmented_ring(self, painter, cx, cy, r, rotation, segments, gap, color):
        painter.setPen(QPen(color, 2, Qt.PenStyle.DashLine))
        span = (360 / segments) - gap
        for i in range(segments):
            start = (rotation + i * (360 / segments)) * 16
            painter.drawArc(int(cx - r), int(cy - r), int(r * 2), int(r * 2), int(start), int(span * 16))

    def _draw_dotted_ring(self, painter, cx, cy, r, rotation, dots, color):
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        for i in range(dots):
            angle = math.radians(rotation + i * (360 / dots))
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)
            painter.drawEllipse(int(px - 1.5), int(py - 1.5), 3, 3)

    def _draw_arc_data(self, painter, cx, cy, r, val, color, width):
        painter.setPen(QPen(color, width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        span = -int(val * 3.6 * 16)
        painter.drawArc(int(cx - r), int(cy - r), int(r * 2), int(r * 2), 90 * 16, span)

class EliteCircularGauge(QWidget):
    """Modern circular gauge for system metrics - Segmented Stark Edition"""
    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.setMinimumSize(70, 70)
        self.value = 0.0
        self.label = label
        self.color = QColor(0, 242, 255, 200)

    def set_value(self, val):
        self.value = val
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        side = min(w, h) - 10
        rect = QRectF((w - side) / 2, (h - side) / 2, side, side)
        
        # 1. SEGMENTED BACKGROUND
        painter.setPen(QPen(QColor(0, 242, 255, 30), 2, Qt.PenStyle.DotLine))
        painter.drawEllipse(rect)
        
        # 2. DATA SEGMENTS (Stark Style)
        segments = 20
        span = 360 / segments
        active_segments = int((self.value / 100.0) * segments)
        
        painter.setPen(QPen(self.color, 4))
        for i in range(active_segments):
            start = (90 - i * span) * 16
            painter.drawArc(rect, int(start), -int((span - 2) * 16))
        
        # 3. GLOW LINE (Outer)
        painter.setPen(QPen(QColor(255, 255, 255, 50), 1))
        painter.drawArc(rect.adjusted(-2, -2, 2, 2), 90 * 16, -int(self.value * 3.6 * 16))
        
        # 4. LABEL (Cyber)
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{int(self.value)}%\n{self.label}")

class ModernTelemetryWidget(QWidget):
    """
    Holographic telemetry display for Neural & Emotional states
    Stark HUD 2.0 Edition
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 10, 15, 10)
        
        # Left Stats
        self.sync_gauge = EliteCircularGauge("SINCRO")
        self.layout.addWidget(self.sync_gauge)
        
        # Center Emotion
        self.emotion_container = QWidget()
        em_layout = QVBoxLayout(self.emotion_container)
        em_layout.setSpacing(2)
        
        lbl = QLabel("NEURAL MAPPING")
        lbl.setStyleSheet("color: rgba(0, 242, 255, 0.6); font-size: 8px; font-weight: bold; letter-spacing: 3px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.emotion_val = QLabel("NEUTRO")
        self.emotion_val.setStyleSheet("""
            color: #00F2FF; 
            font-size: 11px; 
            font-family: 'Consolas'; 
            font-weight: bold; 
            padding: 6px; 
            background: rgba(0, 242, 255, 0.05); 
            border: 1px solid rgba(0, 242, 255, 0.3);
            border-radius: 2px;
        """)
        self.emotion_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        em_layout.addWidget(lbl)
        em_layout.addWidget(self.emotion_val)
        self.layout.addWidget(self.emotion_container, 1)
        
        # Right Pulse
        self.cpu_gauge = EliteCircularGauge("NÚCLEO")
        self.layout.addWidget(self.cpu_gauge)

    def update_stats(self, sync=None, emotion=None, cpu=None, pulse=None):
        if sync is not None:
            # Handle string like "98.5%"
            try:
                val = float(str(sync).replace('%', ''))
                self.sync_gauge.set_value(val)
            except: pass
            
        if cpu is not None:
            self.cpu_gauge.set_value(float(cpu))
            
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
        self.events.insert(0, f"▸ {timestamp} | {text}")
        if len(self.events) > 5:
            self.events.pop()
        
        for i, event in enumerate(self.events):
            self.labels[i].setText(event)
            # Alpha based on age
            opacity = 0.8 - (i * 0.15)
            self.labels[i].setStyleSheet(f"color: rgba(0, 242, 255, {opacity}); font-size: 9px; font-family: 'Consolas';")

class ManualSettingsDrawer(QWidget):
    """Hidden panel for manual configurations inside the HUD"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)
        self.setStyleSheet("""
            background: rgba(5, 10, 20, 250);
            border-left: 2px solid #00B4FF;
            border-top: 1px solid rgba(0, 180, 255, 0.2);
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 20)
        
        title = QLabel("AJUSTES MANUAIS")
        title.setStyleSheet("font-size: 12px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        # Shortcuts for settings
        btn_face = QPushButton("📸 Recadastrar Bio Facial")
        btn_voice = QPushButton("🎤 Recadastrar Bio Vocal")
        for b in [btn_face, btn_voice]:
            b.setStyleSheet("background: rgba(0, 180, 255, 0.1); color: #00B4FF; padding: 10px; border: 1px solid #00B4FF; margin-top: 5px;")
            layout.addWidget(b)
            
        layout.addStretch()
        
        close_btn = QPushButton("FECHAR")
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn)

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
        # Particle System for background neural flow
        self.particles = []
        for _ in range(30):
            self.particles.append({
                'pos': QPointF(random.randint(0, 1000), random.randint(0, 800)),
                'speed': random.uniform(0.5, 2.0),
                'size': random.uniform(1, 3),
                'opacity': random.uniform(0.1, 0.5)
            })
            
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
        
        # High-Fidelity Glassmorphism Style - Stark 2.0
        central.setStyleSheet("""
            QWidget#main_panel {
                background: qradialgradient(
                    cx:0.5, cy:0.3, radius:1.5,
                    fx:0.5, fy:0,
                    stop:0 rgba(15, 30, 60, 240),
                    stop:0.6 rgba(5, 10, 20, 248),
                    stop:1 rgba(0, 0, 0, 255)
                );
                border: 1px solid rgba(0, 242, 255, 0.2);
                border-radius: 12px;
            }
            QLabel {
                background: transparent;
                color: #00F2FF;
                font-family: 'Consolas', 'Outfit', 'Segoe UI';
            }
        """)
        
        # Main Layout (Structured & Responsive)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # 1. HEADER (Title & Stats)
        header = QHBoxLayout()
        title_lbl = QLabel("J.A.R.V.I.S. // STARK-OS v10.0")
        title_lbl.setStyleSheet("font-size: 9px; font-weight: bold; letter-spacing: 4px; color: rgba(0, 242, 255, 0.7);")
        header.addWidget(title_lbl)
        header.addStretch()
        layout.addLayout(header)
        
        # 2. CORE REACTOR (Dynamic Center)
        self.reactor = ModernReactorCore()
        layout.addWidget(self.reactor, 4)
        
        # 3. RESPONSE AREA (Neural Typewriter)
        self.response_label = QLabel("PROTOCOLO DE INTERFACE STARK-OS ATIVO...")
        self.response_label.setWordWrap(True)
        self.response_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.response_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.95); 
            font-size: 11px; 
            font-family: 'Consolas';
            padding: 12px; 
            background: rgba(0, 242, 255, 0.03);
            border-left: 3px solid #00F2FF;
            line-height: 1.4;
        """)
        self.response_label.setMinimumHeight(100)
        layout.addWidget(self.response_label)
        
        # 4. TELEMETRY & FEED
        self.telemetry = ModernTelemetryWidget()
        layout.addWidget(self.telemetry)
        
        self.ticker = HUDEventTicker()
        layout.addWidget(self.ticker)
        
        # 5. FOOTER (Status & Settings Button)
        footer = QHBoxLayout()
        self.status_label = QLabel("NÚCLEO ESTÁVEL")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #00F2FF; font-family: 'Consolas'; font-size: 10px; font-weight: bold; letter-spacing: 3px;")
        
        self.btn_settings = QPushButton("⚙")
        self.btn_settings.setFixedSize(25, 25)
        self.btn_settings.setStyleSheet("""
            QPushButton {
                background: rgba(0, 242, 255, 0.05); 
                border: 1px solid rgba(0, 242, 255, 0.3); 
                color: #00F2FF;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: rgba(0, 242, 255, 0.2);
            }
        """)
        self.btn_settings.clicked.connect(self._toggle_settings_drawer)
        
        footer.addWidget(self.status_label, 1)
        footer.addWidget(self.btn_settings)
        layout.addLayout(footer)
        
        # 6. HIDDEN DRAWER
        self.drawer = ManualSettingsDrawer(central)
        self.drawer.hide()
        
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
        """High-Fidelity Cybernetic Rendering for JARVIS Stark 2.0"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # 1. APPLY SUBTLE STABLE 3D TRANSFORM (Holographic tilt)
        transform = QTransform()
        transform.translate(cx, cy)
        transform.rotate(self.perspective_angle, Qt.Axis.YAxis)
        transform.translate(-cx, -cy)
        painter.setTransform(transform)
        
        # 2. STARK-FRAME (Advanced Glass with Neon Edges)
        path = QPainterPath()
        m, c = 8, 25
        path.moveTo(m + c, m)
        path.lineTo(w - m - c, m)
        path.lineTo(w - m, m + c)
        path.lineTo(w - m, h - m - c)
        path.lineTo(w - m - c, h - m)
        path.lineTo(m + c, h - m)
        path.lineTo(m, h - m - c)
        path.lineTo(m, m + c)
        path.closeSubpath()
        
        painter.setClipPath(path)
        
        # Glass Gradient Background
        bg_grad = QLinearGradient(0, 0, 0, h)
        bg_grad.setColorAt(0, QColor(10, 25, 45, 235))
        bg_grad.setColorAt(1, QColor(0, 0, 0, 250))
        painter.fillPath(path, QBrush(bg_grad))
        
        # Neon Border (Electric Glow)
        border_color = QColor(self.reactor.current_color)
        border_color.setAlpha(180)
        painter.setPen(QPen(border_color, 1.5))
        painter.drawPath(path)
        
        # 3. ATMOSPHERIC SCANNING & GLITCH
        self._draw_hex_grid(painter)
        self._draw_scanning_laser(painter)
        
        # Random Micro Glitch
        if random.random() > 0.98:
            self._draw_glitch_effect(painter)
        
        # 4. NEURAL DATA FLOW (Synapses)
        self._draw_neural_nodes(painter)
        self._draw_particles(painter)

    def _draw_neural_nodes(self, painter):
        """Draw animated neural nodes and connections"""
        painter.save()
        w, h = self.width(), self.height()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw some static "nodes" with pulsing glow
        nodes = [
            (w * 0.2, h * 0.3), (w * 0.8, h * 0.3),
            (w * 0.5, h * 0.7), (w * 0.2, h * 0.7),
            (w * 0.8, h * 0.7)
        ]
        
        pulse = (math.sin(time.time() * 2) + 1) / 2
        color = QColor(self.reactor.current_color)
        
        for i, (nx, ny) in enumerate(nodes):
            # Glow
            grad = QRadialGradient(nx, ny, 30 * pulse)
            c = QColor(color)
            c.setAlpha(int(100 * pulse))
            grad.setColorAt(0, c)
            grad.setColorAt(1, Qt.GlobalColor.transparent)
            painter.setBrush(grad)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(nx, ny), 30 * pulse, 30 * pulse)
            
            # Core
            painter.setBrush(color)
            painter.drawEllipse(QPointF(nx, ny), 3, 3)
            
            # Connections
            if i > 0:
                px, py = nodes[i-1]
                painter.setPen(QPen(c, 0.5))
                painter.drawLine(QPointF(nx, ny), QPointF(px, py))
        
        painter.restore()

    def _draw_particles(self, painter):
        """Draw and update background particles"""
        painter.save()
        w, h = self.width(), self.height()
        color = QColor(self.reactor.current_color)
        
        for p in self.particles:
            # Update position
            p['pos'].setX(p['pos'].x() + p['speed'])
            if p['pos'].x() > w:
                p['pos'].setX(0)
                p['pos'].setY(random.randint(0, h))
                
            # Draw
            c = QColor(color)
            c.setAlpha(int(255 * p['opacity']))
            painter.setBrush(c)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(p['pos'], p['size'], p['size'])
            
        painter.restore()

    def _draw_glitch_effect(self, painter):
        """Real-time technical interference simulation"""
        w, h = self.width(), self.height()
        painter.save()
        painter.setOpacity(0.3)
        for _ in range(3):
            gy = random.randint(0, h)
            gh = random.randint(2, 10)
            gx = random.randint(-20, 20)
            # Offset part of the screen
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Difference)
            painter.setBrush(QColor(0, 242, 255, 100))
            painter.drawRect(gx, gy, w, gh)
        painter.restore()

    def _draw_hex_grid(self, painter):
        """Pulsating geometric overlay"""
        painter.save()
        painter.setOpacity(0.15)
        hex_size = 25
        h_hex = hex_size * math.sqrt(3) / 2
        p_val = (math.sin(time.time() * 1.5) + 1) / 2
        painter.setPen(QPen(QColor(0, 242, 255, int(50 * p_val)), 0.5))
        
        for row in range(-1, self.height() // int(h_hex) + 1):
            for col in range(-1, self.width() // int(hex_size * 1.5) + 1):
                x = col * hex_size * 1.5
                y = row * h_hex * 2 + (col % 2) * h_hex
                # Efficiently draw 3 lines of hexagon instead of polygon
                painter.drawLine(int(x), int(y - h_hex), int(x + hex_size/2), int(y))
                painter.drawLine(int(x + hex_size/2), int(y), int(x), int(y + h_hex))
        painter.restore()

    def _draw_scanning_laser(self, painter):
        """Military-grade horizontal scanning line"""
        self.scan_y += 4 * self.scan_dir
        if self.scan_y > self.height() or self.scan_y < 0:
            self.scan_dir *= -1
            
        w = self.width()
        laser_color = QColor(0, 242, 255, 120)
        grad = QLinearGradient(0, self.scan_y - 15, 0, self.scan_y + 15)
        grad.setColorAt(0, QColor(0, 0, 0, 0))
        grad.setColorAt(0.5, laser_color)
        grad.setColorAt(1, QColor(0, 0, 0, 0))
        
        painter.fillRect(6, self.scan_y - 15, w - 12, 30, QBrush(grad))
        painter.setPen(QPen(laser_color, 1))
        painter.drawLine(10, self.scan_y, w - 10, self.scan_y)

    def _draw_particles(self, painter):
        """Data particles flowing towards the Reactor Core"""
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        for p in self.particles:
            # Move towards center (cx, cy)
            dx = cx - (p['x']/1000)*w
            dy = cy - (p['y']/1000)*h
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < 40: # Reset if reached core
                p['x'] = random.randint(0, 1000)
                p['y'] = random.randint(0, 1000)
            else:
                p['speed_mod'] = 1.0 + (100 / dist)
                p['x'] += (dx / dist) * p['speed'] * p['speed_mod'] * 2
                p['y'] += (dy / dist) * p['speed'] * p['speed_mod'] * 2
                
            px, py = (p['x']/1000)*w, (p['y']/1000)*h
            
            alpha = max(20, min(150, int(200 * (1.0 - dist/(w/2)))))
            painter.setBrush(QColor(0, 242, 255, alpha))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(int(px), int(py), int(p['size']), int(p['size']))

    def _on_telemetry_updated(self, data: dict):
        """Update 3D state and labels based on system telemetry"""
        sync = str(data.get("sync", "98.5%"))
        cpu = data.get("cpu", 0)
        emotion = data.get("emotion", "NEUTRAL")
        pulse = data.get("pulse", "STABLE")
        
        # 1. Update Reactor (Orbital Rings & State)
        try:
            # Clean sync value for float conversion
            clean_sync = float(sync.replace('%', ''))
            self.reactor.set_data(sync=clean_sync, nucleo=cpu)
            
            # Update perspective and particle speed based on load
            self.perspective_angle = 12 + (clean_sync / 50.0) # Adaptive 3D tilt
            for p in self.particles: 
                p['speed'] = 0.5 + (cpu / 40.0)
                
            if emotion:
                self.reactor.set_status(emotion.lower())
        except Exception as e:
            logger.debug(f"Reactor update fail: {e}")
        
        # 2. Update Telemetry Widget (Labels)
        self.telemetry.update_stats(sync=sync, emotion=emotion, cpu=cpu, pulse=pulse)
        
        # 3. Process Ticker events for critical load
        if cpu > 80:
            self.log_event(f"SYSTEM OVERLOAD: {cpu}%")
        
        # Force repaint for 60FPS fluid feel
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

    def _toggle_settings_drawer(self):
        """Toggle manual settings inside HUD"""
        if self.drawer.isVisible():
            self.drawer.hide()
        else:
            self.drawer.show()
            # Position drawer to the right
            self.drawer.move(self.width() - self.drawer.width(), 0)
            self.drawer.setFixedHeight(self.height())

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
