import unittest
from unittest.mock import MagicMock, patch
import sys
import tkinter as tk
import os

# Mock imports
sys.modules['src.core.democratic_core'] = MagicMock()
sys.modules['src.core.identity.microsoft_device_identifier'] = MagicMock()
sys.modules['src.core.identity.enhanced_biometric_verifier'] = MagicMock()
sys.modules['pynvml'] = MagicMock()
sys.modules['torch'] = MagicMock()
sys.modules['psutil'] = MagicMock()

# Mock src.utils.config
sys.modules['src.utils.config'] = MagicMock()


from src.core.interface.democratic_control_interface import DemocraticControlInterface
from src.core.interface.tabs.identity_tab import IdentityTab
from src.core.interface.tabs.devices_tab import DevicesTab
from src.core.interface.tabs.network_tab import NetworkTab
from src.core.interface.tabs.training_tab import TrainingTab
from src.core.interface.tabs.integrations_tab import IntegrationsTab
from src.core.interface.tabs.monitoring_tab import MonitoringTab
from src.core.interface.tabs.power_tools_tab import PowerToolsTab

class TestDemocraticInterfaceStructure(unittest.TestCase):
    def setUp(self):
        self.jarvis_core = MagicMock()
        self.jarvis_core.config = {"system": {"base_path": "."}}

        # Try to initialize Tk, if it fails (headless), we skip GUI tests
        try:
            self.root = tk.Tk()
            self.interface = DemocraticControlInterface(self.jarvis_core)
            self.interface.root = self.root
        except tk.TclError:
            self.root = None
            self.interface = None
            print("⚠️ Skipping GUI initialization due to missing display")

    def tearDown(self):
        if self.root:
            self.root.destroy()

    def test_tabs_initialization(self):
        if not self.root:
            return

        # We can just verify that the class has the tab attributes initialized to None
        self.assertIsNone(self.interface.identity_tab)

        # Now let's try to initialize tabs manually or via _create_main_interface
        try:
            self.interface._create_main_interface()

            self.assertIsInstance(self.interface.identity_tab, IdentityTab)
            self.assertIsInstance(self.interface.devices_tab, DevicesTab)
            self.assertIsInstance(self.interface.network_tab, NetworkTab)
            self.assertIsInstance(self.interface.training_tab, TrainingTab)
            self.assertIsInstance(self.interface.integrations_tab, IntegrationsTab)
            self.assertIsInstance(self.interface.monitoring_tab, MonitoringTab)
            self.assertIsInstance(self.interface.power_tools_tab, PowerToolsTab)

            print("✅ Tabs initialized successfully")
        except Exception as e:
             self.fail(f"Failed to initialize interface: {e}")

if __name__ == '__main__':
    # Set DISPLAY to handle potential X11 issues if applicable
    if 'DISPLAY' not in os.environ:
         # Minimal effort to support headless
         pass
    unittest.main()
