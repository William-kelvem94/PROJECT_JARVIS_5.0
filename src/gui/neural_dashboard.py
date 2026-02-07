"""
JARVIS 5.0 - Neural Control Dashboard
======================================
Sprint 5: Polish & Advanced
Dashboard completo para monitoramento neural

USAGE: python src/gui/neural_dashboard.py
"""

import sys
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QTabWidget, QGroupBox, QPushButton, QTextEdit,
        QTableWidget, QTableWidgetItem, QProgressBar, QComboBox
    )
    from PyQt6.QtCore import QTimer, Qt
    from PyQt6.QtGui import QFont, QColor
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    logger.warning("PyQt6 not available")

try:
    import pyqtgraph as pg
    import numpy as np
    PYQTGRAPH_AVAILABLE = True
except ImportError:
    PYQTGRAPH_AVAILABLE = False
    logger.warning("PyQtGraph not available")


class EmotionGauge(QWidget):
    """Gauge visual para emoção atual"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_emotion = "neutral"
        self.confidence = 0.0
        self.setMinimumSize(300, 150)
    
    def set_emotion(self, emotion: str, confidence: float):
        """Atualizar emoção"""
        self.current_emotion = emotion
        self.confidence = confidence
        self.update()


class EmotionTimeline(QWidget):
    """Timeline de emoções dos últimos 10min"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        if PYQTGRAPH_AVAILABLE:
            self.plot_widget = pg.PlotWidget()
            self.plot_widget.setBackground('w')
            self.plot_widget.setLabel('left', 'Confidence')
            self.plot_widget.setLabel('bottom', 'Time (seconds)')
            self.plot_widget.setYRange(0, 1.0)
            
            layout = QVBoxLayout()
            layout.addWidget(self.plot_widget)
            self.setLayout(layout)
            
            # Data storage
            self.emotions_data = {}
            self.time_data = []
            self.max_points = 600  # 10 minutes at 1 sample/sec
        else:
            self.plot_widget = None
    
    def add_emotion_point(self, emotion: str, confidence: float, timestamp: float):
        """Adicionar ponto de emoção à timeline"""
        if not PYQTGRAPH_AVAILABLE:
            return
        
        if emotion not in self.emotions_data:
            self.emotions_data[emotion] = []
        
        self.time_data.append(timestamp)
        self.emotions_data[emotion].append(confidence)
        
        # Limitar pontos
        if len(self.time_data) > self.max_points:
            self.time_data.pop(0)
            for em_list in self.emotions_data.values():
                if len(em_list) > 0:
                    em_list.pop(0)
        
        self.update_plot()
    
    def update_plot(self):
        """Atualizar gráfico"""
        if not self.plot_widget:
            return
        
        self.plot_widget.clear()
        
        colors = {
            'neutral': (128, 128, 128),
            'happy': (255, 215, 0),
            'sad': (0, 0, 255),
            'angry': (255, 0, 0),
            'fear': (128, 0, 128),
            'surprise': (255, 165, 0),
            'disgust': (0, 128, 0)
        }
        
        for emotion, data in self.emotions_data.items():
            if len(data) > 0:
                color = colors.get(emotion, (128, 128, 128))
                self.plot_widget.plot(
                    self.time_data[-len(data):],
                    data,
                    pen=pg.mkPen(color, width=2),
                    name=emotion
                )


class MemoryGraphView(QWidget):
    """Visualização do Knowledge Graph"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout()
        
        # Controls
        controls = QHBoxLayout()
        self.concept_input = QComboBox()
        self.concept_input.setEditable(True)
        self.concept_input.setPlaceholderText("Select or type concept...")
        
        self.visualize_btn = QPushButton("Visualize")
        self.visualize_btn.clicked.connect(self.on_visualize)
        
        controls.addWidget(QLabel("Concept:"))
        controls.addWidget(self.concept_input)
        controls.addWidget(self.visualize_btn)
        
        layout.addLayout(controls)
        
        # Graph view
        if PYQTGRAPH_AVAILABLE:
            self.graph_widget = pg.GraphicsLayoutWidget()
            self.view = self.graph_widget.addViewBox()
            self.view.setAspectLocked()
            layout.addWidget(self.graph_widget)
        else:
            self.graph_widget = None
            info_label = QLabel("PyQtGraph not available")
            layout.addWidget(info_label)
        
        self.setLayout(layout)
    
    def on_visualize(self):
        """Visualizar conceito selecionado"""
        concept = self.concept_input.currentText()
        if concept:
            logger.info(f"Visualizing concept: {concept}")
            # TODO: Implementar visualização real do grafo
    
    def load_concepts(self, concepts: list):
        """Carregar lista de conceitos"""
        self.concept_input.clear()
        self.concept_input.addItems(concepts)


class PredictionsView(QWidget):
    """Timeline de previsões do LSTM"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout()
        
        # Predictions table
        self.predictions_table = QTableWidget()
        self.predictions_table.setColumnCount(4)
        self.predictions_table.setHorizontalHeaderLabels(['Time', 'Action', 'Confidence', 'Status'])
        
        layout.addWidget(QLabel("Predicted Next Actions:"))
        layout.addWidget(self.predictions_table)
        
        self.setLayout(layout)
    
    def add_prediction(self, time: str, action: str, confidence: float, status: str):
        """Adicionar previsão"""
        row = self.predictions_table.rowCount()
        self.predictions_table.insertRow(row)
        
        self.predictions_table.setItem(row, 0, QTableWidgetItem(time))
        self.predictions_table.setItem(row, 1, QTableWidgetItem(action))
        self.predictions_table.setItem(row, 2, QTableWidgetItem(f"{confidence:.2%}"))
        self.predictions_table.setItem(row, 3, QTableWidgetItem(status))


