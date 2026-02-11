"""
Gerenciador de Hardware do Jarvis 5.0
Detecta e otimiza o uso de CPU/GPU para todos os módulos de IA.
"""

import logging
import platform
import os
from typing import Dict, Any

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

import threading

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
        if self._initialized: return
        with self._lock:
            if self._initialized: return
        
        if TORCH_AVAILABLE and torch and torch.cuda.is_available():
            self.device = "cuda"
            self.accelerator = "cuda"
            self.gpu_name = torch.cuda.get_device_name(0)
        elif OPENVINO_AVAILABLE:
            # Detectar se há uma GPU Intel (Iris Xe / Arc) compatível com OpenVINO
            try:
                core = ov.Core()
                devices = core.available_devices
                if "GPU" in devices:
                    self.device = "cpu" # Torch device string (cpu/cuda). OpenVINO acts as a compiler/accelerator on top of CPU.
                    self.accelerator = "openvino"
                    self.gpu_name = "Intel Iris Xe / Arc (OpenVINO Accelerator)"
                else:
                    self.device = "cpu"
                    self.accelerator = None
                    self.gpu_name = "None"
            except:
                self.device = "cpu"
                self.accelerator = None
                self.gpu_name = "None"
        else:
            self.device = "cpu"
            self.accelerator = None
            self.gpu_name = "None"
        self.system = platform.system()
        
        # 🆕 COMPUTE TIERING (Military Grade Scaling)
        self.tier = "BALANCED"
        if self.device == "cuda" or (hasattr(self, 'accelerator') and self.accelerator == "openvino"):
            self.tier = "ULTRA"
        else:
            import psutil
            logical_cores = psutil.cpu_count(logical=True) or 4
            physical_cores = psutil.cpu_count(logical=False) or 2
            
            if logical_cores >= 12: self.tier = "FAST"
            elif logical_cores >= 6: self.tier = "BALANCED"
            else: self.tier = "LITE"

        if TORCH_AVAILABLE and torch and self.device == "cuda":
            torch.backends.cudnn.benchmark = True
            logger.info(f"🏛️ JARVIS [ULTRA]: Rodando em GPU: {self.gpu_name}")
        else:
            import psutil
            logical_cores = psutil.cpu_count(logical=True) or 4
            
            # ADAPTIVE THREADING: Unlock full potential while preserving GUI responsiveness
            # Previous "Safe Mode" capped at 1 thread or half cores. 
            # New Staged Boot Protocol allows us to be more aggressive.
            
            if self.tier == "FAST":
                threads = logical_cores
            elif self.tier == "BALANCED":
                threads = max(1, logical_cores - 2) # Leave 2 threads for GUI/OS
            else:
                threads = max(1, logical_cores // 2) # LITE mode still conservative
            
            if TORCH_AVAILABLE and torch:
                torch.set_num_threads(threads)
                
            logger.info(f"🏛️ JARVIS [{self.tier}]: Rodando em CPU ({threads} threads ativas / {logical_cores} totais).")
            
        self._start_monitoring_thread()
        self._initialized = True

    def _start_monitoring_thread(self):
        """Inicia monitoramento em background para alertas proativos"""
        thread = threading.Thread(target=self._monitoring_loop, daemon=True, name="HardwareProactiveMonitor")
        thread.start()

    def _monitoring_loop(self):
        """Loop de monitoramento contínuo (Phase 3)"""
        import psutil
        import time
        from src.utils.web_emitter import emit_log_sync
        
        last_alert = 0
        while True:
            try:
                cpu = psutil.cpu_percent(interval=10) # Verifica a cada 10s
                
                if cpu > 90:
                    now = time.time()
                    if now - last_alert > 60: # Evitar spam (1 alerta por minuto max)
                        msg = f"ALERTA DE SISTEMA: Sobrecarga Crítica detectada ({cpu}%)"
                        logger.warning(msg)
                        
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
                        except: pass
                        
                        last_alert = now
            except Exception as e:
                logger.debug(f"Erro no monitoramento de hardware: {e}")
                time.sleep(30)

    def get_tier(self) -> str:
        """Retorna o nível de processamento (ULTRA, FAST, BALANCED, LITE)"""
        return self.tier

    def get_device(self) -> str:
        """Retorna 'cuda' ou 'cpu'"""
        return self.device

    def get_torch_device(self):
        """Retorna o objeto torch.device atual"""
        if TORCH_AVAILABLE and torch:
            # openvino is not a native torch device string
            dev = self.device
            if dev == "openvino":
                dev = "cpu"
            return torch.device(dev)
        return None

    def get_compute_type(self) -> str:
        """Retorna tipo de float mais rápido para o hardware (bfloat16/float16/float32)"""
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
             # mas por segurança contra 0xC0000005, mantemos float32 como fallback
             pass

        return "float32"

    def clear_gpu_cache(self):
        """Limpa cache de memória da GPU e aciona GC"""
        import gc
        gc.collect()
        if TORCH_AVAILABLE and torch and self.device == "cuda":
            torch.cuda.empty_cache()
            logger.info("🧹 VRAM Cache limpo com sucesso.")

    @property
    def neural_lock(self):
        """Global lock for heavy model loading"""
        if not hasattr(self, '_neural_lock'):
             self._neural_lock = threading.Lock()
        return self._neural_lock

    def get_memory_status(self) -> Dict[str, float]:
        """Retorna RAM livre (GB) e VRAM livre (GB)"""
        import psutil
        ram = psutil.virtual_memory()
        free_ram_gb = ram.available / (1024**3)
        
        free_vram_gb = 0.0
        if self.device == "cuda":
            # torch.cuda.mem_get_info() retorna (free, total) em bytes
            free, total = torch.cuda.mem_get_info()
            free_vram_gb = free / (1024**3)
            
        return {
            "ram_free_gb": round(free_ram_gb, 2),
            "vram_free_gb": round(free_vram_gb, 2)
        }

    def get_status(self) -> Dict[str, Any]:
        """Retorna status humano do hardware"""
        mem = self.get_memory_status()
        threads = torch.get_num_threads() if (TORCH_AVAILABLE and torch) else 0
        cuda_avail = torch.cuda.is_available() if (TORCH_AVAILABLE and torch) else False
        
        return {
            "tier": self.tier,
            "device": self.device,
            "accelerator": getattr(self, 'accelerator', None),
            "gpu_name": self.gpu_name,
            "threads": threads,
            "cuda": cuda_avail,
            "ram_free_gb": mem["ram_free_gb"],
            "vram_free_gb": mem["vram_free_gb"]
        }

# Instância global
hardware_manager = HardwareManager()
