"""
Interface - Notification System
Sistema de notificações do HUD
"""

import logging
from typing import Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"

class Notification:
    """Notificação individual"""
    
    def __init__(self, message: str, type: NotificationType, duration: int = 5):
        self.message = message
        self.type = type
        self.duration = duration
        self.timestamp = datetime.now()
        self.id = f"{self.timestamp.timestamp()}"
    
    def __repr__(self):
        return f"<Notification {self.type.value}: {self.message}>"

class NotificationSystem:
    """Sistema de notificações"""
    
    def __init__(self):
        self.notifications = []
        self.max_notifications = 5
        self.qt_available = False
        
        try:
            from PyQt6.QtWidgets import QLabel
            self.QLabel = QLabel
            self.qt_available = True
            logger.info("✅ Notification System disponível")
        except ImportError:
            logger.warning("⚠️ PyQt6 não disponível")
    
    def show(self, message: str, type: NotificationType = NotificationType.INFO, duration: int = 5):
        """Mostra notificação"""
        notif = Notification(message, type, duration)
        
        # Adicionar à lista
        self.notifications.append(notif)
        
        # Limitar quantidade
        if len(self.notifications) > self.max_notifications:
            self.notifications.pop(0)
        
        # Log
        icon = {
            NotificationType.INFO: "ℹ️",
            NotificationType.SUCCESS: "✅",
            NotificationType.WARNING: "⚠️",
            NotificationType.ERROR: "❌"
        }
        
        logger.info(f"{icon[type]} {message}")
        
        # Mostrar no HUD (se disponível)
        if self.qt_available:
            self._render_notification(notif)
    
    def _render_notification(self, notif: Notification):
        """Renderiza notificação no HUD"""
        # Implementar com PyQt6
        # Criar QLabel transparente
        # Posicionar no canto
        # Auto-fade após duration
        pass
    
    def info(self, message: str, duration: int = 5):
        """Notificação de informação"""
        self.show(message, NotificationType.INFO, duration)
    
    def success(self, message: str, duration: int = 5):
        """Notificação de sucesso"""
        self.show(message, NotificationType.SUCCESS, duration)
    
    def warning(self, message: str, duration: int = 7):
        """Notificação de aviso"""
        self.show(message, NotificationType.WARNING, duration)
    
    def error(self, message: str, duration: int = 10):
        """Notificação de erro"""
        self.show(message, NotificationType.ERROR, duration)
    
    def clear_all(self):
        """Limpa todas as notificações"""
        self.notifications = []
        logger.debug("🗑️ Notificações limpas")
    
    def get_active(self) -> List[Notification]:
        """Retorna notificações ativas"""
        now = datetime.now()
        active = []
        
        for notif in self.notifications:
            elapsed = (now - notif.timestamp).total_seconds()
            if elapsed < notif.duration:
                active.append(notif)
        
        return active


# Instância global
notification_system = NotificationSystem()
