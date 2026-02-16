import tkinter as tk
from tkinter import ttk
from src.core.interface.tabs.base_tab import BaseTab

class DevicesTab(BaseTab):
    def __init__(self, notebook, interface):
        super().__init__(notebook, interface, "📱 Dispositivos")

    def create_widgets(self):
        # ===== DESCOBERTA DE DISPOSITIVOS =====
        discovery_frame = ttk.LabelFrame(
            self.frame, text="Device Discovery & Connection", padding=10
        )
        discovery_frame.pack(fill="x", padx=10, pady=5)

        # Controles de descoberta
        discovery_controls = tk.Frame(discovery_frame, bg="#1a1a1a")
        discovery_controls.pack(fill="x", pady=5)

        ttk.Button(
            discovery_controls,
            text="🔍 Escanear Rede",
            command=self._scan_network_devices,
        ).pack(side="left", padx=5)

        ttk.Button(
            discovery_controls,
            text="🆔 Detectar JARVIS",
            command=self._detect_jarvis_instances,
        ).pack(side="left", padx=5)

        ttk.Button(
            discovery_controls,
            text="🤝 Conectar Dispositivo",
            command=self._connect_device_manual,
        ).pack(side="left", padx=5)

        ttk.Button(
            discovery_controls,
            text="⚡ Força Democrática",
            command=self._force_democratic_election,
        ).pack(side="left", padx=5)

        # ===== LISTA DE DISPOSITIVOS =====
        devices_list_frame = ttk.LabelFrame(
            self.frame, text="Connected Devices", padding=10
        )
        devices_list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # TreeView para dispositivos
        columns = ("Device", "Type", "Status", "Capabilities", "Last Seen")
        self.devices_tree = ttk.Treeview(
            devices_list_frame, columns=columns, show="tree headings"
        )

        for col in columns:
            self.devices_tree.heading(col, text=col)
            self.devices_tree.column(col, width=150)

        scrollbar_devices = ttk.Scrollbar(
            devices_list_frame, orient="vertical", command=self.devices_tree.yview
        )
        self.devices_tree.configure(yscrollcommand=scrollbar_devices.set)

        self.devices_tree.pack(side="left", fill="both", expand=True)
        scrollbar_devices.pack(side="right", fill="y")

        # Controles de dispositivos
        device_controls = tk.Frame(self.frame, bg="#1a1a1a")
        device_controls.pack(fill="x", padx=10, pady=5)

        ttk.Button(
            device_controls,
            text="📊 Status Detalhado",
            command=self._show_device_details,
        ).pack(side="left", padx=5)

        ttk.Button(
            device_controls, text="🔄 Sincronizar", command=self._sync_selected_device
        ).pack(side="left", padx=5)

        ttk.Button(
            device_controls,
            text="❌ Desconectar",
            command=self._disconnect_selected_device,
        ).pack(side="left", padx=5)

    def _scan_network_devices(self):
        self.interface._log("🔍 Escaneando dispositivos na rede...")

    def _detect_jarvis_instances(self):
        self.interface._log("🆔 Detectando instâncias JARVIS...")

    def _connect_device_manual(self):
        self.interface._log("🤝 Conectando dispositivo manualmente...")

    def _force_democratic_election(self):
        self.interface._log("⚡ Forçando eleição democrática...")

    def _show_device_details(self):
        self.interface._log("📊 Mostrando detalhes do dispositivo...")

    def _sync_selected_device(self):
        self.interface._log("🔄 Sincronizando dispositivo selecionado...")

    def _disconnect_selected_device(self):
        self.interface._log("❌ Desconectando dispositivo...")
