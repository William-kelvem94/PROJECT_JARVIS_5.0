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

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, Qt
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut, QAction, QFont

from src.interface.ui_signals import ui_signals

logger = logging.getLogger(__name__)


class InterfaceMode(Enum):
    """Interface display modes"""

    HUD_OVERLAY = "hud"  # Transparent overlay
    DASHBOARD = "dashboard"  # Full control panel
    HIDDEN = "hidden"  # All interfaces hidden
    ORB = "orb"  # Floating orb
    EMERGENCY = "emergency"  # Manual override


# =============================
# Fallback de fonte Unicode para PyQt6
# =============================
def set_unicode_font(app):
    """
    Define uma fonte Unicode padrão para garantir visualização correta de emojis e caracteres especiais.
    Recomendada: Segoe UI, Arial Unicode MS, Noto Sans, DejaVu Sans.
    """
    font = QFont("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)


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
    mode_changed = pyqtSignal(
        object
    )  # Using object for better Enum resilience across modules
    status_update = pyqtSignal(str, str)  # (status_type, message)

    # Internal Signal for thread-safe mode switching
    _request_mode_switch = pyqtSignal(object)

    def __init__(self, app: QApplication, jarvis_core=None):
        """
        Initialize Window Manager.

        Args:
            app: QApplication instance
            jarvis_core: Reference to JarvisSingularity core for dashboard integration
        """
        super().__init__()
        self.app = app
        self.jarvis_core = jarvis_core
        self.current_mode = InterfaceMode.HIDDEN

        # Sinais de Controle Interno
        self._request_mode_switch.connect(self._do_switch_mode)

        # Conectar Hub de Sinais Global (Thread-Safe)
        ui_signals.update_status.connect(self._on_status_received)
        ui_signals.update_listening_state.connect(self._on_listening_received)
        ui_signals.show_notification.connect(self._on_notification_received)
        ui_signals.update_learning_status.connect(self._on_learning_status)
        
        # Connect Internal Status Handler
        self.status_update.connect(self._handle_status_update)

        # Interfaces
        self._hud = None
        self._dashboard = None
        self._mini_orb = None
        self._manual_panel = None

        # System tray
        self._tray_icon = None
        self._tray_menu = None

        # Callbacks
        self.on_mode_switch: Optional[Callable[[InterfaceMode], None]] = None

        # Conectar ao Signal Hub Global
        try:
            from src.utils.web_emitter import register_subscriber

            register_subscriber(self._on_global_signal)
            logger.info("âœ… WindowManager conectado ao Signal Hub")
        except Exception as e:
            logger.warning(f"âš ï¸ Falha ao conectar ao Signal Hub: {e}")

        # Carregar posições salvas das janelas
        self._load_window_positions()

        # Initialize components via Safe Loader
        from PyQt6.QtCore import QMetaObject, Q_ARG
        QMetaObject.invokeMethod(self, "_safe_ui_init", Qt.ConnectionType.QueuedConnection)

        logger.info("✅ Window Manager initialized (UI deferred)")

    @pyqtSlot()
    def _safe_ui_init(self):
        """Initialize UI components on the correct thread (Main Thread)"""
        try:
            self._setup_system_tray()
            self._setup_global_shortcuts()
            logger.info("✅ Window Manager: UI Components Initialized on Main Thread")
        except Exception as e:
            logger.error(f"❌ Window Manager UI Init Failed: {e}")

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
            hud_action.triggered.connect(
                lambda: self.switch_mode(InterfaceMode.HUD_OVERLAY)
            )
            self._tray_menu.addAction(hud_action)

            orb_action = QAction("💫 Mini Orb Mode", self._tray_menu)
            orb_action.triggered.connect(lambda: self.switch_mode(InterfaceMode.ORB))
            self._tray_menu.addAction(orb_action)

            dashboard_action = QAction("🛠️ Control Dashboard", self._tray_menu)
            dashboard_action.triggered.connect(
                lambda: self.switch_mode(InterfaceMode.DASHBOARD)
            )
            self._tray_menu.addAction(dashboard_action)

            self._tray_menu.addSeparator()

            # Quick actions
            hide_action = QAction("🙈 Hide All", self._tray_menu)
            hide_action.triggered.connect(
                lambda: self.switch_mode(InterfaceMode.HIDDEN)
            )
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

            logger.info("âœ… System tray initialized")

        except Exception as e:
            logger.error(f"âŒ Failed to setup system tray: {e}")

    def _setup_global_shortcuts(self):
        """Setup global keyboard shortcuts"""
        try:
            # Create main window for shortcuts (invisible)
            from PyQt6.QtWidgets import QMainWindow

            self._shortcut_window = QMainWindow()
            self._shortcut_window.hide()

            # Ctrl+Shift+J - Toggle Dashboard
            toggle_dashboard = QShortcut(
                QKeySequence("Ctrl+Shift+J"), self._shortcut_window
            )
            toggle_dashboard.activated.connect(self._toggle_dashboard)

            # Ctrl+Shift+H - Toggle HUD
            toggle_hud = QShortcut(QKeySequence("Ctrl+Shift+H"), self._shortcut_window)
            toggle_hud.activated.connect(self._toggle_hud)

            # Ctrl+Shift+O - Toggle Mini Orb
            toggle_orb = QShortcut(QKeySequence("Ctrl+Shift+O"), self._shortcut_window)
            toggle_orb.activated.connect(self._toggle_orb)

            # ðŸ†• Ctrl+Shift+Alt+J - Emergency Manual Panel
            emergency_panel = QShortcut(
                QKeySequence("Ctrl+Shift+Alt+J"), self._shortcut_window
            )
            emergency_panel.activated.connect(self._toggle_manual_panel)

            # Ctrl+Shift+X - Hide all
            hide_all = QShortcut(QKeySequence("Ctrl+Shift+X"), self._shortcut_window)
            hide_all.activated.connect(lambda: self.switch_mode(InterfaceMode.HIDDEN))

            logger.info("âœ… Global shortcuts registered")
            logger.info("   Ctrl+Shift+J - Toggle Dashboard")
            logger.info("   Ctrl+Shift+H - Toggle HUD")
            logger.info("   Ctrl+Shift+O - Toggle Mini Orb")
            logger.info("   Ctrl+Shift+Alt+J - EMERGENCY MANUAL PANEL")
            logger.info("   Ctrl+Shift+X - Hide All")

        except Exception as e:
            logger.error(f"âŒ Failed to setup shortcuts: {e}")

    def _on_tray_activated(self, reason):
        """Handle system tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._toggle_dashboard()

    @pyqtSlot()
    def _toggle_dashboard(self):
        """Toggle dashboard on/off"""
        if self.current_mode == InterfaceMode.DASHBOARD:
            self.switch_mode(InterfaceMode.HUD_OVERLAY)
        else:
            self.switch_mode(InterfaceMode.DASHBOARD)

    @pyqtSlot()
    def _toggle_hud(self):
        """Toggle HUD on/off"""
        if self.current_mode == InterfaceMode.HUD_OVERLAY:
            self.switch_mode(InterfaceMode.HIDDEN)
        else:
            self.switch_mode(InterfaceMode.HUD_OVERLAY)

    @pyqtSlot()
    def _toggle_orb(self):
        """Toggle Mini Orb on/off"""
        if self.current_mode == InterfaceMode.ORB:
            self.switch_mode(InterfaceMode.HIDDEN)
        else:
            self.switch_mode(InterfaceMode.ORB)

    @pyqtSlot(str)
    def _on_status_received(self, message: str):
        """Receptor de status do AIAgent"""
        if self._hud:
            self._hud.update_status(message)

    @pyqtSlot(bool)
    def _on_listening_received(self, state: bool):
        """Receptor de estado de voz"""
        if self._hud:
            self._hud.reactor.set_listening(state)

    @pyqtSlot(str, str)
    def _on_notification_received(self, title: str, message: str):
        """Mostra notificaÃ§Ã£o no sistema"""
        if self._tray_icon:
            self._tray_icon.showMessage(
                title, message, QSystemTrayIcon.MessageIcon.Information, 5000
            )

    def _toggle_manual_panel(self):
        """Toggle emergency manual control panel"""
        if not self._manual_panel:
            try:
                from .manual_control_panel import ManualControlPanel

                self._manual_panel = ManualControlPanel()
                logger.info("âœ… Emergency Manual Panel initialized")
            except Exception as e:
                logger.error(f"âŒ Failed to initialize Manual Panel: {e}")
                return

        if self._manual_panel.isVisible():
            self._manual_panel.hide()
        else:
            self._manual_panel.show()
            self._manual_panel.raise_()
            self._manual_panel.activateWindow()

    def switch_mode(self, mode: InterfaceMode):
        """
        Switch to specified interface mode (Thread-Safe Bridge).

        Args:
            mode: Target interface mode
        """
        import threading

        # Check if we are running in the Main Thread
        if threading.current_thread() is threading.main_thread():
            self._do_switch_mode(mode)
        else:
            # We are in a background thread, dispatch to Main Thread
            logger.debug(
                f"ðŸ”€ Redirecting switch_mode request ({mode.value}) to Main Thread"
            )
            self._request_mode_switch.emit(mode)

    @pyqtSlot(object)
    def _do_switch_mode(self, mode: InterfaceMode):
        """
        Actual mode switching, always runs on main thread.
        """
        if mode == self.current_mode:
            return

        logger.info(
            f"ðŸ”„ Switching interface mode: {self.current_mode.value} â†’ {mode.value}"
        )

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

        # Salvar posições quando interfaces são ocultas
        self._save_window_positions()

    def _show_current(self):
        """Show current active interface"""
        if self.current_mode == InterfaceMode.HUD_OVERLAY:
            if not self._hud:
                self._initialize_hud()
            # VerificaÃ§Ã£o de seguranÃ§a: _initialize_hud pode falhar e usar fallback
            if self._hud:
                self._restore_window_position(self._hud, "hud")
                self._hud.show()
                self._hud.raise_()
                self._hud.activateWindow()

        elif self.current_mode == InterfaceMode.DASHBOARD:
            if not self._dashboard:
                self._initialize_dashboard()
            if self._dashboard:
                self._dashboard.show()
                self._dashboard.raise_()
                self._dashboard.activateWindow()

        elif self.current_mode == InterfaceMode.ORB:
            if not self._mini_orb:
                self._initialize_mini_orb()
            if self._mini_orb:
                self._restore_window_position(self._mini_orb, "mini_orb")
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

            logger.info("âœ… HUD Overlay initialized")

        except Exception as e:
            logger.error(f"âŒ Failed to initialize HUD: {e}")
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

                def update_state(self, state):
                    """Stub para evitar crash se o HUD principal falhar"""
                    pass

                def update_status(self, status):
                    """Stub para compatibilidade com on_status_received"""
                    print(f"Fallback HUD Status: {status}")

            self._hud = FallbackHUD()

    def _initialize_dashboard(self):
        """Lazy initialization of Stark Dashboard"""
        try:
            from .stark_dashboard import StarkDashboard

            self._dashboard = StarkDashboard(jarvis_core=self.jarvis_core)

            # Connect mode switch request from dashboard
            self._dashboard.mode_switch_requested.connect(self.switch_mode)

            logger.info("âœ… Stark Dashboard initialized")

        except Exception as e:
            logger.error(f"âŒ Failed to initialize Dashboard: {e}")
            self._create_placeholder_dashboard()

    def _initialize_mini_orb(self):
        """Lazy initialization of Mini Orb"""
        try:
            from .mini_orb import MiniOrb

            self._mini_orb = MiniOrb()

            # Connect mode switch request
            self._mini_orb.mode_switch_requested.connect(self.switch_mode)

            logger.info("âœ… Mini Hub Orb initialized")

        except Exception as e:
            logger.error(f"âŒ Failed to initialize Mini Orb: {e}")

    def _load_window_positions(self):
        """Carrega posições salvas das janelas"""
        try:
            import json
            from pathlib import Path

            config_dir = Path(__file__).parent.parent.parent / "data"
            config_dir.mkdir(exist_ok=True)
            positions_file = config_dir / "window_positions.json"

            if positions_file.exists():
                with open(positions_file, "r", encoding="utf-8") as f:
                    positions = json.load(f)
                    self._saved_positions = positions
                    logger.info("âœ… Posições das janelas carregadas")
            else:
                self._saved_positions = {}

        except Exception as e:
            logger.warning(f"âš ï¸ Falha ao carregar posições das janelas: {e}")
            self._saved_positions = {}

    def _save_window_positions(self):
        """Salva posições atuais das janelas"""
        try:
            import json
            from pathlib import Path

            positions = {}

            # Salvar posição do HUD
            if self._hud and self._hud.isVisible():
                pos = self._hud.pos()
                positions["hud"] = {"x": pos.x(), "y": pos.y()}

            # Salvar posição do Mini Orb
            if self._mini_orb and self._mini_orb.isVisible():
                pos = self._mini_orb.pos()
                positions["mini_orb"] = {"x": pos.x(), "y": pos.y()}

            if positions:
                config_dir = Path(__file__).parent.parent.parent / "data"
                config_dir.mkdir(exist_ok=True)
                positions_file = config_dir / "window_positions.json"

                with open(positions_file, "w", encoding="utf-8") as f:
                    json.dump(positions, f, indent=2)

                logger.info("âœ… Posições das janelas salvas")

        except Exception as e:
            logger.warning(f"âš ï¸ Falha ao salvar posições das janelas: {e}")

    def _restore_window_position(self, window, window_type: str):
        """Restaura posição salva de uma janela"""
        try:
            if (
                hasattr(self, "_saved_positions")
                and window_type in self._saved_positions
            ):
                pos_data = self._saved_positions[window_type]
                # Verificar se a posição está dentro de algum monitor disponível
                screens = self.app.screens()
                valid_position = False

                for screen in screens:
                    geometry = screen.geometry()
                    if (
                        geometry.left() <= pos_data["x"] < geometry.right()
                        and geometry.top() <= pos_data["y"] < geometry.bottom()
                    ):
                        valid_position = True
                        break

                if valid_position:
                    window.move(pos_data["x"], pos_data["y"])
                    logger.info(f"âœ… Posição restaurada para {window_type}")
                else:
                    logger.info(
                        f"âš ï¸ Posição salva para {window_type} não é válida, usando padrão"
                    )

        except Exception as e:
            logger.warning(f"âš ï¸ Falha ao restaurar posição para {window_type}: {e}")

    def _create_placeholder_dashboard(self):
        """Create placeholder dashboard"""
        from PyQt6.QtWidgets import (
            QMainWindow,
            QLabel,
            QVBoxLayout,
            QWidget,
            QPushButton,
        )

        self._dashboard = QMainWindow()
        self._dashboard.setWindowTitle("JARVIS Control Dashboard (Placeholder)")
        self._dashboard.resize(800, 600)

        central = QWidget()
        layout = QVBoxLayout()

        label = QLabel(
            "ðŸš§ Control Dashboard - Coming Soon\n\n"
            "This will include:\n"
            "â€¢ Brain Configuration\n"
            "â€¢ Voice Settings\n"
            "â€¢ Vision System\n"
            "â€¢ System Logs\n"
            "â€¢ Hardware Monitor"
        )
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
        Update status on active interface (Thread-Safe via Signal).

        Args:
            status_type: Type of status update
            message: Status message
        """
        # Emit signal which will be handled by _handle_status_update on the main thread
        self.status_update.emit(status_type, message)

    @pyqtSlot(str, str)
    def _handle_status_update(self, status_type: str, message: str):
        """Slot to handle status updates on the main thread"""
        # Update active interface
        if self.current_mode == InterfaceMode.HUD_OVERLAY and self._hud:
            if hasattr(self._hud, "show_response"):
                self._hud.show_response(message)

        elif self.current_mode == InterfaceMode.DASHBOARD and self._dashboard:
            if hasattr(self._dashboard, "add_log_message"):
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
                title, message, QSystemTrayIcon.MessageIcon.Information, duration
            )

    @pyqtSlot(str, bool)
    def _on_learning_status(self, topic: str, is_studying: bool):
        """Handle learning status update"""
        # Repassa para o Mini Orb
        if self._mini_orb and hasattr(self._mini_orb, "set_studying"):
            self._mini_orb.set_studying(topic, is_studying)

        # O Dashboard já conecta direto ao sinal, mas se o HUD precisasse de intermediário seria aqui.
        # No caso, o HUD Moderno também já conecta direto.

    def shutdown(self):
        """Shutdown seguro do WindowManager"""
        try:
            # Esconde todas as janelas primeiro
            self.switch_mode(InterfaceMode.HIDDEN)

            # Para timers (se existirem)
            if hasattr(self, "update_timer") and self.update_timer:
                self.update_timer.stop()

            # Limpa widgets
            if hasattr(self, "_hud") and self._hud:
                self._hud.hide()
                self._hud.close()
                self._hud.deleteLater()
                self._hud = None

            if hasattr(self, "_dashboard") and self._dashboard:
                self._dashboard.hide()
                self._dashboard.close()
                self._dashboard.deleteLater()
                self._dashboard = None

            if hasattr(self, "_mini_orb") and self._mini_orb:
                self._mini_orb.hide()
                self._mini_orb.close()
                self._mini_orb.deleteLater()
                self._mini_orb = None

            if self._tray_icon:
                self._tray_icon.hide()

            logger.info("âœ… Window Manager cleaned up")

        except Exception as e:
            logger.error(f"âŒ Erro no shutdown do WindowManager: {e}")

    def _on_global_signal(self, event_type: str, data: dict):
        """Callback recebido do Signal Hub (thread-safe bridging)"""
        if event_type == "status":
            msg = data.get("details", "")
            status = data.get("status", "idle")
            model = data.get("model", "")
            tier = data.get("tier", "balanced")
            # Repassar para o HUD
            if self._hud:
                if hasattr(self._hud, "status_changed"):
                    self._hud.status_changed.emit(status)
                if tier and hasattr(self._hud, "tier_changed"):
                    self._hud.tier_changed.emit(tier)
                if msg and hasattr(self._hud, "response_ready"):
                    self._hud.response_ready.emit(msg)

        elif event_type == "context":
            app = data.get("app", "Sistema")
            if self._hud and hasattr(self._hud, "context_updated"):
                self._hud.context_updated.emit(app)

        elif event_type == "telemetry":
            if self._hud and hasattr(self._hud, "telemetry_updated"):
                self._hud.telemetry_updated.emit(data)

    def cleanup(self):
        """Cleanup resources (Delegates to shutdown)"""
        self.shutdown()


