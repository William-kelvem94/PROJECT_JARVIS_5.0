import tkinter as tk
from tkinter import ttk, messagebox
import threading
from src.core.interface.tabs.base_tab import BaseTab

class IdentityTab(BaseTab):
    def __init__(self, notebook, interface):
        super().__init__(notebook, interface, "🆔 Identidade")

    def create_widgets(self):
        # ===== MICROSOFT ACCOUNT =====
        ms_frame = ttk.LabelFrame(
            self.frame, text="Microsoft Account Detection", padding=10
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
            self.frame, text="Google Drive Integration", padding=10
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
            self.frame, text="Biometric Verification", padding=10
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

    def update_status(self):
        """Updates the status labels based on interface state."""
        try:
            # Microsoft Account Status
            if (
                self.interface.microsoft_identifier
                and hasattr(self.interface.microsoft_identifier, "microsoft_account")
                and self.interface.microsoft_identifier.microsoft_account
            ):
                account_email = getattr(
                    self.interface.microsoft_identifier.microsoft_account,
                    "account_email",
                    "unknown",
                )
                self.ms_status_label.config(text=f"✅ Conectado: {account_email}")
            else:
                self.ms_status_label.config(text="❌ Conta não detectada")

            # Google Drive Status
            if (
                self.interface.microsoft_identifier
                and hasattr(self.interface.microsoft_identifier, "google_drive_detected")
                and getattr(self.interface.microsoft_identifier, "google_drive_detected", False)
            ):
                self.drive_status_label.config(text="✅ Google Drive detectado")
            else:
                self.drive_status_label.config(text="❌ Google Drive não encontrado")

            # Biometric Status
            if self.interface.biometric_verifier:
                status = self.interface.biometric_verifier.get_verification_status()
                if status["status"] == "configured":
                    self.bio_status_label.config(
                        text=f"✅ Configurado - {status['face_samples']} faces, {status['voice_samples']} voice"
                    )
                else:
                    self.bio_status_label.config(text="⚙️ Não configurado")

        except Exception as e:
            self.interface._log(f"❌ Erro atualizando status: {e}")

    def _redetect_microsoft_account(self):
        """🔍 RE-DETECTA CONTA MICROSOFT"""

        self.interface._log("🔄 Re-detectando conta Microsoft...")

        def redetect():
            try:
                if self.interface.microsoft_identifier:
                    if hasattr(self.interface.microsoft_identifier, "initialize"):
                        self.interface.microsoft_identifier.initialize()
                    if self.interface.root is not None:
                        self.interface.root.after(0, self.update_status)
                    self.interface._log("✅ Re-detecção concluída")
                else:
                    self.interface._log("❌ Sistema de identificação não inicializado")
            except Exception as e:
                self.interface._log(f"❌ Erro na re-detecção: {e}")

        threading.Thread(target=redetect, daemon=True).start()

    def _manual_microsoft_config(self):
        """⚙️ CONFIGURAÇÃO MANUAL DA CONTA MICROSOFT"""

        # Criar janela de configuração manual
        config_window = tk.Toplevel(self.interface.root)
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

        ttk.Label(email_frame, text="Email:", style="Status.TLabel").pack(side="left")

        from src.utils.config import config

        target_email = config.get_setting("portability.target_user_email", "")

        email_var = tk.StringVar(value=target_email)
        ttk.Entry(email_frame, textvariable=email_var, width=40).pack(side="right")

        # Display name
        name_frame = tk.Frame(config_window, bg="#1a1a1a")
        name_frame.pack(fill="x", padx=20, pady=5)

        ttk.Label(name_frame, text="Nome:", style="Status.TLabel").pack(side="left")
        name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=name_var, width=40).pack(side="right")

        # Botões
        button_frame = tk.Frame(config_window, bg="#1a1a1a")
        button_frame.pack(fill="x", padx=20, pady=20)

        def save_manual_config():
            if self.interface.microsoft_identifier:
                # Configuração manual (implementar método no identifier)
                self.interface._log(f"💾 Configuração manual salva: {email_var.get()}")
                config_window.destroy()
                self.update_status()
            else:
                messagebox.showerror(
                    "Erro", "Sistema de identificação não inicializado"
                )

        ttk.Button(button_frame, text="💾 Salvar", command=save_manual_config).pack(
            side="left", padx=5
        )

        ttk.Button(
            button_frame, text="❌ Cancelar", command=config_window.destroy
        ).pack(side="left", padx=5
        )

    def _show_microsoft_details(self):
        """📋 MOSTRA DETALHES COMPLETOS DA CONTA MICROSOFT"""

        if not self.interface.microsoft_identifier:
            messagebox.showwarning(
                "Aviso", "Sistema de identificação não inicializado"
            )
            return

        # Criar janela de detalhes
        details_window = tk.Toplevel(self.interface.root)
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

        details_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        # Obter e exibir detalhes
        def load_details():
            try:
                details_info = "🆔 DETALHES COMPLETOS DA IDENTIFICAÇÃO MICROSOFT\n"
                details_info += "=" * 60 + "\n\n"

                if (
                    self.interface.microsoft_identifier
                    and hasattr(self.interface.microsoft_identifier, "microsoft_account")
                    and self.interface.microsoft_identifier.microsoft_account
                ):
                    account = self.interface.microsoft_identifier.microsoft_account
                    details_info += (
                        f"📧 Email: {getattr(account, 'account_email', 'unknown')}\n"
                    )
                    details_info += (
                        f"👤 Nome: {getattr(account, 'display_name', 'unknown')}\n"
                    )
                else:
                    details_info += "❌ Conta Microsoft não detectada\n\n"

                if (
                    self.interface.microsoft_identifier
                    and hasattr(self.interface.microsoft_identifier, "device_fingerprint")
                    and self.interface.microsoft_identifier.device_fingerprint
                ):
                    fingerprint = self.interface.microsoft_identifier.device_fingerprint
                    details_info += "🖥️ DEVICE FINGERPRINT:\n"
                    details_info += f"🆔 Device ID: {getattr(fingerprint, 'device_id', 'unknown')}\n"
                    details_info += f"💻 Computer Name: {getattr(fingerprint, 'computer_name', 'unknown')}\n"
                    details_info += f"🏠 Motherboard: {getattr(fingerprint, 'motherboard_serial', 'unknown')}\n"
                    details_info += f"⚡ BIOS: {getattr(fingerprint, 'bios_serial', 'unknown')}\n\n"
                else:
                    details_info += "❌ Device fingerprint não criado\n\n"

                # Google Drive status
                details_info += "☁️ GOOGLE DRIVE:\n"
                if (
                    self.interface.microsoft_identifier
                    and hasattr(self.interface.microsoft_identifier, "google_drive_auth")
                    and self.interface.microsoft_identifier.google_drive_auth
                ):
                    details_info += "✅ Status: Detectado\n"
                    drive_path = getattr(
                        self.interface.microsoft_identifier.google_drive_auth,
                        "drive_path",
                        "unknown",
                    )
                    details_info += f"📍 Path: {drive_path}\n"
                else:
                    details_info += "❌ Status: Não detectado\n"

                details_text.insert(tk.END, details_info)

            except Exception as e:
                details_text.insert(tk.END, f"❌ Erro carregando detalhes: {e}")

        threading.Thread(target=load_details, daemon=True).start()

    def _connect_google_drive(self):
        self.interface._log("🔗 Conectando Google Drive...")

    def _setup_drive_structure(self):
        self.interface._log("📍 Configurando estrutura do Drive...")

    def _sync_google_drive(self):
        self.interface._log("☁️ Sincronizando Google Drive...")

    def _setup_biometric_profile(self):
        if self.interface.biometric_verifier:
            threading.Thread(
                target=self.interface.biometric_verifier.setup_user_profile, daemon=True
            ).start()
        else:
            self.interface._log("❌ Sistema biométrico não inicializado")

    def _verify_identity_now(self):
        self.interface._log("🔍 Verificando identidade...")

    def _toggle_biometric_monitoring(self):
        self.interface._log("👁️ Alternando monitoramento biométrico...")
