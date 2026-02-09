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
        self.sync_val = 0  # HUD data ring value
        self.nucleo_val = 0  # HUD nucleo value
        
        # 💎 SINGULARITY 2.0: Tons de luxo e minimalismo
        self.palettes = {
            "stable": QColor(0, 255, 140, 220),      # Esmeralda Vibrante
            "thinking": QColor(0, 150, 255, 220),   # Azul Cobalto 
            "alert": QColor(255, 200, 0, 220),      # Dourado Sutil
            "critical": QColor(255, 50, 50, 230),    # Vermelho Sangue
            "listening": QColor(255, 255, 255, 240), # Branco Neve (Ativo)
            "loading_model": QColor(0, 200, 255, 200),
            "calibrating": QColor(255, 255, 255, 150),
            "offline": QColor(50, 50, 50, 180)
        }
        self.current_color = self.palettes["stable"]
        
        # 🔥 60 FPS para fluidez máxima
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(16)  # 60 FPS - smooth animations
        
    def _animate(self):
        # 🔥 Animações fluidas e dinâmicas
        self.pulse_value = (self.pulse_value + 2) % 360
        self.rotation_inner -= 1.5
        self.rotation_mid += 0.8
        self.rotation_outer -= 0.4
        self.plasma_phase += 0.08
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
        
        # Pulsação ultra-sutil (Luxury feel)
        pulse_factor = (math.sin(math.radians(self.pulse_value)) + 1) / 2
        
        # 💎 CORE GEOMETRY: Hexágono minimalista em vez de círculo
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.rotation_inner * 0.2)
        
        # Linhas ultra-finas (0.5px - 1px)
        pen = QPen(self.current_color, 0.8)
        painter.setPen(pen)
        
        # Desenhar hexágonos concêntricos com transparência variável
        for i in range(3):
            r = (40 + i * 15 + pulse_factor * 5) * scale
            opacity = 255 - (i * 60)
            c = QColor(self.current_color)
            c.setAlpha(max(20, opacity))
            painter.setPen(QPen(c, 0.5))
            
            points = QPolygonF()
            for j in range(6):
                angle = math.radians(j * 60)
                points.append(QPointF(r * math.cos(angle), r * math.sin(angle)))
            painter.drawPolygon(points)
            
        painter.restore()

        # 💎 DATA RINGS (Thin & Discrete)
        # Outer ring - extremely thin dots
        self._draw_dotted_ring(painter, cx, cy, 90 * scale, self.rotation_outer, 60, QColor(self.current_color.red(), self.current_color.green(), self.current_color.blue(), 40))
        
        # Data Arc (Status OK / sync)
        self._draw_arc_data(painter, cx, cy, 85 * scale, self.sync_val, QColor(self.current_color.red(), self.current_color.green(), self.current_color.blue(), 150), 1.2 * scale)

        # 💎 CENTRAL STATUS (The Pulse)
        core_r = (25 + pulse_factor * 3) * scale
        glow = QRadialGradient(cx, cy, core_r)
        c_glow = QColor(self.current_color)
        c_glow.setAlpha(int(60 + 40 * pulse_factor))
        glow.setColorAt(0, c_glow)
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(glow)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(cx - core_r), int(cy - core_r), int(core_r * 2), int(core_r * 2))

        # 💎 LABEL MINIMALISTA
        painter.setPen(QPen(QColor(255, 255, 255, 180), 1))
        font = QFont("Segoe UI Semibold", int(7 * scale))
        painter.setFont(font)
        status_txt = f"SYNC // {int(self.sync_val)}%"
        painter.drawText(QRectF(cx - 50*scale, cy + 60*scale, 100*scale, 20*scale), Qt.AlignmentFlag.AlignCenter, status_txt)

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
        self.color = QColor(0, 150, 255, 180) # Cobalt Light

    def set_value(self, val):
        self.value = val
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        side = min(w, h) - 10
        rect = QRectF((w - side) / 2, (h - side) / 2, side, side)
        
        # 1. MINIMALIST BACKGROUND
        painter.setPen(QPen(QColor(255, 255, 255, 20), 0.5))
        painter.drawEllipse(rect)
        
        # 2. DATA SEGMENTS (Hyper-Link Style)
        segments = 40
        span = 360 / segments
        active_segments = int((self.value / 100.0) * segments)
        
        painter.setPen(QPen(self.color, 1.5))
        for i in range(active_segments):
            start = (90 - i * span) * 16
            painter.drawArc(rect, int(start), -int((span - 1) * 16))
        
        # 3. LABEL (Modern)
        painter.setPen(QPen(QColor(255, 255, 255, 220), 1))
        painter.setFont(QFont("Segoe UI", 7))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{int(self.value)}%\n{self.label}")

