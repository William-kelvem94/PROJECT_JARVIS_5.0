"""
Gerenciador de Hardware do Jarvis 5.0
Detecta e otimiza o uso de CPU/GPU para todos os módulos de IA.
"""

import threading
import logging
import platform
import os
import sys
from typing import Dict, Any, List

# 🛡️ GLOBAL MONKEY PATCH: Correção Crítica para OpenVINO/Optimum-Intel
try:
    import openvino

    # openvino.runtime is deprecated in favor of openvino
    node_obj = getattr(openvino, "Node", None)
    if not node_obj and "openvino.runtime" in sys.modules:
        node_obj = getattr(sys.modules["openvino.runtime"], "Node", None)

    if node_obj:
        if not hasattr(openvino, "Node"):
            openvino.Node = node_obj

    op_obj = getattr(openvino, "op", None)
    if not op_obj and "openvino.runtime" in sys.modules:
        op_obj = getattr(sys.modules["openvino.runtime"], "op", None)

    if op_obj:
        sys.modules["openvino.op"] = op_obj
        if not hasattr(openvino, "op"):
            openvino.op = op_obj
except Exception:
    pass

# Lazy import torch to avoid startup issues
TORCH_AVAILABLE = False
torch = None


def _ensure_torch():
    global TORCH_AVAILABLE, torch
    if not TORCH_AVAILABLE and torch is None:
        try:
            import torch

            TORCH_AVAILABLE = True
        except (ImportError, OSError) as e:
            TORCH_AVAILABLE = False
            torch = None
            logging.warning(f"⚠️ torch not available in hardware_manager: {e}")


try:
    import openvino as ov

    OPENVINO_AVAILABLE = True
except ImportError:
    OPENVINO_AVAILABLE = False
    ov = None

logger = logging.getLogger(__name__)


