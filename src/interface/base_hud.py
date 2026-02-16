"""
JARVIS 5.0 - Base HUD Interface
===============================
Interface base unificada para todos os componentes de interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseHUD(ABC):
    """
    Interface base para todos os componentes de HUD do JARVIS.
    Fornece estrutura comum e métodos abstratos.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa o HUD base.

        Args:
            config: Configuração específica do HUD
        """
        self.config = config or {}
        self.is_visible = False
        self.position = self.config.get("position", {"x": 100, "y": 100})
        self.size = self.config.get("size", {"width": 400, "height": 300})
        self.opacity = self.config.get("opacity", 0.9)
        self.theme = self._load_theme()

        logger.info(f"Initialized {self.__class__.__name__} with config: {self.config}")

    def _load_theme(self) -> Dict[str, Any]:
        """Carrega configuração de tema"""
        try:
            from .theme import JarvisTheme

            return {
                "primary": JarvisTheme.PRIMARY_CYAN,
                "secondary": JarvisTheme.SECONDARY_ORANGE,
                "background": JarvisTheme.BG_DARK,
                "text": JarvisTheme.TEXT_PRIMARY,
            }
        except ImportError:
            # Fallback para tema básico
            return {
                "primary": "#00FFFF",
                "secondary": "#FF8C00",
                "background": "#141414",
                "text": "#FFFFFF",
            }

    @abstractmethod
    def render(self) -> None:
        """
        Renderiza/mostra o HUD.
        Deve ser implementado por subclasses.
        """
        pass

    @abstractmethod
    def hide(self) -> None:
        """
        Oculta o HUD.
        Deve ser implementado por subclasses.
        """
        pass

    @abstractmethod
    def update_status(self, status: Dict[str, Any]) -> None:
        """
        Atualiza o status exibido no HUD.

        Args:
            status: Dicionário com informações de status
        """
        pass

    @abstractmethod
    def update_position(self, x: int, y: int) -> None:
        """
        Atualiza a posição do HUD.

        Args:
            x: Coordenada X
            y: Coordenada Y
        """
        pass

    def toggle_visibility(self) -> None:
        """Alterna visibilidade do HUD"""
        if self.is_visible:
            self.hide()
        else:
            self.render()

    def set_opacity(self, opacity: float) -> None:
        """
        Define opacidade do HUD.

        Args:
            opacity: Valor entre 0.0 e 1.0
        """
        self.opacity = max(0.0, min(1.0, opacity))
        self._apply_opacity()

    @abstractmethod
    def _apply_opacity(self) -> None:
        """Aplica configuração de opacidade"""
        pass

    def get_config(self) -> Dict[str, Any]:
        """Retorna configuração atual do HUD"""
        return {
            "position": self.position,
            "size": self.size,
            "opacity": self.opacity,
            "visible": self.is_visible,
            "theme": self.theme,
        }

    def cleanup(self) -> None:
        """Limpa recursos do HUD"""
        self.hide()
        logger.info(f"Cleaned up {self.__class__.__name__}")


class HUDManager:
    """
    Gerenciador centralizado de HUDs.
    Gerencia múltiplos HUDs e suas interações.
    """

    def __init__(self):
        self.huds: Dict[str, BaseHUD] = {}
        self.active_hud: Optional[str] = None

    def register_hud(self, name: str, hud: BaseHUD) -> None:
        """
        Registra um HUD no gerenciador.

        Args:
            name: Nome identificador do HUD
            hud: Instância do HUD
        """
        self.huds[name] = hud
        logger.info(f"Registered HUD: {name}")

    def get_hud(self, name: str) -> Optional[BaseHUD]:
        """
        Retorna HUD pelo nome.

        Args:
            name: Nome do HUD

        Returns:
            Instância do HUD ou None se não encontrado
        """
        return self.huds.get(name)

    def show_hud(self, name: str) -> bool:
        """
        Mostra um HUD específico.

        Args:
            name: Nome do HUD

        Returns:
            True se conseguiu mostrar, False caso contrário
        """
        hud = self.get_hud(name)
        if hud:
            hud.render()
            self.active_hud = name
            return True
        return False

    def hide_hud(self, name: str) -> bool:
        """
        Oculta um HUD específico.

        Args:
            name: Nome do HUD

        Returns:
            True se conseguiu ocultar, False caso contrário
        """
        hud = self.get_hud(name)
        if hud:
            hud.hide()
            if self.active_hud == name:
                self.active_hud = None
            return True
        return False

    def hide_all(self) -> None:
        """Oculta todos os HUDs"""
        for hud in self.huds.values():
            hud.hide()
        self.active_hud = None

    def cleanup_all(self) -> None:
        """Limpa todos os HUDs"""
        for hud in self.huds.values():
            hud.cleanup()
        self.huds.clear()
        self.active_hud = None


# Singleton instance
hud_manager = HUDManager()
