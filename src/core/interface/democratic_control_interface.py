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
from tkinter import ttk, messagebox, filedialog
import threading
import asyncio
import json
import requests
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from pathlib import Path
import logging
import subprocess
import webbrowser
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

logger = logging.getLogger(__name__)

class DemocraticControlInterface:
    """
    🔥 INTERFACE DE CONTROLE DEMOCRÁTICO TOTAL
    
    Esta interface dá ao usuário PODER TOTAL sobre:
    - Identificação e conexão de dispositivos
    - Configuração automática de Google Drive
    - Controle da rede democrática
    - Verificação biométrica avançada
    - Treinamento distribuÃ­do
    - Monitoramento em tempo real
    - ConfiguraÃ§Ã£o de webhooks e integraÃ§Ãµes
    
    âœ¨ LIBERDADE TOTAL - SEM PRÃ‰-CONFIGURAÃ‡Ã•ES
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
        
        # ConfiguraÃ§Ãµes do usuÃ¡rio
        self.user_preferences = self._load_user_preferences()
        
        print("ðŸ”¥ Democratic Control Interface inicializada")
        print("ðŸ’ª PODER TOTAL HABILITADO")
    
    def launch_interface(self):
        """ðŸš€ LANÃ‡A INTERFACE PRINCIPAL DE CONTROLE"""
        
        if self.root is not None:
            return
        
        self.root = tk.Tk()
        self.root.title("JARVIS SINGULARITY - CONTROLE DEMOCRÃTICO")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a1a')
        
        # Configurar estilo escuro
        self._setup_dark_theme()
        
        # Criar interface principal
        self._create_main_interface()
        
        # Inicializar sistemas
        self._initialize_systems()
        
        # Loop principal
        self.root.mainloop()
    
    def _setup_dark_theme(self):
        """ðŸŽ¨ TEMA ESCURO PROFISSIONAL"""
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores personalizadas
        style.configure('Title.TLabel', 
                       background='#1a1a1a', 
                       foreground='#00ff00', 
                       font=('Arial', 16, 'bold'))
        
        style.configure('Status.TLabel',
                       background='#1a1a1a',
                       foreground='#ffffff',
                       font=('Arial', 10))
        
        style.configure('Success.TLabel',
                       background='#1a1a1a',
                       foreground='#00ff00',
                       font=('Arial', 10, 'bold'))
        
        style.configure('Error.TLabel',
                       background='#1a1a1a',
                       foreground='#ff0000',
                       font=('Arial', 10, 'bold'))
        
        style.configure('Control.TButton',
                       font=('Arial', 10, 'bold'))
    
    def _create_main_interface(self):
        """ðŸ—ï¸ CONSTRÃ“I INTERFACE PRINCIPAL"""
        
        # ===== HEADER =====
        header_frame = tk.Frame(self.root, bg='#1a1a1a', height=80)
        header_frame.pack(fill='x', padx=10, pady=5)
        header_frame.pack_propagate(False)
        
        title_label = ttk.Label(header_frame, 
                               text="ðŸ”¥ JARVIS DEMOCRÃTICO - CONTROLE TOTAL",
                               style='Title.TLabel')
        title_label.pack(side='left', padx=10, pady=20)
        
        # Status geral
        self.status_label = ttk.Label(header_frame,
                                     text="âš¡ SISTEMA DEMOCRÃTICO ATIVO",
                                     style='Success.TLabel')
        self.status_label.pack(side='right', padx=10, pady=20)
        
        # ===== NOTEBOOK PRINCIPAL =====
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Abas principais
        self._create_identity_tab()
        self._create_devices_tab()
        self._create_network_tab()
        self._create_training_tab()
        self._create_integrations_tab()
        self._create_monitoring_tab()
        self._create_power_tools_tab()
        
        # ===== FOOTER DE CONTROLE RÃPIDO =====
        self._create_control_footer()
    
    def _create_identity_tab(self):
        """ðŸ†” ABA DE GESTÃƒO DE IDENTIDADE"""
        
        identity_frame = ttk.Frame(self.notebook)
        self.notebook.add(identity_frame, text="ðŸ†” Identidade")
        
        # ===== MICROSOFT ACCOUNT =====
        ms_frame = ttk.LabelFrame(identity_frame, text="Microsoft Account Detection", padding=10)
        ms_frame.pack(fill='x', padx=10, pady=5)
        
        # Status da conta
        self.ms_status_label = ttk.Label(ms_frame, text="ðŸ” Detectando...", style='Status.TLabel')
        self.ms_status_label.pack(anchor='w')
        
        # Controles
        ms_controls = tk.Frame(ms_frame, bg='#1a1a1a')
        ms_controls.pack(fill='x', pady=5)
        
        ttk.Button(ms_controls, text="ðŸ”„ Re-detectar Conta", 
                  command=self._redetect_microsoft_account).pack(side='left', padx=5)
        
        ttk.Button(ms_controls, text="âš™ï¸ Configurar Manualmente",
                  command=self._manual_microsoft_config).pack(side='left', padx=5)
        
        ttk.Button(ms_controls, text="ðŸ“‹ Ver Detalhes Completos",
                  command=self._show_microsoft_details).pack(side='left', padx=5)
        
        # ===== GOOGLE DRIVE =====
        drive_frame = ttk.LabelFrame(identity_frame, text="Google Drive Integration", padding=10)
        drive_frame.pack(fill='x', padx=10, pady=5)
        
        # Status do Drive
        self.drive_status_label = ttk.Label(drive_frame, text="ðŸ“‚ Analisando...", style='Status.TLabel')
        self.drive_status_label.pack(anchor='w')
        
        # Controles do Drive
        drive_controls = tk.Frame(drive_frame, bg='#1a1a1a')
        drive_controls.pack(fill='x', pady=5)
        
        ttk.Button(drive_controls, text="ðŸ”— Conectar Google Drive",
                  command=self._connect_google_drive).pack(side='left', padx=5)
        
        ttk.Button(drive_controls, text="ðŸ“ Configurar Estrutura",
                  command=self._setup_drive_structure).pack(side='left', padx=5)
        
        ttk.Button(drive_controls, text="â˜ï¸ Sincronizar Agora",
                  command=self._sync_google_drive).pack(side='left', padx=5)
        
        # ===== VERIFICAÃ‡ÃƒO BIOMÃ‰TRICA =====
        bio_frame = ttk.LabelFrame(identity_frame, text="Biometric Verification", padding=10)
        bio_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Status biomÃ©trico
        self.bio_status_label = ttk.Label(bio_frame, text="ðŸ” NÃ£o configurado", style='Status.TLabel')
        self.bio_status_label.pack(anchor='w')
        
        # Controles biomÃ©tricos
        bio_controls = tk.Frame(bio_frame, bg='#1a1a1a')
        bio_controls.pack(fill='x', pady=5)
        
        ttk.Button(bio_controls, text="ðŸ‘¤ Configurar Perfil",
                  command=self._setup_biometric_profile).pack(side='left', padx=5)
        
        ttk.Button(bio_controls, text="ðŸ” Verificar Agora",
                  command=self._verify_identity_now).pack(side='left', padx=5)
        
        ttk.Button(bio_controls, text="ðŸ‘ï¸ Monitoramento ContÃ­nuo",
                  command=self._toggle_biometric_monitoring).pack(side='left', padx=5)
    
    def _create_devices_tab(self):
        """ðŸ“± ABA DE GESTÃƒO DE DISPOSITIVOS"""
        
        devices_frame = ttk.Frame(self.notebook)
        self.notebook.add(devices_frame, text="ðŸ“± Dispositivos")
        
        # ===== DESCOBERTA DE DISPOSITIVOS =====
        discovery_frame = ttk.LabelFrame(devices_frame, text="Device Discovery & Connection", padding=10)
        discovery_frame.pack(fill='x', padx=10, pady=5)
        
        # Controles de descoberta
        discovery_controls = tk.Frame(discovery_frame, bg='#1a1a1a')
        discovery_controls.pack(fill='x', pady=5)
        
        ttk.Button(discovery_controls, text="ðŸ” Escanear Rede",
                  command=self._scan_network_devices).pack(side='left', padx=5)
        
        ttk.Button(discovery_controls, text="ðŸ†” Detectar JARVIS",
                  command=self._detect_jarvis_instances).pack(side='left', padx=5)
        
        ttk.Button(discovery_controls, text="ðŸ¤ Conectar Dispositivo",
                  command=self._connect_device_manual).pack(side='left', padx=5)
        
        ttk.Button(discovery_controls, text="âš¡ ForÃ§a DemocrÃ¡tica",
                  command=self._force_democratic_election).pack(side='left', padx=5)
        
        # ===== LISTA DE DISPOSITIVOS =====
        devices_list_frame = ttk.LabelFrame(devices_frame, text="Connected Devices", padding=10)
        devices_list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # TreeView para dispositivos
        columns = ('Device', 'Type', 'Status', 'Capabilities', 'Last Seen')
        self.devices_tree = ttk.Treeview(devices_list_frame, columns=columns, show='tree headings')
        
        for col in columns:
            self.devices_tree.heading(col, text=col)
            self.devices_tree.column(col, width=150)
        
        scrollbar_devices = ttk.Scrollbar(devices_list_frame, orient='vertical', command=self.devices_tree.yview)
        self.devices_tree.configure(yscrollcommand=scrollbar_devices.set)
        
        self.devices_tree.pack(side='left', fill='both', expand=True)
        scrollbar_devices.pack(side='right', fill='y')
        
        # Controles de dispositivos
        device_controls = tk.Frame(devices_frame, bg='#1a1a1a')
        device_controls.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(device_controls, text="ðŸ“Š Status Detalhado",
                  command=self._show_device_details).pack(side='left', padx=5)
        
        ttk.Button(device_controls, text="ðŸ”„ Sincronizar",
                  command=self._sync_selected_device).pack(side='left', padx=5)
        
        ttk.Button(device_controls, text="âŒ Desconectar",
                  command=self._disconnect_selected_device).pack(side='left', padx=5)
    
    def _create_network_tab(self):
        """ðŸŒ ABA DA REDE DEMOCRÃTICA"""
        
        network_frame = ttk.Frame(self.notebook)
        self.notebook.add(network_frame, text="ðŸŒ Rede DemocrÃ¡tica")
        
        # ===== STATUS DA REDE =====
        network_status_frame = ttk.LabelFrame(network_frame, text="Network Status", padding=10)
        network_status_frame.pack(fill='x', padx=10, pady=5)
        
        # Grid de status
        status_grid = tk.Frame(network_status_frame, bg='#1a1a1a')
        status_grid.pack(fill='x')
        
        # Status labels
        self.network_labels = {}
        status_items = [
            ('Leader', 'ðŸ‘‘ Status do LÃ­der'),
            ('Devices', 'ðŸ“± Dispositivos Conectados'),
            ('Sync', 'ðŸ”„ SincronizaÃ§Ã£o'),
            ('Training', 'ðŸ§  Treinamento Ativo')
        ]
        
        for i, (key, label) in enumerate(status_items):
            row = i // 2
            col = i % 2
            
            frame = tk.Frame(status_grid, bg='#1a1a1a')
            frame.grid(row=row, column=col, sticky='ew', padx=10, pady=5)
            
            ttk.Label(frame, text=label, style='Status.TLabel').pack(anchor='w')
            self.network_labels[key] = ttk.Label(frame, text="ðŸ” Detectando...", style='Status.TLabel')
            self.network_labels[key].pack(anchor='w')
        
        status_grid.columnconfigure(0, weight=1)
        status_grid.columnconfigure(1, weight=1)
        
        # ===== CONTROLES DEMOCRÃTICOS =====
        democratic_controls_frame = ttk.LabelFrame(network_frame, text="Democratic Controls", padding=10)
        democratic_controls_frame.pack(fill='x', padx=10, pady=5)
        
        controls_grid = tk.Frame(democratic_controls_frame, bg='#1a1a1a')
        controls_grid.pack(fill='x')
        
        # Linha 1
        row1 = tk.Frame(controls_grid, bg='#1a1a1a')
        row1.pack(fill='x', pady=2)
        
        ttk.Button(row1, text="ðŸ—³ï¸ ForÃ§ar EleiÃ§Ã£o",
                  command=self._force_election).pack(side='left', padx=5)
        
        ttk.Button(row1, text="ðŸ‘‘ Candidatar-se a LÃ­der",
                  command=self._run_for_leader).pack(side='left', padx=5)
        
        ttk.Button(row1, text="ðŸ”„ SincronizaÃ§Ã£o Total",
                  command=self._full_network_sync).pack(side='left', padx=5)
        
        # Linha 2
        row2 = tk.Frame(controls_grid, bg='#1a1a1a')
        row2.pack(fill='x', pady=2)
        
        ttk.Button(row2, text="ðŸ“Š AnÃ¡lise de Rede",
                  command=self._analyze_network).pack(side='left', padx=5)
        
        ttk.Button(row2, text="âš¡ OtimizaÃ§Ã£o AutomÃ¡tica",
                  command=self._auto_optimize_network).pack(side='left', padx=5)
        
        ttk.Button(row2, text="ðŸ›¡ï¸ SeguranÃ§a AvanÃ§ada",
                  command=self._advanced_security_config).pack(side='left', padx=5)
    
    def _create_training_tab(self):
        """ðŸ§  ABA DE TREINAMENTO DISTRIBUÃDO"""
        
        training_frame = ttk.Frame(self.notebook)
        self.notebook.add(training_frame, text="ðŸ§  Treinamento")
        
        # ===== CONTROLE DE TREINAMENTO =====
        training_control_frame = ttk.LabelFrame(training_frame, text="Distributed Training Control", padding=10)
        training_control_frame.pack(fill='x', padx=10, pady=5)
        
        # Status do treinamento
        self.training_status_label = ttk.Label(training_control_frame, 
                                              text="ðŸ’¤ Treinamento Inativo", 
                                              style='Status.TLabel')
        self.training_status_label.pack(anchor='w', pady=5)
        
        # Controles principais
        training_controls = tk.Frame(training_control_frame, bg='#1a1a1a')
        training_controls.pack(fill='x', pady=5)
        
        ttk.Button(training_controls, text="ðŸš€ Iniciar Treinamento",
                  command=self._start_distributed_training).pack(side='left', padx=5)
        
        ttk.Button(training_controls, text="â¸ï¸ Pausar",
                  command=self._pause_training).pack(side='left', padx=5)
        
        ttk.Button(training_controls, text="â¹ï¸ Parar",
                  command=self._stop_training).pack(side='left', padx=5)
        
        ttk.Button(training_controls, text="ðŸ“ˆ MÃ©tricas",
                  command=self._show_training_metrics).pack(side='left', padx=5)
        
        # ===== CONFIGURAÃ‡ÃƒO DE MODELOS =====
        models_frame = ttk.LabelFrame(training_frame, text="Model Configuration", padding=10)
        models_frame.pack(fill='x', padx=10, pady=5)
        
        # SeleÃ§Ã£o de modelo
        model_selection = tk.Frame(models_frame, bg='#1a1a1a')
        model_selection.pack(fill='x', pady=5)
        
        ttk.Label(model_selection, text="Tipo de Modelo:", style='Status.TLabel').pack(side='left', padx=5)
        
        self.model_type_var = tk.StringVar(value="neural_network")
        model_combo = ttk.Combobox(model_selection, textvariable=self.model_type_var,
                                  values=["neural_network", "transformer", "cnn", "rnn", "custom"])
        model_combo.pack(side='left', padx=5)
        
        ttk.Button(model_selection, text="âš™ï¸ Configurar",
                  command=self._configure_model).pack(side='left', padx=5)
        
        # Dataset selection
        dataset_selection = tk.Frame(models_frame, bg='#1a1a1a')
        dataset_selection.pack(fill='x', pady=5)
        
        ttk.Label(dataset_selection, text="Dataset:", style='Status.TLabel').pack(side='left', padx=5)
        
        ttk.Button(dataset_selection, text="ðŸ“ Selecionar Dataset",
                  command=self._select_dataset).pack(side='left', padx=5)
        
        ttk.Button(dataset_selection, text="ðŸ”„ Gerar Dataset",
                  command=self._generate_dataset).pack(side='left', padx=5)
        
        # ===== CONSOLE DE TREINAMENTO =====
        console_frame = ttk.LabelFrame(training_frame, text="Training Console", padding=10)
        console_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.training_console = tk.Text(console_frame, bg='#000000', fg='#00ff00',
                                       font=('Consolas', 10), wrap=tk.WORD)
        
        console_scrollbar = ttk.Scrollbar(console_frame, orient='vertical', command=self.training_console.yview)
        self.training_console.configure(yscrollcommand=console_scrollbar.set)
        
        self.training_console.pack(side='left', fill='both', expand=True)
        console_scrollbar.pack(side='right', fill='y')
    
    def _create_integrations_tab(self):
        """ðŸ”— ABA DE INTEGRAÃ‡Ã•ES"""
        
        integrations_frame = ttk.Frame(self.notebook)
        self.notebook.add(integrations_frame, text="ðŸ”— IntegraÃ§Ãµes")
        
        # ===== GOOGLE SERVICES =====
        google_frame = ttk.LabelFrame(integrations_frame, text="Google Services", padding=10)
        google_frame.pack(fill='x', padx=10, pady=5)
        
        google_controls = tk.Frame(google_frame, bg='#1a1a1a')
        google_controls.pack(fill='x', pady=5)
        
        ttk.Button(google_controls, text="ðŸ“§ Gmail Integration",
                  command=self._setup_gmail_integration).pack(side='left', padx=5)
        
        ttk.Button(google_controls, text="ðŸ“… Calendar Sync",
                  command=self._setup_calendar_sync).pack(side='left', padx=5)
        
        ttk.Button(google_controls, text="â˜ï¸ Cloud Functions",
                  command=self._setup_cloud_functions).pack(side='left', padx=5)
        
        # ===== MICROSOFT SERVICES =====
        microsoft_frame = ttk.LabelFrame(integrations_frame, text="Microsoft Services", padding=10)
        microsoft_frame.pack(fill='x', padx=10, pady=5)
        
        ms_controls = tk.Frame(microsoft_frame, bg='#1a1a1a')
        ms_controls.pack(fill='x', pady=5)
        
        ttk.Button(ms_controls, text="ðŸ“§ Outlook Integration",
                  command=self._setup_outlook_integration).pack(side='left', padx=5)
        
        ttk.Button(ms_controls, text="â˜ï¸ OneDrive Sync",
                  command=self._setup_onedrive_sync).pack(side='left', padx=5)
        
        ttk.Button(ms_controls, text="ðŸ’¼ Office 365",
                  command=self._setup_office365).pack(side='left', padx=5)
        
        # ===== WEBHOOKS & APIS =====
        webhooks_frame = ttk.LabelFrame(integrations_frame, text="Webhooks & APIs", padding=10)
        webhooks_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Lista de webhooks
        self.webhooks_listbox = tk.Listbox(webhooks_frame, bg='#2a2a2a', fg='#ffffff',
                                          font=('Consolas', 10))
        self.webhooks_listbox.pack(fill='both', expand=True, side='left')
        
        webhook_scrollbar = ttk.Scrollbar(webhooks_frame, orient='vertical', command=self.webhooks_listbox.yview)
        self.webhooks_listbox.configure(yscrollcommand=webhook_scrollbar.set)
        webhook_scrollbar.pack(side='right', fill='y')
        
        # Controles de webhook
        webhook_controls = tk.Frame(integrations_frame, bg='#1a1a1a')
        webhook_controls.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(webhook_controls, text="âž• Novo Webhook",
                  command=self._create_webhook).pack(side='left', padx=5)
        
        ttk.Button(webhook_controls, text="âœï¸ Editar",
                  command=self._edit_webhook).pack(side='left', padx=5)
        
        ttk.Button(webhook_controls, text="ðŸ§ª Testar",
                  command=self._test_webhook).pack(side='left', padx=5)
        
        ttk.Button(webhook_controls, text="âŒ Remover",
                  command=self._remove_webhook).pack(side='left', padx=5)
    
    def _create_monitoring_tab(self):
        """ðŸ“Š ABA DE MONITORAMENTO"""
        
        monitoring_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitoring_frame, text="ðŸ“Š Monitoramento")
        
        # ===== MÉTRICAS EM TEMPO REAL =====
        metrics_frame = ttk.LabelFrame(monitoring_frame, text="Real-time Metrics", padding=10)
        metrics_frame.pack(fill='x', padx=10, pady=5)
        
        # Grid de mÃ©tricas 2x2
        metrics_grid = tk.Frame(metrics_frame, bg='#1a1a1a')
        metrics_grid.pack(fill='x')
        
        self.metrics_labels = {}
        metrics_items = [
            ('cpu', 'CPU Usage: 0%'),
            ('memory', 'Memory: 0%'),
            ('network', 'Network: 0 KB/s'),
            ('gpu', 'GPU: Detecting...')
        ]
        
        for i, (key, default_text) in enumerate(metrics_items):
            row = i // 2
            col = i % 2
            
            frame = tk.Frame(metrics_grid, bg='#1a1a1a', relief='ridge', bd=1)
            frame.grid(row=row, column=col, sticky='ew', padx=5, pady=5)
            
            self.metrics_labels[key] = ttk.Label(frame, text=default_text, 
                                               style='Status.TLabel', font=('Arial', 12, 'bold'))
            self.metrics_labels[key].pack(padx=10, pady=10)
        
        metrics_grid.columnconfigure(0, weight=1)
        metrics_grid.columnconfigure(1, weight=1)
        
        # ===== LOGS EM TEMPO REAL =====
        logs_frame = ttk.LabelFrame(monitoring_frame, text="Real-time Logs", padding=10)
        logs_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Log viewer
        self.log_text = tk.Text(logs_frame, bg='#000000', fg='#00ff00',
                               font=('Consolas', 9), wrap=tk.WORD)
        
        log_scrollbar = ttk.Scrollbar(logs_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        log_scrollbar.pack(side='right', fill='y')
        
        # Controles de log
        log_controls = tk.Frame(monitoring_frame, bg='#1a1a1a')
        log_controls.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(log_controls, text="ðŸ”„ Refresh",
                  command=self._refresh_logs).pack(side='left', padx=5)
        
        ttk.Button(log_controls, text="ðŸ’¾ Salvar Logs",
                  command=self._save_logs).pack(side='left', padx=5)
        
        ttk.Button(log_controls, text="ðŸ—‘ï¸ Limpar",
                  command=self._clear_logs).pack(side='left', padx=5)
        
        # Filtro de logs
        ttk.Label(log_controls, text="Filtro:", style='Status.TLabel').pack(side='left', padx=10)
        
        self.log_filter_var = tk.StringVar()
        log_filter = ttk.Entry(log_controls, textvariable=self.log_filter_var, width=20)
        log_filter.pack(side='left', padx=5)
        log_filter.bind('<KeyRelease>', self._filter_logs)
    
    def _create_power_tools_tab(self):
        """ðŸ”¥ ABA DE FERRAMENTAS DE PODER"""
        
        power_frame = ttk.Frame(self.notebook)
        self.notebook.add(power_frame, text="ðŸ”¥ Power Tools")
        
        # ===== EXECUÃ‡ÃƒO REMOTA =====
        remote_frame = ttk.LabelFrame(power_frame, text="Remote Execution", padding=10)
        remote_frame.pack(fill='x', padx=10, pady=5)
        
        # Console remoto
        remote_console_frame = tk.Frame(remote_frame, bg='#1a1a1a')
        remote_console_frame.pack(fill='x', pady=5)
        
        ttk.Label(remote_console_frame, text="Comando:", style='Status.TLabel').pack(side='left', padx=5)
        
        self.remote_command_var = tk.StringVar()
        remote_entry = ttk.Entry(remote_console_frame, textvariable=self.remote_command_var, width=50)
        remote_entry.pack(side='left', padx=5, fill='x', expand=True)
        
        ttk.Button(remote_console_frame, text="â–¶ï¸ Executar",
                  command=self._execute_remote_command).pack(side='left', padx=5)
        
        # SeleÃ§Ã£o de alvo
        target_frame = tk.Frame(remote_frame, bg='#1a1a1a')
        target_frame.pack(fill='x', pady=5)
        
        ttk.Label(target_frame, text="Alvo:", style='Status.TLabel').pack(side='left', padx=5)
        
        self.target_device_var = tk.StringVar()
        target_combo = ttk.Combobox(target_frame, textvariable=self.target_device_var,
                                   values=["Todos os Dispositivos", "LÃ­der Atual", "Dispositivo EspecÃ­fico"])
        target_combo.pack(side='left', padx=5)
        
        # ===== AUTOMAÃ‡ÃƒO AVANÃ‡ADA =====
        automation_frame = ttk.LabelFrame(power_frame, text="Advanced Automation", padding=10)
        automation_frame.pack(fill='x', padx=10, pady=5)
        
        automation_controls = tk.Frame(automation_frame, bg='#1a1a1a')
        automation_controls.pack(fill='x', pady=5)
        
        ttk.Button(automation_controls, text="ðŸ¤– Auto-Setup Total",
                  command=self._complete_auto_setup).pack(side='left', padx=5)
        
        ttk.Button(automation_controls, text="ðŸ”® PrevisÃ£o Inteligente",
                  command=self._intelligent_prediction).pack(side='left', padx=5)
        
        ttk.Button(automation_controls, text="ðŸ› ï¸ Auto-CorreÃ§Ã£o",
                  command=self._auto_correction).pack(side='left', padx=5)
        
        ttk.Button(automation_controls, text="âš¡ Modo Deus",
                  command=self._god_mode).pack(side='left', padx=5)
        
        # ===== SCRIPT EXECUTOR =====
        script_frame = ttk.LabelFrame(power_frame, text="Custom Script Executor", padding=10)
        script_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Editor de script
        self.script_text = tk.Text(script_frame, bg='#1a1a1a', fg='#ffffff',
                                  font=('Consolas', 11), wrap=tk.NONE)
        
        script_scrollbar = ttk.Scrollbar(script_frame, orient='vertical', command=self.script_text.yview)
        self.script_text.configure(yscrollcommand=script_scrollbar.set)
        
        self.script_text.pack(side='left', fill='both', expand=True)
        script_scrollbar.pack(side='right', fill='y')
        
        # Controles de script
        script_controls = tk.Frame(power_frame, bg='#1a1a1a')
        script_controls.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(script_controls, text="ðŸ“ Carregar Script",
                  command=self._load_script).pack(side='left', padx=5)
        
        ttk.Button(script_controls, text="ðŸ’¾ Salvar Script",
                  command=self._save_script).pack(side='left', padx=5)
        
        ttk.Button(script_controls, text="â–¶ï¸ Executar",
                  command=self._execute_script).pack(side='left', padx=5)
        
        ttk.Button(script_controls, text="ðŸ”¥ ExecuÃ§Ã£o DistribuÃ­da",
                  command=self._execute_script_distributed).pack(side='left', padx=5)
    
    def _create_control_footer(self):
        """ðŸŽ›ï¸ FOOTER DE CONTROLE RÃPIDO"""
        
        footer_frame = tk.Frame(self.root, bg='#2a2a2a', height=60)
        footer_frame.pack(fill='x', padx=10, pady=5)
        footer_frame.pack_propagate(False)
        
        # Controles de emergÃªncia
        emergency_frame = tk.Frame(footer_frame, bg='#2a2a2a')
        emergency_frame.pack(side='left', padx=10, pady=10)
        
        ttk.Button(emergency_frame, text="ðŸš¨ STOP ALL",
                  command=self._emergency_stop).pack(side='left', padx=5)
        
        ttk.Button(emergency_frame, text="ðŸ”„ RESTART",
                  command=self._emergency_restart).pack(side='left', padx=5)
        
        # Status global
        status_frame = tk.Frame(footer_frame, bg='#2a2a2a')
        status_frame.pack(side='right', padx=10, pady=10)
        
        self.global_status_label = ttk.Label(status_frame,
                                           text="ðŸ”¥ SISTEMA DEMOCRÃTICO ATIVO",
                                           style='Success.TLabel')
        self.global_status_label.pack(side='right', padx=5)
    
    def _initialize_systems(self):
        """âš¡ INICIALIZA TODOS OS SISTEMAS"""
        
        try:
            # Thread separada para nÃ£o bloquear interface
            init_thread = threading.Thread(target=self._init_systems_background, daemon=True)
            init_thread.start()
            
            # Iniciar refresh de status
            self._start_status_refresh()
            
        except Exception as e:
            self._log(f"âŒ Erro inicializando sistemas: {e}")
    
    def _init_systems_background(self):
        """ðŸ”„ INICIALIZAÃ‡ÃƒO EM BACKGROUND"""
        
        try:
            # 1. Microsoft Device Identifier
            self._log("ðŸ” Inicializando identificaÃ§Ã£o Microsoft...")
            data_path = Path(self.jarvis_core.config['system']['base_path']) / "data"
            self.microsoft_identifier = MicrosoftDeviceIdentifier(str(data_path))
            self.microsoft_identifier.initialize()
            
            # 2. Biometric Verifier
            self._log("ðŸ” Inicializando verificaÃ§Ã£o biomÃ©trica...")
            self.biometric_verifier = EnhancedBiometricVerifier(self.jarvis_core, self.microsoft_identifier)
            
            # 3. Democratic Core
            self._log("ðŸ—³ï¸ Inicializando nÃºcleo democrÃ¡tico...")
            if DemocraticCore:
                self.democratic_core = DemocraticCore(self.jarvis_core)
            else:
                self._log("âš ï¸ DemocraticCore nÃ£o disponÃ­vel (ImportError)")
            
            self._log("âœ… Todos os sistemas inicializados com sucesso!")
            
            # Atualizar interface
            if self.root:
                self.root.after(0, self._update_initial_status)
            
        except Exception as e:
            self._log(f"âŒ Erro na inicializaÃ§Ã£o: {e}")
    
    def _update_initial_status(self):
        """ðŸ“Š ATUALIZA STATUS INICIAL DA INTERFACE"""
        
        try:
            # Microsoft Account Status
            if (self.microsoft_identifier and 
                hasattr(self.microsoft_identifier, 'microsoft_account') and 
                self.microsoft_identifier.microsoft_account):
                account_email = getattr(self.microsoft_identifier.microsoft_account, 'account_email', 'unknown')
                self.ms_status_label.config(text=f"âœ… Conectado: {account_email}")
            else:
                self.ms_status_label.config(text="âŒ Conta nÃ£o detectada")
            
            # Google Drive Status  
            if (self.microsoft_identifier and 
                hasattr(self.microsoft_identifier, 'google_drive_detected') and 
                getattr(self.microsoft_identifier, 'google_drive_detected', False)):
                self.drive_status_label.config(text="âœ… Google Drive detectado")
            else:
                self.drive_status_label.config(text="âŒ Google Drive nÃ£o encontrado")
            
            # Biometric Status
            if self.biometric_verifier:
                status = self.biometric_verifier.get_verification_status()
                if status['status'] == 'configured':
                    self.bio_status_label.config(text=f"âœ… Configurado - {status['face_samples']} faces, {status['voice_samples']} voice")
                else:
                    self.bio_status_label.config(text="âš™ï¸ NÃ£o configurado")
            
        except Exception as e:
            self._log(f"âŒ Erro atualizando status: {e}")
    
    def _start_status_refresh(self):
        """ðŸ”„ INICIA REFRESH AUTOMÃTICO DE STATUS"""
        
        def refresh_loop():
            try:
                self._refresh_metrics()
                self._refresh_network_status()
                self._check_devices()
            except Exception as e:
                self._log(f"Erro no refresh: {e}")
            finally:
                # Agendar prÃ³ximo refresh
                if self.root is not None:
                    self.root.after(5000, refresh_loop)  # A cada 5 segundos
        
        # Iniciar loop
        if self.root is not None:
            self.root.after(1000, refresh_loop)  # Primeiro refresh em 1 segundo
    
    # ===== MÃ‰TODOS DE CALLBACK =====
    
    def _redetect_microsoft_account(self):
        """ðŸ” RE-DETECTA CONTA MICROSOFT"""
        
        self._log("ðŸ”„ Re-detectando conta Microsoft...")
        
        def redetect():
            try:
                if self.microsoft_identifier:
                    if hasattr(self.microsoft_identifier, 'initialize'):
                        self.microsoft_identifier.initialize()
                    if self.root is not None:
                        self.root.after(0, self._update_initial_status)
                    self._log("âœ… Re-detecÃ§Ã£o concluÃ­da")
                else:
                    self._log("âŒ Sistema de identificaÃ§Ã£o nÃ£o inicializado")
            except Exception as e:
                self._log(f"âŒ Erro na re-detecÃ§Ã£o: {e}")
        
        threading.Thread(target=redetect, daemon=True).start()
    
    def _manual_microsoft_config(self):
        """âš™ï¸ CONFIGURAÃ‡ÃƒO MANUAL DA CONTA MICROSOFT"""
        
        # Criar janela de configuraÃ§Ã£o manual
        config_window = tk.Toplevel(self.root)
        config_window.title("ConfiguraÃ§Ã£o Manual - Microsoft Account")
        config_window.geometry("500x300")
        config_window.configure(bg='#1a1a1a')
        
        # Campos de entrada
        ttk.Label(config_window, text="ConfiguraÃ§Ã£o Manual da Conta Microsoft", 
                 style='Title.TLabel').pack(pady=10)
        
        # Email
        email_frame = tk.Frame(config_window, bg='#1a1a1a')
        email_frame.pack(fill='x', padx=20, pady=5)
        
        ttk.Label(email_frame, text="Email:", style='Status.TLabel').pack(side='left')
        email_var = tk.StringVar(value="" + self.config.get("target_user_email", os.getenv("JARVIS_USER_EMAIL", "" + self.config.get("target_user_email", os.getenv("JARVIS_USER_EMAIL", "williamkelvem64@gmail.com")) + "")) + "")
        ttk.Entry(email_frame, textvariable=email_var, width=40).pack(side='right')
        
        # Display name  
        name_frame = tk.Frame(config_window, bg='#1a1a1a')
        name_frame.pack(fill='x', padx=20, pady=5)
        
        ttk.Label(name_frame, text="Nome:", style='Status.TLabel').pack(side='left')
        name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=name_var, width=40).pack(side='right')
        
        # BotÃµes
        button_frame = tk.Frame(config_window, bg='#1a1a1a')
        button_frame.pack(fill='x', padx=20, pady=20)
        
        def save_manual_config():
            if self.microsoft_identifier:
                # ConfiguraÃ§Ã£o manual (implementar mÃ©todo no identifier)
                self._log(f"ðŸ’¾ ConfiguraÃ§Ã£o manual salva: {email_var.get()}")
                config_window.destroy()
                self._update_initial_status()
            else:
                messagebox.showerror("Erro", "Sistema de identificaÃ§Ã£o nÃ£o inicializado")
        
        ttk.Button(button_frame, text="ðŸ’¾ Salvar",
                  command=save_manual_config).pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="âŒ Cancelar",
                  command=config_window.destroy).pack(side='left', padx=5)
    
    def _show_microsoft_details(self):
        """ðŸ“‹ MOSTRA DETALHES COMPLETOS DA CONTA MICROSOFT"""
        
        if not self.microsoft_identifier:
            messagebox.showwarning("Aviso", "Sistema de identificaÃ§Ã£o nÃ£o inicializado")
            return
        
        # Criar janela de detalhes
        details_window = tk.Toplevel(self.root)
        details_window.title("Detalhes Completos - Microsoft Account")
        details_window.geometry("700x500")
        details_window.configure(bg='#1a1a1a')
        
        # Text widget para mostrar detalhes
        details_text = tk.Text(details_window, bg='#000000', fg='#00ff00',
                              font=('Consolas', 10), wrap=tk.WORD)
        
        scrollbar = ttk.Scrollbar(details_window, orient='vertical', command=details_text.yview)
        details_text.configure(yscrollcommand=scrollbar.set)
        
        details_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        # Obter e exibir detalhes
        def load_details():
            try:
                details_info = "ðŸ†” DETALHES COMPLETOS DA IDENTIFICAÃ‡ÃƒO MICROSOFT\n"
                details_info += "=" * 60 + "\n\n"
                
                if self.microsoft_identifier and hasattr(self.microsoft_identifier, 'microsoft_account') and self.microsoft_identifier.microsoft_account:
                    account = self.microsoft_identifier.microsoft_account
                    details_info += f"ðŸ“§ Email: {getattr(account, 'account_email', 'unknown')}\n"
                    details_info += f"ðŸ‘¤ Nome: {getattr(account, 'display_name', 'unknown')}\n"
                    # details_info += f"ðŸ†” User ID: {getattr(account, 'user_id', 'unknown')}\n"
                    # details_info += f"ðŸ  Microsoft ID: {getattr(account, 'microsoft_id', 'unknown')}\n\n"
                else:
                    details_info += "âŒ Conta Microsoft nÃ£o detectada\n\n"
                
                if self.microsoft_identifier and hasattr(self.microsoft_identifier, 'device_fingerprint') and self.microsoft_identifier.device_fingerprint:
                    fingerprint = self.microsoft_identifier.device_fingerprint
                    details_info += "ðŸ–¥ï¸ DEVICE FINGERPRINT:\n"
                    details_info += f"ðŸ†” Device ID: {getattr(fingerprint, 'device_id', 'unknown')}\n"
                    details_info += f"ðŸ’» Computer Name: {getattr(fingerprint, 'computer_name', 'unknown')}\n"
                    # details_info += f"ðŸ”§ CPU ID: {getattr(fingerprint, 'cpu_id', 'unknown')}\n"
                    details_info += f"ðŸ  Motherboard: {getattr(fingerprint, 'motherboard_serial', 'unknown')}\n"
                    details_info += f"âš¡ BIOS: {getattr(fingerprint, 'bios_serial', 'unknown')}\n\n"
                else:
                    details_info += "âŒ Device fingerprint nÃ£o criado\n\n"
                
                # Google Drive status
                details_info += "â˜ï¸ GOOGLE DRIVE:\n"
                if self.microsoft_identifier and hasattr(self.microsoft_identifier, 'google_drive_auth') and self.microsoft_identifier.google_drive_auth:
                    details_info += f"âœ… Status: Detectado\n"
                    drive_path = getattr(self.microsoft_identifier.google_drive_auth, 'drive_path', 'unknown')
                    details_info += f"ðŸ“ Path: {drive_path}\n"
                else:
                    details_info += "âŒ Status: NÃ£o detectado\n"
                
                details_text.insert(tk.END, details_info)
                
            except Exception as e:
                details_text.insert(tk.END, f"âŒ Erro carregando detalhes: {e}")
        
        threading.Thread(target=load_details, daemon=True).start()
    
    # ===== MÃ‰TODOS UTILITÃRIOS =====
    
    def _log(self, message: str):
        """ðŸ“ LOG PARA CONSOLE E INTERFACE"""
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        print(log_message.strip())  # Console
        
        # Interface (se disponÃ­vel)
        try:
            if hasattr(self, 'log_text'):
                self.log_text.insert(tk.END, log_message)
                self.log_text.see(tk.END)
            
            if hasattr(self, 'training_console'):
                self.training_console.insert(tk.END, log_message)
                self.training_console.see(tk.END)
        except:
            pass
    
    def _load_user_preferences(self) -> Dict[str, Any]:
        """ðŸ“ CARREGA PREFERÃŠNCIAS DO USUÃRIO"""
        
        try:
            prefs_path = Path(self.jarvis_core.config['system']['base_path']) / "data" / "user_preferences.json"
            
            if prefs_path.exists():
                with open(prefs_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # PreferÃªncias padrÃ£o
                return {
                    'theme': 'dark',
                    'auto_monitoring': True,
                    'auto_training': False,
                    'notification_level': 'normal',
                    'device_discovery_interval': 30,
                    'biometric_verification_required': True
                }
        except Exception as e:
            print(f"âŒ Erro carregando preferÃªncias: {e}")
            return {}
    
    def _save_user_preferences(self):
        """ðŸ’¾ SALVA PREFERÃŠNCIAS DO USUÃRIO"""
        
        try:
            prefs_path = Path(self.jarvis_core.config['system']['base_path']) / "data" / "user_preferences.json"
            prefs_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(prefs_path, 'w', encoding='utf-8') as f:
                json.dump(self.user_preferences, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"âŒ Erro salvando preferÃªncias: {e}")
    
    # ===== MÃ‰TODOS PLACEHOLDER (IMPLEMENTAR CONFORME NECESSÃRIO) =====
    
    def _connect_google_drive(self): self._log("ðŸ”— Conectando Google Drive...")
    def _setup_drive_structure(self): self._log("ðŸ“ Configurando estrutura do Drive...")
    def _sync_google_drive(self): self._log("â˜ï¸ Sincronizando Google Drive...")
    def _setup_biometric_profile(self): 
        if self.biometric_verifier:
            threading.Thread(target=self.biometric_verifier.setup_user_profile, daemon=True).start()
        else:
            self._log("âŒ Sistema biomÃ©trico nÃ£o inicializado")
    
    def _verify_identity_now(self): self._log("ðŸ” Verificando identidade...")
    def _toggle_biometric_monitoring(self): self._log("ðŸ‘ï¸ Alternando monitoramento biomÃ©trico...")
    def _scan_network_devices(self): self._log("ðŸ” Escaneando dispositivos na rede...")
    def _detect_jarvis_instances(self): self._log("ðŸ†” Detectando instÃ¢ncias JARVIS...")
    def _connect_device_manual(self): self._log("ðŸ¤ Conectando dispositivo manualmente...")
    def _force_democratic_election(self): self._log("âš¡ ForÃ§ando eleiÃ§Ã£o democrÃ¡tica...")
    def _show_device_details(self): self._log("ðŸ“Š Mostrando detalhes do dispositivo...")
    def _sync_selected_device(self): self._log("ðŸ”„ Sincronizando dispositivo selecionado...")
    def _disconnect_selected_device(self): self._log("âŒ Desconectando dispositivo...")
    def _force_election(self): self._log("ðŸ—³ï¸ ForÃ§ando eleiÃ§Ã£o...")
    def _run_for_leader(self): self._log("ðŸ‘‘ Candidatando-se a lÃ­der...")
    def _full_network_sync(self): self._log("ðŸ”„ SincronizaÃ§Ã£o total da rede...")
    def _analyze_network(self): self._log("ðŸ“Š Analisando rede...")
    def _auto_optimize_network(self): self._log("âš¡ OtimizaÃ§Ã£o automÃ¡tica da rede...")
    def _advanced_security_config(self): self._log("ðŸ›¡ï¸ ConfiguraÃ§Ã£o avanÃ§ada de seguranÃ§a...")
    def _start_distributed_training(self): self._log("ðŸš€ Iniciando treinamento distribuÃ­do...")
    def _pause_training(self): self._log("â¸ï¸ Pausando treinamento...")
    def _stop_training(self): self._log("â¹ï¸ Parando treinamento...")
    def _show_training_metrics(self): self._log("ðŸ“ˆ Mostrando mÃ©tricas de treinamento...")
    def _configure_model(self): self._log("âš™ï¸ Configurando modelo...")
    def _select_dataset(self): self._log("ðŸ“ Selecionando dataset...")
    def _generate_dataset(self): self._log("ðŸ”„ Gerando dataset...")
    def _setup_gmail_integration(self): self._log("ðŸ“§ Configurando integraÃ§Ã£o Gmail...")
    def _setup_calendar_sync(self): self._log("ðŸ“… Configurando sincronizaÃ§Ã£o de calendÃ¡rio...")
    def _setup_cloud_functions(self): self._log("â˜ï¸ Configurando Cloud Functions...")
    def _setup_outlook_integration(self): self._log("ðŸ“§ Configurando integraÃ§Ã£o Outlook...")
    def _setup_onedrive_sync(self): self._log("â˜ï¸ Configurando sincronizaÃ§Ã£o OneDrive...")
    def _setup_office365(self): self._log("ðŸ’¼ Configurando Office 365...")
    def _create_webhook(self): self._log("âž• Criando webhook...")
    def _edit_webhook(self): self._log("âœï¸ Editando webhook...")
    def _test_webhook(self): self._log("ðŸ§ª Testando webhook...")
    def _remove_webhook(self): self._log("âŒ Removendo webhook...")
    def _refresh_logs(self): self._log("ðŸ”„ Atualizando logs...")
    def _save_logs(self): self._log("ðŸ’¾ Salvando logs...")
    def _clear_logs(self): 
        if hasattr(self, 'log_text'):
            self.log_text.delete(1.0, tk.END)
    def _filter_logs(self, event): pass  # Implementar filtro de logs
    def _execute_remote_command(self): self._log("â–¶ï¸ Executando comando remoto...")
    def _complete_auto_setup(self): self._log("ðŸ¤– Executando auto-setup total...")
    def _intelligent_prediction(self): self._log("ðŸ”® Executando previsÃ£o inteligente...")
    def _auto_correction(self): self._log("ðŸ› ï¸ Executando auto-correÃ§Ã£o...")
    def _god_mode(self): self._log("âš¡ MODO DEUS ATIVADO...")
    def _load_script(self): self._log("ðŸ“ Carregando script...")
    def _save_script(self): self._log("ðŸ’¾ Salvando script...")
    def _execute_script(self): self._log("â–¶ï¸ Executando script...")
    def _execute_script_distributed(self): self._log("ðŸ”¥ Executando script distribuÃ­do...")
    def _emergency_stop(self): self._log("ðŸš¨ PARADA DE EMERGÃŠNCIA!")
    def _emergency_restart(self): self._log("ðŸ”„ REINÃCIO DE EMERGÃŠNCIA!")
    def _refresh_metrics(self):
        """ðŸ“Š ATUALIZA MÃ‰TRICAS EM TEMPO REAL"""
        try:
            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.metrics_labels['cpu'].config(text=f"CPU Usage: {cpu_percent:.1f}%")
            
            # Memory Usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024**3)
            memory_total_gb = memory.total / (1024**3)
            self.metrics_labels['memory'].config(text=f"Memory: {memory_percent:.1f}% ({memory_used_gb:.1f}GB/{memory_total_gb:.1f}GB)")
            
            # Network Usage (simplified)
            network = psutil.net_io_counters()
            if network:
                bytes_sent = network.bytes_sent
                bytes_recv = network.bytes_recv
                total_mb = (bytes_sent + bytes_recv) / (1024**2)
                self.metrics_labels['network'].config(text=f"Network: {total_mb:.1f} MB total")
            else:
                self.metrics_labels['network'].config(text="Network: N/A")
            
            # GPU Usage
            gpu_text = self._get_gpu_metrics_text()
            self.metrics_labels['gpu'].config(text=gpu_text)
            
        except Exception as e:
            self._log(f"Erro atualizando métricas: {e}")
            # Fallback values
            self.metrics_labels['cpu'].config(text="CPU Usage: Error")
            self.metrics_labels['memory'].config(text="Memory: Error")
            self.metrics_labels['network'].config(text="Network: Error")
            self.metrics_labels['gpu'].config(text="GPU: Error")

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
    def _refresh_network_status(self): pass  # Implementar refresh de status da rede
    def _check_devices(self): pass  # Implementar verificaÃ§Ã£o de dispositivos

# FunÃ§Ã£o principal de lanÃ§amento
def launch_democratic_interface(jarvis_core):
    """ðŸš€ LANÃ‡A INTERFACE DEMOCRÃTICA"""
    
    interface = DemocraticControlInterface(jarvis_core)
    interface.launch_interface()
    return interface

if __name__ == "__main__":
    # Para testes
    print("ðŸ”¥ Democratic Control Interface - Teste")
    print("âž¡ï¸  Use launch_democratic_interface(jarvis_core) para executar")
