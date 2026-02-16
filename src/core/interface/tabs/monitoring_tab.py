import tkinter as tk
from tkinter import ttk
import psutil
from src.core.interface.tabs.base_tab import BaseTab

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


class MonitoringTab(BaseTab):
    def __init__(self, notebook, interface):
        self.metrics_labels = {}
        super().__init__(notebook, interface, "📊 Monitoramento")

    def create_widgets(self):
        # ===== MÉTRICAS EM TEMPO REAL =====
        metrics_frame = ttk.LabelFrame(
            self.frame, text="Real-time Metrics", padding=10
        )
        metrics_frame.pack(fill="x", padx=10, pady=5)

        # Grid de métricas 2x2
        metrics_grid = tk.Frame(metrics_frame, bg="#1a1a1a")
        metrics_grid.pack(fill="x")

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
        logs_frame = ttk.LabelFrame(self.frame, text="Real-time Logs", padding=10)
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
        log_controls = tk.Frame(self.frame, bg="#1a1a1a")
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
        log_filter = ttk.Entry(log_controls, textvariable=self.log_filter_var, width=20)
        log_filter.pack(side="left", padx=5)
        log_filter.bind("<KeyRelease>", self._filter_logs)

    def append_log(self, message: str):
        """Append a log message to the log viewer."""
        if hasattr(self, "log_text"):
            self.log_text.insert(tk.END, message)
            self.log_text.see(tk.END)

    def refresh_metrics(self):
        """📊 ATUALIZA MÉTRICAS EM TEMPO REAL"""
        try:
            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.metrics_labels["cpu"].config(text=f"CPU Usage: {cpu_percent:.1f}%")

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
            self.interface._log(f"Erro atualizando métricas: {e}")
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

    def _refresh_logs(self):
        self.interface._log("🔄 Atualizando logs...")

    def _save_logs(self):
        self.interface._log("💾 Salvando logs...")

    def _clear_logs(self):
        if hasattr(self, "log_text"):
            self.log_text.delete(1.0, tk.END)

    def _filter_logs(self, event):
        pass  # Implementar filtro de logs
