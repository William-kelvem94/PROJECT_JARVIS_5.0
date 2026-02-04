"""
Gerenciador de Hardware do Jarvis 5.0
Detecta e otimiza o uso de CPU/GPU para todos os módulos de IA.
"""

import logging
import torch
import platform
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

class HardwareManager:
    """Singleton para gerenciar recursos de hardware"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized: return
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.gpu_name = torch.cuda.get_device_name(0) if self.device == "cuda" else "None"
        self.system = platform.system()
        
        # Otimizações globais de performance
        if self.device == "cuda":
            # Habilitar algoritmo de convolução da NVIDIA para performance
            torch.backends.cudnn.benchmark = True
            logger.info(f"JARVIS: Rodando em GPU: {self.gpu_name}")
        else:
            # Otimizar número de threads para CPU se não houver GPU
            # Evita sobrecarregar o sistema com muitas threads em modelos menores
            # Geralmente cpu_count / 2 é um bom ponto de equilíbrio para processos em BG
            import psutil
            cpu_count = psutil.cpu_count(logical=False) or 4
            torch.set_num_threads(max(1, cpu_count // 2))
            logger.info("JARVIS: Rodando em CPU (GPU não detectada ou indisponível).")
            
        self._initialized = True

    def get_device(self) -> str:
        """Retorna 'cuda' ou 'cpu'"""
        return self.device

    def get_torch_device(self):
        """Retorna o objeto torch.device atual"""
        return torch.device(self.device)

    def get_compute_type(self) -> str:
        """Retorna tipo de float mais rápido para o hardware"""
        if self.device == "cuda":
            # float16 é muito mais rápido em GPUs modernas
            return "float16"
        return "float32"

    def get_status(self) -> Dict[str, Any]:
        """Retorna status humano do hardware"""
        return {
            "device": self.device,
            "gpu_name": self.gpu_name,
            "threads_limit": torch.get_num_threads(),
            "cuda_available": torch.cuda.is_available()
        }

# Instância global
hardware_manager = HardwareManager()