# Singleton instance
_window_manager: Optional[WindowManager] = None


def get_window_manager(
    app: Optional[QApplication] = None, jarvis_core=None
) -> WindowManager:
    """
    Get or create Window Manager singleton.

    Args:
        app: QApplication instance (required for first call)
        jarvis_core: Reference to JarvisSingularity core for dashboard integration

    Returns:
        WindowManager instance
    """
    global _window_manager

    if _window_manager is None:
        if app is None:
            raise ValueError(
                "QApplication required for first WindowManager initialization"
            )
        _window_manager = WindowManager(app, jarvis_core)
    elif jarvis_core is not None and _window_manager.jarvis_core is None:
        # Update jarvis_core if it wasn't set before
        _window_manager.jarvis_core = jarvis_core

    return _window_manager


# Testing
if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    app = QApplication(sys.argv)
    app.setApplicationName("JARVIS Singularity")

    # Create window manager
    wm = get_window_manager(app)

    # Start in HUD mode
    wm.switch_mode(InterfaceMode.HUD_OVERLAY)

    print("\n" + "=" * 60)
    print("JARVIS Window Manager Test")
    print("=" * 60)
    print("\nKeyboard Shortcuts:")
    print("  Ctrl+Shift+J - Toggle Dashboard")
    print("  Ctrl+Shift+H - Toggle HUD")
    print("  Ctrl+Shift+X - Hide All")
    print("\nSystem Tray:")
    print("  Double-click - Toggle Dashboard")
    print("  Right-click - Menu")
    print("\n" + "=" * 60 + "\n")

    sys.exit(app.exec())
