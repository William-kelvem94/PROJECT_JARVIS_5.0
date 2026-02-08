#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Window Manager (Dual Interface Controller)
================================================================
Manages switching between HUD Overlay and Control Dashboard modes.

Architecture:
- Mode 1: HUD Overlay (transparent, minimal, always-on-top)
- Mode 2: Control Dashboard (full window, configuration panel)
- System Tray Integration
- Voice/hotkey command switching
"""

import sys
import logging
from typing import Optional, Callable
from enum import Enum
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, Qt
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut, QAction

logger = logging.getLogger(__name__)


class InterfaceMode(Enum):
    """Interface display modes"""
    HUD_OVERLAY = "hud"  # Transparent overlay
    DASHBOARD = "dashboard"  # Full control panel
    HIDDEN = "hidden"  # All interfaces hidden


class WindowManager(QObject):
    """
    Central controller for JARVIS interface modes.
    
    Responsibilities:
    - Switch between HUD and Dashboard
    - Manage system tray icon
    - Handle keyboard shortcuts
    - Coordinate interface state
    
    Signals:
    - mode_changed: Emitted when interface mode changes
    - status_update: Status messages for HUD/Dashboard
    """
    
    # Signals
    mode_changed = pyqtSignal(InterfaceMode)
    status_update = pyqtSignal(str, str)  # (status_type, message)
    
    def __init__(self, app: QApplication):
        """
        Initialize Window Manager.
        
        Args:
            app: QApplication instance
        """
        super().__init__()
        self.app = app
        self.current_mode = InterfaceMode.HIDDEN  # Start hidden to force refresh on first switch
        
        # Interface instances (lazy loaded)
        self._hud = None
        self._dashboard = None
        
        # System tray
        self._tray_icon = None
        self._tray_menu = None
        
        # Callbacks
        self.on_mode_switch: Optional[Callable[[InterfaceMode], None]] = None
        
        # Initialize components
        self._setup_system_tray()
        self._setup_global_shortcuts()
        
        logger.info("✅ Window Manager initialized")
        
    def _setup_system_tray(self):
        """Setup system tray icon and menu"""
        try:
            # Create tray icon
            icon_path = Path(__file__).parent.parent.parent / "data" / "icon.png"
            if icon_path.exists():
                icon = QIcon(str(icon_path))
            else:
                # Use a better looking fallback or create a tiny colored bitbmap
                from PyQt6.QtGui import QPixmap, QPainter, QColor
                pixmap = QPixmap(64, 64)
                pixmap.fill(Qt.GlobalColor.transparent)
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setBrush(QColor(100, 200, 255))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(10, 10, 44, 44)
                painter.end()
                icon = QIcon(pixmap)
            
            self._tray_icon = QSystemTrayIcon(icon, self.app)
            
            # Create menu
            self._tray_menu = QMenu()
            
            # Mode switching actions
            hud_action = QAction("🎯 HUD Overlay Mode", self._tray_menu)
            hud_action.triggered.connect(lambda: self.switch_mode(InterfaceMode.HUD_OVERLAY))
            self._tray_menu.addAction(hud_action)
            
            dashboard_action = QAction("🎛️ Control Dashboard", self._tray_menu)
            dashboard_action.triggered.connect(lambda: self.switch_mode(InterfaceMode.DASHBOARD))
            self._tray_menu.addAction(dashboard_action)
            
            self._tray_menu.addSeparator()
            
            # Quick actions
            hide_action = QAction("🙈 Hide All", self._tray_menu)
            hide_action.triggered.connect(lambda: self.switch_mode(InterfaceMode.HIDDEN))
            self._tray_menu.addAction(hide_action)
            
            self._tray_menu.addSeparator()
            
            # Exit action
            quit_action = QAction("❌ Exit JARVIS", self._tray_menu)
            quit_action.triggered.connect(self.app.quit)
            self._tray_menu.addAction(quit_action)
            
            # Set menu and show tray
            self._tray_icon.setContextMenu(self._tray_menu)
            self._tray_icon.setToolTip("JARVIS Singularity")
            self._tray_icon.show()
            
            # Double-click to toggle
            self._tray_icon.activated.connect(self._on_tray_activated)
            
            logger.info("✅ System tray initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup system tray: {e}")
            
    def _setup_global_shortcuts(self):
        """Setup global keyboard shortcuts"""
        try:
            # Create main window for shortcuts (invisible)
            from PyQt6.QtWidgets import QMainWindow
            self._shortcut_window = QMainWindow()
            self._shortcut_window.hide()
            
            # Ctrl+Shift+J - Toggle Dashboard
            toggle_dashboard = QShortcut(QKeySequence("Ctrl+Shift+J"), self._shortcut_window)
            toggle_dashboard.activated.connect(self._toggle_dashboard)
            
            # Ctrl+Shift+H - Toggle HUD
            toggle_hud = QShortcut(QKeySequence("Ctrl+Shift+H"), self._shortcut_window)
            toggle_hud.activated.connect(self._toggle_hud)
            
            # Ctrl+Shift+X - Hide all
            hide_all = QShortcut(QKeySequence("Ctrl+Shift+X"), self._shortcut_window)
            hide_all.activated.connect(lambda: self.switch_mode(InterfaceMode.HIDDEN))
            
            logger.info("✅ Global shortcuts registered")
            logger.info("   Ctrl+Shift+J - Toggle Dashboard")
            logger.info("   Ctrl+Shift+H - Toggle HUD")
            logger.info("   Ctrl+Shift+X - Hide All")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup shortcuts: {e}")
            
    def _on_tray_activated(self, reason):
        """Handle system tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._toggle_dashboard()
            
    def _toggle_dashboard(self):
        """Toggle dashboard on/off"""
        if self.current_mode == InterfaceMode.DASHBOARD:
            self.switch_mode(InterfaceMode.HUD_OVERLAY)
        else:
            self.switch_mode(InterfaceMode.DASHBOARD)
            
    def _toggle_hud(self):
        """Toggle HUD on/off"""
        if self.current_mode == InterfaceMode.HUD_OVERLAY:
            self.switch_mode(InterfaceMode.HIDDEN)
        else:
            self.switch_mode(InterfaceMode.HUD_OVERLAY)
            
    @pyqtSlot(InterfaceMode)
    def switch_mode(self, mode: InterfaceMode):
        """
        Switch to specified interface mode.
        
        Args:
            mode: Target interface mode
        """
        if mode == self.current_mode:
            return
            
        logger.info(f"🔄 Switching interface mode: {self.current_mode.value} → {mode.value}")
        
        # Hide current interface
        self._hide_current()
        
        # Show target interface
        self.current_mode = mode
        self._show_current()
        
        # Emit signal
        self.mode_changed.emit(mode)
        
        # Call callback if registered
        if self.on_mode_switch:
            self.on_mode_switch(mode)
            
        # Update tray tooltip
        if self._tray_icon:
            self._tray_icon.setToolTip(f"JARVIS - {mode.value.upper()} Mode")
            
    def _hide_current(self):
        """Hide current active interface"""
        if self.current_mode == InterfaceMode.HUD_OVERLAY and self._hud:
            self._hud.hide()
        elif self.current_mode == InterfaceMode.DASHBOARD and self._dashboard:
            self._dashboard.hide()
            
    def _show_current(self):
        """Show current active interface"""
        if self.current_mode == InterfaceMode.HUD_OVERLAY:
            if not self._hud:
                self._initialize_hud()
            self._hud.show()
            self._hud.raise_()
            self._hud.activateWindow()
            
        elif self.current_mode == InterfaceMode.DASHBOARD:
            if not self._dashboard:
                self._initialize_dashboard()
            self._dashboard.show()
            self._dashboard.raise_()
            self._dashboard.activateWindow()
            
    def _initialize_hud(self):
        """Lazy initialization of HUD overlay"""
        try:
            from .modern_hud import ModernHUD
            self._hud = ModernHUD()
            
            # Connect signals
            self._hud.status_changed.connect(
                lambda status: self.status_update.emit("hud_status", status)
            )
            
            logger.info("✅ HUD Overlay initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize HUD: {e}")
            # Fallback to basic window
            from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
            self._hud = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(QLabel("HUD initialization failed"))
            self._hud.setLayout(layout)
            
    def _initialize_dashboard(self):
        """Lazy initialization of Control Dashboard"""
        try:
            from .control_dashboard import ControlDashboard
            self._dashboard = ControlDashboard()
            
            # Connect mode switch request from dashboard
            self._dashboard.mode_switch_requested.connect(self.switch_mode)
            
            logger.info("✅ Control Dashboard initialized")
            
        except ImportError:
            logger.warning("⚠️ Control Dashboard not yet implemented, using placeholder")
            self._create_placeholder_dashboard()
        except Exception as e:
            logger.error(f"❌ Failed to initialize Dashboard: {e}")
            self._create_placeholder_dashboard()
            
    def _create_placeholder_dashboard(self):
        """Create placeholder dashboard"""
        from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
        
        self._dashboard = QMainWindow()
        self._dashboard.setWindowTitle("JARVIS Control Dashboard (Placeholder)")
        self._dashboard.resize(800, 600)
        
        central = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel("🚧 Control Dashboard - Coming Soon\n\n"
                      "This will include:\n"
                      "• Brain Configuration\n"
                      "• Voice Settings\n"
                      "• Vision System\n"
                      "• System Logs\n"
                      "• Hardware Monitor")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        # Add switch button
        switch_btn = QPushButton("Switch to HUD Overlay")
        switch_btn.clicked.connect(lambda: self.switch_mode(InterfaceMode.HUD_OVERLAY))
        layout.addWidget(switch_btn)
        
        central.setLayout(layout)
        self._dashboard.setCentralWidget(central)
        
    def get_hud(self):
        """Get HUD instance (initialize if needed)"""
        if not self._hud:
            self._initialize_hud()
        return self._hud
        
    def get_dashboard(self):
        """Get Dashboard instance (initialize if needed)"""
        if not self._dashboard:
            self._initialize_dashboard()
        return self._dashboard
        
    def update_status(self, status_type: str, message: str):
        """
        Update status on active interface.
        
        Args:
            status_type: Type of status update
            message: Status message
        """
        self.status_update.emit(status_type, message)
        
        # Update active interface
        if self.current_mode == InterfaceMode.HUD_OVERLAY and self._hud:
            if hasattr(self._hud, 'show_response'):
                self._hud.show_response(message)
                
        elif self.current_mode == InterfaceMode.DASHBOARD and self._dashboard:
            if hasattr(self._dashboard, 'add_log_message'):
                self._dashboard.add_log_message(status_type, message)
                
    def show_notification(self, title: str, message: str, duration: int = 3000):
        """
        Show system tray notification.
        
        Args:
            title: Notification title
            message: Notification message
            duration: Duration in milliseconds
        """
        if self._tray_icon:
            self._tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.MessageIcon.Information,
                duration
            )
            
    def cleanup(self):
        """Cleanup resources"""
        if self._hud:
            self._hud.close()
        if self._dashboard:
            self._dashboard.close()
        if self._tray_icon:
            self._tray_icon.hide()
        if self._shortcut_window:
            self._shortcut_window.close()
            
        logger.info("✅ Window Manager cleaned up")


# Singleton instance
_window_manager: Optional[WindowManager] = None


def get_window_manager(app: Optional[QApplication] = None) -> WindowManager:
    """
    Get or create Window Manager singleton.
    
    Args:
        app: QApplication instance (required for first call)
        
    Returns:
        WindowManager instance
    """
    global _window_manager
    
    if _window_manager is None:
        if app is None:
            raise ValueError("QApplication required for first WindowManager initialization")
        _window_manager = WindowManager(app)
        
    return _window_manager


# Testing
if __name__ == "__main__":
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("JARVIS Singularity")
    
    # Create window manager
    wm = get_window_manager(app)
    
    # Start in HUD mode
    wm.switch_mode(InterfaceMode.HUD_OVERLAY)
    
    print("\n" + "="*60)
    print("JARVIS Window Manager Test")
    print("="*60)
    print("\nKeyboard Shortcuts:")
    print("  Ctrl+Shift+J - Toggle Dashboard")
    print("  Ctrl+Shift+H - Toggle HUD")
    print("  Ctrl+Shift+X - Hide All")
    print("\nSystem Tray:")
    print("  Double-click - Toggle Dashboard")
    print("  Right-click - Menu")
    print("\n" + "="*60 + "\n")
    
    sys.exit(app.exec())
