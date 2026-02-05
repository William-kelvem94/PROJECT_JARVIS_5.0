"""
Interface - Theme Manager
Gerenciador de temas do HUD
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)

class Theme:
    """Tema do HUD"""
    
    def __init__(self, name: str, colors: Dict[str, str]):
        self.name = name
        self.colors = colors
    
    def get_color(self, element: str) -> str:
        """Retorna cor de um elemento"""
        return self.colors.get(element, "#FFFFFF")

class ThemeManager:
    """Gerenciador de temas"""
    
    def __init__(self):
        self.current_theme = "iron_man"
        self.themes = {}
        
        # Registrar temas padrão
        self._register_default_themes()
        
        logger.info(f"✅ Theme Manager inicializado (tema: {self.current_theme})")
    
    def _register_default_themes(self):
        """Registra temas padrão"""
        
        # Iron Man (azul ciano)
        self.themes["iron_man"] = Theme("Iron Man", {
            "primary": "#00D9FF",
            "secondary": "#0080FF",
            "accent": "#00FFFF",
            "background": "#000000",
            "text": "#FFFFFF",
            "orb": "#00D9FF",
            "glow": "#00FFFF"
        })
        
        # JARVIS (dourado)
        self.themes["jarvis"] = Theme("JARVIS", {
            "primary": "#FFD700",
            "secondary": "#FFA500",
            "accent": "#FFFF00",
            "background": "#000000",
            "text": "#FFFFFF",
            "orb": "#FFD700",
            "glow": "#FFFF00"
        })
        
        # Matrix (verde)
        self.themes["matrix"] = Theme("Matrix", {
            "primary": "#00FF00",
            "secondary": "#00AA00",
            "accent": "#00FF00",
            "background": "#000000",
            "text": "#00FF00",
            "orb": "#00FF00",
            "glow": "#00FF00"
        })
        
        # Cyberpunk (roxo/rosa)
        self.themes["cyberpunk"] = Theme("Cyberpunk", {
            "primary": "#FF00FF",
            "secondary": "#AA00FF",
            "accent": "#FF00AA",
            "background": "#000000",
            "text": "#FFFFFF",
            "orb": "#FF00FF",
            "glow": "#FF00AA"
        })
        
        # Minimal (branco)
        self.themes["minimal"] = Theme("Minimal", {
            "primary": "#FFFFFF",
            "secondary": "#CCCCCC",
            "accent": "#AAAAAA",
            "background": "#000000",
            "text": "#FFFFFF",
            "orb": "#FFFFFF",
            "glow": "#CCCCCC"
        })
    
    def set_theme(self, theme_name: str) -> bool:
        """Define tema atual"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            logger.info(f"🎨 Tema alterado: {theme_name}")
            return True
        else:
            logger.warning(f"⚠️ Tema não encontrado: {theme_name}")
            return False
    
    def get_current_theme(self) -> Theme:
        """Retorna tema atual"""
        return self.themes[self.current_theme]
    
    def get_color(self, element: str) -> str:
        """Retorna cor de um elemento do tema atual"""
        theme = self.get_current_theme()
        return theme.get_color(element)
    
    def list_themes(self) -> list:
        """Lista temas disponíveis"""
        return list(self.themes.keys())
    
    def create_custom_theme(self, name: str, colors: Dict[str, str]):
        """Cria tema customizado"""
        self.themes[name] = Theme(name, colors)
        logger.info(f"✅ Tema customizado criado: {name}")


# Instância global
theme_manager = ThemeManager()
