import tkinter as tk
from tkinter import ttk
from src.core.interface.tabs.base_tab import BaseTab

class IntegrationsTab(BaseTab):
    def __init__(self, notebook, interface):
        super().__init__(notebook, interface, "🔗 Integrações")

    def create_widgets(self):
        # ===== GOOGLE SERVICES =====
        google_frame = ttk.LabelFrame(
            self.frame, text="Google Services", padding=10
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
            self.frame, text="Microsoft Services", padding=10
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
            self.frame, text="Webhooks & APIs", padding=10
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
        webhook_controls = tk.Frame(self.frame, bg="#1a1a1a")
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

    def _setup_gmail_integration(self):
        self.interface._log("📧 Configurando integração Gmail...")

    def _setup_calendar_sync(self):
        self.interface._log("📅 Configurando sincronização de calendário...")

    def _setup_cloud_functions(self):
        self.interface._log("☁️ Configurando Cloud Functions...")

    def _setup_outlook_integration(self):
        self.interface._log("📧 Configurando integração Outlook...")

    def _setup_onedrive_sync(self):
        self.interface._log("☁️ Configurando sincronização OneDrive...")

    def _setup_office365(self):
        self.interface._log("💼 Configurando Office 365...")

    def _create_webhook(self):
        self.interface._log("➕ Criando webhook...")

    def _edit_webhook(self):
        self.interface._log("✏️ Editando webhook...")

    def _test_webhook(self):
        self.interface._log("🧪 Testando webhook...")

    def _remove_webhook(self):
        self.interface._log("❌ Removendo webhook...")
