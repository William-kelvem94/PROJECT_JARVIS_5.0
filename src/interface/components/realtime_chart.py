from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QPolygonF
import collections

class RealtimeChart(QWidget):
    """
    GrÃ¡fico de linha simples em tempo real para monitoramento de recursos.
    """
    def __init__(self, title, max_points=60, parent=None):
        super().__init__(parent)
        self.title = title
        self.max_points = max_points
        self.data_points = collections.deque([0]*max_points, maxlen=max_points)
        self.setMinimumSize(300, 150)
        self.setStyleSheet("background-color: #0b0f19; border: 1px solid #1f293a; border-radius: 5px;")
        
        self.line_color = QColor(0, 195, 255)
        self.fill_color = QColor(0, 195, 255, 30)
        
    def add_data(self, value):
        self.data_points.append(value)
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fundo jÃ¡ desenhado pelo styleSheet ou custom aqui se quiser
        # painter.fillRect(self.rect(), QColor(10, 15, 20))
        
        width = self.width()
        height = self.height()
        
        # Margens
        margin_left = 10
        margin_right = 10
        margin_top = 20
        margin_bottom = 10
        
        plot_width = width - margin_left - margin_right
        plot_height = height - margin_top - margin_bottom
        
        # TÃ­tulo
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(10, 15, self.title)
        
        if not self.data_points:
            return
            
        # Calcular pontos
        points = []
        step_x = plot_width / (self.max_points - 1)
        
        max_val = 100 # Assumindo percentual por enquanto
        
        for i, val in enumerate(self.data_points):
            x = margin_left + (i * step_x)
            # Inverter Y (0 em cima, H em baixo)
            # Normalizar val entre 0 e plot_height
            y_norm = (val / max_val) * plot_height
            y = (margin_top + plot_height) - y_norm
            points.append(QPointF(x, y))
            
        # Desenhar PolÃ­gono (Preenchimento)
        poly_points = [QPointF(margin_left, margin_top + plot_height)] + points + [QPointF(width - margin_right, margin_top + plot_height)]
        painter.setBrush(self.fill_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(QPolygonF(poly_points))
        
        # Desenhar Linha
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self.line_color, 2))
        painter.drawPolyline(QPolygonF(points))
