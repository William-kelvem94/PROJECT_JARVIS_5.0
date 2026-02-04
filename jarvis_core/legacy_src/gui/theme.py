"""
Configuration file for the Stark UI Theme (Iron Man Aesthetic)
Defines colors, fonts, and dimensions for the application.
"""

class COLORS:
    # Primary Accents (Arc Reactor)
    PRIMARY = "#00F0FF"        # Cyan Neon
    PRIMARY_HOVER = "#00BCD4"  # Darker Cyan
    PRIMARY_DIM = "rgba(0, 240, 255, 0.1)" # Check if CTK supports alpha, otherwise hex

    # Backgrounds (Midnight)
    BG_MAIN = "#050505"        # Deepest Black
    BG_SIDEBAR = "#0A0A0A"     # Slightly Lighter Black
    BG_CARD = "#121212"        # Material Dark
    BG_CARD_HOVER = "#1E1E1E"
    
    # Text
    TEXT_MAIN = "#FFFFFF"
    TEXT_SUB = "#A0A0A0"
    TEXT_ACCENT = "#00F0FF"
    
    # Status
    SUCCESS = "#00E676"
    WARNING = "#FFEA00"
    ERROR = "#FF1744"
    
    # Border
    BORDER_SUBTLE = "#1F1F1F"
    BORDER_ACCENT = "#004044"

class FONTS:
    # Font Families - Prioritize Segoe UI Variable (Win 11) -> Segoe UI -> Roboto -> Arial
    FAMILY = "Segoe UI Variable Text"
    FAMILY_DISPLAY = "Segoe UI Variable Display"
    FAMILY_MONO = "Consolas"
    
    # Sizes
    H1 = 28
    H2 = 22
    H3 = 18
    BODY = 13
    SMALL = 11

class DIMENSIONS:
    CORNER_RADIUS = 15
    BUTTON_HEIGHT = 40
    SIDEBAR_WIDTH = 220
    TITLE_BAR_HEIGHT = 35