class HardwareManager:
    """Singleton para gerenciar recursos de hardware"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        with self._lock:
            if self._initialized:
                return

        # Initialize basic attributes without loading torch yet
        self.device = "cpu"
        self.accelerator = None
        self.memory_gb = 0
        self.cpu_count = 0
        self.gpu_available = False
        self.torch_device = None
        self.openvino_available = OPENVINO_AVAILABLE
        self.system = platform.system()
        self.tier = "BALANCED"  # Default tier
        self.gpu_name = "None"

        # Mark as initialized but defer heavy hardware detection
        self._hardware_initialized = False
        self._initialized = True

    def _ensure_hardware_initialized(self):
        """Initialize hardware detection only when needed (lazy)"""
        if self._hardware_initialized:
            return

        with self._lock:
            if self._hardware_initialized:
                return

            # Now perform the heavy hardware detection
            if TORCH_AVAILABLE and torch and torch.cuda.is_available():
                self.device = "cuda"
                self.accelerator = "cuda"
                self.gpu_name = torch.cuda.get_device_name(0)
            elif OPENVINO_AVAILABLE:
                # Detectar se há uma GPU Intel (Iris Xe / Arc) compatível com
                # OpenVINO
                try:
                    core = ov.Core()
                    devices = core.available_devices
                    if "GPU" in devices:
                        # Torch device string (cpu/cuda). OpenVINO acts as a
                        # compiler/accelerator on top of CPU.
                        self.device = "cpu"
                        self.accelerator = "openvino"
                        self.gpu_name = "Intel Iris Xe / Arc (OpenVINO Accelerator)"
                    else:
                        self.device = "cpu"
                        self.accelerator = None
                        self.gpu_name = "None"
                except BaseException:
                    self.device = "cpu"
                    self.accelerator = None
                    self.gpu_name = "None"
            else:
                self.device = "cpu"
                self.accelerator = None
                self.gpu_name = "None"

            # 🆕 COMPUTE TIERING (Military Grade Scaling)
            if self.device == "cuda" or (
                hasattr(self, "accelerator") and self.accelerator == "openvino"
            ):
                self.tier = "ULTRA"
            else:
                import psutil

                try:
                    logical_cores = psutil.cpu_count(logical=True)
                    if not isinstance(logical_cores, int):
                        logical_cores = 4
                except BaseException:
                    logical_cores = 4

                if logical_cores >= 12:
                    self.tier = "FAST"
                elif logical_cores >= 6:
                    self.tier = "BALANCED"
                else:
                    self.tier = "LITE"

            if TORCH_AVAILABLE and torch and self.device == "cuda":
                torch.backends.cudnn.benchmark = True
                logger.info(
                    f"👑 JARVIS [ULTRA]: Rodando em GPU NVIDIA (CUDA): {self.gpu_name}"
                )
            elif hasattr(self, "accelerator") and self.accelerator == "openvino":
                # For OpenVINO, we might be using the GPU even if torch device
                # is 'cpu'
                logger.info(
                    f"👑 JARVIS [{self.tier}]: Rodando em GPU Intel ({self.gpu_name} via OpenVINO)."
                )
            else:
                import psutil

                try:
                    logical_cores = psutil.cpu_count(logical=True) or 4
                except BaseException:
                    logical_cores = 4

                # ADAPTIVE THREADING: Unlock full potential while preserving GUI responsiveness
                # Previous "Safe Mode" capped at 1 thread or half cores.
                # New Staged Boot Protocol allows us to be more aggressive.

                if self.tier == "FAST":
                    threads = logical_cores
                elif self.tier == "BALANCED":
                    # Leave 2 threads for GUI/OS
                    threads = max(1, logical_cores - 2)
                else:
                    # LITE mode still conservative
                    threads = max(1, logical_cores // 2)

                # Apply ai_config.yaml override if present
                try:
                    from src.utils.config import config as global_config

                    cfg_threads = global_config.get_ai_config(
                        "resources.torch_threads", None
                    )
                    if cfg_threads:
                        cfg_val = int(cfg_threads)
                        if cfg_val > 0:
                            threads = cfg_val
                except Exception:
                    pass

                # Honor environment override if present (allows quick tuning)
                try:
                    env_threads = os.environ.get("JARVIS_FORCE_TORCH_THREADS")
                    if env_threads:
                        env_val = int(env_threads)
                        if env_val > 0:
                            threads = env_val
                except Exception:
                    pass

                if TORCH_AVAILABLE and torch:
                    torch.set_num_threads(threads)

                logger.info(
                    f"👑 JARVIS [{self.tier}]: Rodando em CPU ({threads} threads ativas / {logical_cores} totais)."
                )

            # During test runs we avoid starting background threads that use native
            # extensions (psutil, tqdm monitors, etc.) to reduce flakiness and
            # crashes.
            is_pytest = ("PYTEST_CURRENT_TEST" in os.environ) or (
                os.environ.get("PYTEST_ADDOPTS") is not None
            )
            if (
                os.environ.get("JARVIS_TEST_MODE") in ("1", "true", "True", "yes", "on")
                or is_pytest
            ):
                logger.info(
                    "Test mode detected: skipping hardware monitoring thread startup"
                )
            else:
                self._start_monitoring_thread()
            self._hardware_initialized = True

    def _start_monitoring_thread(self):
        """Inicia monitoramento em background para alertas proativos"""
        # Respect both explicit test-mode flag and pytest environment
        is_pytest = ("PYTEST_CURRENT_TEST" in os.environ) or (
            os.environ.get("PYTEST_ADDOPTS") is not None
        )
        if (
            os.environ.get("JARVIS_TEST_MODE") in ("1", "true", "True", "yes", "on")
            or is_pytest
        ):
            logger.debug(
                "Test mode active: not starting HardwareProactiveMonitor thread"
            )
            return
        thread = threading.Thread(
            target=self._monitoring_loop, daemon=True, name="HardwareProactiveMonitor"
        )
        thread.start()

    def _monitoring_loop(self):
        """Loop de monitoramento contínuo (Phase 3)"""
        # Exit immediately in test mode to avoid native extension issues
        if os.environ.get("JARVIS_TEST_MODE") in ("1", "true", "True", "yes", "on"):
            logger.debug("Test mode active: exiting hardware monitoring loop")
            return

        import psutil
        import time
        from src.utils.web_emitter import emit_log_sync

        last_alert = 0
        while True:
            try:
                cpu = psutil.cpu_percent(interval=10)  # Verifica a cada 10s

                if cpu > 99:
                    now = time.time()
                    if now - last_alert > 120:  # Evitar spam (1 alerta por 2 min)
                        msg = (
                            f"ALERTA DE SISTEMA: Alta carga de CPU detectada ({cpu}%)"
                        )
                        logger.info(msg)

                        # 1. Dashboard Web
                        emit_log_sync(msg, level="WARNING")

                        # 2. HUD Overlay
                        try:
                            from src.interface.window_manager import get_window_manager

                            # Só tenta acessar se o app Qt estiver rodando
                            from PyQt6.QtWidgets import QApplication

                            if QApplication.instance():
                                wm = get_window_manager()
                                if wm and wm.get_hud():
                                    wm.get_hud().log_event(msg)
                        except BaseException:
                            pass

                        last_alert = now
            except Exception as e:
                logger.debug(f"Erro no monitoramento de hardware: {e}")
                time.sleep(30)

    @property
    def is_throttled(self) -> bool:
        """
        Returns True if the system is under heavy load and should reduce intensity.
        Thresholds: CPU > 85%, RAM < 1.0 GB, or Emergency Mode active.
        """
        try:
            # Check Emergency Mode first (Stark Protocol)
            try:
                if getattr(auto_recovery_system, "is_emergency_mode", False):
                    return True
            except BaseException:
                pass

            import psutil

            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().available / (1024**3)

            throttled = cpu > 85 or ram < 1.0
            if throttled:
                logger.warning(f"⚠️ THROTTLING ACTIVE: CPU={cpu}%, RAM={ram:.1f}GB")
            return throttled
        except BaseException:
            return False

    def get_tier(self) -> str:
        """Retorna o nível de processamento (ULTRA, FAST, BALANCED, LITE)"""
        self._ensure_hardware_initialized()
        return self.tier

    def get_device(self) -> str:
        """Retorna 'cuda' ou 'cpu'"""
        self._ensure_hardware_initialized()
        return self.device

    def get_torch_device(self):
        """Retorna o objeto torch.device atual"""
        self._ensure_hardware_initialized()
        _ensure_torch()
        if TORCH_AVAILABLE and torch:
            # openvino is not a native torch device string
            dev = self.device
            if dev == "openvino":
                dev = "cpu"
            return torch.device(dev)
        return None

    def get_compute_type(self) -> str:
        """Retorna tipo de float mais rápido para o hardware (bfloat16/float16/float32)"""
        self._ensure_hardware_initialized()
        if self.device == "cuda":
            # Verificar suporte a bfloat16 (GPUs Ampere+)
            if TORCH_AVAILABLE and torch and torch.cuda.is_bf16_supported():
                return "bfloat16"
            return "float16"

        # CPUs modernas frequentemente suportam bfloat16 (AVX-512 BF16)
        # Em CPU, float32 ainda é o mais estável para Transformers pura,
        # mas bfloat16 pode ser usado se disponível no torch.
        if TORCH_AVAILABLE and torch:
            # Heurística: se for CPU mas tier for FAST, talvez valha bfloat16
            # mas por segurança contra 0xC0000005, mantemos float32 como
            # fallback
            pass

        return "float32"

    def clear_gpu_cache(self):
        """Limpa cache de memória da GPU e aciona GC"""
        self._ensure_hardware_initialized()
        import gc

        gc.collect()
        _ensure_torch()
        if TORCH_AVAILABLE and torch and self.device == "cuda":
            torch.cuda.empty_cache()
            logger.info("🧹 VRAM Cache limpo com sucesso.")

    @property
    def neural_lock(self):
        """Global lock for heavy model loading"""
        if not hasattr(self, "_neural_lock"):
            self._neural_lock = threading.Lock()
        return self._neural_lock

    def get_memory_status(self) -> Dict[str, float]:
        """Retorna RAM livre (GB) e VRAM livre (GB)"""
        self._ensure_hardware_initialized()
        import psutil

        try:
            ram = psutil.virtual_memory()
            free_ram_gb = ram.available / (1024**3)
        except BaseException:
            free_ram_gb = 0.0

        free_vram_gb = 0.0
        if self.device == "cuda":
            _ensure_torch()
            try:
                # torch.cuda.mem_get_info() retorna (free, total) em bytes
                free, total = torch.cuda.mem_get_info()
                free_vram_gb = free / (1024**3)
            except BaseException:
                pass

        return {
            "ram_free_gb": round(free_ram_gb, 2),
            "vram_free_gb": round(free_vram_gb, 2),
        }

    def get_status(self) -> Dict[str, Any]:
        """Retorna status humano do hardware"""
        self._ensure_hardware_initialized()
        mem = self.get_memory_status()
        _ensure_torch()
        threads = torch.get_num_threads() if (TORCH_AVAILABLE and torch) else 0
        cuda_avail = torch.cuda.is_available() if (TORCH_AVAILABLE and torch) else False

        return {
            "tier": self.tier,
            "device": self.device,
            "accelerator": getattr(self, "accelerator", None),
            "gpu_name": self.gpu_name,
            "threads": threads,
            "cuda": cuda_avail,
            "ram_free_gb": mem["ram_free_gb"],
            "vram_free_gb": mem["vram_free_gb"],
        }

    # =========================================================================
    # SOBERANIA DE HARDWARE (Singularity Edition)
    # =========================================================================

    def get_running_processes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna processos com maior consumo de CPU/RAM"""
        import psutil

        processes = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Ordenar por CPU e pegar top N
        sorted_procs = sorted(processes, key=lambda x: x["cpu_percent"], reverse=True)
        return sorted_procs[:limit]

    def set_process_priority(self, pid: int, level: str) -> bool:
        """Altera a prioridade de um processo (IDLE, BELOW_NORMAL, NORMAL, ABOVE_NORMAL, HIGH, REALTIME)"""
        import psutil

        try:
            p = psutil.Process(pid)
            # Use getattr with default to avoid crashes on non-Windows systems where these constants are missing
            levels = {
                "IDLE": getattr(psutil, "IDLE_PRIORITY_CLASS", 0),
                "BELOW_NORMAL": getattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS", 0),
                "NORMAL": getattr(psutil, "NORMAL_PRIORITY_CLASS", 0),
                "ABOVE_NORMAL": getattr(psutil, "ABOVE_NORMAL_PRIORITY_CLASS", 0),
                "HIGH": getattr(psutil, "HIGH_PRIORITY_CLASS", 0),
                "REALTIME": getattr(psutil, "REALTIME_PRIORITY_CLASS", 0),
            }

            if self.system != "Windows" and level not in ["NORMAL", "IDLE"]:
                # Map Windows priorities to nice values for Linux/Mac
                if level == "HIGH" or level == "REALTIME":
                    p.nice(-10) # Higher priority
                elif level == "ABOVE_NORMAL":
                     p.nice(-5)
                elif level == "BELOW_NORMAL":
                     p.nice(5)
                elif level == "IDLE":
                     p.nice(19) # Lowest priority
                else:
                     p.nice(0)
                logger.info(f"🚀 Prioridade do processo {pid} alterada (Nice value)")
                return True

            if level in levels and self.system == "Windows":
                p.nice(levels[level])
                logger.info(f"🚀 Prioridade do processo {pid} alterada para {level}")
                return True

        except Exception as e:
            logger.error(f"Erro ao alterar prioridade: {e}")
        return False

    def set_power_plan(self, mode: str) -> bool:
        """Altera o plano de energia do Windows (GAMER/HIGH_PERFORMANCE, BALANCED, POWER_SAVER)"""
        if self.system != "Windows":
            return False

        import subprocess

        # GUIDs padrão do Windows
        plans = {
            "GAMER": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",  # High Performance
            "BALANCED": "381b4222-f694-41f0-9685-ff5bb260df2e",
            "POWER_SAVER": "a1841308-3541-4fab-bc81-f71556f20b4a",
        }

        try:
            guid = plans.get(mode.upper())
            if guid:
                subprocess.run(["powercfg", "/setactive", guid], check=True)
                logger.info(f"🔋 Plano de energia alterado para: {mode}")
                return True
        except Exception as e:
            logger.error(f"Erro ao alterar plano de energia: {e}")
        return False

    def suggest_optimizations(self) -> str:
        """Analisa o contexto e sugere otimizações soberanas"""
        status = self.get_status()
        import psutil

        try:
            cpu_usage = psutil.cpu_percent()
        except BaseException:
            cpu_usage = 0

        if cpu_usage > 85:
            return "Sugestão: O sistema está sob carga pesada. Recomendo alterar para o modo 'GAMER/HIGH_PERFORMANCE' e reduzir prioridade de processos em background."
        elif status["ram_free_gb"] < 2.0:
            return "Sugestão: Pouca memória RAM disponível. Recomendo fechar aplicações não essenciais ou limpar cache de VRAM."

        return "Sistema operando em parâmetros ideais."

    def get_heartbeat_report(self) -> Dict[str, Any]:
        """Gera um relatório completo de saúde do sistema (Heartbeat)"""
        import psutil
        import time

        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory()
            ram_percent = ram.percent
        except BaseException:
            cpu = 0
            ram_percent = 0

        # Alertas proativos
        alerts = []
        if cpu > 80:
            alerts.append("Alta carga de processamento")
        if ram_percent > 90:
            alerts.append("Memória RAM quase esgotada")

        status = self.get_status()

        return {
            "timestamp": time.time(),
            "cpu_usage": cpu,
            "ram_usage": ram_percent,
            "alerts": alerts,
            "tier": status["tier"],
            "device": status["device"],
            "vram_free": status["vram_free_gb"],
        }


# Instância global (Singleton) - Lazy initialization
_hardware_manager_instance = None


def get_hardware_manager():
    """Retorna a instância singleton do hardware manager (lazy)"""
    global _hardware_manager_instance
    if _hardware_manager_instance is None:
        _hardware_manager_instance = HardwareManager()
    return _hardware_manager_instance


# Instância global
hardware_manager = get_hardware_manager()
