"""
Gerenciador de Hardware do Jarvis 5.0
Detecta e otimiza o uso de CPU/GPU para todos os módulos de IA.
"""

import logging
import platform
import os
import sys
from typing import Dict, Any, List, Optional

# 🛡️ GLOBAL MONKEY PATCH: Correção Crítica para OpenVINO/Optimum-Intel
try:
    import openvino
    import openvino.runtime
    node_obj = getattr(openvino.runtime, 'Node', None)
    if node_obj:
        if not hasattr(openvino, 'Node'): openvino.Node = node_obj
        if not hasattr(openvino.runtime, 'Node'): openvino.runtime.Node = node_obj
    if hasattr(openvino.runtime, 'op'):
        sys.modules['openvino.op'] = openvino.runtime.op
except Exception:
    pass

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

    # =========================================================================
    # SOBERANIA DE HARDWARE (Singularity Edition)
    # =========================================================================

    def get_running_processes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna processos com maior consumo de CPU/RAM"""
        import psutil
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Ordenar por CPU e pegar top N
        sorted_procs = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)
        return sorted_procs[:limit]

    def set_process_priority(self, pid: int, level: str) -> bool:
        """Altera a prioridade de um processo (IDLE, BELOW_NORMAL, NORMAL, ABOVE_NORMAL, HIGH, REALTIME)"""
        import psutil
        try:
            p = psutil.Process(pid)
            levels = {
                "IDLE": psutil.IDLE_PRIORITY_CLASS,
                "BELOW_NORMAL": psutil.BELOW_NORMAL_PRIORITY_CLASS,
                "NORMAL": psutil.NORMAL_PRIORITY_CLASS,
                "ABOVE_NORMAL": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
                "HIGH": psutil.HIGH_PRIORITY_CLASS,
                "REALTIME": psutil.REALTIME_PRIORITY_CLASS
            }
            if level in levels:
                p.nice(levels[level])
                logger.info(f"🚀 Prioridade do processo {pid} alterada para {level}")
                return True
        except Exception as e:
            logger.error(f"Erro ao alterar prioridade: {e}")
        return False

    def set_power_plan(self, mode: str) -> bool:
        """Altera o plano de energia do Windows (GAMER/HIGH_PERFORMANCE, BALANCED, POWER_SAVER)"""
        if self.system != "Windows": return False
        
        import subprocess
        # GUIDs padrão do Windows
        plans = {
            "GAMER": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c", # High Performance
            "BALANCED": "381b4222-f694-41f0-9685-ff5bb260df2e",
            "POWER_SAVER": "a1841308-3541-4fab-bc81-f71556f20b4a"
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
        cpu_usage = psutil.cpu_percent()
        
        if cpu_usage > 85:
            return "Sugestão: O sistema está sob carga pesada. Recomendo alterar para o modo 'GAMER/HIGH_PERFORMANCE' e reduzir prioridade de processos em background."
        elif status["ram_free_gb"] < 2.0:
            return "Sugestão: Pouca memória RAM disponível. Recomendo fechar aplicações não essenciais ou limpar cache de VRAM."
        
        return "Sistema operando em parâmetros ideais."

# Instância global
hardware_manager = HardwareManager()
