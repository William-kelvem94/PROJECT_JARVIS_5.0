"""JARVIS 5.0 - Unified Theme System."""

<<<<<<< Updated upstream
from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtCore import Qt
=======
from __future__ import annotations

from dataclasses import dataclass

try:
    from PyQt6.QtGui import QColor, QFont, QPalette

    PYQT_AVAILABLE = True
except Exception:
    PYQT_AVAILABLE = False

    @dataclass(frozen=True)
    class QColor:  # type: ignore[override]
        _r: int
        _g: int
        _b: int
        _a: int = 255

        def red(self) -> int:
            return self._r

        def green(self) -> int:
            return self._g

        def blue(self) -> int:
            return self._b

        def alpha(self) -> int:
            return self._a

        def name(self) -> str:
            return f"#{self._r:02x}{self._g:02x}{self._b:02x}"

    class QFont:  # type: ignore[override]
        def __init__(self, family: str, size: int):
            self.family = family
            self.size = size
            self.bold = False

        def setBold(self, value: bool):  # noqa: N802
            self.bold = value

    class QPalette:  # type: ignore[override]
        class ColorRole:
            Window = "window"
            WindowText = "window_text"
            Base = "base"
            AlternateBase = "alternate_base"
            Text = "text"
            BrightText = "bright_text"
            Button = "button"
            ButtonText = "button_text"
            Highlight = "highlight"
            HighlightedText = "highlighted_text"

        def __init__(self):
            self.colors = {}

        def setColor(self, role, color):  # noqa: N802
            self.colors[role] = color

>>>>>>> Stashed changes

class JarvisTheme:
    """Shared color and style definitions for JARVIS interfaces."""

<<<<<<< Updated upstream
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
=======
    PRIMARY_CYAN = QColor(0, 255, 255)
    SECONDARY_ORANGE = QColor(255, 140, 0)
    ACCENT_GOLD = QColor(255, 215, 0)
    SUCCESS_GREEN = QColor(0, 255, 0)
    WARNING_YELLOW = QColor(255, 255, 0)
    ERROR_RED = QColor(255, 0, 0)

    BG_DARK = QColor(20, 20, 20)
    BG_MEDIUM = QColor(35, 35, 35)
    BG_LIGHT = QColor(50, 50, 50)

    TEXT_PRIMARY = QColor(255, 255, 255)
    TEXT_SECONDARY = QColor(200, 200, 200)
    TEXT_MUTED = QColor(150, 150, 150)
>>>>>>> Stashed changes

    ALPHA_FULL = 255
    ALPHA_HIGH = 200
    ALPHA_MEDIUM = 150
    ALPHA_LOW = 100
    ALPHA_GLOW = 50

    @classmethod
    def get_dark_palette(cls):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, cls.BG_DARK)
        palette.setColor(QPalette.ColorRole.WindowText, cls.TEXT_PRIMARY)
        palette.setColor(QPalette.ColorRole.Base, cls.BG_MEDIUM)
        palette.setColor(QPalette.ColorRole.AlternateBase, cls.BG_LIGHT)
        palette.setColor(QPalette.ColorRole.Text, cls.TEXT_PRIMARY)
        palette.setColor(QPalette.ColorRole.BrightText, cls.TEXT_SECONDARY)
        palette.setColor(QPalette.ColorRole.Button, cls.BG_MEDIUM)
        palette.setColor(QPalette.ColorRole.ButtonText, cls.TEXT_PRIMARY)
        palette.setColor(QPalette.ColorRole.Highlight, cls.PRIMARY_CYAN)
        palette.setColor(QPalette.ColorRole.HighlightedText, cls.BG_DARK)
        return palette

    @classmethod
    def get_font(cls, size: int = 10, bold: bool = False):
        font = QFont("Consolas", size)
        if hasattr(font, "setBold"):
            font.setBold(bold)
        return font

    @classmethod
    def apply_theme(cls, widget):
<<<<<<< Updated upstream
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
=======
        if hasattr(widget, "setPalette"):
            widget.setPalette(cls.get_dark_palette())

        if hasattr(widget, "setStyleSheet"):
            bg_rgb = (
                f"rgb({cls.BG_DARK.red()}, {cls.BG_DARK.green()}, {cls.BG_DARK.blue()})"
            )
            text_rgb = f"rgb({cls.TEXT_PRIMARY.red()}, {cls.TEXT_PRIMARY.green()}, {cls.TEXT_PRIMARY.blue()})"
            btn_bg_rgb = f"rgb({cls.BG_MEDIUM.red()}, {cls.BG_MEDIUM.green()}, {cls.BG_MEDIUM.blue()})"
            cyan_rgb = f"rgb({cls.PRIMARY_CYAN.red()}, {cls.PRIMARY_CYAN.green()}, {cls.PRIMARY_CYAN.blue()})"
            widget.setStyleSheet(
                f"QWidget {{ background-color: {bg_rgb}; color: {text_rgb}; font-family: Consolas; }}\n"
                f"QPushButton {{ background-color: {btn_bg_rgb}; border: 1px solid {cyan_rgb}; border-radius: 5px; padding: 8px 16px; }}"
            )

    @classmethod
    def get_color_with_alpha(cls, color: QColor, alpha: int):
        return QColor(color.red(), color.green(), color.blue(), alpha)


__all__ = ["JarvisTheme", "PYQT_AVAILABLE"]
>>>>>>> Stashed changes
