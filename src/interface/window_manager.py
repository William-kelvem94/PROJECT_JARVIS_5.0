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
    ORB = "orb" # Floating orb
    EMERGENCY = "emergency" # Manual override


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
    mode_changed = pyqtSignal(object) # Using object for better Enum resilience across modules
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
        self._mini_orb = None
        self._manual_panel = None
        
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

            # 🆕 Ctrl+Shift+Alt+J - Emergency Manual Panel
            emergency_panel = QShortcut(QKeySequence("Ctrl+Shift+Alt+J"), self._shortcut_window)
            emergency_panel.activated.connect(self._toggle_manual_panel)
            
            # Ctrl+Shift+X - Hide all
            hide_all = QShortcut(QKeySequence("Ctrl+Shift+X"), self._shortcut_window)
            hide_all.activated.connect(lambda: self.switch_mode(InterfaceMode.HIDDEN))
            
            logger.info("✅ Global shortcuts registered")
            logger.info("   Ctrl+Shift+J - Toggle Dashboard")
            logger.info("   Ctrl+Shift+H - Toggle HUD")
            logger.info("   Ctrl+Shift+Alt+J - EMERGENCY MANUAL PANEL")
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

    def _toggle_manual_panel(self):
        """Toggle emergency manual control panel"""
        if not self._manual_panel:
            try:
                from .manual_control_panel import ManualControlPanel
                self._manual_panel = ManualControlPanel()
                logger.info("✅ Emergency Manual Panel initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Manual Panel: {e}")
                return

        if self._manual_panel.isVisible():
            self._manual_panel.hide()
        else:
            self._manual_panel.show()
            self._manual_panel.raise_()
            self._manual_panel.activateWindow()
            
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
        elif self.current_mode == InterfaceMode.ORB and self._mini_orb:
            self._mini_orb.hide()
            
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

        elif self.current_mode == InterfaceMode.ORB:
            if not self._mini_orb:
                self._initialize_mini_orb()
            self._mini_orb.show()
            self._mini_orb.raise_()
            self._mini_orb.activateWindow()
            
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
            # Fallback to basic window with log_event support
            from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
            
            class FallbackHUD(QWidget):
                def __init__(self):
                    super().__init__()
                    layout = QVBoxLayout(self)
                    layout.addWidget(QLabel("HUD initialization failed"))
                    self.setLayout(layout)
                
                def log_event(self, message):
                    print(f"Fallback HUD Log: {message}")
                
                def show_response(self, text):
                    print(f"Fallback HUD Response: {text}")

            self._hud = FallbackHUD()
            
    def _initialize_dashboard(self):
        """Lazy initialization of Stark Dashboard"""
        try:
            from .stark_dashboard import StarkDashboard
            self._dashboard = StarkDashboard()
            
            # Connect mode switch request from dashboard
            self._dashboard.mode_switch_requested.connect(self.switch_mode)
            
            logger.info("✅ Stark Dashboard initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Dashboard: {e}")
            self._create_placeholder_dashboard()

    def _initialize_mini_orb(self):
        """Lazy initialization of Mini Orb"""
        try:
            from .mini_orb import MiniOrb
            self._mini_orb = MiniOrb()
            
            # Connect mode switch request
            self._mini_orb.mode_switch_requested.connect(self.switch_mode)
            
            logger.info("✅ Mini Hub Orb initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Mini Orb: {e}")

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
            
    def shutdown(self):
        """Shutdown seguro do WindowManager"""
        try:
            # Esconde todas as janelas primeiro
            self.switch_mode(InterfaceMode.HIDDEN)
            
            # Para timers (se existirem)
            if hasattr(self, 'update_timer') and self.update_timer:
                self.update_timer.stop()
                
            # Limpa widgets
            if hasattr(self, '_hud') and self._hud:
                self._hud.close()
                self._hud.deleteLater()
                self._hud = None
                
            if hasattr(self, '_dashboard') and self._dashboard:
                self._dashboard.close()
                self._dashboard.deleteLater()
                self._dashboard = None
                
            if hasattr(self, 'mini_orb') and getattr(self, 'mini_orb', None):
                self.mini_orb.close()
                self.mini_orb.deleteLater()
                self.mini_orb = None
                
            if self._tray_icon:
                self._tray_icon.hide()
                
            logger.info("✅ Window Manager cleaned up")
            
        except Exception as e:
            logger.error(f"❌ Erro no shutdown do WindowManager: {e}")

    def cleanup(self):
        """Cleanup resources (Delegates to shutdown)"""
        self.shutdown()


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
