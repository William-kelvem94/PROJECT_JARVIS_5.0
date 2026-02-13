import sys
import psutil
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QTabWidget, QLabel, QStatusBar, QFormLayout, QSlider, 
    QComboBox, QDoubleSpinBox, QPushButton, QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QAction

# Import custom components
try:
    from src.interface.components.circular_gauge import CircularGauge
    from src.interface.components.realtime_chart import RealtimeChart
except ImportError:
    # Fallback for direct testing if package structure not set
    from .components.circular_gauge import CircularGauge
    from .components.realtime_chart import RealtimeChart

class StarkDashboard(QMainWindow):
    """
    Janela principal do Control Panel (Stark Tech Style).
    Permite monitoramento em tempo real e configuraÃ§Ã£o manual do sistema.
    """
    
    # Signals
    mode_switch_requested = pyqtSignal(object) # Request switch to HUD/ORB
    
    def __init__(self, jarvis_core=None):
        super().__init__()
        self.jarvis = jarvis_core
        self.setWindowTitle("JARVIS Stark Control Panel")
        self.resize(1024, 768)
        
        # Stylesheet (Dark Stark Theme)
        self.setStyleSheet("""
            QMainWindow { background-color: #050a10; color: #e0e0e0; }
            QTabWidget::pane { border: 1px solid #1f293a; background: #0b0f19; }
            QTabBar::tab { background: #0b0f19; color: #8899a6; padding: 10px 20px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background: #1f293a; color: #00c3ff; border-bottom: 2px solid #00c3ff; }
            QLabel { color: #e0e0e0; font-family: 'Segoe UI'; }
            QPushButton { background-color: #1f293a; color: #00c3ff; border: 1px solid #00c3ff; padding: 8px; border-radius: 4px; }
            QPushButton:hover { background-color: #00c3ff; color: #050a10; }
            QGroupBox { border: 1px solid #1f293a; margin-top: 20px; font-weight: bold; color: #00c3ff; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        """)
        
        self.setup_ui()
        
        # Timer para atualizaÃ§Ã£o de mÃ©tricas
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_metrics)
        self.update_timer.start(1000) # 1s
        
    def setup_ui(self):
        # Layout principal com abas
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Abas
        self.setup_monitor_tab()
        self.setup_config_tab()
        self.setup_console_tab()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("âœ… Sistema JARVIS Online - Protocolo Stark Ativo")
        
        # Menu Bar para troca rÃ¡pida
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
        # Para evitar dependÃªncia circular, importamos InterfaceMode apenas aqui
        try:
            from src.interface.window_manager import InterfaceMode
            if mode_str == "hud":
                self.mode_switch_requested.emit(InterfaceMode.HUD_OVERLAY)
            elif mode_str == "orb":
                self.mode_switch_requested.emit(InterfaceMode.ORB)
            elif mode_str == "hidden":
                self.mode_switch_requested.emit(InterfaceMode.HIDDEN)
        except ImportError:
            # Fallback se nÃ£o conseguir importar (usar string)
            self.mode_switch_requested.emit(mode_str)

    def setup_monitor_tab(self):
        """Aba de monitoramento em tempo real"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Grid de mÃ©tricas (Gauges)
        metrics_group = QGroupBox("MÃ©tricas do Sistema")
        metrics_grid = QGridLayout()
        
        self.cpu_gauge = CircularGauge("CPU", 0, 100, "%")
        metrics_grid.addWidget(self.cpu_gauge, 0, 0)
        
        self.ram_gauge = CircularGauge("RAM", 0, 100, "%")
        metrics_grid.addWidget(self.ram_gauge, 0, 1)
        
        # Placeholder para GPU e Temperatura (simulados por enquanto se lib nÃ£o detectar)
        self.disk_gauge = CircularGauge("Disk", 0, 100, "%")
        metrics_grid.addWidget(self.disk_gauge, 0, 2)
        
        metrics_group.setLayout(metrics_grid)
        layout.addWidget(metrics_group)
        
        # GrÃ¡ficos em tempo real
        charts_group = QGroupBox("HistÃ³rico de Desempenho")
        charts_layout = QHBoxLayout()
        
        self.cpu_chart = RealtimeChart("Uso de CPU (60s)")
        charts_layout.addWidget(self.cpu_chart)
        
        self.ram_chart = RealtimeChart("Uso de RAM (60s)")
        charts_layout.addWidget(self.ram_chart)
        
        charts_group.setLayout(charts_layout)
        layout.addWidget(charts_group)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "ðŸ“Š Monitoramento")
        
    def setup_config_tab(self):
        """Aba de configuraÃ§Ãµes manuais"""
        tab = QWidget()
        layout = QFormLayout()
        layout.setSpacing(15)
        
        # ConfiguraÃ§Ãµes de Voz
        voice_group = QGroupBox("ConfiguraÃ§Ãµes de Voz")
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
        
        # ConfiguraÃ§Ãµes de IA
        ai_group = QGroupBox("InteligÃªncia Artificial")
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
        
        # BotÃµes de aÃ§Ã£o
        actions_layout = QHBoxLayout()
        self.save_btn = QPushButton("ðŸ’¾ Salvar ConfiguraÃ§Ãµes")
        self.reset_btn = QPushButton("ðŸ”„ Restaurar PadrÃµes")
        
        actions_layout.addWidget(self.save_btn)
        actions_layout.addWidget(self.reset_btn)
        
        layout.addRow(actions_layout)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "âš™ï¸ ConfiguraÃ§Ãµes")

    def setup_console_tab(self):
        """Aba de logs do sistema"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Console de Logs do Sistema:"))
        
        self.log_area = QLabel("Iniciando logs...\n")
        self.log_area.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.log_area.setWordWrap(True)
        self.log_area.setStyleSheet("background-color: #000; color: #0f0; font-family: Consolas; padding: 10px;")
        
        scroll = QScrollArea()
        scroll.setWidget(self.log_area)
        scroll.setWidgetResizable(True)
        
        layout.addWidget(scroll)
        
        # BotÃ£o limpar
        clear_btn = QPushButton("Limpar Logs")
        clear_btn.clicked.connect(lambda: self.log_area.setText(""))
        layout.addWidget(clear_btn)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "ðŸ’» Console")

    def update_metrics(self):
        """Atualiza mÃ©tricas em tempo real"""
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            self.cpu_gauge.set_value(cpu)
            self.ram_gauge.set_value(ram)
            self.disk_gauge.set_value(disk)
            
            self.cpu_chart.add_data(cpu)
            self.ram_chart.add_data(ram)
        except Exception:
            pass

    def add_log_message(self, level, message):
        """Adiciona mensagem ao console de logs"""
        current_text = self.log_area.text()
        if len(current_text) > 5000: current_text = current_text[-4000:]
        
        # Formata com cores HTML bÃ¡sico se suportado ou apenas texto
        new_line = f"[{level}] {message}\n"
        self.log_area.setText(current_text + new_line)
        # Scroll to bottom logic if needed (usually automatic if widget resizes, but explicit scroll bar value set is better)
        # For simple QLabel inside ScrollArea, auto-scroll is manual.
        
