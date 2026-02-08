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
    QRadialGradient, QKeySequence, QShortcut, QPolygonF
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
        
        # Color schemes for different states
        self.colors = {
            "idle": QColor(100, 200, 255, 200),      # Cyan
            "listening": QColor(100, 255, 100, 200), # Green
            "thinking": QColor(100, 100, 255, 200),  # Blue
            "speaking": QColor(255, 165, 0, 200),    # Orange
            "error": QColor(255, 50, 50, 200),       # Red
            "success": QColor(50, 255, 150, 200),    # Bright Green
            # Emotion Mappings
            "happy": QColor(255, 255, 100, 200),     # Yellow
            "sad": QColor(100, 100, 200, 200),       # Soft Blue
            "angry": QColor(255, 0, 0, 220),         # Sharp Red
            "surprise": QColor(255, 100, 255, 200),  # Pink
            "fear": QColor(100, 0, 100, 200),        # Purple
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
        
    def paintEvent(self, event):
        """Paint the animated reactor core"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        
        # Calculate pulse size
        import math
        pulse_factor = (math.sin(math.radians(self.pulse_value)) + 1) / 2
        
        # Outer glow (largest)
        glow_radius = 80 + (pulse_factor * 20)
        glow_gradient = QRadialGradient(center_x, center_y, glow_radius)
        glow_color = QColor(self.current_color)
        glow_color.setAlpha(50 + int(pulse_factor * 100))
        glow_gradient.setColorAt(0, glow_color)
        glow_gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(glow_gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            int(center_x - glow_radius),
            int(center_y - glow_radius),
            int(glow_radius * 2),
            int(glow_radius * 2)
        )
        
        # Middle ring (rotating)
        ring_radius = 60
        painter.setPen(QPen(self.current_color, 3))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Draw rotating arcs
        for i in range(3):
            start_angle = (self.rotation + i * 120) * 16
            span_angle = 80 * 16
            painter.drawArc(
                int(center_x - ring_radius),
                int(center_y - ring_radius),
                int(ring_radius * 2),
                int(ring_radius * 2),
                start_angle,
                span_angle
            )
        
        # Inner ring (pulsing)
        inner_radius = 40 + (pulse_factor * 5)
        painter.setPen(QPen(self.current_color, 2))
        painter.drawEllipse(
            int(center_x - inner_radius),
            int(center_y - inner_radius),
            int(inner_radius * 2),
            int(inner_radius * 2)
        )
        
        # Sub-Core details (Holographic details)
        core_radius = 25  # Base core radius
        painter.setPen(QPen(glow_color, 1))
        for i in range(12):
            angle = (self.rotation + i * 30)
            rad = math.radians(angle)
            x1 = center_x + math.cos(rad) * inner_radius
            y1 = center_y + math.sin(rad) * inner_radius
            x2 = center_x + math.cos(rad) * core_radius
            y2 = center_y + math.sin(rad) * core_radius
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Core (solid pulsing)
        core_radius_pulse = core_radius + (pulse_factor * 5)
        core_gradient = QRadialGradient(center_x, center_y, core_radius_pulse)
        core_color = QColor(self.current_color)
        core_color.setAlpha(255)
        core_gradient.setColorAt(0, core_color)
        core_gradient.setColorAt(1, QColor(self.current_color.red(), 
                                           self.current_color.green(),
                                           self.current_color.blue(), 150))
        painter.setBrush(QBrush(core_gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            int(center_x - core_radius_pulse),
            int(center_y - core_radius_pulse),
            int(core_radius_pulse * 2),
            int(core_radius_pulse * 2)
        )

class EliteCircularGauge(QWidget):
    """Modern circular gauge for system metrics"""
    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 60)
        self.value = 0.0
        self.label = label
        self.color = QColor(100, 200, 255, 200)

    def set_value(self, val):
        self.value = val
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = QRectF(5, 5, 50, 50)
        
        # Background ring
        painter.setPen(QPen(QColor(100, 200, 255, 30), 2))
        painter.drawEllipse(rect)
        
        # Value arc
        painter.setPen(QPen(self.color, 3))
        span_angle = -int(self.value * 3.6 * 16)
        painter.drawArc(rect, 90 * 16, span_angle)
        
        # Label
        painter.setPen(QPen(QColor(100, 200, 255, 150), 1))
        painter.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
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
        
        self.neural_gauge = EliteCircularGauge("SYNC")
        self.system_gauge = EliteCircularGauge("CPU")
        
        # Emotion stays as text but with better style
        self.emotion_container = QWidget()
        em_layout = QVBoxLayout(self.emotion_container)
        lbl = QLabel("USER EMOTION")
        lbl.setStyleSheet("color: rgba(100, 200, 255, 0.7); font-size: 8px; font-weight: bold;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.emotion_val = QLabel("NEUTRAL")
        self.emotion_val.setStyleSheet("color: white; font-size: 11px; font-family: 'Consolas'; font-weight: bold;")
        self.emotion_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        em_layout.addWidget(lbl)
        em_layout.addWidget(self.emotion_val)
        
        self.layout.addWidget(self.neural_gauge)
        self.layout.addWidget(self.emotion_container)
        self.layout.addWidget(self.system_gauge)

    def update_stats(self, sync=None, emotion=None, pulse=None, cpu=None):
        if sync:
            try:
                val = float(sync.replace('%',''))
                self.neural_gauge.set_value(val)
            except: pass
        if emotion: self.emotion_val.setText(emotion.upper())
        if cpu is not None:
            self.system_gauge.set_value(cpu)
        elif pulse:
            # Fallback if raw CPU not sent
            self.system_gauge.set_value(75 if pulse == "ADAPTIVE" else (95 if pulse == "CRITICAL" else 25))


class HUDEventTicker(QWidget):
    """Scrolling ticker for system events"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
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
        
        # Neural Typewriter
        self.full_response = ""
        self.current_display_text = ""
        self.type_timer = QTimer()
        self.type_timer.timeout.connect(self._update_typewriter)
        
        # Animation loop
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.update)
        self.ui_timer.start(33) # 30 FPS for grid/laser
        
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
        
        # Default size
        self.resize(400, 600)
        
    def _setup_ui(self):
        """Create UI components"""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Apply glassmorphism style with advanced effects
        central.setStyleSheet("""
            QWidget#main_panel {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(10, 15, 30, 245),
                    stop:0.5 rgba(15, 25, 45, 240),
                    stop:1 rgba(10, 15, 30, 245)
                );
                border-radius: 20px;
                border: 2px solid rgba(100, 200, 255, 0.4);
            }
            QLabel {
                background: transparent;
                color: #64C8FF;
                font-family: 'Segoe UI', Arial;
            }
            QPushButton {
                background: rgba(100, 200, 255, 0.1);
                border: 1px solid rgba(100, 200, 255, 0.3);
                border-radius: 8px;
                color: #64C8FF;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(100, 200, 255, 0.2);
                border: 1px solid rgba(100, 200, 255, 0.6);
            }
        """)
        central.setObjectName("main_panel")
        
        # Main layout
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # ======================================================================
        # HEADER - Title and drag handle
        # ======================================================================
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        
        # Drag handle
        drag_handle = QLabel("⋮⋮")
        drag_handle.setStyleSheet("""
            QLabel {
                color: rgba(100, 200, 255, 0.6);
                font-size: 16px;
                padding: 5px;
            }
        """)
        drag_handle.setCursor(Qt.CursorShape.SizeAllCursor)
        header_layout.addWidget(drag_handle)
        
        # Title
        title = QLabel("J.A.R.V.I.S.")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("""
            QLabel {
                color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #64C8FF,
                    stop:0.5 #0080FF,
                    stop:1 #64C8FF
                );
                letter-spacing: 4px;
            }
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 100, 100, 0.2);
                border: 1px solid rgba(255, 100, 100, 0.4);
                border-radius: 15px;
                font-size: 20px;
                font-weight: bold;
                padding: 0;
            }
            QPushButton:hover {
                background: rgba(255, 100, 100, 0.4);
            }
        """)
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        
        layout.addWidget(header_container)
        
        # ======================================================================
        # REACTOR CORE
        # ======================================================================
        self.reactor = ModernReactorCore()
        self.reactor.setFixedHeight(200)
        layout.addWidget(self.reactor)
        
        # ======================================================================
        # STATUS LABEL
        # ======================================================================
        self.status_label = QLabel("IDLE")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.status_label.setStyleSheet("""
            QLabel {
                color: #64C8FF;
                letter-spacing: 3px;
                padding: 10px;
                background: rgba(100, 200, 255, 0.1);
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # ======================================================================
        # RESPONSE TEXT
        # ======================================================================
        self.response_label = QLabel("Sistemas online...")
        self.response_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.response_label.setFont(QFont("Segoe UI", 11))
        self.response_label.setWordWrap(True)
        self.response_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                padding: 15px;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                line-height: 1.5;
            }
        """)
        self.response_label.setMinimumHeight(120)
        layout.addWidget(self.response_label)

        # ======================================================================
        # TELEMETRY WIDGET (Quantum Core)
        # ======================================================================
        self.telemetry = ModernTelemetryWidget()
        layout.addWidget(self.telemetry)
        
        # ======================================================================
        # EVENT TICKER (Stark Grade)
        # ======================================================================
        self.ticker = HUDEventTicker()
        layout.addWidget(self.ticker)
        
        layout.addStretch()
        
        # ======================================================================
        # FOOTER - Quick actions
        # ======================================================================
        footer = QHBoxLayout()
        footer.setSpacing(10)
        
        # Minimize button
        min_btn = QPushButton("_")
        min_btn.setFixedSize(40, 30)
        min_btn.clicked.connect(self.showMinimized)
        footer.addWidget(min_btn)
        
        footer.addStretch()
        
        # Info label
        info = QLabel("Press Ctrl+H to toggle")
        info.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.5);
                font-size: 9px;
            }
        """)
        footer.addWidget(info)
        
        layout.addLayout(footer)
        
        # Size grip for resizing
        self.size_grip = QSizeGrip(central)
        self.size_grip.setFixedSize(20, 20)
        self.size_grip.setStyleSheet("""
            QSizeGrip {
                background: rgba(100, 200, 255, 0.3);
                border-radius: 5px;
            }
        """)
        
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
        """Stop dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            self._save_position()
            event.accept()
            
    def paintEvent(self, event):
        """Draw advanced holographic effects"""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 1. HOLOGRAPHIC HEX-GRID (Subtle)
        self._draw_hex_grid(painter)
        
        # 2. SCANNING LASER BORDER
        self._draw_scanning_laser(painter)
        
        # 3. HOLOGRAPHIC SCANLINES & JITTER
        scanline_color = QColor(100, 200, 255, 12)
        painter.setPen(scanline_color)
        
        offset = int(time.time() * 30) % 20
        glitch_y = random.randint(0, self.height()) if random.random() > 0.98 else -1
        
        for y in range(offset, self.height(), 4):
            jitter = random.randint(-2, 2) if y == glitch_y else 0
            painter.drawLine(10 + jitter, y, self.width() - 10 + jitter, y)
            
        # 4. CORNER BRACKETS (Glow Effect)
        pen = QPen(QColor(100, 200, 255, 180), 2)
        painter.setPen(pen)
        size = 20
        # Corners
        painter.drawLine(5, 5, 5 + size, 5); painter.drawLine(5, 5, 5, 5 + size)
        painter.drawLine(self.width() - 5, 5, self.width() - 5 - size, 5); painter.drawLine(self.width() - 5, 5, self.width() - 5, 5 + size)
        painter.drawLine(5, self.height() - 5, 5 + size, self.height() - 5); painter.drawLine(5, self.height() - 5, 5, self.height() - 5 - size)
        painter.drawLine(self.width() - 5, self.height() - 5, self.width() - 5 - size, self.height() - 5); painter.drawLine(self.width() - 5, self.height() - 5, self.width() - 5, self.height() - 5 - size)

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
        """Handle status change (thread-safe)"""
        self.reactor.set_status(status)
        self.status_label.setText(status.upper())
        
        # Animate status label
        effect = QGraphicsOpacityEffect()
        self.status_label.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(300)
        animation.setStartValue(0.5)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        animation.start()
        
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
        
    def update_telemetry(self, stats: dict):
        """Update telemetry stats (can be called from any thread)"""
        self.telemetry_updated.emit(stats)

    def _on_telemetry_updated(self, stats: dict):
        """Handle telemetry update (thread-safe)"""
        if hasattr(self, 'telemetry'):
            self.telemetry.update_stats(
                sync=stats.get('sync'),
                emotion=stats.get('emotion'),
                pulse=stats.get('pulse'),
                cpu=stats.get('cpu')
            )
            
        if 'emotion' in stats:
            # Sync reactor color with emotion
            self.reactor.set_status(stats['emotion'].lower())
        
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
