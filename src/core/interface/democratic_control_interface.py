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

# Imports dos sistemas democráticos
try:
    from src.core.democratic_core import DemocraticIntelligenceCore as DemocraticCore
except ImportError:
    DemocraticCore = None
from src.core.identity.microsoft_device_identifier import MicrosoftDeviceIdentifier
from src.core.identity.enhanced_biometric_verifier import EnhancedBiometricVerifier

# Imports das abas
from src.core.interface.tabs.identity_tab import IdentityTab
from src.core.interface.tabs.devices_tab import DevicesTab
from src.core.interface.tabs.network_tab import NetworkTab
from src.core.interface.tabs.training_tab import TrainingTab
from src.core.interface.tabs.integrations_tab import IntegrationsTab
from src.core.interface.tabs.monitoring_tab import MonitoringTab
from src.core.interface.tabs.power_tools_tab import PowerToolsTab

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

        # Tabs
        self.identity_tab = None
        self.devices_tab = None
        self.network_tab = None
        self.training_tab = None
        self.integrations_tab = None
        self.monitoring_tab = None
        self.power_tools_tab = None

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

        # Initialize tabs
        self.identity_tab = IdentityTab(self.notebook, self)
        self.devices_tab = DevicesTab(self.notebook, self)
        self.network_tab = NetworkTab(self.notebook, self)
        self.training_tab = TrainingTab(self.notebook, self)
        self.integrations_tab = IntegrationsTab(self.notebook, self)
        self.monitoring_tab = MonitoringTab(self.notebook, self)
        self.power_tools_tab = PowerToolsTab(self.notebook, self)

        # ===== FOOTER DE CONTROLE RÁPIDO =====
        self._create_control_footer()

    def _create_control_footer(self):
        """🕹️ FOOTER DE CONTROLE RÁPIDO"""

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
            data_path = Path(self.jarvis_core.config["system"]["base_path"]) / "data"
            self.microsoft_identifier = MicrosoftDeviceIdentifier(str(data_path))
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
        if self.identity_tab:
            self.identity_tab.update_status()

    def _start_status_refresh(self):
        """🔄 INICIA REFRESH AUTOMÁTICO DE STATUS"""

        def refresh_loop():
            try:
                if self.monitoring_tab:
                    self.monitoring_tab.refresh_metrics()
            except Exception as e:
                self._log(f"Erro no refresh: {e}")
            finally:
                # Agendar próximo refresh
                if self.root is not None:
                    self.root.after(5000, refresh_loop)  # A cada 5 segundos

        # Iniciar loop
        if self.root is not None:
            self.root.after(1000, refresh_loop)  # Primeiro refresh em 1 segundo

    def _log(self, message: str):
        """📝 LOG PARA CONSOLE E INTERFACE"""

        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        print(log_message.strip())  # Console

        # Interface (se disponível)
        try:
            if self.monitoring_tab:
                self.monitoring_tab.append_log(log_message)
            if self.training_tab:
                self.training_tab.append_log(log_message)
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
                json.dump(self.user_preferences, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"❌ Erro salvando preferências: {e}")

    def _emergency_stop(self):
        self._log("🚨 PARADA DE EMERGÊNCIA!")

    def _emergency_restart(self):
        self._log("🔄 REINÍCIO DE EMERGÊNCIA!")

# Função principal de lançamento
def launch_democratic_interface(jarvis_core):
    """🚀 LANÇA INTERFACE DEMOCRÁTICA"""

    interface = DemocraticControlInterface(jarvis_core)
    interface.launch_interface()
    return interface


if __name__ == "__main__":
    # Para testes
    print("🔥 Democratic Control Interface - Teste")
    print("➡️ Use launch_democratic_interface(jarvis_core) para executar")
