#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Democratic Control Interface
===========================================================
Interface democrática que dá ao usuário PODER E CONTROLE sobre
todo o sistema. Não pré-configurações: LIBERDADE TOTAL.

🔥 O PODER, A ESTRUTURA PARA QUE ISSO ACONTEÇA
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
from typing import Dict, Any
from datetime import datetime
from pathlib import Path
import logging
import psutil

# GPU detection imports
try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import pynvml

    pynvml.nvmlInit()
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False

# Imports dos sistemas democráticos
try:
    from src.core.democratic_core import DemocraticIntelligenceCore as DemocraticCore
except ImportError:
    DemocraticCore = None
from src.core.identity.microsoft_device_identifier import MicrosoftDeviceIdentifier
from src.core.identity.enhanced_biometric_verifier import EnhancedBiometricVerifier
from src.utils.config import config

logger = logging.getLogger(__name__)


class DemocraticControlInterface:
    """
    🔥 INTERFACE DE CONTROLE DEMOCRÁTICO TOTAL

    Esta interface dá ao usuário PODER TOTAL sobre:
    - Identificação e conexão de dispositivos
    - Configuração automática de Google Drive
    - Controle da rede democrática
    - Verificação biométrica avançada
    - Treinamento distribuído
    - Monitoramento em tempo real
    - Configuração de webhooks e integrações

    ✨ LIBERDADE TOTAL - SEM PRÉ-CONFIGURAÇÕES
    """

    def __init__(self, jarvis_core):
        self.jarvis_core = jarvis_core
        self.root = None

        # Sistemas principais
        self.microsoft_identifier = None
        self.biometric_verifier = None
        self.democratic_core = None

        # Estados da interface
        self.connected_devices = {}
        self.monitoring_active = False
        self.auto_training_active = False

        # Configurações do usuário
        self.user_preferences = self._load_user_preferences()

        print("🔥 Democratic Control Interface inicializada")
        print("💪 PODER TOTAL HABILITADO")

    def launch_interface(self):
        """🚀 LANÇA INTERFACE PRINCIPAL DE CONTROLE"""

        if self.root is not None:
            return

        self.root = tk.Tk()
        self.root.title("JARVIS SINGULARITY - CONTROLE DEMOCRÁTICO")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1a1a1a")

        # Configurar estilo escuro
        self._setup_dark_theme()

        # Criar interface principal
        self._create_main_interface()

        # Inicializar sistemas
        self._initialize_systems()

        # Loop principal
        self.root.mainloop()

    def _setup_dark_theme(self):
        """🎨 TEMA ESCURO PROFISSIONAL"""

        style = ttk.Style()
        style.theme_use("clam")

        # Cores personalizadas
        style.configure(
            "Title.TLabel",
            background="#1a1a1a",
            foreground="#00ff00",
            font=("Arial", 16, "bold"),
        )

        style.configure(
            "Status.TLabel",
            background="#1a1a1a",
            foreground="#ffffff",
            font=("Arial", 10),
        )

        style.configure(
            "Success.TLabel",
            background="#1a1a1a",
            foreground="#00ff00",
            font=("Arial", 10, "bold"),
        )

        style.configure(
            "Error.TLabel",
            background="#1a1a1a",
            foreground="#ff0000",
            font=("Arial", 10, "bold"),
        )

        style.configure("Control.TButton", font=("Arial", 10, "bold"))

    def _create_main_interface(self):
        """🏗️ CONSTRÓI INTERFACE PRINCIPAL"""

        # ===== HEADER =====
        header_frame = tk.Frame(self.root, bg="#1a1a1a", height=80)
        header_frame.pack(fill="x", padx=10, pady=5)
        header_frame.pack_propagate(False)

        title_label = ttk.Label(
            header_frame,
            text="🔥 JARVIS DEMOCRÁTICO - CONTROLE TOTAL",
            style="Title.TLabel",
        )
        title_label.pack(side="left", padx=10, pady=20)

        # Status geral
        self.status_label = ttk.Label(
            header_frame, text="⚡ SISTEMA DEMOCRÁTICO ATIVO", style="Success.TLabel"
        )
        self.status_label.pack(side="right", padx=10, pady=20)

        # ===== NOTEBOOK PRINCIPAL =====
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Abas principais
        self._create_identity_tab()
        self._create_devices_tab()
        self._create_network_tab()
        self._create_training_tab()
        self._create_integrations_tab()
        self._create_monitoring_tab()
        self._create_power_tools_tab()

        # ===== FOOTER DE CONTROLE RÁPIDO =====
        self._create_control_footer()

    def _create_identity_tab(self):
        """🆔 ABA DE GESTÃO DE IDENTIDADE"""

        identity_frame = ttk.Frame(self.notebook)
        self.notebook.add(identity_frame, text="🆔 Identidade")

        # ===== MICROSOFT ACCOUNT =====
        ms_frame = ttk.LabelFrame(
            identity_frame, text="Microsoft Account Detection", padding=10
        )
        ms_frame.pack(fill="x", padx=10, pady=5)

        # Status da conta
        self.ms_status_label = ttk.Label(
            ms_frame, text="🔍 Detectando...", style="Status.TLabel"
        )
        self.ms_status_label.pack(anchor="w")

        # Controles
        ms_controls = tk.Frame(ms_frame, bg="#1a1a1a")
        ms_controls.pack(fill="x", pady=5)

        ttk.Button(
            ms_controls,
            text="🔄 Re-detectar Conta",
            command=self._redetect_microsoft_account,
        ).pack(side="left", padx=5)

        ttk.Button(
            ms_controls,
            text="⚙️ Configurar Manualmente",
            command=self._manual_microsoft_config,
        ).pack(side="left", padx=5)

        ttk.Button(
            ms_controls,
            text="📋 Ver Detalhes Completos",
            command=self._show_microsoft_details,
        ).pack(side="left", padx=5)

        # ===== GOOGLE DRIVE =====
        drive_frame = ttk.LabelFrame(
            identity_frame, text="Google Drive Integration", padding=10
        )
        drive_frame.pack(fill="x", padx=10, pady=5)

        # Status do Drive
        self.drive_status_label = ttk.Label(
            drive_frame, text="📂 Analisando...", style="Status.TLabel"
        )
        self.drive_status_label.pack(anchor="w")

        # Controles do Drive
        drive_controls = tk.Frame(drive_frame, bg="#1a1a1a")
        drive_controls.pack(fill="x", pady=5)

        ttk.Button(
            drive_controls,
            text="🔗 Conectar Google Drive",
            command=self._connect_google_drive,
        ).pack(side="left", padx=5)

        ttk.Button(
            drive_controls,
            text="📍 Configurar Estrutura",
            command=self._setup_drive_structure,
        ).pack(side="left", padx=5)

        ttk.Button(
            drive_controls,
            text="☁️ Sincronizar Agora",
            command=self._sync_google_drive,
        ).pack(side="left", padx=5)

        # ===== VERIFICAÇÃO BIOMÉTRICA =====
        bio_frame = ttk.LabelFrame(
            identity_frame, text="Biometric Verification", padding=10
        )
        bio_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Status biométrico
        self.bio_status_label = ttk.Label(
            bio_frame, text="🔍 Não configurado", style="Status.TLabel"
        )
        self.bio_status_label.pack(anchor="w")

        # Controles biométricos
        bio_controls = tk.Frame(bio_frame, bg="#1a1a1a")
        bio_controls.pack(fill="x", pady=5)

        ttk.Button(
            bio_controls,
            text="👤 Configurar Perfil",
            command=self._setup_biometric_profile,
        ).pack(side="left", padx=5)

        ttk.Button(
            bio_controls, text="🔍 Verificar Agora", command=self._verify_identity_now
        ).pack(side="left", padx=5)

        ttk.Button(
            bio_controls,
            text="👁️ Monitoramento Contínuo",
            command=self._toggle_biometric_monitoring,
        ).pack(side="left", padx=5)

    def _create_devices_tab(self):
        """📱 ABA DE GESTÃO DE DISPOSITIVOS"""

        devices_frame = ttk.Frame(self.notebook)
        self.notebook.add(devices_frame, text="📱 Dispositivos")

        # ===== DESCOBERTA DE DISPOSITIVOS =====
        discovery_frame = ttk.LabelFrame(
            devices_frame, text="Device Discovery & Connection", padding=10
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
            devices_frame, text="Connected Devices", padding=10
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
        device_controls = tk.Frame(devices_frame, bg="#1a1a1a")
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

    def _create_network_tab(self):
        """🌐 ABA DA REDE DEMOCRÁTICA"""

        network_frame = ttk.Frame(self.notebook)
        self.notebook.add(network_frame, text="🌐 Rede Democrática")

        # ===== STATUS DA REDE =====
        network_status_frame = ttk.LabelFrame(
            network_frame, text="Network Status", padding=10
        )
        network_status_frame.pack(fill="x", padx=10, pady=5)

        # Grid de status
        status_grid = tk.Frame(network_status_frame, bg="#1a1a1a")
        status_grid.pack(fill="x")

        # Status labels
        self.network_labels = {}
        status_items = [
            ("Leader", "👑 Status do Líder"),
            ("Devices", "📱 Dispositivos Conectados"),
            ("Sync", "🔄 Sincronização"),
            ("Training", "🧠 Treinamento Ativo"),
        ]

        for i, (key, label) in enumerate(status_items):
            row = i // 2
            col = i % 2

            frame = tk.Frame(status_grid, bg="#1a1a1a")
            frame.grid(row=row, column=col, sticky="ew", padx=10, pady=5)

            ttk.Label(
    frame,
    text=label,
    style="Status.TLabel").pack(
        anchor="w")
            self.network_labels[key] = ttk.Label(
                frame, text="🔍 Detectando...", style="Status.TLabel"
            )
            self.network_labels[key].pack(anchor="w")

        status_grid.columnconfigure(0, weight=1)
        status_grid.columnconfigure(1, weight=1)

        # ===== CONTROLES DEMOCRÁTICOS =====
        democratic_controls_frame = ttk.LabelFrame(
            network_frame, text="Democratic Controls", padding=10
        )
        democratic_controls_frame.pack(fill="x", padx=10, pady=5)

        controls_grid = tk.Frame(democratic_controls_frame, bg="#1a1a1a")
        controls_grid.pack(fill="x")

        # Linha 1
        row1 = tk.Frame(controls_grid, bg="#1a1a1a")
        row1.pack(fill="x", pady=2)

        ttk.Button(
            row1, text="🗳️ Forçar Eleição", command=self._force_election
        ).pack(side="left", padx=5)

        ttk.Button(
            row1, text="👑 Candidatar-se a Líder", command=self._run_for_leader
        ).pack(side="left", padx=5)

        ttk.Button(
            row1, text="🔄 Sincronização Total", command=self._full_network_sync
        ).pack(side="left", padx=5)

        # Linha 2
        row2 = tk.Frame(controls_grid, bg="#1a1a1a")
        row2.pack(fill="x", pady=2)

        ttk.Button(
            row2, text="📊 Análise de Rede", command=self._analyze_network
        ).pack(side="left", padx=5)

        ttk.Button(
            row2,
            text="⚡ Otimização Automática",
            command=self._auto_optimize_network,
        ).pack(side="left", padx=5)

        ttk.Button(
            row2,
            text="🛡️ Segurança Avançada",
            command=self._advanced_security_config,
        ).pack(side="left", padx=5)

    def _create_training_tab(self):
        """🧠 ABA DE TREINAMENTO DISTRIBUÍDO"""

        training_frame = ttk.Frame(self.notebook)
        self.notebook.add(training_frame, text="🧠 Treinamento")

        # ===== CONTROLE DE TREINAMENTO =====
        training_control_frame = ttk.LabelFrame(
            training_frame, text="Distributed Training Control", padding=10
        )
        training_control_frame.pack(fill="x", padx=10, pady=5)

        # Status do treinamento
        self.training_status_label = ttk.Label(
            training_control_frame,
            text="💤 Treinamento Inativo",
            style="Status.TLabel",
        )
        self.training_status_label.pack(anchor="w", pady=5)

        # Controles principais
        training_controls = tk.Frame(training_control_frame, bg="#1a1a1a")
        training_controls.pack(fill="x", pady=5)

        ttk.Button(
            training_controls,
            text="🚀 Iniciar Treinamento",
            command=self._start_distributed_training,
        ).pack(side="left", padx=5)

        ttk.Button(
            training_controls, text="⏸️ Pausar", command=self._pause_training
        ).pack(side="left", padx=5)

        ttk.Button(
            training_controls, text="⏹️ Parar", command=self._stop_training
        ).pack(side="left", padx=5)

        ttk.Button(
            training_controls,
            text="📈 Métricas",
            command=self._show_training_metrics,
        ).pack(side="left", padx=5)

        # ===== CONFIGURAÇÃO DE MODELOS =====
        models_frame = ttk.LabelFrame(
            training_frame, text="Model Configuration", padding=10
        )
        models_frame.pack(fill="x", padx=10, pady=5)

        # Seleção de modelo
        model_selection = tk.Frame(models_frame, bg="#1a1a1a")
        model_selection.pack(fill="x", pady=5)

        ttk.Label(model_selection, text="Tipo de Modelo:", style="Status.TLabel").pack(
            side="left", padx=5
        )

        self.model_type_var = tk.StringVar(value="neural_network")
        model_combo = ttk.Combobox(
            model_selection,
            textvariable=self.model_type_var,
            values=["neural_network", "transformer", "cnn", "rnn", "custom"],
        )
        model_combo.pack(side="left", padx=5)

        ttk.Button(
            model_selection, text="⚙️ Configurar", command=self._configure_model
        ).pack(side="left", padx=5)

        # Dataset selection
        dataset_selection = tk.Frame(models_frame, bg="#1a1a1a")
        dataset_selection.pack(fill="x", pady=5)

        ttk.Label(dataset_selection, text="Dataset:", style="Status.TLabel").pack(
            side="left", padx=5
        )

        ttk.Button(
            dataset_selection,
            text="📁 Selecionar Dataset",
            command=self._select_dataset,
        ).pack(side="left", padx=5)

        ttk.Button(
            dataset_selection, text="🔄 Gerar Dataset", command=self._generate_dataset
        ).pack(side="left", padx=5)

        # ===== CONSOLE DE TREINAMENTO =====
        console_frame = ttk.LabelFrame(
            training_frame, text="Training Console", padding=10
        )
        console_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.training_console = tk.Text(
            console_frame,
            bg="#000000",
            fg="#00ff00",
            font=("Consolas", 10),
            wrap=tk.WORD,
        )

        console_scrollbar = ttk.Scrollbar(
            console_frame, orient="vertical", command=self.training_console.yview
        )
        self.training_console.configure(yscrollcommand=console_scrollbar.set)

        self.training_console.pack(side="left", fill="both", expand=True)
        console_scrollbar.pack(side="right", fill="y")

    def _create_integrations_tab(self):
        """🔗 ABA DE INTEGRAÇÕES"""

        integrations_frame = ttk.Frame(self.notebook)
        self.notebook.add(integrations_frame, text="🔗 Integrações")

        # ===== GOOGLE SERVICES =====
        google_frame = ttk.LabelFrame(
            integrations_frame, text="Google Services", padding=10
        )
        google_frame.pack(fill="x", padx=10, pady=5)

        google_controls = tk.Frame(google_frame, bg="#1a1a1a")
        google_controls.pack(fill="x", pady=5)

        ttk.Button(
            google_controls,
            text="📧 Gmail Integration",
            command=self._setup_gmail_integration,
        ).pack(side="left", padx=5)

        ttk.Button(
            google_controls,
            text="📅 Calendar Sync",
            command=self._setup_calendar_sync,
        ).pack(side="left", padx=5)

        ttk.Button(
            google_controls,
            text="☁️ Cloud Functions",
            command=self._setup_cloud_functions,
        ).pack(side="left", padx=5)

        # ===== MICROSOFT SERVICES =====
        microsoft_frame = ttk.LabelFrame(
            integrations_frame, text="Microsoft Services", padding=10
        )
        microsoft_frame.pack(fill="x", padx=10, pady=5)

        ms_controls = tk.Frame(microsoft_frame, bg="#1a1a1a")
        ms_controls.pack(fill="x", pady=5)

        ttk.Button(
            ms_controls,
            text="📧 Outlook Integration",
            command=self._setup_outlook_integration,
        ).pack(side="left", padx=5)

        ttk.Button(
            ms_controls, text="☁️ OneDrive Sync", command=self._setup_onedrive_sync
        ).pack(side="left", padx=5)

        ttk.Button(
            ms_controls, text="💼 Office 365", command=self._setup_office365
        ).pack(side="left", padx=5)

        # ===== WEBHOOKS & APIS =====
        webhooks_frame = ttk.LabelFrame(
            integrations_frame, text="Webhooks & APIs", padding=10
        )
        webhooks_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Lista de webhooks
        self.webhooks_listbox = tk.Listbox(
            webhooks_frame, bg="#2a2a2a", fg="#ffffff", font=("Consolas", 10)
        )
        self.webhooks_listbox.pack(fill="both", expand=True, side="left")

        webhook_scrollbar = ttk.Scrollbar(
            webhooks_frame, orient="vertical", command=self.webhooks_listbox.yview
        )
        self.webhooks_listbox.configure(yscrollcommand=webhook_scrollbar.set)
        webhook_scrollbar.pack(side="right", fill="y")

        # Controles de webhook
        webhook_controls = tk.Frame(integrations_frame, bg="#1a1a1a")
        webhook_controls.pack(fill="x", padx=10, pady=5)

        ttk.Button(
            webhook_controls, text="➕ Novo Webhook", command=self._create_webhook
        ).pack(side="left", padx=5)

        ttk.Button(
            webhook_controls, text="✏️ Editar", command=self._edit_webhook
        ).pack(side="left", padx=5)

        ttk.Button(
            webhook_controls, text="🧪 Testar", command=self._test_webhook
        ).pack(side="left", padx=5)

        ttk.Button(
            webhook_controls, text="❌ Remover", command=self._remove_webhook
        ).pack(side="left", padx=5)

    def _create_monitoring_tab(self):
        """📊 ABA DE MONITORAMENTO"""

        monitoring_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitoring_frame, text="📊 Monitoramento")

        # ===== MÉTRICAS EM TEMPO REAL =====
        metrics_frame = ttk.LabelFrame(
            monitoring_frame, text="Real-time Metrics", padding=10
        )
        metrics_frame.pack(fill="x", padx=10, pady=5)

        # Grid de métricas 2x2
        metrics_grid = tk.Frame(metrics_frame, bg="#1a1a1a")
        metrics_grid.pack(fill="x")

        self.metrics_labels = {}
        metrics_items = [
            ("cpu", "CPU Usage: 0%"),
            ("memory", "Memory: 0%"),
            ("network", "Network: 0 KB/s"),
            ("gpu", "GPU: Detecting..."),
        ]

        for i, (key, default_text) in enumerate(metrics_items):
            row = i // 2
            col = i % 2

            frame = tk.Frame(metrics_grid, bg="#1a1a1a", relief="ridge", bd=1)
            frame.grid(row=row, column=col, sticky="ew", padx=5, pady=5)

            self.metrics_labels[key] = ttk.Label(
                frame,
                text=default_text,
                style="Status.TLabel",
                font=("Arial", 12, "bold"),
            )
            self.metrics_labels[key].pack(padx=10, pady=10)

        metrics_grid.columnconfigure(0, weight=1)
        metrics_grid.columnconfigure(1, weight=1)

        # ===== LOGS EM TEMPO REAL =====
        logs_frame = ttk.LabelFrame(
    monitoring_frame,
    text="Real-time Logs",
     padding=10)
        logs_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Log viewer
        self.log_text = tk.Text(
            logs_frame, bg="#000000", fg="#00ff00", font=("Consolas", 9), wrap=tk.WORD
        )

        log_scrollbar = ttk.Scrollbar(
            logs_frame, orient="vertical", command=self.log_text.yview
        )
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")

        # Controles de log
        log_controls = tk.Frame(monitoring_frame, bg="#1a1a1a")
        log_controls.pack(fill="x", padx=10, pady=5)

        ttk.Button(log_controls, text="🔄 Refresh", command=self._refresh_logs).pack(
            side="left", padx=5
        )

        ttk.Button(log_controls, text="💾 Salvar Logs", command=self._save_logs).pack(
            side="left", padx=5
        )

        ttk.Button(log_controls, text="🗑️ Limpar", command=self._clear_logs).pack(
            side="left", padx=5
        )

        # Filtro de logs
        ttk.Label(log_controls, text="Filtro:", style="Status.TLabel").pack(
            side="left", padx=10
        )

        self.log_filter_var = tk.StringVar()
        log_filter = ttk.Entry(
    log_controls,
    textvariable=self.log_filter_var,
     width=20)
        log_filter.pack(side="left", padx=5)
        log_filter.bind("<KeyRelease>", self._filter_logs)

    def _create_power_tools_tab(self):
        """🔥 ABA DE FERRAMENTAS DE PODER"""

        power_frame = ttk.Frame(self.notebook)
        self.notebook.add(power_frame, text="🔥 Power Tools")

        # ===== EXECUÇÃO REMOTA =====
        remote_frame = ttk.LabelFrame(
    power_frame, text="Remote Execution", padding=10)
        remote_frame.pack(fill="x", padx=10, pady=5)

        # Console remoto
        remote_console_frame = tk.Frame(remote_frame, bg="#1a1a1a")
        remote_console_frame.pack(fill="x", pady=5)

        ttk.Label(remote_console_frame, text="Comando:", style="Status.TLabel").pack(
            side="left", padx=5
        )

        self.remote_command_var = tk.StringVar()
        remote_entry = ttk.Entry(
            remote_console_frame, textvariable=self.remote_command_var, width=50
        )
        remote_entry.pack(side="left", padx=5, fill="x", expand=True)

        ttk.Button(
            remote_console_frame,
            text="▶️ Executar",
            command=self._execute_remote_command,
        ).pack(side="left", padx=5)

        # Seleção de alvo
        target_frame = tk.Frame(remote_frame, bg="#1a1a1a")
        target_frame.pack(fill="x", pady=5)

        ttk.Label(target_frame, text="Alvo:", style="Status.TLabel").pack(
            side="left", padx=5
        )

        self.target_device_var = tk.StringVar()
        target_combo = ttk.Combobox(
            target_frame,
            textvariable=self.target_device_var,
            values=[
    "Todos os Dispositivos",
    "Líder Atual",
     "Dispositivo Específico"],
        )
        target_combo.pack(side="left", padx=5)

        # ===== AUTOMAÇÃO AVANÇADA =====
        automation_frame = ttk.LabelFrame(
            power_frame, text="Advanced Automation", padding=10
        )
        automation_frame.pack(fill="x", padx=10, pady=5)

        automation_controls = tk.Frame(automation_frame, bg="#1a1a1a")
        automation_controls.pack(fill="x", pady=5)

        ttk.Button(
            automation_controls,
            text="🤖 Auto-Setup Total",
            command=self._complete_auto_setup,
        ).pack(side="left", padx=5)

        ttk.Button(
            automation_controls,
            text="🔮 Previsão Inteligente",
            command=self._intelligent_prediction,
        ).pack(side="left", padx=5)

        ttk.Button(
            automation_controls,
            text="🛠️ Auto-Correção",
            command=self._auto_correction,
        ).pack(side="left", padx=5)

        ttk.Button(
            automation_controls, text="⚡ Modo Deus", command=self._god_mode
        ).pack(side="left", padx=5)

        # ===== SCRIPT EXECUTOR =====
        script_frame = ttk.LabelFrame(
            power_frame, text="Custom Script Executor", padding=10
        )
        script_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Editor de script
        self.script_text = tk.Text(
            script_frame,
            bg="#1a1a1a",
            fg="#ffffff",
            font=("Consolas", 11),
            wrap=tk.NONE,
        )

        script_scrollbar = ttk.Scrollbar(
            script_frame, orient="vertical", command=self.script_text.yview
        )
        self.script_text.configure(yscrollcommand=script_scrollbar.set)

        self.script_text.pack(side="left", fill="both", expand=True)
        script_scrollbar.pack(side="right", fill="y")

        # Controles de script
        script_controls = tk.Frame(power_frame, bg="#1a1a1a")
        script_controls.pack(fill="x", padx=10, pady=5)

        ttk.Button(
            script_controls, text="📁 Carregar Script", command=self._load_script
        ).pack(side="left", padx=5)

        ttk.Button(
            script_controls, text="💾 Salvar Script", command=self._save_script
        ).pack(side="left", padx=5)

        ttk.Button(
            script_controls, text="▶️ Executar", command=self._execute_script
        ).pack(side="left", padx=5)

        ttk.Button(
            script_controls,
            text="🔥 Execução Distribuída",
            command=self._execute_script_distributed,
        ).pack(side="left", padx=5)

    def _create_control_footer(self):
        """🎮 FOOTER DE CONTROLE RÁPIDO"""

        footer_frame = tk.Frame(self.root, bg="#2a2a2a", height=60)
        footer_frame.pack(fill="x", padx=10, pady=5)
        footer_frame.pack_propagate(False)

        # Controles de emergência
        emergency_frame = tk.Frame(footer_frame, bg="#2a2a2a")
        emergency_frame.pack(side="left", padx=10, pady=10)

        ttk.Button(
            emergency_frame, text="🚨 STOP ALL", command=self._emergency_stop
        ).pack(side="left", padx=5)

        ttk.Button(
            emergency_frame, text="🔄 RESTART", command=self._emergency_restart
        ).pack(side="left", padx=5)

        # Status global
        status_frame = tk.Frame(footer_frame, bg="#2a2a2a")
        status_frame.pack(side="right", padx=10, pady=10)

        self.global_status_label = ttk.Label(
            status_frame, text="🔥 SISTEMA DEMOCRÁTICO ATIVO", style="Success.TLabel"
        )
        self.global_status_label.pack(side="right", padx=5)

    def _initialize_systems(self):
        """⚡ INICIALIZA TODOS OS SISTEMAS"""

        try:
            # Thread separada para não bloquear interface
            init_thread = threading.Thread(
                target=self._init_systems_background, daemon=True
            )
            init_thread.start()

            # Iniciar refresh de status
            self._start_status_refresh()

        except Exception as e:
            self._log(f"❌ Erro inicializando sistemas: {e}")

    def _init_systems_background(self):
        """🔄 INICIALIZAÇÃO EM BACKGROUND"""

        try:
            # 1. Microsoft Device Identifier
            self._log("🔍 Inicializando identificação Microsoft...")
            data_path = Path(
    self.jarvis_core.config["system"]["base_path"]) / "data"
            self.microsoft_identifier = MicrosoftDeviceIdentifier(
                str(data_path))
            self.microsoft_identifier.initialize()

            # 2. Biometric Verifier
            self._log("🔍 Inicializando verificação biométrica...")
            self.biometric_verifier = EnhancedBiometricVerifier(
                self.jarvis_core, self.microsoft_identifier
            )

            # 3. Democratic Core
            self._log("🗳️ Inicializando núcleo democrático...")
            if DemocraticCore:
                self.democratic_core = DemocraticCore(self.jarvis_core)
            else:
                self._log("⚠️ DemocraticCore não disponível (ImportError)")

            self._log("✅ Todos os sistemas inicializados com sucesso!")

            # Atualizar interface
            if self.root:
                self.root.after(0, self._update_initial_status)

        except Exception as e:
            self._log(f"❌ Erro na inicialização: {e}")

    def _update_initial_status(self):
        """📊 ATUALIZA STATUS INICIAL DA INTERFACE"""

        try:
            # Microsoft Account Status
            if (
                self.microsoft_identifier
                and hasattr(self.microsoft_identifier, "microsoft_account")
                and self.microsoft_identifier.microsoft_account
            ):
                account_email = getattr(
                    self.microsoft_identifier.microsoft_account,
                    "account_email",
                    "unknown",
                )
                self.ms_status_label.config(
    text=f"✅ Conectado: {account_email}")
            else:
                self.ms_status_label.config(text="❌ Conta não detectada")

            # Google Drive Status
            if (
                self.microsoft_identifier
                and hasattr(self.microsoft_identifier, "google_drive_detected")
                and getattr(self.microsoft_identifier, "google_drive_detected", False)
            ):
                self.drive_status_label.config(
                    text="✅ Google Drive detectado")
            else:
                self.drive_status_label.config(
    text="❌ Google Drive não encontrado")

            # Biometric Status
            if self.biometric_verifier:
                status = self.biometric_verifier.get_verification_status()
                if status["status"] == "configured":
                    self.bio_status_label.config(
                        text=f"✅ Configurado - {status['face_samples']} faces, {status['voice_samples']} voice"
                    )
                else:
                    self.bio_status_label.config(
                        text="⚙️ Não configurado")

        except Exception as e:
            self._log(f"❌ Erro atualizando status: {e}")

    def _start_status_refresh(self):
        """🔄 INICIA REFRESH AUTOMÁTICO DE STATUS"""

        def refresh_loop():
            try:
                self._refresh_metrics()
                self._refresh_network_status()
                self._check_devices()
            except Exception as e:
                self._log(f"Erro no refresh: {e}")
            finally:
                # Agendar próximo refresh
                if self.root is not None:
                    self.root.after(5000, refresh_loop)  # A cada 5 segundos

        # Iniciar loop
        if self.root is not None:
            # Primeiro refresh em 1 segundo
            self.root.after(1000, refresh_loop)

    # ===== MÉTODOS DE CALLBACK =====

    def _redetect_microsoft_account(self):
        """🔍 RE-DETECTA CONTA MICROSOFT"""

        self._log("🔄 Re-detectando conta Microsoft...")

        def redetect():
            try:
                if self.microsoft_identifier:
                    if hasattr(self.microsoft_identifier, "initialize"):
                        self.microsoft_identifier.initialize()
                    if self.root is not None:
                        self.root.after(0, self._update_initial_status)
                    self._log("✅ Re-detecção concluída")
                else:
                    self._log(
                        "❌ Sistema de identificação não inicializado")
            except Exception as e:
                self._log(f"❌ Erro na re-detecção: {e}")

        threading.Thread(target=redetect, daemon=True).start()

    def _manual_microsoft_config(self):
        """⚙️ CONFIGURAÇÃO MANUAL DA CONTA MICROSOFT"""

        # Criar janela de configuração manual
        config_window = tk.Toplevel(self.root)
        config_window.title("Configuração Manual - Microsoft Account")
        config_window.geometry("500x300")
        config_window.configure(bg="#1a1a1a")

        # Campos de entrada
        ttk.Label(
            config_window,
            text="Configuração Manual da Conta Microsoft",
            style="Title.TLabel",
        ).pack(pady=10)

        # Email
        email_frame = tk.Frame(config_window, bg="#1a1a1a")
        email_frame.pack(fill="x", padx=20, pady=5)

        ttk.Label(
    email_frame,
    text="Email:",
    style="Status.TLabel").pack(
        side="left")


        target_email = config.get_setting("portability.target_user_email", "")

        email_var = tk.StringVar(value=target_email)
        ttk.Entry(
    email_frame,
    textvariable=email_var,
    width=40).pack(
        side="right")

        # Display name
        name_frame = tk.Frame(config_window, bg="#1a1a1a")
        name_frame.pack(fill="x", padx=20, pady=5)

        ttk.Label(
    name_frame,
    text="Nome:",
    style="Status.TLabel").pack(
        side="left")
        name_var = tk.StringVar()
        ttk.Entry(
    name_frame,
    textvariable=name_var,
    width=40).pack(
        side="right")

        # Botões
        button_frame = tk.Frame(config_window, bg="#1a1a1a")
        button_frame.pack(fill="x", padx=20, pady=20)

        def save_manual_config():
            if self.microsoft_identifier:
                # Configuração manual (implementar método no identifier)
                self._log(
                    f"💾 Configuração manual salva: {email_var.get()}")
                config_window.destroy()
                self._update_initial_status()
            else:
                messagebox.showerror(
                    "Erro", "Sistema de identificação não inicializado"
                )

        ttk.Button(button_frame, text="💾 Salvar", command=save_manual_config).pack(
            side="left", padx=5
        )

        ttk.Button(
            button_frame, text="❌ Cancelar", command=config_window.destroy
        ).pack(side="left", padx=5)

    def _show_microsoft_details(self):
        """📋 MOSTRA DETALHES COMPLETOS DA CONTA MICROSOFT"""

        if not self.microsoft_identifier:
            messagebox.showwarning(
                "Aviso", "Sistema de identificação não inicializado"
            )
            return

        # Criar janela de detalhes
        details_window = tk.Toplevel(self.root)
        details_window.title("Detalhes Completos - Microsoft Account")
        details_window.geometry("700x500")
        details_window.configure(bg="#1a1a1a")

        # Text widget para mostrar detalhes
        details_text = tk.Text(
            details_window,
            bg="#000000",
            fg="#00ff00",
            font=("Consolas", 10),
            wrap=tk.WORD,
        )

        scrollbar = ttk.Scrollbar(
            details_window, orient="vertical", command=details_text.yview
        )
        details_text.configure(yscrollcommand=scrollbar.set)

        details_text.pack(
    side="left",
    fill="both",
    expand=True,
    padx=10,
     pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        # Obter e exibir detalhes
        def load_details():
            try:
                details_info = "🆔 DETALHES COMPLETOS DA IDENTIFICAÇÃO MICROSOFT\n"
                details_info += "=" * 60 + "\n\n"

                if (
                    self.microsoft_identifier
                    and hasattr(self.microsoft_identifier, "microsoft_account")
                    and self.microsoft_identifier.microsoft_account
                ):
                    account = self.microsoft_identifier.microsoft_account
                    details_info += (
                        f"📧 Email: {getattr(account, 'account_email', 'unknown')}\n"
                    )
                    details_info += (
                        f"👤 Nome: {getattr(account, 'display_name', 'unknown')}\n"
                    )
                    # details_info += f"🆔 User ID: {getattr(account, 'user_id', 'unknown')}\n"
                    # details_info += f"🏠 Microsoft ID: {getattr(account,
                    # 'microsoft_id', 'unknown')}\n\n"
                else:
                    details_info += "❌ Conta Microsoft não detectada\n\n"

                if (
                    self.microsoft_identifier
                    and hasattr(self.microsoft_identifier, "device_fingerprint")
                    and self.microsoft_identifier.device_fingerprint
                ):
                    fingerprint = self.microsoft_identifier.device_fingerprint
                    details_info += "🖥️ DEVICE FINGERPRINT:\n"
                    details_info += f"🆔 Device ID: {getattr(fingerprint, 'device_id', 'unknown')}\n"
                    details_info += f"💻 Computer Name: {getattr(fingerprint, 'computer_name', 'unknown')}\n"
                    # details_info += f"🔧 CPU ID: {getattr(fingerprint,
                    # 'cpu_id', 'unknown')}\n"
                    details_info += f"🏠 Motherboard: {getattr(fingerprint, 'motherboard_serial', 'unknown')}\n"
                    details_info += f"⚡ BIOS: {getattr(fingerprint, 'bios_serial', 'unknown')}\n\n"
                else:
                    details_info += "❌ Device fingerprint não criado\n\n"

                # Google Drive status
                details_info += "☁️ GOOGLE DRIVE:\n"
                if (
                    self.microsoft_identifier
                    and hasattr(self.microsoft_identifier, "google_drive_auth")
                    and self.microsoft_identifier.google_drive_auth
                ):
                    details_info += "✅ Status: Detectado\n"
                    drive_path = getattr(
                        self.microsoft_identifier.google_drive_auth,
                        "drive_path",
                        "unknown",
                    )
                    details_info += f"📍 Path: {drive_path}\n"
                else:
                    details_info += "❌ Status: Não detectado\n"

                details_text.insert(tk.END, details_info)

            except Exception as e:
                details_text.insert(
    tk.END, f"❌ Erro carregando detalhes: {e}")

        threading.Thread(target=load_details, daemon=True).start()

    # ===== MÉTODOS UTILITÁRIOS =====

    def _log(self, message: str):
        """📝 LOG PARA CONSOLE E INTERFACE"""

        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        print(log_message.strip())  # Console

        # Interface (se disponível)
        try:
            if hasattr(self, "log_text"):
                self.log_text.insert(tk.END, log_message)
                self.log_text.see(tk.END)

            if hasattr(self, "training_console"):
                self.training_console.insert(tk.END, log_message)
                self.training_console.see(tk.END)
        except:
            pass

    def _load_user_preferences(self) -> Dict[str, Any]:
        """📝 CARREGA PREFERÊNCIAS DO USUÁRIO"""

        try:
            prefs_path = (
                Path(self.jarvis_core.config["system"]["base_path"])
                / "data"
                / "user_preferences.json"
            )

            if prefs_path.exists():
                with open(prefs_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                # Preferências padrão
                return {
                    "theme": "dark",
                    "auto_monitoring": True,
                    "auto_training": False,
                    "notification_level": "normal",
                    "device_discovery_interval": 30,
                    "biometric_verification_required": True,
                }
        except Exception as e:
            print(f"❌ Erro carregando preferências: {e}")
            return {}

    def _save_user_preferences(self):
        """💾 SALVA PREFERÊNCIAS DO USUÁRIO"""

        try:
            prefs_path = (
                Path(self.jarvis_core.config["system"]["base_path"])
                / "data"
                / "user_preferences.json"
            )
            prefs_path.parent.mkdir(parents=True, exist_ok=True)

            with open(prefs_path, "w", encoding="utf-8") as f:
                json.dump(
    self.user_preferences,
    f,
    indent=2,
     ensure_ascii=False)

        except Exception as e:
            print(f"❌ Erro salvando preferências: {e}")

    # ===== MÉTODOS PLACEHOLDER (IMPLEMENTAR CONFORME NECESSÁRIO) =====

    def _connect_google_drive(self):
        self._log("🔗 Conectando Google Drive...")

    def _setup_drive_structure(self):
        self._log("📍 Configurando estrutura do Drive...")

    def _sync_google_drive(self):
        self._log("☁️ Sincronizando Google Drive...")

    def _setup_biometric_profile(self):
        if self.biometric_verifier:
            threading.Thread(
                target=self.biometric_verifier.setup_user_profile, daemon=True
            ).start()
        else:
            self._log("❌ Sistema biométrico não inicializado")

    def _verify_identity_now(self):
        self._log("🔍 Verificando identidade...")

    def _toggle_biometric_monitoring(self):
        self._log("👁️ Alternando monitoramento biométrico...")

    def _scan_network_devices(self):
        self._log("🔍 Escaneando dispositivos na rede...")

    def _detect_jarvis_instances(self):
        self._log("🆔 Detectando instâncias JARVIS...")

    def _connect_device_manual(self):
        self._log("🤝 Conectando dispositivo manualmente...")

    def _force_democratic_election(self):
        self._log("⚡ Forçando eleição democrática...")

    def _show_device_details(self):
        self._log("📊 Mostrando detalhes do dispositivo...")

    def _sync_selected_device(self):
        self._log("🔄 Sincronizando dispositivo selecionado...")

    def _disconnect_selected_device(self):
        self._log("❌ Desconectando dispositivo...")

    def _force_election(self):
        self._log("🗳️ Forçando eleição...")

    def _run_for_leader(self):
        self._log("👑 Candidatando-se a líder...")

    def _full_network_sync(self):
        self._log("🔄 Sincronização total da rede...")

    def _analyze_network(self):
        self._log("📊 Analisando rede...")

    def _auto_optimize_network(self):
        self._log("⚡ Otimização automática da rede...")

    def _advanced_security_config(self):
        self._log("🛡️ Configuração avançada de segurança...")

    def _start_distributed_training(self):
        self._log("🚀 Iniciando treinamento distribuído...")

    def _pause_training(self):
        self._log("⏸️ Pausando treinamento...")

    def _stop_training(self):
        self._log("⏹️ Parando treinamento...")

    def _show_training_metrics(self):
        self._log("📈 Mostrando métricas de treinamento...")

    def _configure_model(self):
        self._log("⚙️ Configurando modelo...")

    def _select_dataset(self):
        self._log("📁 Selecionando dataset...")

    def _generate_dataset(self):
        self._log("🔄 Gerando dataset...")

    def _setup_gmail_integration(self):
        self._log("📧 Configurando integração Gmail...")

    def _setup_calendar_sync(self):
        self._log("📅 Configurando sincronização de calendário...")

    def _setup_cloud_functions(self):
        self._log("☁️ Configurando Cloud Functions...")

    def _setup_outlook_integration(self):
        self._log("📧 Configurando integração Outlook...")

    def _setup_onedrive_sync(self):
        self._log("☁️ Configurando sincronização OneDrive...")

    def _setup_office365(self):
        self._log("💼 Configurando Office 365...")

    def _create_webhook(self):
        self._log("➕ Criando webhook...")

    def _edit_webhook(self):
        self._log("✏️ Editando webhook...")

    def _test_webhook(self):
        self._log("🧪 Testando webhook...")

    def _remove_webhook(self):
        self._log("❌ Removendo webhook...")

    def _refresh_logs(self):
        self._log("🔄 Atualizando logs...")

    def _save_logs(self):
        self._log("💾 Salvando logs...")

    def _clear_logs(self):
        if hasattr(self, "log_text"):
            self.log_text.delete(1.0, tk.END)

    def _filter_logs(self, event):
        pass  # Implementar filtro de logs

    def _execute_remote_command(self):
        self._log("▶️ Executando comando remoto...")

    def _complete_auto_setup(self):
        self._log("🤖 Executando auto-setup total...")

    def _intelligent_prediction(self):
        self._log("🔮 Executando previsão inteligente...")

    def _auto_correction(self):
        self._log("🛠️ Executando auto-correção...")

    def _god_mode(self):
        self._log("⚡ MODO DEUS ATIVADO...")

    def _load_script(self):
        self._log("📁 Carregando script...")

    def _save_script(self):
        self._log("💾 Salvando script...")

    def _execute_script(self):
        self._log("▶️ Executando script...")

    def _execute_script_distributed(self):
        self._log("🔥 Executando script distribuído...")

    def _emergency_stop(self):
        self._log("🚨 PARADA DE EMERGÊNCIA!")

    def _emergency_restart(self):
        self._log("🔄 REINÍCIO DE EMERGÊNCIA!")

    def _refresh_metrics(self):
        """📊 ATUALIZA MÉTRICAS EM TEMPO REAL"""
        try:
            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.metrics_labels["cpu"].config(
    text=f"CPU Usage: {cpu_percent:.1f}%")

            # Memory Usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024**3)
            memory_total_gb = memory.total / (1024**3)
            self.metrics_labels["memory"].config(
                text=f"Memory: {memory_percent:.1f}% ({memory_used_gb:.1f}GB/{memory_total_gb:.1f}GB)"
            )

            # Network Usage (simplified)
            network = psutil.net_io_counters()
            if network:
                bytes_sent = network.bytes_sent
                bytes_recv = network.bytes_recv
                total_mb = (bytes_sent + bytes_recv) / (1024**2)
                self.metrics_labels["network"].config(
                    text=f"Network: {total_mb:.1f} MB total"
                )
            else:
                self.metrics_labels["network"].config(text="Network: N/A")

            # GPU Usage
            gpu_text = self._get_gpu_metrics_text()
            self.metrics_labels["gpu"].config(text=gpu_text)

        except Exception as e:
            self._log(f"Erro atualizando métricas: {e}")
            # Fallback values
            self.metrics_labels["cpu"].config(text="CPU Usage: Error")
            self.metrics_labels["memory"].config(text="Memory: Error")
            self.metrics_labels["network"].config(text="Network: Error")
            self.metrics_labels["gpu"].config(text="GPU: Error")

    def _get_gpu_metrics_text(self) -> str:
        """Obtém texto de métricas da GPU"""
        try:
            if not TORCH_AVAILABLE or not torch.cuda.is_available():
                return "GPU: Not Available"

            gpu_count = torch.cuda.device_count()
            if gpu_count == 0:
                return "GPU: Not Available"

            # GPU 0 (principal)
            gpu_name = torch.cuda.get_device_name(0)

            # Utilização via NVML (mais preciso)
            if NVML_AVAILABLE:
                try:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    gpu_util = util.gpu

                    # Memória
                    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    memory_used_gb = memory_info.used / (1024**3)
                    memory_total_gb = memory_info.total / (1024**3)

                    return f"GPU: {gpu_util}% ({memory_used_gb:.1f}GB/{memory_total_gb:.1f}GB)"
                except Exception:
                    pass

            # Fallback via PyTorch (memória apenas)
            memory_allocated = torch.cuda.memory_allocated(0)
            memory_total = torch.cuda.get_device_properties(0).total_memory
            memory_percent = (memory_allocated / memory_total) * 100

            return f"GPU: ~{memory_percent:.1f}% (mem) - {gpu_name[:15]}..."

        except Exception:
            return "GPU: Error"

    def _refresh_network_status(self):
        pass  # Implementar refresh de status da rede

    def _check_devices(self):
        pass  # Implementar verificação de dispositivos


# Função principal de lançamento
def launch_democratic_interface(jarvis_core):
    """🚀 LANÇA INTERFACE DEMOCRÁTICA"""

    interface = DemocraticControlInterface(jarvis_core)
    interface.launch_interface()
    return interface


if __name__ == "__main__":
    # Para testes
    print("🔥 Democratic Control Interface - Teste")
    print("➡️  Use launch_democratic_interface(jarvis_core) para executar")