class TrainingMonitor(QWidget):
    """Monitor de progresso do Dream Cycle"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout()
        
        # Status
        self.status_label = QLabel("Status: Idle")
        self.status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Metrics
        metrics_layout = QHBoxLayout()
        
        self.loss_label = QLabel("Loss: --")
        self.perplexity_label = QLabel("Perplexity: --")
        self.accuracy_label = QLabel("Accuracy: --")
        
        metrics_layout.addWidget(self.loss_label)
        metrics_layout.addWidget(self.perplexity_label)
        metrics_layout.addWidget(self.accuracy_label)
        
        layout.addLayout(metrics_layout)
        
        # Log
        layout.addWidget(QLabel("Training Log:"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)
        
        self.setLayout(layout)
    
    def update_status(self, status: str, progress: int = 0):
        """Atualizar status"""
        self.status_label.setText(f"Status: {status}")
        self.progress_bar.setValue(progress)
    
    def update_metrics(self, loss: float, perplexity: float, accuracy: float):
        """Atualizar métricas"""
        self.loss_label.setText(f"Loss: {loss:.4f}")
        self.perplexity_label.setText(f"Perplexity: {perplexity:.2f}")
        self.accuracy_label.setText(f"Accuracy: {accuracy:.2%}")
    
    def add_log(self, message: str):
        """Adicionar mensagem ao log"""
        self.log_text.append(message)


class VoiceSignaturesEditor(QWidget):
    """Editor de voice signatures"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout()
        
        # Controls
        controls = QHBoxLayout()
        self.record_btn = QPushButton("🎤 Record Signature")
        self.record_btn.clicked.connect(self.on_record)
        
        self.delete_btn = QPushButton("🗑️ Delete Selected")
        self.delete_btn.clicked.connect(self.on_delete)
        
        controls.addWidget(self.record_btn)
        controls.addWidget(self.delete_btn)
        
        layout.addLayout(controls)
        
        # Signatures table
        self.signatures_table = QTableWidget()
        self.signatures_table.setColumnCount(4)
        self.signatures_table.setHorizontalHeaderLabels(['Name', 'Duration', 'Quality', 'Actions'])
        
        layout.addWidget(self.signatures_table)
        
        self.setLayout(layout)
    
    def on_record(self):
        """Gravar nova signature"""
        logger.info("Recording voice signature...")
        # TODO: Implementar gravação
    
    def on_delete(self):
        """Deletar signature selecionada"""
        selected = self.signatures_table.currentRow()
        if selected >= 0:
            self.signatures_table.removeRow(selected)
            logger.info(f"Deleted signature at row {selected}")


class NeuralDashboard(QMainWindow):
    """
    Dashboard Neural Completo do JARVIS
    
    Tabs:
    1. Emotion Monitoring
    2. Memory Graph
    3. Predictions
    4. Training Monitor
    5. Voice Signatures
    """
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("JARVIS Neural Control Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Title
        title = QLabel("🧠 JARVIS Neural Control Dashboard")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Emotion Monitoring
        emotion_tab = QWidget()
        emotion_layout = QVBoxLayout()
        
        self.emotion_gauge = EmotionGauge()
        self.emotion_timeline = EmotionTimeline()
        
        emotion_layout.addWidget(QLabel("Current Emotion:"))
        emotion_layout.addWidget(self.emotion_gauge)
        emotion_layout.addWidget(QLabel("Emotion Timeline (last 10 min):"))
        emotion_layout.addWidget(self.emotion_timeline)
        
        emotion_tab.setLayout(emotion_layout)
        self.tabs.addTab(emotion_tab, "😊 Emotions")
        
        # Tab 2: Memory Graph
        self.memory_graph = MemoryGraphView()
        self.tabs.addTab(self.memory_graph, "🧠 Memory Graph")
        
        # Tab 3: Predictions
        self.predictions_view = PredictionsView()
        self.tabs.addTab(self.predictions_view, "🔮 Predictions")
        
        # Tab 4: Training Monitor
        self.training_monitor = TrainingMonitor()
        self.tabs.addTab(self.training_monitor, "🏋️ Training")
        
        # Tab 5: Voice Signatures
        self.voice_signatures = VoiceSignaturesEditor()
        self.tabs.addTab(self.voice_signatures, "🎙️ Voice Signatures")
        
        layout.addWidget(self.tabs)
        
        # Status bar
        self.statusBar().showMessage("Dashboard initialized")
        
        # Timer for updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.on_timer_update)
        self.update_timer.start(1000)  # Update every second
        
        logger.info("✅ Neural Dashboard initialized")
    
    def on_timer_update(self):
        """Atualização periódica"""
        # TODO: Atualizar com dados reais
        pass


def main():
    """Run dashboard"""
    if not PYQT_AVAILABLE:
        print("❌ PyQt6 not available")
        return 1
    
    app = QApplication(sys.argv)
    
    # Apply dark theme (optional)
    app.setStyle('Fusion')
    
    dashboard = NeuralDashboard()
    dashboard.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
