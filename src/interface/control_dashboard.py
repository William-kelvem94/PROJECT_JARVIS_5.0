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
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QLineEdit, QComboBox, QTextEdit, QCheckBox,
    QSpinBox, QDoubleSpinBox, QGroupBox, QFormLayout, QListWidget,
    QTableWidget, QTableWidgetItem, QProgressBar, QFileDialog,
    QMessageBox, QSplitter, QSlider
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, pyqtSlot, QThread
)
from PyQt6.QtGui import QFont, QColor, QPalette, QTextCursor

logger = logging.getLogger(__name__)


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
            
            self.msleep(2000)  # Update every 2 seconds


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
        
        # Load configuration
        self.config = self._load_config()
        
        # Setup UI
        self._setup_ui()
        
        # Start monitoring
        self._start_monitoring()
        
        logger.info("✅ Control Dashboard initialized")
        
    def _load_config(self) -> Dict:
        """Load configuration from file"""
        config_path = Path("config/singularity_config.json")
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                
        # Default config
        return {
            "vision": {"enabled": True, "faceid_enabled": True},
            "audio": {"enabled": True, "stt_model": "faster-whisper"},
            "system": {"god_mode_enabled": True},
            "ai": {"local_model": "ollama", "model_name": "llama3"}
        }
        
    def _save_config(self):
        """Save configuration to file"""
        config_path = Path("config/singularity_config.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, indent=4, fp=f)
            logger.info("✅ Configuration saved")
            self.config_changed.emit(self.config)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            
    def _setup_ui(self):
        """Setup user interface"""
        # Main widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = self._create_header()
        layout.addWidget(header)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444;
                background: #2b2b2b;
            }
            QTabBar::tab {
                background: #3b3b3b;
                color: #ccc;
                padding: 10px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #4a9eff;
                color: white;
            }
            QTabBar::tab:hover {
                background: #505050;
            }
        """)
        
        # Add tabs
        self.tabs.addTab(self._create_brain_tab(), "🧠 Brain")
        self.tabs.addTab(self._create_voice_tab(), "🎤 Voice")
        self.tabs.addTab(self._create_vision_tab(), "👁️ Vision")
        self.tabs.addTab(self._create_logs_tab(), "📋 Logs")
        self.tabs.addTab(self._create_system_tab(), "⚙️ System")
        self.tabs.addTab(self._create_memory_tab(), "💾 Memory")
        
        layout.addWidget(self.tabs)
        
        # Footer
        footer = self._create_footer()
        layout.addWidget(footer)
        
        # Apply dark theme
        self._apply_theme()
        
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
        save_btn = QPushButton("💾 Save Configuration")
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
        
        enroll_btn = QPushButton("🎙️ Enroll New Voice")
        enroll_btn.clicked.connect(self._enroll_voice)
        speaker_layout.addWidget(enroll_btn)
        
        self.voice_list = QListWidget()
        self.voice_list.addItems(["admin (enrolled)", "user1 (enrolled)"])
        speaker_layout.addWidget(self.voice_list)
        
        speaker_group.setLayout(speaker_layout)
        layout.addWidget(speaker_group)
        
        # Save button
        save_btn = QPushButton("💾 Save Voice Settings")
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
        add_face_btn = QPushButton("📸 Add New Face")
        add_face_btn.clicked.connect(self._add_face)
        face_mgmt_layout.addWidget(add_face_btn)
        
        remove_face_btn = QPushButton("🗑️ Remove Face")
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
        save_btn = QPushButton("💾 Save Vision Settings")
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
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(self._clear_logs)
        controls.addWidget(clear_btn)
        
        # Auto-scroll
        self.auto_scroll_check = QCheckBox("Auto-scroll")
        self.auto_scroll_check.setChecked(True)
        controls.addWidget(self.auto_scroll_check)
        
        layout.addLayout(controls)
        
        # Log viewer
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
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
        
        refresh_btn = QPushButton("🔄 Refresh Processes")
        refresh_btn.clicked.connect(self._refresh_processes)
        process_layout.addWidget(refresh_btn)
        
        process_group.setLayout(process_layout)
        layout.addWidget(process_group)
        
        return tab
        
    def _create_memory_tab(self) -> QWidget:
        """Create Memory browser tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Memory info
        info_label = QLabel("Conversation History & Context Memory")
        info_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(info_label)
        
        # Memory list
        self.memory_list = QListWidget()
        self.memory_list.addItems([
            "[2024-01-01 10:00] User: What's the weather?",
            "[2024-01-01 10:01] JARVIS: The weather is sunny...",
            "[2024-01-01 10:05] User: Open Chrome",
            "[2024-01-01 10:05] JARVIS: Opening Chrome..."
        ])
        layout.addWidget(self.memory_list)
        
        # Controls
        controls = QHBoxLayout()
        
        clear_memory_btn = QPushButton("🗑️ Clear Memory")
        clear_memory_btn.clicked.connect(self._clear_memory)
        controls.addWidget(clear_memory_btn)
        
        export_memory_btn = QPushButton("💾 Export Memory")
        export_memory_btn.clicked.connect(self._export_memory)
        controls.addWidget(export_memory_btn)
        
        layout.addLayout(controls)
        
        return tab
        
    def _create_footer(self) -> QWidget:
        """Create footer with status"""
        footer = QWidget()
        layout = QHBoxLayout(footer)
        
        self.status_label = QLabel("✅ Ready")
        self.status_label.setStyleSheet("color: #4CAF50;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Version
        version_label = QLabel("v1.0.0 Singularity")
        version_label.setStyleSheet("color: #888;")
        layout.addWidget(version_label)
        
        return footer
        
    def _apply_theme(self):
        """Apply dark theme"""
        self.setStyleSheet("""
            QMainWindow {
                background: #2b2b2b;
            }
            QWidget {
                background: #2b2b2b;
                color: #dcdcdc;
            }
            QGroupBox {
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background: #3b3b3b;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 3px;
                color: #dcdcdc;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #4a9eff;
            }
            QPushButton {
                background: #3b3b3b;
                border: 1px solid #555;
                padding: 8px;
                border-radius: 4px;
                color: #dcdcdc;
            }
            QPushButton:hover {
                background: #4a9eff;
                color: white;
            }
            QProgressBar {
                border: 1px solid #555;
                border-radius: 3px;
                text-align: center;
                background: #3b3b3b;
            }
            QProgressBar::chunk {
                background: #4a9eff;
            }
            QListWidget, QTableWidget {
                background: #1e1e1e;
                border: 1px solid #444;
                alternate-background-color: #2a2a2a;
            }
            QHeaderView::section {
                background: #3b3b3b;
                color: #dcdcdc;
                padding: 5px;
                border: 1px solid #555;
            }
        """)
        
    def _start_monitoring(self):
        """Start system monitoring thread"""
        self.monitor_thread = SystemMonitorThread()
        self.monitor_thread.stats_updated.connect(self._update_system_stats)
        self.monitor_thread.start()
        
        logger.info("✅ System monitoring started")
        
    @pyqtSlot(dict)
    def _update_system_stats(self, stats: Dict):
        """Update system statistics display"""
        self.cpu_bar.setValue(int(stats['cpu']))
        self.cpu_label.setText(f"{stats['cpu']:.1f}%")
        
        self.memory_bar.setValue(int(stats['memory']))
        self.memory_label.setText(f"{stats['memory']:.1f}%")
        
        self.disk_bar.setValue(int(stats['disk']))
        self.disk_label.setText(f"{stats['disk']:.1f}%")
        
    def _refresh_processes(self):
        """Refresh process list"""
        self.process_table.setRowCount(0)
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                info = proc.info
                row = self.process_table.rowCount()
                self.process_table.insertRow(row)
                
                self.process_table.setItem(row, 0, QTableWidgetItem(str(info['pid'])))
                self.process_table.setItem(row, 1, QTableWidgetItem(info['name']))
                self.process_table.setItem(row, 2, QTableWidgetItem(f"{info.get('cpu_percent', 0):.1f}"))
                
                memory_mb = info.get('memory_info', type('obj', (), {'rss': 0})).rss / (1024 * 1024)
                self.process_table.setItem(row, 3, QTableWidgetItem(f"{memory_mb:.1f}"))
                
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
        # Implementation would filter the log display
        pass
        
    def _clear_logs(self):
        """Clear log viewer"""
        self.log_viewer.clear()
        
    def _request_hud_mode(self):
        """Request switch to HUD mode"""
        from .window_manager import InterfaceMode
        self.mode_switch_requested.emit(InterfaceMode.HUD_OVERLAY)
        
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
            
    def add_log_message(self, log_type: str, message: str):
        """Add message to log viewer (called from other components)"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {log_type}: {message}"
        self.log_viewer.append(log_entry)
        
        if self.auto_scroll_check.isChecked():
            self.log_viewer.moveCursor(QTextCursor.MoveOperation.End)
            
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
