"""
JARVIS 5.0 - SINGULARITY GUI
Interface Visual Moderna e Profissional
"""

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFrame, QGridLayout, QProgressBar,
    QTabWidget, QScrollArea, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon
import sys
import asyncio
import threading
from datetime import datetime
import psutil


class JarvisWorker(QThread):
    """Thread worker para executar JARVIS em background"""
    log_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str, str)  # (module, status)
    error_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = False
        
    def run(self):
        """Executa main_singularity em thread separada"""
        self.running = True
        try:
            import main_singularity
            
            # Criar novo event loop para esta thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            self.log_signal.emit("🚀 Iniciando JARVIS Singularity...")
            loop.run_until_complete(main_singularity.main())
            
        except Exception as e:
            self.error_signal.emit(f"❌ Erro: {str(e)}")
        finally:
            self.running = False
    
    def stop(self):
        """Para a execução"""
        self.running = False
        self.quit()


class ModuleStatusWidget(QFrame):
    """Widget para mostrar status de um módulo"""
    
    def __init__(self, name, icon):
        super().__init__()
        self.name = name
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
                border: 2px solid #00d9ff;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Ícone e nome
        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px; border: none;")
        header.addWidget(icon_label)
        
        name_label = QLabel(name)
        name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #00d9ff; border: none;")
        header.addWidget(name_label)
        header.addStretch()
        
        # Status indicator
        self.status_label = QLabel("●")
        self.status_label.setStyleSheet("font-size: 20px; color: #666; border: none;")
        header.addWidget(self.status_label)
        
        layout.addLayout(header)
        
        # Status text
        self.status_text = QLabel("Aguardando...")
        self.status_text.setStyleSheet("font-size: 11px; color: #888; border: none;")
        layout.addWidget(self.status_text)
        
        self.setLayout(layout)
    
    def set_status(self, status, color="#666"):
        """Atualiza status do módulo"""
        self.status_label.setStyleSheet(f"font-size: 20px; color: {color}; border: none;")
        self.status_text.setText(status)
        self.status_text.setStyleSheet(f"font-size: 11px; color: {color}; border: none;")


