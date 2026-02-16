import tkinter as tk
from tkinter import ttk
from src.core.interface.tabs.base_tab import BaseTab

class TrainingTab(BaseTab):
    def __init__(self, notebook, interface):
        super().__init__(notebook, interface, "🧠 Treinamento")

    def create_widgets(self):
        # ===== CONTROLE DE TREINAMENTO =====
        training_control_frame = ttk.LabelFrame(
            self.frame, text="Distributed Training Control", padding=10
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
            self.frame, text="Model Configuration", padding=10
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
            text="📂 Selecionar Dataset",
            command=self._select_dataset,
        ).pack(side="left", padx=5)

        ttk.Button(
            dataset_selection, text="🔄 Gerar Dataset", command=self._generate_dataset
        ).pack(side="left", padx=5)

        # ===== CONSOLE DE TREINAMENTO =====
        console_frame = ttk.LabelFrame(
            self.frame, text="Training Console", padding=10
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

    def append_log(self, message: str):
        """Append log message to training console."""
        if hasattr(self, "training_console"):
            self.training_console.insert(tk.END, message)
            self.training_console.see(tk.END)

    def _start_distributed_training(self):
        self.interface._log("🚀 Iniciando treinamento distribuído...")

    def _pause_training(self):
        self.interface._log("⏸️ Pausando treinamento...")

    def _stop_training(self):
        self.interface._log("⏹️ Parando treinamento...")

    def _show_training_metrics(self):
        self.interface._log("📈 Mostrando métricas de treinamento...")

    def _configure_model(self):
        self.interface._log("⚙️ Configurando modelo...")

    def _select_dataset(self):
        self.interface._log("📂 Selecionando dataset...")

    def _generate_dataset(self):
        self.interface._log("🔄 Gerando dataset...")
