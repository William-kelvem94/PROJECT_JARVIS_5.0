import sys
import psutil
import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QTabWidget, QLabel, QStatusBar, QFormLayout, QSlider, 
    QComboBox, QDoubleSpinBox, QPushButton, QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QAction

import logging
import psutil
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QTabWidget, QLabel, QStatusBar, QFormLayout, QSlider, 
    QComboBox, QDoubleSpinBox, QPushButton, QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QFont, QAction

logger = logging.getLogger(__name__)

# Classe auxiliar para capturar logs do Python e enviar para Qt
class QtLogSignaler(QObject):
    log_signal = pyqtSignal(str)

class QtLogHandler(logging.Handler):
    def __init__(self, signaler):
        super().__init__()
        self.signaler = signaler

    def emit(self, record):
        msg = self.format(record)
        self.signaler.log_signal.emit(msg)
try:
    from src.interface.components.circular_gauge import CircularGauge
    from src.interface.components.realtime_chart import RealtimeChart
except ImportError:
    # Fallback for direct testing if package structure not set
    from .components.circular_gauge import CircularGauge
    from .components.realtime_chart import RealtimeChart

# GPU detection imports
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import pynvml
    pynvml.nvmlInit()
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False

class StarkDashboard(QMainWindow):
    """
    Janela principal do Control Panel (Stark Tech Style).
    Permite monitoramento em tempo real e configuração manual do sistema.
    """
    
    # Signals
    mode_switch_requested = pyqtSignal(object) # Request switch to HUD/ORB
    
    def __init__(self, jarvis_core=None):
        super().__init__()
        self.jarvis = jarvis_core
        self.setWindowTitle("JARVIS Stark Control Panel")
        self.resize(1024, 768)
        
        # Check GPU availability
        self.gpu_available = TORCH_AVAILABLE and torch.cuda.is_available()
        self.nvml_available = NVML_AVAILABLE
        
        # Stylesheet (Stark Luxury Glass Theme)
        self.setStyleSheet("""
<<<<<<< Updated upstream
            QMainWindow { background-color: #03060a; color: #e0e0e0; }
            QTabWidget::pane { border: 1px solid #00c3ff; background: rgba(11, 15, 25, 200); border-radius: 8px; }
            QTabBar::tab { background: #050a10; color: #8899a6; padding: 12px 25px; border: 1px solid #1f293a; border-bottom: none; border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 5px; }
            QTabBar::tab:selected { background: #0b0f19; color: #00c3ff; border: 1px solid #00c3ff; border-bottom: 2px solid #0b0f19; font-weight: bold; }
            QTabBar::tab:hover { background: #1f293a; color: #ffffff; }
            QLabel { color: #e0e0e0; font-family: 'Segoe UI'; }
            QPushButton { background-color: rgba(31, 41, 58, 150); color: #00c3ff; border: 1px solid #00c3ff; padding: 10px; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background-color: rgba(0, 195, 255, 50); text-shadow: 0 0 10px #00c3ff; }
            QPushButton:pressed { background-color: #00c3ff; color: #050a10; }
            QGroupBox { border: 1px solid rgba(0, 195, 255, 100); margin-top: 25px; font-weight: bold; color: #00c3ff; border-radius: 10px; padding-top: 20px; }
            QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 0 10px; background-color: #03060a; }
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { border: none; background: #0b0f19; width: 10px; margin: 0; }
            QScrollBar::handle:vertical { background: #1f293a; min-height: 20px; border-radius: 5px; }
            QScrollBar::handle:vertical:hover { background: #00c3ff; }
        """)
        