class ModernTelemetryWidget(QWidget):
    """
    Holographic telemetry display for Neural & Emotional states
    Stark HUD 2.0 Edition
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        # Stats Row 1: Memory & Network
        self.stats_row1 = QHBoxLayout()
        self.mem_gauge = EliteCircularGauge("MEMÓRIA")
        self.net_gauge = EliteCircularGauge("LATÊNCIA")
        self.stats_row1.addWidget(self.mem_gauge)
        self.stats_row1.addWidget(self.net_gauge)
        
        # Center: Emotion & Status (The Core Info)
        self.emotion_container = QWidget()
        em_layout = QVBoxLayout(self.emotion_container)
        em_layout.setSpacing(2)
        
        lbl = QLabel("NEURAL MAPPING // QUANTUM")
        lbl.setStyleSheet("color: rgba(255, 255, 255, 0.4); font-size: 8px; font-weight: regular; letter-spacing: 2px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.emotion_val = QLabel("ESTÁVEL")
        self.emotion_val.setStyleSheet("""
            color: #FFFFFF; 
            font-size: 10px; 
            font-family: 'Segoe UI Semibold'; 
            padding: 4px; 
            background: rgba(255, 255, 255, 0.02); 
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        """)
        self.emotion_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        em_layout.addWidget(lbl)
        em_layout.addWidget(self.emotion_val)
        
        # Stats Row 2: CPU & Sync
        self.stats_row2 = QHBoxLayout()
        self.cpu_gauge = EliteCircularGauge("NÚCLEO")
        self.sync_gauge = EliteCircularGauge("SINCRO")
        self.stats_row2.addWidget(self.cpu_gauge)
        self.stats_row2.addWidget(self.sync_gauge)

        # Assemble main layout
        main_stats_layout = QVBoxLayout()
        main_stats_layout.addLayout(self.stats_row1)
        main_stats_layout.addWidget(self.emotion_container)
        main_stats_layout.addLayout(self.stats_row2)
        
        self.setLayout(main_stats_layout)

    def update_stats(self, data: dict):
        """Update system-wide metrics"""
        if 'sync' in data:
            try:
                val = float(str(data['sync']).replace('%', ''))
                self.sync_gauge.set_value(val)
            except: pass
            
        if 'cpu' in data: self.cpu_gauge.set_value(float(data['cpu']))
        if 'memory' in data: self.mem_gauge.set_value(float(data['memory']))
        if 'network' in data: self.net_gauge.set_value(float(data['network']))
        
        if 'emotion' in data:
            em_map = {"NEUTRAL": "ESTÁVEL", "HAPPY": "OTIMISTA", "SAD": "ANALÍTICO", 
                      "ANGRY": "ALERTA", "THINKING": "PROCESSANDO"}
            emotion = data['emotion']
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
        painter.setPen(QPen(QColor(255, 255, 255, 40), 0.5))
        
        points = QPolygonF()
        for x in range(0, w, 2):
            # Complex wave simulation
            y = h/2 + math.sin(x*0.05 + self.phase) * 10 * math.sin(x*0.01)
            points.append(QPointF(x, y))
            
        painter.drawPolyline(points)
        # Add glow line
        painter.setPen(QPen(QColor(0, 150, 255, 120), 0.8))
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
        for i in range(5):
            lbl = QLabel("")
            lbl.setStyleSheet("color: rgba(255, 255, 255, 0.3); font-size: 8px; font-family: 'Segoe UI';")
            self.layout.addWidget(lbl)
            self.labels.append(lbl)

    def add_event(self, text):
        timestamp = time.strftime("%H:%M")
        self.events.insert(0, f"{timestamp} › {text}")
        if len(self.events) > 5:
            self.events.pop()
        
        for i, event in enumerate(self.events):
            self.labels[i].setText(event)
            opacity = 0.7 - (i * 0.12)
            self.labels[i].setStyleSheet(f"color: rgba(255, 255, 255, {opacity}); font-size: 8px; font-family: 'Segoe UI';")

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
    input_received = pyqtSignal(str)
    task_initiated = pyqtSignal(str)
    telemetry_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        
        # State
        self.is_compact = False
        
        # Configuration
        self.config_file = Path.home() / ".jarvis" / "hud_config.json"
        self.config_file.parent.mkdir(exist_ok=True)
        
        # Window setup
        self._setup_window()
        
        # UI Components
        self._setup_ui()
        
        # Load saved position
        self._load_position()
        
        # Elite Animations & Effects
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(500)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutQuint)
        
        # Setup keyboard shortcuts
        self._setup_shortcuts()
        
        # Connect signals
        self.status_changed.connect(self._on_status_changed)
        self.response_ready.connect(self._on_response_ready)
        self.input_received.connect(self._on_input_received)
        self.task_initiated.connect(self._on_task_initiated)
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
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(5, 15, 35, 250),
                    stop:1 rgba(2, 5, 15, 253)
                );
                border: 0.5px solid rgba(255, 255, 255, 0.15);
                border-radius: 2px;
            }
            QLabel {
                background: transparent;
                color: #FFFFFF;
                font-family: 'Segoe UI', 'Bahnschrift', 'Arial';
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
        
        # 3. INTERACTION STACK
        self.interaction_container = QWidget()
        stack_layout = QVBoxLayout(self.interaction_container)
        stack_layout.setContentsMargins(0, 0, 0, 0)
        stack_layout.setSpacing(10)

        # A. INPUT AREA (User Voice)
        self.input_label = QLabel("AGUARDANDO INPUT...")
        self.input_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.5); 
            font-size: 9px; 
            font-family: 'Segoe UI Semibold';
            padding: 8px; 
            border-bottom: 0.5px solid rgba(255, 255, 255, 0.1);
        """)
        stack_layout.addWidget(self.input_label)

        # B. ACTION AREA (System Intent)
        self.task_label = QLabel("PLAN: IDLE")
        self.task_label.setStyleSheet("""
            color: #00FF8C; 
            font-size: 8px; 
            font-family: 'Segoe UI Bold';
            letter-spacing: 1px;
            padding: 4px 8px;
            background: rgba(0, 255, 140, 0.05);
        """)
        stack_layout.addWidget(self.task_label)

        # C. RESPONSE AREA (Neural Typewriter)
        self.response_label = QLabel("SINGULARITY PROTOCOL ACTIVE...")
        self.response_label.setWordWrap(True)
        self.response_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.response_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.95); 
            font-size: 11px; 
            font-family: 'Segoe UI';
            padding: 12px; 
            background: rgba(255, 255, 255, 0.02);
            border-left: 1px solid rgba(255, 255, 255, 0.2);
            line-height: 1.5;
        """)
        self.response_label.setMinimumHeight(120)
        stack_layout.addWidget(self.response_label)
        
        layout.addWidget(self.interaction_container)
        
        # 4. TELEMETRY & FEED
        self.telemetry = ModernTelemetryWidget()
        layout.addWidget(self.telemetry)
        
        self.ticker = HUDEventTicker()
        layout.addWidget(self.ticker)
        
        # 5. FOOTER (Status & Settings Button)
        footer = QHBoxLayout()
        self.status_label = QLabel("SISTEMA NOMINAL")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: rgba(255, 255, 255, 0.6); font-family: 'Segoe UI'; font-size: 9px; letter-spacing: 2px;")
        
        self.btn_settings = QPushButton("···")
        self.btn_settings.setFixedSize(30, 20)
        self.btn_settings.setStyleSheet("""
            QPushButton {
                background: transparent; 
                border: 0.5px solid rgba(255, 255, 255, 0.2); 
                color: white;
                border-radius: 1px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
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
        
        # Ctrl+M to toggle Compact Mode
        mode_shortcut = QShortcut(QKeySequence("Ctrl+M"), self)
        mode_shortcut.activated.connect(self.toggle_compact_mode)
        
        # Escape to close
        escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        escape_shortcut.activated.connect(self.close)
        
    def _toggle_visibility(self):
        """Toggle HUD visibility with cinematic fade"""
        if self.isVisible():
            self.fade_anim.setStartValue(self.windowOpacity())
            self.fade_anim.setEndValue(0.0)
            self.fade_anim.finished.connect(self.hide)
            self.fade_anim.start()
        else:
            try: self.fade_anim.finished.disconnect(self.hide)
            except: pass
            self.show()
            self.fade_anim.setStartValue(0.0)
            self.fade_anim.setEndValue(0.95)
            self.fade_anim.start()
            
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
            # Store the initial global position and window position
            self._drag_start_global = event.globalPosition().toPoint()
            self._drag_start_window = self.pos()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """Handle dragging with global coordinates for multi-monitor support"""
        if self._is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            # Calculate delta from start
            delta = event.globalPosition().toPoint() - self._drag_start_global
            # Apply delta to initial window position
            self.move(self._drag_start_window + delta)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Stop dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            self._save_position()
            event.accept()

    def paintEvent(self, event):
        """High-Fidelity Cybernetic Rendering for JARVIS Stark 2.0"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        
        # 1. REMOVED EXPERIMENTAL 3D TRANSFORM (Causes glitches on movement)
        # We stick to flat, high-quality 2D rendering for stability

        
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
        
        # Neon Border (Ultra Thin luxury line)
        border_color = QColor(255, 255, 255, 40)
        painter.setPen(QPen(border_color, 0.5))
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
            painter.setBrush(QColor(255, 255, 255, alpha))
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
        self.telemetry.update_stats(data)
        
        # 3. Process Ticker events for critical load
        if cpu > 80:
            self.log_event(f"SYSTEM OVERLOAD: {cpu}%")
        
        # Force repaint for 60FPS fluid feel
        self.update()

    def update_telemetry(self, data: dict):
        """
        Public API: Atualiza telemetria do sistema (called from main.py).
        Converte chamada de método para signal emit (thread-safe).
        
        Args:
            data: Dict com keys: 'sync', 'emotion', 'pulse', 'cpu', etc.
        """
        # Emitir signal para processar no thread principal do Qt
        self.telemetry_updated.emit(data)

    def _draw_hex_grid(self, painter):
        """Draws an extremely subtle grid overlay"""
        painter.save()
        grid_size = 40
        painter.setPen(QPen(QColor(255, 255, 255, 10), 0.5))
        
        # Simple dots instead of hexagons for a cleaner look
        for x in range(0, self.width(), grid_size):
            for y in range(0, self.height(), grid_size):
                painter.drawPoint(x, y)
        painter.restore()

    def _draw_scanning_laser(self, painter):
        """Draws a moving horizontal laser line with glow"""
        self.scan_y += 3 * self.scan_dir
        if self.scan_y > self.height() or self.scan_y < 0:
            self.scan_dir *= -1
            
        laser_color = QColor(255, 255, 255, 30)
        gradient = QLinearGradient(0, self.scan_y - 10, 0, self.scan_y + 10)
        gradient.setColorAt(0, QColor(0, 0, 0, 0))
        gradient.setColorAt(0.5, laser_color)
        gradient.setColorAt(1, QColor(0, 0, 0, 0))
        
        painter.fillRect(5, self.scan_y - 10, self.width() - 10, 20, QBrush(gradient))
        painter.setPen(QPen(laser_color, 0.5))
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
        
        # Singularity 2.0 Technical Mapping
        status_map = {
            "idle": "NOMINAL",
            "listening": "BIOMETRIC CAPTURE",
            "thinking": "NEURAL PROCESSING",
            "speaking": "RESONANCE ACTIVE",
            "error": "L-SYSTEM OVERLOAD",
            "success": "SYNC COMPLETE"
        }
        
        display_status = status_map.get(self.status, status.upper())
        self.status_label.setText(display_status)
        self.update() # Trigger 3D render update
        
    def _on_response_ready(self, text: str):
        """Handle new response with typewriter effect and glow pulse"""
        self.full_response = text
        self.current_display_text = ""
        self.response_label.setText("")
        
        # Start Typewriter
        self.type_timer.start(15) # Faster for modern feel
        
        # Glow flash on new message
        if hasattr(self, 'reactor'):
            self.reactor.pulse_value = 0 # Reset pulse for impact
        
        # Fade and Slide animation for the label
        eff = QGraphicsOpacityEffect(self.response_label)
        self.response_label.setGraphicsEffect(eff)
        
        anim = QPropertyAnimation(eff, b"opacity")
        anim.setDuration(600)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutQuint)
        anim.start()

    def _update_typewriter(self):
        """Animated character by character reveal"""
        if len(self.current_display_text) < len(self.full_response):
            next_chars = self.full_response[len(self.current_display_text):len(self.current_display_text)+2]
            self.current_display_text += next_chars
            self.response_label.setText(self.current_display_text)
        else:
            self.type_timer.stop()

    def toggle_compact_mode(self):
        """Switch between full telemetric view and reduced core view with opacity blending"""
        self.is_compact = not self.is_compact
        
        # Transition components using Opacity effects
        for widget in [self.telemetry, self.ticker]:
            eff = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(eff)
            anim = QPropertyAnimation(eff, b"opacity")
            anim.setDuration(400)
            anim.setStartValue(1.0 if not self.is_compact else 0.0)
            anim.setEndValue(0.0 if self.is_compact else 1.0)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            if self.is_compact:
                anim.finished.connect(widget.hide)
            else:
                widget.show()
            anim.start()
        
        # Smooth Resize Animation
        target_height = 340 if self.is_compact else 680
        self.anim_resize = QPropertyAnimation(self, b"size")
        self.anim_resize.setDuration(600)
        self.anim_resize.setEndValue(QSize(self.width(), target_height))
        self.anim_resize.setEasingCurve(QEasingCurve.Type.OutExpo) # Snappy luxury curve
        self.anim_resize.start()
        
        # Visual protocol log
        self.log_event(f"PROTOCOL: {'COMPACT' if self.is_compact else 'TACTICAL'}")

    def _on_input_received(self, text: str):
        """Updates the 'Heard' text label"""
        self.input_label.setText(f"HEARD › {text.upper()}")

    def _on_task_initiated(self, task: str):
        """Updates the current system intent/action"""
        self.task_label.setText(f"PLAN › {task.upper()}")

    # Public API (thread-safe via signals)
    def update_input(self, text: str):
        """Update what the system heard (can be called from any thread)"""
        self.input_received.emit(text)

    def update_task(self, task: str):
        """Update current action/intent (can be called from any thread)"""
        self.task_initiated.emit(task)

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
