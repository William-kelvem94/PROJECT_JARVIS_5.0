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
        
        if TORCH_AVAILABLE and torch:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.gpu_name = torch.cuda.get_device_name(0) if self.device == "cuda" else "None"
        else:
            self.device = "cpu"
            self.gpu_name = "None"
        self.system = platform.system()
        
        # 🆕 COMPUTE TIERING (Military Grade Scaling)
        self.tier = "BALANCED"
        if self.device == "cuda":
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
            
        self._initialized = True

    def get_tier(self) -> str:
        """Retorna o nível de processamento (ULTRA, FAST, BALANCED, LITE)"""
        return self.tier

    def get_device(self) -> str:
        """Retorna 'cuda' ou 'cpu'"""
        return self.device

    def get_torch_device(self):
        """Retorna o objeto torch.device atual"""
        if TORCH_AVAILABLE and torch:
            return torch.device(self.device)
        return None

    def get_compute_type(self) -> str:
        """Retorna tipo de float mais rápido para o hardware (float16/int8)"""
        if self.device == "cuda":
            return "float16"
        # 🆕 SYSTEM STABILITY: Force float32 on CPU prevents 0xC0000005 Access Violation
        # caused by int8 quantization on unsupported instruction sets (AVX512_VNNI missing).
        # if self.tier in ["BALANCED", "LITE"]:
        #    return "int8"
        return "float32"

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
            "gpu_name": self.gpu_name,
            "threads": threads,
            "cuda": cuda_avail,
            "ram_free_gb": mem["ram_free_gb"],
            "vram_free_gb": mem["vram_free_gb"]
        }

# Instância global
hardware_manager = HardwareManager()
