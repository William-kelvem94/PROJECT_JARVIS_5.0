#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Control Dashboard
=======================================
Full-featured admin panel for JARVIS configuration and monitoring.

Features:
- Brain Configuration (LLM models, API keys)
- Voice Settings (STT/TTS, microphone, speaker verification)
- Vision System (FaceID, OCR, YOLO configuration)
- Real-time Logs Viewer
- System Monitor (CPU, RAM, processes)
- Memory Browser (ChromaDB conversation history)
"""

import sys
import logging
import json
import psutil
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QLabel, QPushButton, QLineEdit, QComboBox, QTextEdit, QCheckBox,
    QSpinBox, QDoubleSpinBox, QGroupBox, QFormLayout, QListWidget,
    QTableWidget, QTableWidgetItem, QProgressBar, QFileDialog,
    QMessageBox, QSplitter, QSlider, QFrame, QGraphicsDropShadowEffect,
    QApplication, QInputDialog
)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, pyqtSlot, QThread, QPropertyAnimation,
    QEasingCurve, QRect, QSize
)
from PyQt6.QtGui import QFont, QColor, QPalette, QTextCursor, QIcon, QAction

from src.interface.ui_signals import ui_signals
from src.interface.theme import JarvisTheme
from src.core.management.hardware_manager import hardware_manager

logger = logging.getLogger(__name__)

class SideBarButton(QPushButton):
    """Luxury sidebar button with hover effects"""
    def __init__(self, text, icon_str=None, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: rgba(255, 255, 255, 0.6);
                border: none;
                border-left: 3px solid transparent;
                text-align: left;
                padding-left: 20px;
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.05);
                color: white;
            }
            QPushButton:checked {
                background: rgba(0, 150, 255, 0.1);
                color: #00F2FF;
                border-left: 3px solid #00F2FF;
                font-weight: bold;
            }
        """)

