from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QBrush

class CircularGauge(QWidget):
    """
    Componente visual de Gauge Circular estilo "Stark Tech".
    Exibe valores percentuais ou absolutos com anel de progresso.
    """
    def __init__(self, title, min_val=0, max_val=100, unit="", parent=None):
        super().__init__(parent)
        self.title = title
        self.min_val = min_val
        self.max_val = max_val
        self.value = min_val
        self.unit = unit
        self.setMinimumSize(150, 150)
        
        # Cores (Padrão Stark: Azul Ciano / Branco)
        self.color_track = QColor(20, 30, 40)
        self.color_active = QColor(0, 195, 255)
        self.color_text = QColor(255, 255, 255)
        
    def set_value(self, val):
        """Atualiza o valor e redesenha"""
        self.value = max(self.min_val, min(val, self.max_val))
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        width = min(rect.width(), rect.height())
        center = rect.center()
        
        # Ajuste de escala
        radius = (width / 2) - 10
        pen_width = 8
        
        # Desenha trilho (fundo)
        painter.setPen(QPen(self.color_track, pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawEllipse(center, int(radius), int(radius))
        
        # Desenha arco de valor
        percent = (self.value - self.min_val) / (self.max_val - self.min_val)
        start_angle = 270 * 16 # Começa no topo (270 graus)
        span_angle = -percent * 360 * 16 # Sentido horário
        
        active_pen = QPen(self.color_active, pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(active_pen)
        painter.drawArc(QRectF(center.x() - radius, center.y() - radius, radius*2, radius*2), start_angle, int(span_angle))
        
        # Texto: Valor
        painter.setPen(self.color_text)
        font_val = QFont("Arial", 20, QFont.Weight.Bold)
        painter.setFont(font_val)
        
        text_rect = QRectF(center.x() - radius, center.y() - 20, radius*2, 40)
        value_str = f"{int(self.value)}"
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, value_str)
        
        # Texto: Unidade (menor)
        font_unit = QFont("Arial", 10)
        painter.setFont(font_unit)
        unit_rect = QRectF(center.x() - radius, center.y() + 15, radius*2, 20)
        painter.drawText(unit_rect, Qt.AlignmentFlag.AlignCenter, self.unit)
        
        # Texto: Título (topo)
        title_rect = QRectF(center.x() - radius, center.y() - 50, radius*2, 30)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, self.title)
