"""
JARVIS 5.0 - Toast Notification System
Sistema moderno de notificações flutuantes para feedback visual
"""

from PyQt6.QtWidgets import QLabel, QFrame, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve
from PyQt6.QtGui import QFont
from src.interface.theme import JarvisTheme

class ToastNotification(QFrame):
    """Modern toast notification with animations"""

    def __init__(self, title: str, message: str, notification_type: str = "info", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Setup appearance based on type
        self.setup_appearance(notification_type)

        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(2)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {self.text_color};")
        layout.addWidget(title_label)

        # Message
        message_label = QLabel(message)
        message_label.setFont(QFont("Segoe UI", 9))
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"color: {self.text_color};")
        layout.addWidget(message_label)

        # Auto-hide timer
        self.hide_timer = QTimer(self)
        self.hide_timer.timeout.connect(self.hide_animation)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.start(3000)  # Hide after 3 seconds

        # Animation
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Position at bottom-right of screen
        self.reposition()

    def setup_appearance(self, notification_type: str):
        """Setup colors and style based on notification type"""
        if notification_type == "success":
            self.bg_color = JarvisTheme.SUCCESS_GREEN
            self.border_color = JarvisTheme.SUCCESS_GREEN
            self.text_color = JarvisTheme.TEXT_PRIMARY
        elif notification_type == "warning":
            self.bg_color = JarvisTheme.WARNING_YELLOW
            self.border_color = JarvisTheme.WARNING_YELLOW
            self.text_color = JarvisTheme.BG_DARK
        elif notification_type == "error":
            self.bg_color = JarvisTheme.ERROR_RED
            self.border_color = JarvisTheme.ERROR_RED
            self.text_color = JarvisTheme.TEXT_PRIMARY
        else:  # info
            self.bg_color = JarvisTheme.PRIMARY_CYAN
            self.border_color = JarvisTheme.PRIMARY_CYAN
            self.text_color = JarvisTheme.BG_DARK

        self.setStyleSheet(f"""
            ToastNotification {{
                background-color: rgba({self.bg_color.red()}, {self.bg_color.green()}, {self.bg_color.blue()}, 230);
                border: 2px solid {self.border_color.name()};
                border-radius: 8px;
            }}
        """)

    def reposition(self):
        """Position toast at bottom-right of screen"""
        screen = self.screen()
        if screen:
            screen_geometry = screen.availableGeometry()
            self.move(
                screen_geometry.right() - self.width() - 20,
                screen_geometry.bottom() - self.height() - 50
            )

    def showEvent(self, event):
        """Start show animation"""
        super().showEvent(event)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()

    def hide_animation(self):
        """Animate hide and destroy"""
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.deleteLater)
        self.fade_animation.start()

    def enterEvent(self, event):
        """Pause auto-hide on hover"""
        super().enterEvent(event)
        self.hide_timer.stop()

    def leaveEvent(self, event):
        """Resume auto-hide when mouse leaves"""
        super().leaveEvent(event)
        self.hide_timer.start(2000)  # Restart with 2 seconds

class ToastManager:
    """Manager for toast notifications"""

    _instance = None

    def __init__(self):
        self.active_toasts = []

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def show_toast(self, title: str, message: str, notification_type: str = "info"):
        """Show a toast notification"""
        toast = ToastNotification(title, message, notification_type)

        # Position above previous toasts
        offset = len(self.active_toasts) * 80
        screen = toast.screen()
        if screen:
            screen_geometry = screen.availableGeometry()
            toast.move(
                screen_geometry.right() - toast.width() - 20,
                screen_geometry.bottom() - toast.height() - 50 - offset
            )

        toast.show()
        self.active_toasts.append(toast)

        # Remove from list when destroyed
        toast.destroyed.connect(lambda: self.active_toasts.remove(toast) if toast in self.active_toasts else None)

# Convenience functions
def show_success_toast(title: str, message: str):
    """Show success notification"""
    ToastManager.get_instance().show_toast(title, message, "success")

def show_warning_toast(title: str, message: str):
    """Show warning notification"""
    ToastManager.get_instance().show_toast(title, message, "warning")

def show_error_toast(title: str, message: str):
    """Show error notification"""
    ToastManager.get_instance().show_toast(title, message, "error")

def show_info_toast(title: str, message: str):
    """Show info notification"""
    ToastManager.get_instance().show_toast(title, message, "info")