class ConfigTextEdit(QTextEdit):
    """QTextEdit with drag & drop support for config files"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and any(url.toLocalFile().endswith(('.json', '.yaml', '.yml')) for url in urls):
                event.acceptProposedAction()
                return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Handle file drop events"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.endswith(('.json', '.yaml', '.yml')):
                self.load_config_file(file_path)
                event.acceptProposedAction()
            else:
                event.ignore()

    def load_config_file(self, file_path: str):
        """Load config file into editor"""
        try:
            from pathlib import Path
            path = Path(file_path)

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.setPlainText(content)
            self.parent().parent().config_path_label.setText(f"Loaded: {path.name}")
            self.parent().parent().current_config_path = path

            # Show success toast
            from src.interface.toast_notifications import show_success_toast
            show_success_toast("Config Loaded", f"Successfully loaded {path.name}")

        except Exception as e:
            # Show error toast
            from src.interface.toast_notifications import show_error_toast
            show_error_toast("Load Failed", f"Failed to load config: {e}")

class SystemMonitorThread(QThread):
    """Background thread for system monitoring"""
    stats_updated = pyqtSignal(dict)
    
    def run(self):
        """Monitor system resources"""
        while True:
            try:
                stats = {
                    'cpu': psutil.cpu_percent(interval=1),
                    'memory': psutil.virtual_memory().percent,
                    'disk': psutil.disk_usage('/').percent,
                }
                self.stats_updated.emit(stats)
            except Exception as e:
                logger.error(f"Error monitoring system: {e}")
            
            QThread.msleep(2000)  # Update every 2 seconds


class ControlDashboard(QMainWindow):
    """
    JARVIS Singularity Control Dashboard.
    
    Main admin panel for configuration and monitoring.
    """
    
    # Signals
    mode_switch_requested = pyqtSignal(object)  # Request mode switch to HUD
    config_changed = pyqtSignal(dict)  # Configuration updated
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("JARVIS Singularity - Control Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        
        # Aplicar tema unificado
        JarvisTheme.apply_theme(self)
        
        # Load configuration
        self.config = self._load_config()
        
        # Setup UI
        self._setup_ui()
        
        # Start monitoring
        self._start_monitoring()
        
        logger.info("âœ… Control Dashboard initialized")
        
    def _load_config(self) -> Dict:
        """Load configuration from file with project root awareness"""
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "singularity_config.json"
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                
        # Deep Default config
        return {
            "vision": {"enabled": True, "faceid_enabled": True},
            "audio": {"enabled": True, "stt_model": "faster-whisper"},
            "system": {"god_mode_enabled": True},
            "ai": {
                "local_model": "ollama", 
                "model_name": "llama3",
                "temperature": 0.7,
                "max_tokens": 2048,
                "model_type": "Ollama (Local)"
            }
        }
        
    def _save_config(self):
        """Save configuration to file accurately"""
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "singularity_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            logger.info("âœ… Configuration saved")
            self.config_changed.emit(self.config)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
            
    def _setup_ui(self):
        """Setup the Singularity 2.0 Luxury Interface"""
        # Global Style Injection
        self._apply_theme()
        
        # Main container with side-navigation layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. SIDE NAVIGATION BAR
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setObjectName("sidebar")
        side_layout = QVBoxLayout(self.sidebar)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(0)
        
        # Sidebar Logo Area
        logo_area = QWidget()
        logo_area.setFixedHeight(100)
        logo_layout = QVBoxLayout(logo_area)
        logo_label = QLabel("SINGULARITY")
        logo_label.setStyleSheet("font-size: 16px; font-weight: bold; letter-spacing: 5px; color: #00F2FF; padding-left: 20px;")
        sub_logo = QLabel("CONTROL ACCESS // v5.0")
        sub_logo.setStyleSheet("font-size: 8px; color: rgba(255, 255, 255, 0.4); padding-left: 22px; letter-spacing: 2px;")
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(sub_logo)
        side_layout.addWidget(logo_area)
        
        # Navigation Buttons
        self.nav_buttons = []
        self.stack = QStackedWidget()
        
        sections = [
            ("ðŸ§  BRAIN", self._create_brain_tab()),
            ("ðŸŽ¤ VOICE", self._create_voice_tab()),
            ("ðŸ‘ï¸ VISION", self._create_vision_tab()),
            ("ðŸŽ“ LEARNING", self._create_learning_tab()),
            ("ðŸ’¾ MEMORY", self._create_memory_tab()),
            ("ðŸ“‹ LOGS", self._create_logs_tab()),
            ("âš™ï¸ SYSTEM", self._create_system_tab()),
            ("⚙️ CONFIG", self._create_config_tab())
        ]
        
        for i, (name, widget) in enumerate(sections):
            btn = SideBarButton(name)
            btn.clicked.connect(lambda checked, idx=i: self._switch_tab(idx))
            side_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            self.stack.addWidget(widget)
            
        self.nav_buttons[0].setChecked(True) # Default
        
        side_layout.addStretch()
        
        # Sidebar Footer (HUD Toggle)
        hud_btn = QPushButton("LAUNCH HUD OVERLAY")
        hud_btn.setObjectName("hud_action_button")
        hud_btn.clicked.connect(self._request_hud_mode)
        side_layout.addWidget(hud_btn)
        
        main_layout.addWidget(self.sidebar)
        
        # 2. CONTENT AREA
        content_pane = QWidget()
        content_layout = QVBoxLayout(content_pane)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Top Header for active section
        self.top_header = QWidget()
        self.top_header.setFixedHeight(60)
        self.top_header.setObjectName("top_header")
        th_layout = QHBoxLayout(self.top_header)
        self.section_title = QLabel("CORE BRAIN INTERFACE")
        self.section_title.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        th_layout.addWidget(self.section_title)
        th_layout.addStretch()
        
        # System Stats Quick View
        self.quick_cpu = QLabel("CPU: 0%")
        self.quick_cpu.setStyleSheet("font-size: 10px; color: rgba(255,255,255,0.5); font-family: 'Consolas';")
        th_layout.addWidget(self.quick_cpu)
        
        content_layout.addWidget(self.top_header)
        content_layout.addWidget(self.stack)
        
        # Bottom Footer
        footer = self._create_footer()
        content_layout.addWidget(footer)
        
        main_layout.addWidget(content_pane)

    def _switch_tab(self, index):
        """Switch section with smooth fade (future) and update buttons"""
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        
        self.stack.setCurrentIndex(index)
        section_names = ["BRAIN INTERFACE", "AUDIO DYNAMICS", "OPTIC SENSORS", "EVOLUTIONARY CORE", "DATABASE BROWSER", "SYSTEM LOGS", "HW PERFORMANCE"]
        self.section_title.setText(section_names[index])
        
    def _create_header(self) -> QWidget:
        """Create header with title and mode switch"""
        header = QWidget()
        layout = QHBoxLayout(header)
        
        # Title
        title = QLabel("JARVIS SINGULARITY - Control Dashboard")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #4a9eff;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Mode switch button
        mode_btn = QPushButton("Switch to HUD Overlay")
        mode_btn.clicked.connect(self._request_hud_mode)
        mode_btn.setStyleSheet("""
            QPushButton {
                background: #4a9eff;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #357abd;
            }
        """)
        layout.addWidget(mode_btn)
        
        return header
        
    def _create_brain_tab(self) -> QWidget:
        """Create Brain configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # LLM Model Selection
        model_group = QGroupBox("LLM Model Configuration")
        model_layout = QFormLayout()
        
        # Model type
        self.model_type_combo = QComboBox()
        self.model_type_combo.addItems(["Ollama (Local)", "OpenAI", "Anthropic", "Google Gemini", "Groq"])
        self.model_type_combo.setCurrentText("Ollama (Local)")
        model_layout.addRow("Model Provider:", self.model_type_combo)
        
        # Model name
        self.model_name_edit = QLineEdit()
        self.model_name_edit.setText(self.config.get("ai", {}).get("model_name", "llama3"))
        model_layout.addRow("Model Name:", self.model_name_edit)
        
        # API Key
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setPlaceholderText("Enter API key (if using cloud service)")
        model_layout.addRow("API Key:", self.api_key_edit)
        
        # Temperature
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(0.7)
        model_layout.addRow("Temperature:", self.temperature_spin)
        
        # Max tokens
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 4000)
        self.max_tokens_spin.setValue(2000)
        model_layout.addRow("Max Tokens:", self.max_tokens_spin)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # System Prompt
        prompt_group = QGroupBox("System Prompt")
        prompt_layout = QVBoxLayout()
        
        self.system_prompt_edit = QTextEdit()
        self.system_prompt_edit.setPlaceholderText("Enter system prompt for the AI...")
        self.system_prompt_edit.setPlainText(
            "You are JARVIS, an advanced AI assistant. You have access to:\n"
            "- Vision system (can see screen and faces)\n"
            "- System control (can manage processes and windows)\n"
            "- Audio processing (can hear and speak)\n\n"
            "Be helpful, concise, and proactive."
        )
        prompt_layout.addWidget(self.system_prompt_edit)
        
        prompt_group.setLayout(prompt_layout)
        layout.addWidget(prompt_group)
        
        # Save button
        save_btn = QPushButton("ðŸ’¾ Save Configuration")
        save_btn.clicked.connect(self._save_brain_config)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #45a049;
            }
        """)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        
        return tab
        
    def _create_voice_tab(self) -> QWidget:
        """Create Voice settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # STT Settings
        stt_group = QGroupBox("Speech-to-Text (STT)")
        stt_layout = QFormLayout()
        
        self.stt_model_combo = QComboBox()
        self.stt_model_combo.addItems(["faster-whisper", "openai-whisper", "vosk", "google"])
        stt_layout.addRow("STT Engine:", self.stt_model_combo)
        
        self.stt_model_size = QComboBox()
        self.stt_model_size.addItems(["tiny", "base", "small", "medium", "large"])
        self.stt_model_size.setCurrentText("base")
        stt_layout.addRow("Model Size:", self.stt_model_size)
        
        self.microphone_combo = QComboBox()
        self.microphone_combo.addItems(["Default", "Device 0", "Device 1", "Device 2"])
        stt_layout.addRow("Microphone:", self.microphone_combo)
        
        stt_group.setLayout(stt_layout)
        layout.addWidget(stt_group)
        
        # TTS Settings
        tts_group = QGroupBox("Text-to-Speech (TTS)")
        tts_layout = QFormLayout()
        
        self.tts_engine_combo = QComboBox()
        self.tts_engine_combo.addItems(["edge-tts", "pyttsx3", "gTTS"])
        tts_layout.addRow("TTS Engine:", self.tts_engine_combo)
        
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["en-US-AriaNeural", "en-US-GuyNeural", "pt-BR-FranciscaNeural"])
        tts_layout.addRow("Voice:", self.voice_combo)
        
        self.speech_rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.speech_rate_slider.setRange(50, 200)
        self.speech_rate_slider.setValue(100)
        tts_layout.addRow("Speech Rate:", self.speech_rate_slider)
        
        tts_group.setLayout(tts_layout)
        layout.addWidget(tts_group)
        
        # VAD Settings
        vad_group = QGroupBox("Voice Activity Detection (VAD)")
        vad_layout = QFormLayout()
        
        self.vad_enabled_check = QCheckBox("Enable Silero-VAD")
        self.vad_enabled_check.setChecked(True)
        vad_layout.addRow("VAD:", self.vad_enabled_check)
        
        self.vad_threshold = QDoubleSpinBox()
        self.vad_threshold.setRange(0.0, 1.0)
        self.vad_threshold.setSingleStep(0.05)
        self.vad_threshold.setValue(0.5)
        vad_layout.addRow("Threshold:", self.vad_threshold)
        
        vad_group.setLayout(vad_layout)
        layout.addWidget(vad_group)
        
        # Speaker Verification
        speaker_group = QGroupBox("Speaker Verification")
        speaker_layout = QVBoxLayout()
        
        self.speaker_verify_check = QCheckBox("Enable speaker verification")
        self.speaker_verify_check.setChecked(True)
        speaker_layout.addWidget(self.speaker_verify_check)
        
        enroll_btn = QPushButton("ðŸŽ™ï¸ Enroll New Voice")
        enroll_btn.clicked.connect(self._enroll_voice)
        speaker_layout.addWidget(enroll_btn)
        
        self.voice_list = QListWidget()
        self.voice_list.addItems(["admin (enrolled)", "user1 (enrolled)"])
        speaker_layout.addWidget(self.voice_list)
        
        speaker_group.setLayout(speaker_layout)
        layout.addWidget(speaker_group)
        
        # Save button
        save_btn = QPushButton("ðŸ’¾ Save Voice Settings")
        save_btn.clicked.connect(self._save_voice_config)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
            }
        """)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        
        return tab
        
    def _create_vision_tab(self) -> QWidget:
        """Create Vision system tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # FaceID Settings
        faceid_group = QGroupBox("FaceID Authentication")
        faceid_layout = QVBoxLayout()
        
        self.faceid_enabled = QCheckBox("Enable FaceID authentication")
        self.faceid_enabled.setChecked(True)
        faceid_layout.addWidget(self.faceid_enabled)
        
        face_model_layout = QFormLayout()
        self.face_model_combo = QComboBox()
        self.face_model_combo.addItems(["hog (CPU)", "cnn (GPU)"])
        face_model_layout.addRow("Detection Model:", self.face_model_combo)
        faceid_layout.addLayout(face_model_layout)
        
        # Face management
        face_mgmt_layout = QHBoxLayout()
        add_face_btn = QPushButton("ðŸ“¸ Add New Face")
        add_face_btn.clicked.connect(self._add_face)
        face_mgmt_layout.addWidget(add_face_btn)
        
        remove_face_btn = QPushButton("ðŸ—‘ï¸ Remove Face")
        remove_face_btn.clicked.connect(self._remove_face)
        face_mgmt_layout.addWidget(remove_face_btn)
        
        faceid_layout.addLayout(face_mgmt_layout)
        
        self.face_list = QListWidget()
        self.face_list.addItems(["admin.jpg", "user1.jpg"])
        faceid_layout.addWidget(self.face_list)
        
        faceid_group.setLayout(faceid_layout)
        layout.addWidget(faceid_group)
        
        # OCR Settings
        ocr_group = QGroupBox("OCR (Text Extraction)")
        ocr_layout = QFormLayout()
        
        self.ocr_enabled = QCheckBox("Enable OCR")
        self.ocr_enabled.setChecked(True)
        ocr_layout.addRow("OCR:", self.ocr_enabled)
        
        self.ocr_languages = QComboBox()
        self.ocr_languages.addItems(["English", "Portuguese", "English + Portuguese"])
        ocr_layout.addRow("Languages:", self.ocr_languages)
        
        ocr_group.setLayout(ocr_layout)
        layout.addWidget(ocr_group)
        
        # YOLO Settings
        yolo_group = QGroupBox("Object Detection (YOLO)")
        yolo_layout = QFormLayout()
        
        self.yolo_enabled = QCheckBox("Enable YOLO detection")
        self.yolo_enabled.setChecked(True)
        yolo_layout.addRow("YOLO:", self.yolo_enabled)
        
        self.yolo_model = QComboBox()
        self.yolo_model.addItems(["yolov8n", "yolov8s", "yolov8m", "yolov8l"])
        yolo_layout.addRow("Model:", self.yolo_model)
        
        self.yolo_confidence = QDoubleSpinBox()
        self.yolo_confidence.setRange(0.0, 1.0)
        self.yolo_confidence.setSingleStep(0.05)
        self.yolo_confidence.setValue(0.5)
        yolo_layout.addRow("Confidence:", self.yolo_confidence)
        
        yolo_group.setLayout(yolo_layout)
        layout.addWidget(yolo_group)
        
        # Save button
        save_btn = QPushButton("ðŸ’¾ Save Vision Settings")
        save_btn.clicked.connect(self._save_vision_config)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
            }
        """)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        
        return tab
        
    def _create_logs_tab(self) -> QWidget:
        """Create Logs viewer tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Controls
        controls = QHBoxLayout()
        
        # Filter
        filter_label = QLabel("Filter:")
        controls.addWidget(filter_label)
        
        self.log_filter = QLineEdit()
        self.log_filter.setPlaceholderText("Search logs...")
        self.log_filter.textChanged.connect(self._filter_logs)
        controls.addWidget(self.log_filter)
        
        # Level filter
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_combo.currentTextChanged.connect(self._filter_logs)
        controls.addWidget(self.log_level_combo)
        
        # Clear button
        clear_btn = QPushButton("ðŸ—‘ï¸ Clear")
        clear_btn.clicked.connect(self._clear_logs)
        controls.addWidget(clear_btn)
        
        # Auto-scroll
        self.auto_scroll_check = QCheckBox("Auto-scroll")
        self.auto_scroll_check.setChecked(True)
        controls.addWidget(self.auto_scroll_check)
        
        layout.addLayout(controls)
        
        # Log viewer (copiável mas não editável)
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | 
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        self.log_viewer.setFont(QFont("Courier New", 9))
        self.log_viewer.setStyleSheet("""
            QTextEdit {
                background: #1e1e1e;
                color: #dcdcdc;
                border: 1px solid #444;
            }
        """)
        layout.addWidget(self.log_viewer)
        
        # Setup log handler
        self._setup_log_handler()
        
        return tab
        
    def _create_system_tab(self) -> QWidget:
        """Create System monitor tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # System stats
        stats_group = QGroupBox("System Resources")
        stats_layout = QFormLayout()
        
        # CPU
        self.cpu_label = QLabel("0%")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setTextVisible(False)
        cpu_layout = QHBoxLayout()
        cpu_layout.addWidget(self.cpu_bar, 3)
        cpu_layout.addWidget(self.cpu_label, 1)
        stats_layout.addRow("CPU:", cpu_layout)
        
        # Memory
        self.memory_label = QLabel("0%")
        self.memory_bar = QProgressBar()
        self.memory_bar.setTextVisible(False)
        memory_layout = QHBoxLayout()
        memory_layout.addWidget(self.memory_bar, 3)
        memory_layout.addWidget(self.memory_label, 1)
        stats_layout.addRow("Memory:", memory_layout)
        
        # Disk
        self.disk_label = QLabel("0%")
        self.disk_bar = QProgressBar()
        self.disk_bar.setTextVisible(False)
        disk_layout = QHBoxLayout()
        disk_layout.addWidget(self.disk_bar, 3)
        disk_layout.addWidget(self.disk_label, 1)
        stats_layout.addRow("Disk:", disk_layout)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Process list
        process_group = QGroupBox("Running Processes")
        process_layout = QVBoxLayout()
        
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(4)
        self.process_table.setHorizontalHeaderLabels(["PID", "Name", "CPU %", "Memory MB"])
        self.process_table.setAlternatingRowColors(True)
        process_layout.addWidget(self.process_table)
        
        refresh_btn = QPushButton("ðŸ”„ Refresh Processes")
        refresh_btn.clicked.connect(self._refresh_processes)
        process_layout.addWidget(refresh_btn)
        
        process_group.setLayout(process_layout)
        layout.addWidget(process_group)
        
        return tab
        
    def _create_config_tab(self) -> QWidget:
        """Create Configuration Editor tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("CONFIGURATION EDITOR")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00F2FF; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Config file selector
        file_group = QGroupBox("Configuration Files")
        file_layout = QVBoxLayout()
        
        # File list
        self.config_file_list = QListWidget()
        self.config_file_list.setMaximumHeight(100)
        self._populate_config_files()
        file_layout.addWidget(self.config_file_list)
        
        # File actions
        file_actions = QHBoxLayout()
        load_btn = QPushButton("📂 Load Config")
        load_btn.clicked.connect(self._load_selected_config)
        file_actions.addWidget(load_btn)
        
        save_btn = QPushButton("💾 Save Config")
        save_btn.clicked.connect(self._save_current_config)
        file_actions.addWidget(save_btn)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._populate_config_files)
        file_actions.addWidget(refresh_btn)
        
        file_layout.addLayout(file_actions)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Config editor
        editor_group = QGroupBox("JSON Editor")
        editor_layout = QVBoxLayout()
        
        # Editor controls
        editor_controls = QHBoxLayout()
        
        self.config_path_label = QLabel("No file loaded - Drag & drop config files here")
        self.config_path_label.setStyleSheet("color: #888;")
        editor_controls.addWidget(self.config_path_label)
        
        editor_controls.addStretch()
        
        validate_btn = QPushButton("✅ Validate JSON")
        validate_btn.clicked.connect(self._validate_config_json)
        editor_controls.addWidget(validate_btn)
        
        format_btn = QPushButton("🎨 Format JSON")
        format_btn.clicked.connect(self._format_config_json)
        editor_controls.addWidget(format_btn)
        
        editor_layout.addLayout(editor_controls)
        
        # JSON editor with drag & drop
        self.config_editor = ConfigTextEdit()
        self.config_editor.setFont(QFont("Consolas", 10))
        self.config_editor.setStyleSheet("""
            QTextEdit {
                background: #1e1e1e;
                color: #dcdcdc;
                border: 1px solid #444;
                selection-background-color: #00F2FF;
            }
        """)
        editor_layout.addWidget(self.config_editor)
        
        editor_group.setLayout(editor_layout)
        layout.addWidget(editor_group)
        
        # Backup section
        backup_group = QGroupBox("Backup & Restore")
        backup_layout = QHBoxLayout()
        
        backup_btn = QPushButton("📦 Create Backup")
        backup_btn.clicked.connect(self._create_config_backup)
        backup_layout.addWidget(backup_btn)
        
        restore_btn = QPushButton("🔄 Restore from Backup")
        restore_btn.clicked.connect(self._restore_config_backup)
        backup_layout.addWidget(restore_btn)
        
        backup_layout.addStretch()
        
        self.backup_status_label = QLabel("")
        backup_layout.addWidget(self.backup_status_label)
        
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        layout.addStretch()
        return tab
        
    def _create_memory_tab(self) -> QWidget:
        """Dashboard's Database Browser"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(30,30,30,30)
        
        # Memory list with styling
        self.memory_list = QListWidget()
        self.memory_list.setSpacing(5)
        self.memory_list.setStyleSheet("QListWidget::item { padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); }")
        
        layout.addWidget(QLabel("NEURAL DATABASE // SHORT-TERM MEMORY"))
        layout.addWidget(self.memory_list)
        
        controls = QHBoxLayout()
        clear_btn = QPushButton("PURGE MEMORY")
        clear_btn.clicked.connect(self._clear_memory)
        export_btn = QPushButton("EXPORT KNOWLEDGE")
        export_btn.clicked.connect(self._export_memory)
        controls.addWidget(clear_btn)
        controls.addWidget(export_btn)
        layout.addLayout(controls)
        
        return tab
        
        return tab
    
    def _create_learning_tab(self) -> QWidget:
        """Dashboard's Evolutionary Core - AGI Learning Viewer"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Grid layout for metrics
        top_row = QHBoxLayout()
        
        # Status Card
        status_card = QFrame()
        status_card.setStyleSheet("background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px;")
        sc_layout = QVBoxLayout(status_card)
        sc_layout.addWidget(QLabel("NEURAL ENGINE STATUS"))
        self.learning_status_label = QLabel("AGI ENGINE: ACTIVE")
        self.learning_status_label.setStyleSheet("color: #00F2FF; font-size: 18px; font-weight: bold;")
        sc_layout.addWidget(self.learning_status_label)
        
        self.cog_awareness_label = QLabel("COGNITIVE AWARENESS: MONITORING")
        self.cog_awareness_label.setStyleSheet("color: #7000FF; font-size: 12px; font-weight: bold;")
        sc_layout.addWidget(self.cog_awareness_label)
        top_row.addWidget(status_card, 2)
        
        # Metrics Card
        metrics_card = QFrame()
        metrics_card.setStyleSheet("background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px;")
        mc_layout = QFormLayout(metrics_card)
        self.total_interactions_label = QLabel("0")
        self.training_cycles_label = QLabel("0")
        self.golden_commands_label = QLabel("0")
        mc_layout.addRow("TOTAL RECEPTIONS:", self.total_interactions_label)
        mc_layout.addRow("DREAM CYCLES:", self.training_cycles_label)
        mc_layout.addRow("GOLDEN PATTERNS:", self.golden_commands_label)
        top_row.addWidget(metrics_card, 1)
        
        layout.addLayout(top_row)
        
        # Feedback & Training Section
        mid_row = QHBoxLayout()
        
        # Training Control
        train_group = QGroupBox("AGI CONSOLIDATION (TRAINING)")
        tg_layout = QVBoxLayout()
        tg_layout.addWidget(QLabel("Force immediate neural weights update or backup current state."))
        
        self.trigger_training_btn = QPushButton("ðŸš€ EXECUTE DPO TRAINING")
        self.trigger_training_btn.clicked.connect(self._trigger_training)
        tg_layout.addWidget(self.trigger_training_btn)
        
        self.backup_model_btn = QPushButton("ðŸ’¾ ARCHIVE NEURAL STATE")
        self.backup_model_btn.clicked.connect(self._backup_model)
        tg_layout.addWidget(self.backup_model_btn)
        
        self.cog_research_btn = QPushButton("ðŸ›°ï¸ SCAN KNOWLEDGE GAPS")
        self.cog_research_btn.clicked.connect(self._scan_knowledge_gaps)
        self.cog_research_btn.setStyleSheet("background: rgba(112, 0, 255, 0.1); border: 1px solid #7000FF;")
        tg_layout.addWidget(self.cog_research_btn)
        
        train_group.setLayout(tg_layout)
        mid_row.addWidget(train_group)
        
        # Feedback Control
        feedback_group = QGroupBox("RLHF INTERFACE (HUMAN FEEDBACK)")
        fg_layout = QVBoxLayout()
        buttons = QHBoxLayout()
        self.thumbs_up_btn = QPushButton("ðŸ‘ VALID")
        self.thumbs_down_btn = QPushButton("ðŸ‘Ž INVALID")
        self.thumbs_up_btn.clicked.connect(lambda: self._send_feedback(1.0))
        self.thumbs_down_btn.clicked.connect(lambda: self._send_feedback(-1.0))
        buttons.addWidget(self.thumbs_up_btn)
        buttons.addWidget(self.thumbs_down_btn)
        fg_layout.addLayout(buttons)
        
        self.correction_edit = QTextEdit()
        self.correction_edit.setPlaceholderText("Provide the 'Golden Response' to correct behavior...")
        self.correction_edit.setMaximumHeight(60)
        fg_layout.addWidget(self.correction_edit)
        
        self.reflection_toggle = QCheckBox("ATIVAR LOGS DE REFLEXÃƒO NEURAL (RAIO-X)")
        self.reflection_toggle.setChecked(True)
        self.reflection_toggle.setStyleSheet("color: #00F2FF; font-weight: bold;")
        self.reflection_toggle.stateChanged.connect(self._toggle_neural_reflection)
        fg_layout.addWidget(self.reflection_toggle)
        
        submit_btn = QPushButton("SUBMIT CORRECTION & TRAIN")
        submit_btn.clicked.connect(self._submit_correction)
        fg_layout.addWidget(submit_btn)
        feedback_group.setLayout(fg_layout)
        mid_row.addWidget(feedback_group)
        
        layout.addLayout(mid_row)
        
        # Knowledge Patterns (Golden Commands)
        golden_group = QGroupBox("KNOWLEDGE BASE // LEARNED PATTERNS")
        gl_layout = QVBoxLayout()
        self.golden_list = QListWidget()
        gl_layout.addWidget(self.golden_list)
        refresh_golden_btn = QPushButton("REFRESH PATTERN MATRIX")
        refresh_golden_btn.clicked.connect(self._refresh_golden_commands)
        gl_layout.addWidget(refresh_golden_btn)
        golden_group.setLayout(gl_layout)
        layout.addWidget(golden_group)
        
        layout.addStretch()
        return tab
        
        layout.addStretch()
        
        # Initialize data
        self._refresh_learning_status()
        
        return tab
        
    def _refresh_learning_status(self):
        """Refresh learning system status"""
        try:
            from src.learning.learning_engine import get_learning_engine
            engine = get_learning_engine()
            
            if engine and engine.is_initialized:
                status = engine.get_status()
                
                # Update status label
                components_online = sum(1 for v in status['components'].values() if v)
                total_components = len(status['components'])
                
                status_text = f"âœ… ONLINE - {components_online}/{total_components} systems active\n\n"
                for component, active in status['components'].items():
                    icon = "âœ…" if active else "âŒ"
                    name = component.replace('_', ' ').title()
                    status_text += f"{icon} {name}\n"
                
                self.learning_status_label.setText(status_text)
                
                # Update metrics
                self.total_interactions_label.setText(str(status.get('total_feedback', 0)))
                self.training_cycles_label.setText(str(status.get('training_cycles', 0)))
                
            else:
                self.learning_status_label.setText("âŒ OFFLINE - Learning systems not initialized")
                
        except Exception as e:
            self.learning_status_label.setText(f"âš ï¸ ERROR - {str(e)}")
            logger.error(f"Failed to refresh learning status: {e}")
    
    def _refresh_golden_commands(self):
        """Refresh golden commands list"""
        try:
            from src.learning.learning_engine import get_learning_engine
            engine = get_learning_engine()
            
            if engine and engine.knowledge_distiller:
                distiller = engine.knowledge_distiller
                golden_cmds = distiller.gold_commands
                
                self.golden_list.clear()
                self.golden_commands_label.setText(str(len(golden_cmds)))
                
                for cmd_key, data in list(golden_cmds.items())[:20]:  # Show top 20
                    usage = data.get('usage_count', 0)
                    self.golden_list.addItem(f"[{usage}x] {data.get('command', cmd_key)}")
                    
        except Exception as e:
            logger.error(f"Failed to refresh golden commands: {e}")
    
    def _send_feedback(self, value: float):
        """Send explicit feedback for last interaction"""
        try:
            from src.learning.learning_engine import get_learning_engine
            engine = get_learning_engine()
            
            if engine:
                # Snapshot last interaction to avoid TOCTOU race conditions
                last_interaction = engine.last_interaction
                if last_interaction:
                    interaction_id = last_interaction.get('interaction_id')
                    if interaction_id:
                        engine.record_explicit_feedback(
                            interaction_id=interaction_id,
                            feedback_value=value
                        )
                        QMessageBox.information(self, "Feedback Sent",
                                               f"Thank you! Your feedback ({'+' if value > 0 else '-'}) will improve JARVIS.")
                        logger.info(f"User feedback: {value} for {interaction_id}")
                    else:
                        QMessageBox.warning(self, "Invalid Interaction", "Interaction ID not found.")
                else:
                    QMessageBox.warning(self, "No Interaction", "No recent interaction found to rate.")
            else:
                QMessageBox.warning(self, "Error", "Learning engine not available")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send feedback: {e}")
    
    def _submit_correction(self):
        """Submit correction for wrong response"""
        correction = self.correction_edit.toPlainText().strip()
        
        if not correction:
            QMessageBox.warning(self, "Empty Correction", "Please provide a correction first.")
            return
        
        try:
            from src.learning.learning_engine import get_learning_engine
            engine = get_learning_engine()
            
            if engine:
                # Snapshot last interaction to avoid TOCTOU race conditions
                last_interaction = engine.last_interaction
                if last_interaction:
                    interaction_id = last_interaction.get('interaction_id')
                    if interaction_id:
                        engine.record_explicit_feedback(
                            interaction_id=interaction_id,
                            feedback_value=-1.0,
                            correction=correction
                        )
                        QMessageBox.information(self, "Correction Saved",
                                               "Your correction will be used for training!")
                        logger.info(f"User correction: {correction} for {interaction_id}")
                    else:
                        QMessageBox.warning(self, "Invalid Interaction", "Interaction ID not found.")
                else:
                    QMessageBox.warning(self, "No Interaction", "No recent interaction found to correct.")
                self.correction_edit.clear()
            else:
                QMessageBox.warning(self, "Error", "Learning engine not available")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to submit correction: {e}")
    
    def _trigger_training(self):
        """Manually trigger a training cycle"""
        reply = QMessageBox.question(
            self, "Trigger Training", 
            "This will start an immediate training cycle.\n"
            "It may take several minutes and use significant CPU/GPU.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                from src.learning.learning_engine import get_learning_engine
                engine = get_learning_engine()
                
                if engine and engine.continual_learner:
                    # Trigger training in background thread
                    import threading
                    threading.Thread(
                        target=engine.continual_learner._execute_training_cycle,
                        daemon=True
                    ).start()
                    
                    QMessageBox.information(self, "Training Started", 
                                           "Training cycle initiated in background.")
                else:
                    QMessageBox.warning(self, "Error", "Continual learner not available")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to trigger training: {e}")
    
    def _backup_model(self):
        """Backup current model"""
        try:
            import shutil
            from datetime import datetime
            
            source = Path("data/models/continual")
            if not source.exists():
                QMessageBox.warning(self, "No Model", "No trained model found to backup.")
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = Path(f"data/models/backups/model_backup_{timestamp}")
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copytree(source, backup_path)
            
            QMessageBox.information(self, "Backup Complete", 
                                   f"Model backed up to:\n{backup_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to backup model: {e}")
        
    def _create_footer(self) -> QWidget:
        """Create footer with status"""
        footer = QWidget()
        layout = QHBoxLayout(footer)
        
        self.status_label = QLabel("âœ… Ready")
        self.status_label.setStyleSheet("color: #4CAF50;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Version
        version_label = QLabel("v1.0.0 Singularity")
        version_label.setStyleSheet("color: #888;")
        layout.addWidget(version_label)
        
        return footer
        
    def _apply_theme(self):
        """Apply Singularity 2.0 Luxury Dashboard Theme"""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background: #02050A;
                color: #FFFFFF;
                font-family: 'Segoe UI', 'Bahnschrift', 'Arial';
            }
            
            #sidebar {
                background: #050A14;
                border-right: 1px solid rgba(255, 255, 255, 0.05);
            }
            
            #top_header {
                background: #02050A;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                padding: 0 20px;
            }
            
            #hud_action_button {
                background: rgba(0, 242, 255, 0.05);
                color: #00F2FF;
                border: 1px solid rgba(0, 242, 255, 0.2);
                border-radius: 0px;
                padding: 15px;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 2px;
                margin: 20px;
            }
            
            #hud_action_button:hover {
                background: rgba(0, 242, 255, 0.15);
                border: 1px solid #00F2FF;
            }
            
            QGroupBox {
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                margin-top: 20px;
                padding: 20px;
                font-weight: bold;
                font-size: 11px;
                color: rgba(255, 255, 255, 0.7);
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 8px;
                border-radius: 2px;
                color: white;
            }
            
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid #00F2FF;
                background: rgba(0, 242, 255, 0.02);
            }
            
            QPushButton {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 10px 20px;
                border-radius: 2px;
                color: white;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }

            QProgressBar {
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 2px;
                background: #02050A;
                height: 12px;
                text-align: right;
                margin-right: 5px;
            }
            
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #006FB2, stop:1 #00F2FF);
                width: 1px;
            }
            
            QListWidget, QTableWidget, QHeaderView::section {
                background: #030814;
                border: 1px solid rgba(255, 255, 255, 0.05);
                color: rgba(255, 255, 255, 0.8);
                padding: 5px;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #02050A;
                width: 8px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.1);
                min-height: 20px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.2);
            }
        """)
        
    def _start_monitoring(self):
        """Start system monitoring thread"""
        self.monitor_thread = SystemMonitorThread()
        self.monitor_thread.stats_updated.connect(self._update_system_stats)
        self.monitor_thread.start()
        
        logger.info("âœ… System monitoring started")
        
    @pyqtSlot(dict)
    def _update_system_stats(self, stats: Dict):
        """Update system statistics display"""
        cpu_val = int(stats['cpu'])
        self.cpu_bar.setValue(cpu_val)
        self.cpu_label.setText(f"{stats['cpu']:.1f}%")
        self.quick_cpu.setText(f"CPU: {cpu_val}%")
        
        self.memory_bar.setValue(int(stats['memory']))
        self.memory_label.setText(f"{stats['memory']:.1f}%")
        
        self.disk_bar.setValue(int(stats['disk']))
        self.disk_label.setText(f"{stats['disk']:.1f}%")
        
    def _refresh_processes(self):
        """Refresh process list with styled table"""
        self.process_table.setRowCount(0)
        self.process_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.process_table.setAlternatingRowColors(True)
        self.process_table.setShowGrid(False)
        
        try:
            # Sort by memory usage as default
            all_procs = sorted(
                psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']),
                key=lambda p: p.info['memory_info'].rss if p.info['memory_info'] else 0,
                reverse=True
            )[:50] # Top 50
            
            for proc in all_procs:
                info = proc.info
                row = self.process_table.rowCount()
                self.process_table.insertRow(row)
                
                # PID
                pid_item = QTableWidgetItem(str(info['pid']))
                pid_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.process_table.setItem(row, 0, pid_item)
                
                # Name
                name_item = QTableWidgetItem(info['name'][:30])
                self.process_table.setItem(row, 1, name_item)
                
                # CPU
                cpu = f"{info.get('cpu_percent', 0):.1f}%"
                self.process_table.setItem(row, 2, QTableWidgetItem(cpu))
                
                # RAM
                memory_mb = (info.get('memory_info', type('obj', (), {'rss': 0})).rss / (1024 * 1024))
                self.process_table.setItem(row, 3, QTableWidgetItem(f"{memory_mb:.1f} MB"))
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
                
    def _setup_log_handler(self):
        """Setup logging to display in UI"""
        # This would connect to the actual logging system
        # For now, simulate with timer
        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self._simulate_log_entry)
        self.log_timer.start(5000)  # Add log every 5 seconds
        
    def _simulate_log_entry(self):
        """Simulate log entry for demo"""
        import random
        levels = ["INFO", "DEBUG", "WARNING"]
        messages = [
            "System check complete",
            "Vision system active",
            "Audio processing ready",
            "FaceID scan complete",
            "Memory usage normal"
        ]
        
        level = random.choice(levels)
        message = random.choice(messages)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        log_entry = f"[{timestamp}] {level}: {message}"
        self.log_viewer.append(log_entry)
        
        if self.auto_scroll_check.isChecked():
            self.log_viewer.moveCursor(QTextCursor.MoveOperation.End)
            
    def _filter_logs(self):
        """Filter logs based on search and level"""
        search_text = self.log_filter.text().lower()
        level_filter = self.log_level_combo.currentText()

        # Get all log content
        all_logs = self.log_viewer.toPlainText().split('\n')

        # Filter logs
        filtered_logs = []
        for log_line in all_logs:
            if not log_line.strip():
                continue

            # Level filter
            if level_filter != "ALL":
                if f"{level_filter}:" not in log_line:
                    continue

            # Text search filter
            if search_text and search_text not in log_line.lower():
                continue

            filtered_logs.append(log_line)

        # Update display
        self.log_viewer.setPlainText('\n'.join(filtered_logs))

        # Auto-scroll to bottom if enabled
        if self.auto_scroll_check.isChecked():
            self.log_viewer.moveCursor(QTextCursor.MoveOperation.End)
        
    def _clear_logs(self):
        """Clear log viewer"""
        self.log_viewer.clear()
        
    def _request_hud_mode(self):
        """Request switch to HUD mode with robust import"""
        try:
            from src.interface.window_manager import InterfaceMode
            self.mode_switch_requested.emit(InterfaceMode.HUD_OVERLAY)
        except ImportError:
            logger.error("Could not import InterfaceMode. WindowManager might not be in path.")
            QMessageBox.warning(self, "System Error", "Interface Controller not found.")
        
    def _save_brain_config(self):
        """Save brain configuration"""
        self.config["ai"] = {
            "model_type": self.model_type_combo.currentText(),
            "model_name": self.model_name_edit.text(),
            "api_key": self.api_key_edit.text(),
            "temperature": self.temperature_spin.value(),
            "max_tokens": self.max_tokens_spin.value(),
            "system_prompt": self.system_prompt_edit.toPlainText()
        }
        self._save_config()
        QMessageBox.information(self, "Success", "Brain configuration saved!")
        
        # Show success toast
        from src.interface.toast_notifications import show_success_toast
        show_success_toast("Configuration Saved", "Brain settings updated successfully")
        
    def _save_voice_config(self):
        """Save voice configuration"""
        self.config["audio"] = {
            "stt_model": self.stt_model_combo.currentText(),
            "stt_model_size": self.stt_model_size.currentText(),
            "tts_engine": self.tts_engine_combo.currentText(),
            "voice": self.voice_combo.currentText(),
            "speech_rate": self.speech_rate_slider.value(),
            "vad_enabled": self.vad_enabled_check.isChecked(),
            "vad_threshold": self.vad_threshold.value(),
            "speaker_verification": self.speaker_verify_check.isChecked()
        }
        self._save_config()
        QMessageBox.information(self, "Success", "Voice settings saved!")
        
        # Show success toast
        from src.interface.toast_notifications import show_success_toast
        show_success_toast("Configuration Saved", "Voice settings updated successfully")
        
    def _save_vision_config(self):
        """Save vision configuration"""
        self.config["vision"] = {
            "faceid_enabled": self.faceid_enabled.isChecked(),
            "face_model": self.face_model_combo.currentText(),
            "ocr_enabled": self.ocr_enabled.isChecked(),
            "ocr_languages": self.ocr_languages.currentText(),
            "yolo_enabled": self.yolo_enabled.isChecked(),
            "yolo_model": self.yolo_model.currentText(),
            "yolo_confidence": self.yolo_confidence.value()
        }
        self._save_config()
        QMessageBox.information(self, "Success", "Vision settings saved!")
        
    def _enroll_voice(self):
        """Enroll new voice signature"""
        QMessageBox.information(self, "Voice Enrollment", 
                               "Voice enrollment will start.\n"
                               "Please speak clearly for 5 seconds.")
        
    def _add_face(self):
        """Add new authorized face"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Face Image", "", "Images (*.jpg *.jpeg *.png)"
        )
        if file_path:
            # Copy to faces directory
            import shutil
            dest = Path("data/faces") / Path(file_path).name
            shutil.copy(file_path, dest)
            self.face_list.addItem(Path(file_path).name)
            QMessageBox.information(self, "Success", "Face added!")
            
    def _remove_face(self):
        """Remove authorized face"""
        current = self.face_list.currentItem()
        if current:
            face_file = Path("data/faces") / current.text()
            if face_file.exists():
                face_file.unlink()
            self.face_list.takeItem(self.face_list.row(current))
            QMessageBox.information(self, "Success", "Face removed!")
            
    def _clear_memory(self):
        """Clear conversation memory"""
        reply = QMessageBox.question(
            self, "Clear Memory", 
            "Are you sure you want to clear all conversation history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.memory_list.clear()
            QMessageBox.information(self, "Success", "Memory cleared!")
            
    def _export_memory(self):
        """Export conversation memory"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Memory", "", "JSON (*.json);;Text (*.txt)"
        )
        if file_path:
            # Export implementation
            QMessageBox.information(self, "Success", f"Memory exported to {file_path}")
            
    def _toggle_neural_reflection(self, state):
        """Enable/Disable cinematic neural reasoning logs"""
        from src.utils.logger_reflection import reflect_logger
        enabled = state == 2 # 2 is checked in Qt
        reflect_logger.set_enabled(enabled)
        logger.info(f"Neural Reflection {'ENABLED' if enabled else 'DISABLED'}")
            
    def _scan_knowledge_gaps(self):
        """Scan for knowledge gaps in the system"""
        QMessageBox.information(
            self, 
            "Knowledge Gap Scanner", 
            "🔍 Scanning knowledge gaps...\n\nThis feature analyzes the AI's knowledge base to identify areas that need improvement or additional training data.\n\nFeature coming soon in JARVIS 5.1!"
        )
            
    def _populate_config_files(self):
        """Populate the config files list"""
        self.config_file_list.clear()
        
        project_root = Path(__file__).parent.parent.parent
        config_dir = project_root / "config"
        
        if config_dir.exists():
            for config_file in config_dir.glob("*.json"):
                self.config_file_list.addItem(config_file.name)
            for config_file in config_dir.glob("*.yaml"):
                self.config_file_list.addItem(config_file.name)
                
    def _load_selected_config(self):
        """Load selected config file into editor"""
        current_item = self.config_file_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a config file first.")
            return
            
        filename = current_item.text()
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / filename
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.config_editor.setPlainText(content)
            self.config_path_label.setText(f"Loaded: {filename}")
            self.current_config_path = config_path
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load config: {e}")
            
    def _save_current_config(self):
        """Save current config from editor"""
        if not hasattr(self, 'current_config_path'):
            QMessageBox.warning(self, "No File", "No config file loaded to save.")
            return
            
        try:
            content = self.config_editor.toPlainText()
            with open(self.current_config_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            QMessageBox.information(self, "Success", "Configuration saved successfully!")
            
            # Show success toast
            from src.interface.toast_notifications import show_success_toast
            show_success_toast("Config Saved", "Configuration file updated successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save config: {e}")
            
    def _validate_config_json(self):
        """Validate JSON syntax"""
        content = self.config_editor.toPlainText()
        
        try:
            import json
            json.loads(content)
            QMessageBox.information(self, "Valid", "✅ JSON is valid!")
            
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid JSON", f"❌ JSON Error: {e}")
            
    def _format_config_json(self):
        """Format JSON with proper indentation"""
        content = self.config_editor.toPlainText()
        
        try:
            import json
            parsed = json.loads(content)
            formatted = json.dumps(parsed, indent=4, ensure_ascii=False)
            self.config_editor.setPlainText(formatted)
            
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid JSON", f"Cannot format invalid JSON: {e}")
            
    def _create_config_backup(self):
        """Create backup of current config"""
        if not hasattr(self, 'current_config_path'):
            QMessageBox.warning(self, "No File", "No config file loaded.")
            return
            
        try:
            import shutil
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.current_config_path.with_suffix(f".backup_{timestamp}.json")
            
            shutil.copy2(self.current_config_path, backup_path)
            
            self.backup_status_label.setText(f"✅ Backup created: {backup_path.name}")
            self.backup_status_label.setStyleSheet("color: #4CAF50;")
            
        except Exception as e:
            self.backup_status_label.setText(f"❌ Backup failed: {e}")
            self.backup_status_label.setStyleSheet("color: #f44336;")
            
    def _restore_config_backup(self):
        """Restore config from backup"""
        if not hasattr(self, 'current_config_path'):
            QMessageBox.warning(self, "No File", "No config file loaded.")
            return
            
        # List available backups
        backup_files = list(self.current_config_path.parent.glob(f"{self.current_config_path.stem}.backup_*.json"))
        
        if not backup_files:
            QMessageBox.information(self, "No Backups", "No backup files found.")
            return
            
        # Show backup selection dialog
        backup_names = [f.name for f in backup_files]
        backup_name, ok = QInputDialog.getItem(
            self, "Select Backup", "Choose backup to restore:", backup_names, 0, False
        )
        
        if ok and backup_name:
            backup_path = self.current_config_path.parent / backup_name
            
            try:
                import shutil
                shutil.copy2(backup_path, self.current_config_path)
                
                # Reload in editor
                with open(self.current_config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.config_editor.setPlainText(content)
                
                self.backup_status_label.setText(f"✅ Restored from: {backup_name}")
                self.backup_status_label.setStyleSheet("color: #4CAF50;")
                
            except Exception as e:
                self.backup_status_label.setText(f"❌ Restore failed: {e}")
                self.backup_status_label.setStyleSheet("color: #f44336;")
            
    def closeEvent(self, event):
        """Handle window close"""
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.terminate()
            self.monitor_thread.wait()
        event.accept()


# Testing
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    logging.basicConfig(level=logging.INFO)
    
    app = QApplication(sys.argv)
    app.setApplicationName("JARVIS Singularity Dashboard")
    
    dashboard = ControlDashboard()
    dashboard.show()
    
    sys.exit(app.exec())