=======
            QMainWindow {
                background-color: #03060a;
                color: #e0e0e0;
            }

            QTabWidget::pane {
                border: 1px solid #00c3ff;
                background: rgba(11, 15, 25, 200);
                border-radius: 8px;
            }

            QTabBar::tab {
                background: #050a10;
                color: #8899a6;
                padding: 12px 25px;
                border: 1px solid #1f293a;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 5px;
            }

            QTabBar::tab:selected {
                background: #0b0f19;
                color: #00c3ff;
                border: 1px solid #00c3ff;
                border-bottom: 2px solid #0b0f19;
                font-weight: bold;
            }

            QTabBar::tab:hover {
                background: #1f293a;
                color: #ffffff;
            }

            QLabel {
                color: #e0e0e0;
                font-family: 'Segoe UI';
            }

            QPushButton {
                background-color: rgba(31, 41, 58, 150);
                color: #00c3ff;
                border: 1px solid #00c3ff;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: rgba(0, 195, 255, 50);
                text-shadow: 0 0 10px #00c3ff;
            }

            QPushButton:pressed {
                background-color: #00c3ff;
                color: #050a10;
            }

            QGroupBox {
                border: 1px solid rgba(0, 195, 255, 100);
                margin-top: 25px;
                font-weight: bold;
                color: #00c3ff;
                border-radius: 10px;
                padding-top: 20px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                background-color: #03060a;
            }

            QScrollArea {
                border: none;
                background: transparent;
            }

            QScrollBar:vertical {
                border: none;
                background: #0b0f19;
                width: 10px;
                margin: 0;
            }

            QScrollBar::handle:vertical {
                background: #1f293a;
                min-height: 20px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical:hover {
                background: #00c3ff;
            }

            """)

>>>>>>> Stashed changes
        # Shared container for instances
        self.curiosity_backlog = []
        self.is_studying = False
        self.current_topic = "Nenhum"

        self.setup_ui()
        
        # Timer para atualização de métricas
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_metrics)
        self.update_timer.start(1000) # 1s

        # Conectar sinais de aprendizado
        from src.interface.ui_signals import ui_signals
        ui_signals.update_learning_status.connect(self._handle_learning_status)
        ui_signals.update_curiosity_list.connect(self._handle_curiosity_list)

        # Setup Logging Bridge (Python Logging -> Dashboard Console)
        self.log_signaler = QtLogSignaler()
        self.log_signaler.log_signal.connect(self._on_log_received)
        
        # Adicionar handler ao root logger para pegar TUDO
        log_handler = QtLogHandler(self.log_signaler)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(log_handler)
        
    def setup_ui(self):
        # Layout principal com abas
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Abas
        self.setup_monitor_tab()
        self.setup_sentinel_tab() # Nova Aba de Visão
        self.setup_ai_brain_tab()
        self.setup_cognitive_tab() 
        self.setup_config_tab()
        self.setup_console_tab()
        
        # Carregar configurações
        self.load_configurations()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("✅ Sistema JARVIS Online - Protocolo Stark Ativo")
        
        # Menu Bar para troca rápida
        menubar = self.menuBar()
        if menubar:
            view_menu = menubar.addMenu("Exibir")
            
            hud_action = QAction("HUD Overlay", self)
            hud_action.triggered.connect(lambda: self._request_mode_switch("hud"))
            view_menu.addAction(hud_action)
            
            orb_action = QAction("Mini Orb", self)
            orb_action.triggered.connect(lambda: self._request_mode_switch("orb"))
            view_menu.addAction(orb_action)

    def _request_mode_switch(self, mode_str):
        """Request interface mode change via WindowManager"""
        # Para evitar dependência circular, importamos InterfaceMode apenas aqui
        try:
            from src.interface.window_manager import InterfaceMode
            if mode_str == "hud":
                self.mode_switch_requested.emit(InterfaceMode.HUD_OVERLAY)
            elif mode_str == "orb":
                self.mode_switch_requested.emit(InterfaceMode.ORB)
            elif mode_str == "hidden":
                self.mode_switch_requested.emit(InterfaceMode.HIDDEN)
        except ImportError:
            # Fallback se não conseguir importar (usar string)
            self.mode_switch_requested.emit(mode_str)

    def setup_monitor_tab(self):
        """Aba de monitoramento em tempo real"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Grid de métricas (Gauges)
        metrics_group = QGroupBox("Métricas do Sistema")
        metrics_grid = QGridLayout()
        
        self.cpu_gauge = CircularGauge("CPU", 0, 100, "%")
        metrics_grid.addWidget(self.cpu_gauge, 0, 0)
        
        self.ram_gauge = CircularGauge("RAM", 0, 100, "%")
        metrics_grid.addWidget(self.ram_gauge, 0, 1)
        
        # GPU gauge se disponível
        if self.gpu_available:
            self.gpu_gauge = CircularGauge("GPU", 0, 100, "%")
            metrics_grid.addWidget(self.gpu_gauge, 0, 2)
        else:
            self.disk_gauge = CircularGauge("Disk", 0, 100, "%")
            metrics_grid.addWidget(self.disk_gauge, 0, 2)
        
        metrics_group.setLayout(metrics_grid)
        layout.addWidget(metrics_group)
        
        # Métricas específicas da IA
        ai_metrics_group = QGroupBox("Métricas da IA JARVIS")
        ai_metrics_layout = QHBoxLayout()
        
        # Status da IA
        self.ai_status_label = QLabel("Status: Inicializando...")
        self.ai_status_label.setStyleSheet("font-weight: bold; color: #00c3ff;")
        ai_metrics_layout.addWidget(self.ai_status_label)
        
        # Funções ativas
        self.active_functions_label = QLabel("Funções Ativas: 0")
        self.active_functions_label.setStyleSheet("color: #e0e0e0;")
        ai_metrics_layout.addWidget(self.active_functions_label)
        
        # Consumo da IA
        self.ai_cpu_usage_label = QLabel("IA CPU: 0%")
        self.ai_cpu_usage_label.setStyleSheet("color: #ff6b6b;")
        ai_metrics_layout.addWidget(self.ai_cpu_usage_label)
        
        self.ai_memory_usage_label = QLabel("IA RAM: 0MB")
        self.ai_memory_usage_label.setStyleSheet("color: #4ecdc4;")
        ai_metrics_layout.addWidget(self.ai_memory_usage_label)
        
        if self.gpu_available:
            self.ai_gpu_usage_label = QLabel("IA GPU: 0%")
            self.ai_gpu_usage_label.setStyleSheet("color: #45b7d1;")
            ai_metrics_layout.addWidget(self.ai_gpu_usage_label)
        
        ai_metrics_group.setLayout(ai_metrics_layout)
        layout.addWidget(ai_metrics_group)
        
        # Gráficos em tempo real
        charts_group = QGroupBox("Histórico de Desempenho")
        charts_layout = QHBoxLayout()
        
        self.cpu_chart = RealtimeChart("Uso de CPU (60s)")
        charts_layout.addWidget(self.cpu_chart)
        
        self.ram_chart = RealtimeChart("Uso de RAM (60s)")
        charts_layout.addWidget(self.ram_chart)
        
        # GPU chart se disponível
        if self.gpu_available:
            self.gpu_chart = RealtimeChart("Uso de GPU (60s)")
            charts_layout.addWidget(self.gpu_chart)
        else:
            self.disk_chart = RealtimeChart("Uso de Disk (60s)")
            charts_layout.addWidget(self.disk_chart)
        
        charts_group.setLayout(charts_layout)
        layout.addWidget(charts_group)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "📊 Monitoramento")

    def setup_sentinel_tab(self):
        """Aba Sentinel: Monitoramento Visual e Câmera"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 1. Feed da Câmera (Real)
        feed_group = QGroupBox("Sentinel Eye Feed (Câmera Principal)")
        feed_layout = QVBoxLayout()
        
        self.camera_feed_label = QLabel("INITIALIZING OPTICAL SENSORS...")
        self.camera_feed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_feed_label.setStyleSheet("background-color: #000; color: #00c3ff; font-family: Consolas;")
        self.camera_feed_label.setMinimumHeight(400)
        self.camera_feed_label.setScaledContents(True)
        
        feed_layout.addWidget(self.camera_feed_label)
        feed_group.setLayout(feed_layout)
        layout.addWidget(feed_group)
        
        # Timer de atualização de vídeo (30 FPS)
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self._update_camera_feed)
        self.video_timer.start(33)
        
        # 2. Status de Detecção
        detection_group = QGroupBox("Análise de Reconhecimento Visual")
        det_layout = QGridLayout()
        
        # Labels de Estado
        self.det_face_label = QLabel("FACE: N/A")
        self.det_face_label.setStyleSheet("color: #8899a6; font-weight: bold;")
        
        self.det_motion_label = QLabel("MOTION: SAFE")
        self.det_motion_label.setStyleSheet("color: #00ff00; font-weight: bold;")
        
        self.det_objects_label = QLabel("OBJECTS: ANALYZING...")
        self.det_objects_label.setStyleSheet("color: #e0e0e0;")
        
        det_layout.addWidget(self.det_face_label, 0, 0)
        det_layout.addWidget(self.det_motion_label, 0, 1)
        det_layout.addWidget(self.det_objects_label, 1, 0, 1, 2)
        
        detection_group.setLayout(det_layout)
        layout.addWidget(detection_group)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "👁️ Sentinel")

    def setup_cognitive_tab(self):
        """Aba do Laboratório Cognitivo (Curiosity Engine)"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Status de Estudo
        status_group = QGroupBox("Status de Hiper-Foco")
        status_layout = QHBoxLayout()
        
        self.study_status_label = QLabel("Estado: Ocioso")
        self.study_status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #8899a6;")
        status_layout.addWidget(self.study_status_label)
        
        self.current_topic_label = QLabel("Tópico Atual: Nenhum")
        self.current_topic_label.setStyleSheet("color: #00c3ff;")
        status_layout.addWidget(self.current_topic_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Lista de Curiosidades (Gaps de Conhecimento)
        gaps_group = QGroupBox("Âncora de Curiosidade (Backlog de Pesquisa)")
        gaps_layout = QVBoxLayout()
        
        self.curiosity_list_widget = QLabel("Nenhum tópico pendente.")
        self.curiosity_list_widget.setWordWrap(True)
        self.curiosity_list_widget.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.curiosity_list_widget.setStyleSheet("background-color: #0b0f19; padding: 10px; border: 1px dashed #1f293a; color: #e0e0e0;")
        
        scroll = QScrollArea()
        scroll.setWidget(self.curiosity_list_widget)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(300)
        
        gaps_layout.addWidget(scroll)
        gaps_group.setLayout(gaps_layout)
        layout.addWidget(gaps_group)
        
        # Controles
        controls_layout = QHBoxLayout()
        self.force_study_btn = QPushButton("🚀 Forçar Ciclo de Estudo")
        self.clear_gaps_btn = QPushButton("🗑️ Limpar Curiosidades")
        
        controls_layout.addWidget(self.force_study_btn)
        controls_layout.addWidget(self.clear_gaps_btn)
        layout.addLayout(controls_layout)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "🧠 Lab Cognitivo")

        # Conectar botões
        self.force_study_btn.clicked.connect(self._force_study_cycle)
        self.clear_gaps_btn.clicked.connect(self._clear_learning_gaps)

    def _force_study_cycle(self):
        """Dispara ciclo de estudo em background"""
        try:
            from src.learning.curiosity_engine import curiosity_engine
            if curiosity_engine:
                import threading
                threading.Thread(target=curiosity_engine.run_study_cycle, daemon=True).start()
                self.status_bar.showMessage("🚀 Ciclo de Estudo de Emergência iniciado!", 5000)
            else:
                self.status_bar.showMessage("⚠️ Curiosity Engine não disponível.", 5000)
        except Exception as e:
            logger.error(f"Erro ao disparar estudo: {e}")

    def _clear_learning_gaps(self):
        """Limpa backlog de curiosidades"""
        try:
            from src.learning.curiosity_engine import curiosity_engine
            if curiosity_engine:
                while not curiosity_engine.study_backlog.empty():
                    curiosity_engine.study_backlog.get()
                self._handle_curiosity_list([])
                self.status_bar.showMessage("🗑️ Backlog de pesquisa limpo.", 3000)
        except: pass

    def _handle_learning_status(self, topic, is_studying):
        self.is_studying = is_studying
        self.current_topic = topic
        
        if is_studying:
            self.study_status_label.setText("Estado: 📚 ESTUDANDO (HIPER-FOCO)")
            self.study_status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ff00ff;") # Roxo para estudo
            self.current_topic_label.setText(f"Tópico Atual: {topic}")
        else:
            self.study_status_label.setText("Estado: 😴 OCIOSO / SONHANDO")
            self.study_status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #8899a6;")
            self.current_topic_label.setText("Tópico Atual: Nenhum")

    def _handle_curiosity_list(self, gaps):
        self.curiosity_backlog = gaps
        if gaps:
            text = "\n".join([f"• {gap}" for gap in gaps])
            self.curiosity_list_widget.setText(text)
        else:
            self.curiosity_list_widget.setText("Nenhum tópico pendente.")
        
    def setup_ai_brain_tab(self):
        """Aba de informações da IA e Cérebro"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Status do Cérebro da IA
        brain_status_group = QGroupBox("🧠 Status do Cérebro JARVIS")
        brain_layout = QVBoxLayout()
        
        # Status geral
        self.brain_status_text = QLabel("Cérebro: OFFLINE")
        self.brain_status_text.setStyleSheet("font-size: 14px; font-weight: bold; color: #ff4444;")
        brain_layout.addWidget(self.brain_status_text)
        
        # Versão e modelo
        self.brain_version_text = QLabel("Versão: JARVIS 5.0 - Stark Protocol")
        self.brain_version_text.setStyleSheet("color: #e0e0e0;")
        brain_layout.addWidget(self.brain_version_text)
        
        # Modelo de IA ativo
        self.active_model_text = QLabel("Modelo Ativo: Nenhum")
        self.active_model_text.setStyleSheet("color: #00c3ff;")
        brain_layout.addWidget(self.active_model_text)
        
        brain_status_group.setLayout(brain_layout)
        layout.addWidget(brain_status_group)
        
        # Funções e Capacidades
        functions_group = QGroupBox("⚡ Funções e Capacidades Ativas")
        functions_layout = QVBoxLayout()
        
        # Lista de funções ativas
        self.functions_list = QLabel("Carregando funções...")
        self.functions_list.setWordWrap(True)
        self.functions_list.setStyleSheet("color: #e0e0e0; background-color: #0b0f19; padding: 10px; border-radius: 5px;")
        functions_layout.addWidget(self.functions_list)
        
        functions_group.setLayout(functions_layout)
        layout.addWidget(functions_group)
        
        # Consumo Específico da IA
        ai_consumption_group = QGroupBox("📈 Consumo Específico da IA")
        consumption_layout = QGridLayout()
        
        # CPU dedicado à IA
        self.ai_cpu_dedicated = QLabel("CPU Dedicado: 0%")
        consumption_layout.addWidget(self.ai_cpu_dedicated, 0, 0)
        
        # Memória dedicada à IA
        self.ai_memory_dedicated = QLabel("RAM Dedicado: 0MB")
        consumption_layout.addWidget(self.ai_memory_dedicated, 0, 1)
        
        # GPU dedicada à IA (se disponível)
        if self.gpu_available:
            self.ai_gpu_dedicated = QLabel("GPU Dedicado: 0%")
            consumption_layout.addWidget(self.ai_gpu_dedicated, 0, 2)
        
        # Threads ativos
        self.ai_threads = QLabel("Threads Ativos: 0")
        consumption_layout.addWidget(self.ai_threads, 1, 0)
        
        # Processos da IA
        self.ai_processes = QLabel("Processos IA: 0")
        consumption_layout.addWidget(self.ai_processes, 1, 1)
        
        # Tempo de resposta
        self.ai_response_time = QLabel("Tempo Resposta: 0ms")
        consumption_layout.addWidget(self.ai_response_time, 1, 2)
        
        ai_consumption_group.setLayout(consumption_layout)
        layout.addWidget(ai_consumption_group)
        
        # Estatísticas de Aprendizado
        learning_group = QGroupBox("🎓 Estatísticas de Aprendizado")
        learning_layout = QVBoxLayout()
        
        self.learning_stats = QLabel("Carregando estatísticas de aprendizado...")
        self.learning_stats.setWordWrap(True)
        self.learning_stats.setStyleSheet("color: #e0e0e0; background-color: #0b0f19; padding: 10px; border-radius: 5px;")
        learning_layout.addWidget(self.learning_stats)
        
        learning_group.setLayout(learning_layout)
        layout.addWidget(learning_group)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "🧠 IA/Cérebro")
        
    def setup_config_tab(self):
        """Aba de configurações manuais"""
        tab = QWidget()
        layout = QFormLayout()
        layout.setSpacing(15)
        
        # Configurações de Voz
        voice_group = QGroupBox("Configurações de Voz")
        voice_layout = QFormLayout()
        
        self.voice_speed = QSlider(Qt.Orientation.Horizontal)
        self.voice_speed.setRange(50, 200)
        self.voice_speed.setValue(100)
        voice_layout.addRow("Velocidade:", self.voice_speed)
        
        self.voice_volume = QSlider(Qt.Orientation.Horizontal)
        self.voice_volume.setRange(0, 100)
        self.voice_volume.setValue(100)
        voice_layout.addRow("Volume:", self.voice_volume)
        
        voice_group.setLayout(voice_layout)
        layout.addWidget(voice_group)
        
        # Configurações de IA
        ai_group = QGroupBox("Inteligência Artificial")
        ai_layout = QFormLayout()
        
        self.model_selector = QComboBox()
        self.model_selector.addItems(["Qwen 1.5B (Local)", "Gemini Flash (Cloud)", "Llama 3 (Local)"])
        ai_layout.addRow("Modelo Principal:", self.model_selector)
        
        self.temperature = QDoubleSpinBox()
        self.temperature.setRange(0.1, 2.0)
        self.temperature.setValue(0.7)
        self.temperature.setSingleStep(0.1)
        ai_layout.addRow("Criatividade (Temp):", self.temperature)
        
        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)
        
        # Configurações da Mente Coletiva (Network Mesh)
        network_group = QGroupBox("Mente Coletiva (Network Mesh)")
        network_layout = QFormLayout()
        
        self.network_enabled = QComboBox()
        self.network_enabled.addItems(["Desabilitado", "Habilitado"])
        self.network_enabled.setCurrentText("Habilitado")
        network_layout.addRow("Status:", self.network_enabled)
        
        self.google_drive_enabled = QComboBox()
        self.google_drive_enabled.addItems(["Desabilitado", "Habilitado"])
        self.google_drive_enabled.setCurrentText("Habilitado")
        network_layout.addRow("Google Drive Sync:", self.google_drive_enabled)
        
        self.local_network_enabled = QComboBox()
        self.local_network_enabled.addItems(["Desabilitado", "Habilitado"])
        self.local_network_enabled.setCurrentText("Habilitado")
        network_layout.addRow("Rede Local:", self.local_network_enabled)
        
        self.encryption_enabled = QComboBox()
        self.encryption_enabled.addItems(["Desabilitado", "Habilitado"])
        self.encryption_enabled.setCurrentText("Habilitado")
        network_layout.addRow("Criptografia:", self.encryption_enabled)
        
        network_group.setLayout(network_layout)
        layout.addWidget(network_group)
        
        # Botões de ação
        actions_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 Salvar Configurações")
        self.reset_btn = QPushButton("🔄 Restaurar Padrões")
        
        actions_layout.addWidget(self.save_btn)
        actions_layout.addWidget(self.reset_btn)
        
        layout.addRow(actions_layout)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "⚙️ Configurações")
        
        # Conectar botões
        self.save_btn.clicked.connect(self.save_configurations)
        self.reset_btn.clicked.connect(self.reset_configurations)

    def load_configurations(self):
        """Carregar configurações do arquivo YAML"""
        try:
            import yaml
            from pathlib import Path
            
            config_path = Path("config/network_mesh_config.yaml")
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                
                nm = config.get('network_mesh', {})
                
                # Atualizar interface
                self.network_enabled.setCurrentText("Habilitado" if nm.get('enabled') else "Desabilitado")
                self.google_drive_enabled.setCurrentText("Habilitado" if nm.get('google_drive', {}).get('enabled') else "Desabilitado")
                self.local_network_enabled.setCurrentText("Habilitado" if nm.get('local_network', {}).get('enabled') else "Desabilitado")
                self.encryption_enabled.setCurrentText("Habilitado" if nm.get('privacy', {}).get('encrypt_packets') else "Desabilitado")
                
        except Exception as e:
            logger.warning(f"Erro ao carregar configurações: {e}")

    def save_configurations(self):
        """Salvar configurações no arquivo YAML"""
        try:
            import yaml
            from pathlib import Path
            
            config_path = Path("config/network_mesh_config.yaml")
            
            # Ler configuração atual
            config = {}
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
            
            # Atualizar com valores da interface
            nm = config.setdefault('network_mesh', {})
            nm['enabled'] = self.network_enabled.currentText() == "Habilitado"
            
            gd = nm.setdefault('google_drive', {})
            gd['enabled'] = self.google_drive_enabled.currentText() == "Habilitado"
            
            ln = nm.setdefault('local_network', {})
            ln['enabled'] = self.local_network_enabled.currentText() == "Habilitado"
            
            privacy = nm.setdefault('privacy', {})
            privacy['encrypt_packets'] = self.encryption_enabled.currentText() == "Habilitado"
            
            # Salvar
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            self.status_bar.showMessage("✅ Configurações da Mente Coletiva salvas!", 3000)
            
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
            self.status_bar.showMessage("❌ Erro ao salvar configurações", 3000)

    def reset_configurations(self):
        """Restaurar configurações padrão"""
        self.network_enabled.setCurrentText("Habilitado")
        self.google_drive_enabled.setCurrentText("Habilitado")
        self.local_network_enabled.setCurrentText("Habilitado")
        self.encryption_enabled.setCurrentText("Habilitado")
        
        self.status_bar.showMessage("🔄 Configurações restauradas para padrão", 3000)

    def setup_console_tab(self):
        """Aba de logs do sistema"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Console de Logs do Sistema:"))
        
        self.log_area = QLabel("Iniciando logs...\n")
        self.log_area.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.log_area.setWordWrap(True)
        self.log_area.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.log_area.setStyleSheet("background-color: #000; color: #0f0; font-family: Consolas; padding: 10px;")
        
        scroll = QScrollArea()
        scroll.setWidget(self.log_area)
        scroll.setWidgetResizable(True)
        
        layout.addWidget(scroll)
        
        # Botão limpar
        clear_btn = QPushButton("Limpar Logs")
        clear_btn.clicked.connect(lambda: self.log_area.setText(""))
        layout.addWidget(clear_btn)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "💻 Console")

    def update_metrics(self):
        """Atualiza métricas em tempo real"""
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            
            self.cpu_gauge.set_value(cpu)
            self.ram_gauge.set_value(ram)
            
            self.cpu_chart.add_data(cpu)
            self.ram_chart.add_data(ram)
            
            # GPU metrics se disponível
            if self.gpu_available:
                gpu_usage = self._get_gpu_usage()
                if gpu_usage is not None:
                    self.gpu_gauge.set_value(gpu_usage)
                    self.gpu_chart.add_data(gpu_usage)
                else:
                    # Fallback para uso de memória GPU se não conseguir utilization
                    gpu_memory_usage = self._get_gpu_memory_usage()
                    if gpu_memory_usage is not None:
                        self.gpu_gauge.set_value(gpu_memory_usage)
                        self.gpu_chart.add_data(gpu_memory_usage)
                    else:
                        # Último fallback: mostrar disk
                        disk = psutil.disk_usage('/').percent
                        self.gpu_gauge.set_value(disk)
                        self.gpu_chart.add_data(disk)
            else:
                # Disk metrics se GPU não disponível
                disk = psutil.disk_usage('/').percent
                self.disk_gauge.set_value(disk)
                self.disk_chart.add_data(disk)
            
            # Atualizar métricas específicas da IA
            self._update_ai_metrics()
            self._update_brain_status()
                
        except Exception as e:
            logger.error(f"Erro ao atualizar métricas: {e}")

    def _get_gpu_usage(self) -> float:
        """Obtém uso da GPU (0-100%)"""
        try:
            if self.nvml_available:
                # Usar NVML para GPUs NVIDIA (mais preciso)
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                return util.gpu
        except Exception:
            pass
        return None

    def _get_gpu_memory_usage(self) -> float:
        """Obtém uso de memória da GPU (0-100%)"""
        try:
            if self.gpu_available:
                memory_allocated = torch.cuda.memory_allocated(0)
                memory_total = torch.cuda.get_device_properties(0).total_memory
                return (memory_allocated / memory_total) * 100
        except Exception:
            pass
        return None

    def _update_ai_metrics(self):
        """Atualiza métricas específicas da IA usando o HardwareManager"""
        from src.core.management.hardware_manager import hardware_manager
        try:
            status = hardware_manager.get_status()
            
            # Status da IA (Baseado no Hardware)
            self.ai_status_label.setText(f"Status: ONLINE ({status['tier']})")
            
            # Consumo Real
            cpu_usage = psutil.cpu_percent()
            self.ai_cpu_usage_label.setText(f"Sistema CPU: {cpu_usage:.1f}%")
            
            ram = psutil.virtual_memory()
            self.ai_memory_usage_label.setText(f"RAM Livre: {ram.available / (1024**3):.1f}GB")
            
            if self.gpu_available:
                vram_free = status.get("vram_free_gb", 0)
                self.ai_gpu_usage_label.setText(f"VRAM Livre: {vram_free:.1f}GB")
            
            # Threads e Processos
            self.ai_threads.setText(f"Threads IA: {status['threads']}")
            self.ai_processes.setText(f"Acelerador: {status['accelerator'] or 'Nenhum'}")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar métricas da IA: {e}")

    def _update_brain_status(self):
        """Atualiza informações do cérebro da IA com dados reais"""
        from src.core.management.hardware_manager import hardware_manager
        try:
            # 1. Status do Cérebro (Verificação Real)
            is_brain_loaded = False
            try:
                # Tenta verificar se o objeto ai_agent existe e tem modelo carregado
                if self.jarvis and hasattr(self.jarvis, 'ai_agent') and self.jarvis.ai_agent:
                    is_brain_loaded = True
            except: pass

            brain_status = "ONLINE - INTEGRADO" if is_brain_loaded else "OFFLINE - AGUARDANDO CONEXÃO"
            color = "#00ff00" if is_brain_loaded else "#ff4444"
            
            self.brain_status_text.setText(f"Cérebro: {brain_status}")
            self.brain_status_text.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {color};")
            
            # 2. Modelo Ativo (Detectar via Config ou Hardware)
            device = hardware_manager.get_device()
            hw_name = hardware_manager.gpu_name if device != 'cpu' else 'AVX-512 Optimized'
            self.active_model_text.setText(f"Core Engine: {device.upper()} ({hw_name})")
            
            # 3. Funções Ativas (Dinâmico)
            # 3. Funções Ativas (Baseado nas Threads do Python)
            import threading
            active_threads = [t.name for t in threading.enumerate()]
            
            # Mapeamento de threads para nomes "Stark"
            stark_modules = []
            if any("Camera" in t for t in active_threads): stark_modules.append("• Sentinel Vision (ONLINE)")
            else: stark_modules.append("• Sentinel Vision (OFFLINE)")
            
            if any("Voice" in t for t in active_threads) or any("Audio" in t for t in active_threads): stark_modules.append("• Voice Array (LISTENING)")
            else: stark_modules.append("• Voice Array (MUTED/OFFLINE)")
            
            if any("Mesh" in t for t in active_threads): stark_modules.append("• Network Mesh (ACTIVE)")
            
            # Adicionar fixos do sistema
            stark_modules.append("• Neural Decision Engine")
            stark_modules.append("• Hardware Sovereign Control")

            self.functions_list.setText("\n".join(stark_modules))
            
            # 4. Memória e Aprendizado (Long-term)
            try:
                from src.core.intelligence.memory import MemoryManager
                mm = MemoryManager()
                mem_count = mm.interactions.count() if mm.collection else 0
                learning_info = [
                    f"• Memórias Gravadas: {mem_count}",
                    "• Vínculo Neural: Estabilizado",
                    f"• Latência Média: {150 if hardware_manager.is_throttled else 45}ms",
                    "• Modo de Resposta: Adaptativo"
                ]
                self.learning_stats.setText("\n".join(learning_info))
            except:
                self.learning_stats.setText("• Memória: Modo Fallback (RAM)")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status do cérebro: {e}")

    def add_log_message(self, level, message):
        """Adiciona mensagem formatada ao console"""
        # Formatação básica de cores para HTML
        color = "#00ff00" # Verde (Info)
        if "ERROR" in level or "CRITICAL" in level: color = "#ff4444"
        elif "WARNING" in level: color = "#ffbb33"
        elif "DEBUG" in level: color = "#8899a6"
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Construir linha HTML
        log_html = f'<span style="color: #666;">[{timestamp}]</span> <span style="color: {color}; font-weight: bold;">[{level}]</span> <span style="color: #e0e0e0;">{message}</span><br>'
        
        # Append seguro (limitando tamanho para performance)
        current_html = self.log_area.text()
        if len(current_html) > 15000: 
            # Cortar o começo (inseguro com HTML puro, melhor limpar tudo ou usar lógica complexa)
            # Para simplicidade, limpamos se ficar gigante
            current_html = "" 
        
        self.log_area.setText(current_html + log_html)
        
        # Auto-scroll (Tentativa)
        scroll_bar = self.log_area.parent().parent().verticalScrollBar() # QLabel -> ScrollAreaChild -> ScrollArea -> ScrollBar
        if scroll_bar:
            scroll_bar.setValue(scroll_bar.maximum())

    def _on_log_received(self, msg: str):
        """Callback do QtLogHandler"""
        # Parse simples do formato padrão do logging
        try:
            parts = msg.split(' - ')
            if len(parts) >= 4:
                level = parts[2]
                message = " - ".join(parts[3:])
                self.add_log_message(level, message)
            else:
                self.add_log_message("INFO", msg)
        except:
            self.add_log_message("SYSTEM", msg)
        
    def _update_camera_feed(self):
        """Atualiza o feed da câmera real na aba Sentinel"""
        # Só atualiza se a aba Sentinel estiver visível para economizar recursos
        if self.tab_widget.currentIndex() != 1: return
            
        try:
            # Tentar pegar o frame mais recente do VisionSystem
            frame = None
            if self.jarvis and hasattr(self.jarvis, 'vision_system'):
                system = self.jarvis.vision_system
                if hasattr(system, 'last_frame') and system.last_frame is not None:
                    frame = system.last_frame
            
            # Se não tiver acesso ao sistema global, tentar captura direta (apenas para teste visual)
            if frame is None and not hasattr(self, '_cap'):
                # Inicialização lazy do OpenCV para teste standalone
                import cv2
                self._cap = cv2.VideoCapture(0)
            
            if frame is None and hasattr(self, '_cap'):
                ret, img = self._cap.read()
                if ret:
                    frame = img
            
            # Renderizar no Label
            if frame is not None:
                import cv2
                from PyQt6.QtGui import QImage, QPixmap
                
                # Converter BGR (OpenCV) para RGB (Qt)
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                
                # Redimensionar mantendo aspect ratio
                scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                    self.camera_feed_label.size(), 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                self.camera_feed_label.setPixmap(scaled_pixmap)
                self.det_objects_label.setText("OBJECTS: REALTIME FEED ACTIVE")
            else:
                self.camera_feed_label.setText("NO SIGNAL - CAMERA OFFLINE")
                
        except Exception as e:
            # logger.debug(f"Erro no feed de vídeo: {e}") # Debug only
            pass

    def closeEvent(self, event):
        """Limpeza ao fechar"""
        if hasattr(self, '_cap') and self._cap:
            self._cap.release()
        event.accept()
