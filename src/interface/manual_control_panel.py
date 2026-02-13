#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Manual Control Panel (Emergency Mode)
==================================================
Interface PyQt6 para controle manual quando a voz falha.
Acessível via Hotkey Global: Ctrl+Shift+Alt+J
"""

import sys
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSlider, QFrame, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont, QColor, QPalette

logger = logging.getLogger(__name__)

class ManualControlPanel(QWidget):
    """Painel de Emergência 'Bug-Proof'"""
    
    # Sinais para comunicação com o núcleo
    settings_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JARVIS - MODO EMERGÊNCIA")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(400, 500)
        
        # Estética Stark (Dark Mode / Blue Glow)
        self._setup_style()
        self._init_ui()
        
    def _setup_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #0b0f19;
                color: #00d4ff;
                border: 2px solid #005666;
                border-radius: 10px;
            }
            QLabel {
                border: none;
                font-family: 'Segoe UI', sans-serif;
            }
            QGroupBox {
                border: 1px solid #005666;
                margin-top: 10px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #002b36;
                border: 1px solid #00d4ff;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #004d61;
            }
            QSlider::handle:horizontal {
                background: #00d4ff;
                width: 18px;
            }
        """)

    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("🏛️ NÚCLEO MECÂNICO - MANUAL")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # --- VOZ ---
        voice_group = QGroupBox("🔉 Configurações de Voz")
        v_layout = QVBoxLayout()
        
        v_layout.addWidget(QLabel("Velocidade da Fala"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 200)
        self.speed_slider.setValue(100)
        v_layout.addWidget(self.speed_slider)
        
        v_layout.addWidget(QLabel("Volume"))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        v_layout.addWidget(self.volume_slider)
        
        voice_group.setLayout(v_layout)
        layout.addWidget(voice_group)
        
        # --- BIOMETRIA ---
        bio_group = QGroupBox("🔐 Biometria e Usuários")
        b_layout = QVBoxLayout()
        
        btn_face = QPushButton("🔄 Recadastrar Face (Manual)")
        btn_face.clicked.connect(self._on_face_record)
        b_layout.addWidget(btn_face)
        
        btn_voice = QPushButton("🎤 Recadastrar Voz (Manual)")
        btn_voice.clicked.connect(self._on_voice_record)
        b_layout.addWidget(btn_voice)
        
        bio_group.setLayout(b_layout)
        layout.addWidget(bio_group)
        
        # --- HARDWARE ---
        hw_group = QGroupBox("⚙️ Gestão de Hardware")
        h_layout = QVBoxLayout()
        
        btn_swap = QPushButton("🚀 Forçar IA para RAM/SWAP")
        btn_swap.clicked.connect(self._on_force_swap)
        h_layout.addWidget(btn_swap)
        
        btn_reset = QPushButton("♻️ Reiniciar Núcleo Neural")
        btn_reset.clicked.connect(self._on_reset_brain)
        h_layout.addWidget(btn_reset)
        
        hw_group.setLayout(h_layout)
        layout.addWidget(hw_group)
        
        # Footer
        btn_close = QPushButton("Sair do Modo Manual")
        btn_close.setStyleSheet("background-color: #4b0000; border-color: #ff0000;")
        btn_close.clicked.connect(self.hide)
        layout.addWidget(btn_close)
        
        self.setLayout(layout)

    def _on_face_record(self):
        logger.info("ManualControl: Iniciando Wizard de FaceID")
        # Aqui dispararemos o wizard no futuro
        
    def _on_voice_record(self):
        logger.info("ManualControl: Iniciando Wizard de VoiceID")

    def _on_force_swap(self):
        logger.warning("ManualControl: Force Swap solicitado manualmente.")
        from src.core.management.hardware_manager import hardware_manager
        # Lógica de offload

    def _on_reset_brain(self):
        logger.critical("ManualControl: RESET NEURAL solicitado.")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ManualControlPanel()
    window.show()
    sys.exit(app.exec())