class JarvisGUI(QMainWindow):
    """Interface Principal do JARVIS"""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()
        self.setup_timers()
        
    def init_ui(self):
        """Inicializa interface"""
        self.setWindowTitle("J.A.R.V.I.S. 5.0 - SINGULARITY")
        self.setGeometry(100, 100, 1400, 900)
        
        # Estilo dark theme
        self.setStyleSheet("""
            QMainWindow {
                background: #0f0f1e;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00d9ff, stop:1 #0099cc);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00ffff, stop:1 #00ccff);
            }
            QPushButton:pressed {
                background: #0088aa;
            }
            QPushButton:disabled {
                background: #333;
                color: #666;
            }
            QTextEdit {
                background: #1a1a2e;
                color: #00ff00;
                border: 2px solid #00d9ff;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
            QTabWidget::pane {
                border: 2px solid #00d9ff;
                border-radius: 8px;
                background: #16213e;
            }
            QTabBar::tab {
                background: #1a1a2e;
                color: #00d9ff;
                padding: 10px 20px;
                border: 2px solid #00d9ff;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #16213e;
                color: #00ffff;
            }
            QProgressBar {
                border: 2px solid #00d9ff;
                border-radius: 8px;
                text-align: center;
                background: #1a1a2e;
                color: white;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d9ff, stop:1 #00ff00);
                border-radius: 6px;
            }
        """)
        
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # === HEADER ===
        header = self.create_header()
        main_layout.addWidget(header)
        
        # === CONTROL PANEL ===
        controls = self.create_controls()
        main_layout.addWidget(controls)
        
        # === TABS ===
        tabs = self.create_tabs()
        main_layout.addWidget(tabs, stretch=1)
        
        # === STATUS BAR ===
        status_bar = self.create_status_bar()
        main_layout.addWidget(status_bar)
    
    def create_header(self):
        """Cria header com logo e status"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
                border: 2px solid #00d9ff;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        layout = QHBoxLayout(header)
        
        # Logo e título
        title_layout = QVBoxLayout()
        
        title = QLabel("J.A.R.V.I.S. 5.0")
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: #00d9ff; border: none;")
        title_layout.addWidget(title)
        
        subtitle = QLabel("Just A Rather Very Intelligent System - SINGULARITY")
        subtitle.setStyleSheet("font-size: 14px; color: #888; border: none;")
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Status principal
        status_layout = QVBoxLayout()
        
        self.main_status_label = QLabel("● OFFLINE")
        self.main_status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff4444; border: none;")
        status_layout.addWidget(self.main_status_label, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.uptime_label = QLabel("Uptime: 00:00:00")
        self.uptime_label.setStyleSheet("font-size: 12px; color: #888; border: none;")
        status_layout.addWidget(self.uptime_label, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(status_layout)
        
        return header
    
    def create_controls(self):
        """Cria painel de controles"""
        controls = QFrame()
        controls.setStyleSheet("""
            QFrame {
                background: #16213e;
                border: 2px solid #00d9ff;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QHBoxLayout(controls)
        
        # Botão Start
        self.start_btn = QPushButton("▶ INICIAR JARVIS")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.clicked.connect(self.start_jarvis)
        layout.addWidget(self.start_btn)
        
        # Botão Stop
        self.stop_btn = QPushButton("■ PARAR")
        self.stop_btn.setMinimumHeight(50)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_jarvis)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff4444, stop:1 #cc0000);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff6666, stop:1 #ff0000);
            }
        """)
        layout.addWidget(self.stop_btn)
        
        # Botão Restart
        restart_btn = QPushButton("🔄 REINICIAR")
        restart_btn.setMinimumHeight(50)
        restart_btn.clicked.connect(self.restart_jarvis)
        layout.addWidget(restart_btn)
        
        # Botão Config
        config_btn = QPushButton("⚙ CONFIGURAÇÕES")
        config_btn.setMinimumHeight(50)
        layout.addWidget(config_btn)
        
        return controls
    
    def create_tabs(self):
        """Cria abas de conteúdo"""
        tabs = QTabWidget()
        
        # === TAB 1: MODULES ===
        modules_tab = QWidget()
        modules_layout = QVBoxLayout(modules_tab)
        
        # Grid de módulos
        modules_grid = QGridLayout()
        modules_grid.setSpacing(15)
        
        self.modules = {
            'brain': ModuleStatusWidget('Brain', '🧠'),
            'senses': ModuleStatusWidget('Senses', '👁️'),
            'mouth': ModuleStatusWidget('Mouth', '🗣️'),
            'hive_mind': ModuleStatusWidget('Hive Mind', '🌐'),
            'world': ModuleStatusWidget('World', '🏠'),
            'interface': ModuleStatusWidget('Interface', '🖥️'),
            'guardian': ModuleStatusWidget('Guardian', '🛡️'),
        }
        
        row, col = 0, 0
        for widget in self.modules.values():
            modules_grid.addWidget(widget, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        modules_layout.addLayout(modules_grid)
        modules_layout.addStretch()
        
        tabs.addTab(modules_tab, "📊 Módulos")
        
        # === TAB 2: LOGS ===
        logs_tab = QWidget()
        logs_layout = QVBoxLayout(logs_tab)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        logs_layout.addWidget(self.log_text)
        
        tabs.addTab(logs_tab, "📝 Logs")
        
        # === TAB 3: SYSTEM ===
        system_tab = QWidget()
        system_layout = QVBoxLayout(system_tab)
        
        # CPU
        cpu_group = QGroupBox("CPU")
        cpu_group.setStyleSheet("QGroupBox { color: #00d9ff; font-weight: bold; }")
        cpu_layout = QVBoxLayout()
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setMinimumHeight(30)
        cpu_layout.addWidget(self.cpu_bar)
        cpu_group.setLayout(cpu_layout)
        system_layout.addWidget(cpu_group)
        
        # RAM
        ram_group = QGroupBox("RAM")
        ram_group.setStyleSheet("QGroupBox { color: #00d9ff; font-weight: bold; }")
        ram_layout = QVBoxLayout()
        self.ram_bar = QProgressBar()
        self.ram_bar.setMinimumHeight(30)
        ram_layout.addWidget(self.ram_bar)
        ram_group.setLayout(ram_layout)
        system_layout.addWidget(ram_group)
        
        # Disk
        disk_group = QGroupBox("Disco")
        disk_group.setStyleSheet("QGroupBox { color: #00d9ff; font-weight: bold; }")
        disk_layout = QVBoxLayout()
        self.disk_bar = QProgressBar()
        self.disk_bar.setMinimumHeight(30)
        disk_layout.addWidget(self.disk_bar)
        disk_group.setLayout(disk_layout)
        system_layout.addWidget(disk_group)
        
        system_layout.addStretch()
        
        tabs.addTab(system_tab, "💻 Sistema")
        
        return tabs
    
    def create_status_bar(self):
        """Cria barra de status inferior"""
        status = QFrame()
        status.setStyleSheet("""
            QFrame {
                background: #1a1a2e;
                border: 2px solid #00d9ff;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout(status)
        
        self.status_text = QLabel("Pronto para iniciar")
        self.status_text.setStyleSheet("color: #00d9ff; border: none;")
        layout.addWidget(self.status_text)
        
        layout.addStretch()
        
        time_label = QLabel(datetime.now().strftime("%H:%M:%S"))
        time_label.setStyleSheet("color: #888; border: none;")
        layout.addWidget(time_label)
        
        return status
    
    def setup_timers(self):
        """Configura timers para atualização"""
        # Timer para system stats
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_system_stats)
        self.stats_timer.start(1000)  # 1 segundo
    
    def update_system_stats(self):
        """Atualiza estatísticas do sistema"""
        try:
            # CPU
            cpu = psutil.cpu_percent()
            self.cpu_bar.setValue(int(cpu))
            self.cpu_bar.setFormat(f"{cpu:.1f}%")
            
            # RAM
            ram = psutil.virtual_memory().percent
            self.ram_bar.setValue(int(ram))
            self.ram_bar.setFormat(f"{ram:.1f}%")
            
            # Disk
            disk = psutil.disk_usage('/').percent
            self.disk_bar.setValue(int(disk))
            self.disk_bar.setFormat(f"{disk:.1f}%")
            
        except Exception as e:
            pass
    
    def start_jarvis(self):
        """Inicia JARVIS"""
        self.log("="*60)
        self.log("🚀 INICIANDO JARVIS SINGULARITY...")
        self.log("="*60)
        
        self.main_status_label.setText("● INICIANDO...")
        self.main_status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffaa00; border: none;")
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Simular inicialização dos módulos
        modules_order = ['hive_mind', 'brain', 'senses', 'mouth', 'world', 'interface', 'guardian']
        
        for i, module in enumerate(modules_order):
            QTimer.singleShot(i * 500, lambda m=module: self.activate_module(m))
        
        # Após todos os módulos, marcar como online
        QTimer.singleShot(len(modules_order) * 500 + 500, self.set_online)
        
        # Iniciar worker thread
        self.worker = JarvisWorker()
        self.worker.log_signal.connect(self.log)
        self.worker.error_signal.connect(self.log_error)
        self.worker.start()
    
    def activate_module(self, module_name):
        """Ativa um módulo"""
        if module_name in self.modules:
            self.modules[module_name].set_status("✅ Online", "#00ff00")
            self.log(f"✅ {module_name.replace('_', ' ').title()} inicializado")
    
    def set_online(self):
        """Marca sistema como online"""
        self.main_status_label.setText("● ONLINE")
        self.main_status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ff00; border: none;")
        self.status_text.setText("Sistema operacional - Todos os módulos ativos")
        self.log("="*60)
        self.log("✅ JARVIS SINGULARITY ONLINE!")
        self.log("="*60)
    
    def stop_jarvis(self):
        """Para JARVIS"""
        self.log("⚠️ Parando JARVIS...")
        
        if self.worker:
            self.worker.stop()
            self.worker.wait()
        
        self.main_status_label.setText("● OFFLINE")
        self.main_status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff4444; border: none;")
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # Desativar módulos
        for module in self.modules.values():
            module.set_status("Offline", "#666")
        
        self.log("✅ JARVIS parado com sucesso")
    
    def restart_jarvis(self):
        """Reinicia JARVIS"""
        if self.stop_btn.isEnabled():
            self.stop_jarvis()
            QTimer.singleShot(2000, self.start_jarvis)
        else:
            self.start_jarvis()
    
    def log(self, message):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def log_error(self, message):
        """Adiciona erro ao log"""
        self.log(f"❌ ERRO: {message}")


def main():
    """Entry point da GUI"""
    app = QApplication(sys.argv)
    
    # Configurar fonte padrão
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Criar e mostrar janela
    window = JarvisGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
