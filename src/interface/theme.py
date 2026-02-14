"""
JARVIS 5.0 - Unified Theme System
Centraliza todos os estilos visuais para consistência
"""

from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtCore import Qt

class JarvisTheme:
    """Tema unificado para todas as interfaces JARVIS"""

    # Cores Base
    PRIMARY_CYAN = QColor(0, 255, 255)        # Neon Principal
    SECONDARY_ORANGE = QColor(255, 140, 0)    # Modo Escuta
    ACCENT_GOLD = QColor(255, 215, 0)         # Destaques
    SUCCESS_GREEN = QColor(0, 255, 0)         # Sucesso
    WARNING_YELLOW = QColor(255, 255, 0)      # Aviso
    ERROR_RED = QColor(255, 0, 0)             # Erro

    # Backgrounds
    BG_DARK = QColor(20, 20, 20)              # Fundo escuro
    BG_MEDIUM = QColor(35, 35, 35)            # Painéis
    BG_LIGHT = QColor(50, 50, 50)             # Hover states

    # Text Colors
    TEXT_PRIMARY = QColor(255, 255, 255)      # Texto principal
    TEXT_SECONDARY = QColor(200, 200, 200)    # Texto secundário
    TEXT_MUTED = QColor(150, 150, 150)        # Texto muted

    # Transparency Levels
    ALPHA_FULL = 255
    ALPHA_HIGH = 200
    ALPHA_MEDIUM = 150
    ALPHA_LOW = 100
    ALPHA_GLOW = 50

    @classmethod
    def get_dark_palette(cls):
        """Retorna QPalette configurada para tema escuro"""
        palette = QPalette()

        # Window (background principal)
        palette.setColor(QPalette.ColorRole.Window, cls.BG_DARK)
        palette.setColor(QPalette.ColorRole.WindowText, cls.TEXT_PRIMARY)

        # Base (widgets)
        palette.setColor(QPalette.ColorRole.Base, cls.BG_MEDIUM)
        palette.setColor(QPalette.ColorRole.AlternateBase, cls.BG_LIGHT)

        # Text
        palette.setColor(QPalette.ColorRole.Text, cls.TEXT_PRIMARY)
        palette.setColor(QPalette.ColorRole.BrightText, cls.TEXT_SECONDARY)

        # Buttons
        palette.setColor(QPalette.ColorRole.Button, cls.BG_MEDIUM)
        palette.setColor(QPalette.ColorRole.ButtonText, cls.TEXT_PRIMARY)

        # Highlights
        palette.setColor(QPalette.ColorRole.Highlight, cls.PRIMARY_CYAN)
        palette.setColor(QPalette.ColorRole.HighlightedText, cls.BG_DARK)

        return palette

    @classmethod
    def get_font(cls, size=10, bold=False):
        """Retorna fonte padronizada"""
        font = QFont("Consolas", size)
        font.setBold(bold)
        return font

    @classmethod
    def apply_theme(cls, widget):
        """Aplica tema unificado ao widget ou aplicação"""
        # Aplicar paleta
        widget.setPalette(cls.get_dark_palette())
        
        # Estilos globais via stylesheet
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: rgb({cls.BG_DARK.red()}, {cls.BG_DARK.green()}, {cls.BG_DARK.blue()});
                color: rgb({cls.TEXT_PRIMARY.red()}, {cls.TEXT_PRIMARY.green()}, {cls.TEXT_PRIMARY.blue()});
                font-family: Consolas;
            }}

            QPushButton {{
                background-color: rgb({cls.BG_MEDIUM.red()}, {cls.BG_MEDIUM.green()}, {cls.BG_MEDIUM.blue()});
                border: 1px solid rgb({cls.PRIMARY_CYAN.red()}, {cls.PRIMARY_CYAN.green()}, {cls.PRIMARY_CYAN.blue()});
                border-radius: 5px;
                padding: 8px 16px;
                color: rgb({cls.TEXT_PRIMARY.red()}, {cls.TEXT_PRIMARY.green()}, {cls.TEXT_PRIMARY.blue()});
            }}

            QPushButton:hover {{
                background-color: rgb({cls.BG_LIGHT.red()}, {cls.BG_LIGHT.green()}, {cls.BG_LIGHT.blue()});
                border-color: rgb({cls.SECONDARY_ORANGE.red()}, {cls.SECONDARY_ORANGE.green()}, {cls.SECONDARY_ORANGE.blue()});
            }}

            QPushButton:pressed {{
                background-color: rgb({cls.PRIMARY_CYAN.red()}, {cls.PRIMARY_CYAN.green()}, {cls.PRIMARY_CYAN.blue()});
                color: rgb({cls.BG_DARK.red()}, {cls.BG_DARK.green()}, {cls.BG_DARK.blue()});
            }}

            QProgressBar {{
                border: 1px solid rgb({cls.PRIMARY_CYAN.red()}, {cls.PRIMARY_CYAN.green()}, {cls.PRIMARY_CYAN.blue()});
                border-radius: 3px;
                text-align: center;
            }}

            QProgressBar::chunk {{
                background-color: rgb({cls.PRIMARY_CYAN.red()}, {cls.PRIMARY_CYAN.green()}, {cls.PRIMARY_CYAN.blue()});
            }}
        """)

    @classmethod
    def get_color_with_alpha(cls, color, alpha):
        """Retorna cor com transparência"""
        return QColor(color.red(), color.green(), color.blue(), alpha)