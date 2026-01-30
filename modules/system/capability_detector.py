"""
Detector de Capacidades do Sistema
Auto-detecta GPU, CPU, RAM e ajusta configurações automaticamente
"""

import platform
import psutil
from typing import Dict, Any, Optional
from core.logger import logger

try:
    import GPUtil
    GPUTIL_AVAILABLE = True
except ImportError:
    GPUTIL_AVAILABLE = False
    logger.debug("GPUtil não disponível para detecção de GPU NVIDIA")

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.debug("PyTorch não disponível")

class CapabilityDetector:
    """
    Detecta capacidades do hardware e sugere configurações.
    """
    
    def __init__(self):
        self.capabilities = {}
        self._detect_all()
        logger.info("CapabilityDetector inicializado")
    
    def _detect_all(self):
        """Detecta todas as capacidades do sistema."""
        self.capabilities = {
            "cpu": self._detect_cpu(),
            "memory": self._detect_memory(),
            "gpu": self._detect_gpu(),
            "storage": self._detect_storage(),
            "os": self._detect_os()
        }
        
        # Calcular score geral
        self.capabilities["overall_score"] = self._calculate_score()
        
        # Sugerir modelo LLM
        self.capabilities["recommended_model"] = self._recommend_model()
    
    def _detect_cpu(self) -> Dict[str, Any]:
        """Detecta informações da CPU."""
        try:
            cpu_count = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                "cores": cpu_count,
                "frequency_mhz": cpu_freq.current if cpu_freq else None,
                "usage_percent": cpu_percent,
                "platform": platform.processor(),
                "architecture": platform.machine()
            }
        except Exception as e:
            logger.error(f"Erro ao detectar CPU: {e}")
            return {"error": str(e)}
    
    def _detect_memory(self) -> Dict[str, Any]:
        """Detecta informações de memória."""
        try:
            memory = psutil.virtual_memory()
            
            return {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "used_gb": memory.used / (1024**3),
                "percent": memory.percent
            }
        except Exception as e:
            logger.error(f"Erro ao detectar memória: {e}")
            return {"error": str(e)}
    
    def _detect_gpu(self) -> Dict[str, Any]:
        """Detecta informações de GPU."""
        gpu_info = {
            "available": False,
            "cuda_available": False,
            "type": None,
            "count": 0,
            "details": []
        }
        
        # Detectar CUDA (NVIDIA)
        if TORCH_AVAILABLE:
            try:
                if torch.cuda.is_available():
                    gpu_info["cuda_available"] = True
                    gpu_info["count"] = torch.cuda.device_count()
                    gpu_info["type"] = "NVIDIA CUDA"
                    
                    for i in range(torch.cuda.device_count()):
                        gpu_info["details"].append({
                            "id": i,
                            "name": torch.cuda.get_device_name(i),
                            "memory_total": torch.cuda.get_device_properties(i).total_memory / (1024**3),
                        })
            except Exception:
                pass
        
        # Detectar GPU via GPUtil (NVIDIA)
        if GPUTIL_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_info["available"] = True
                    if not gpu_info["type"]:
                        gpu_info["type"] = "NVIDIA"
                    gpu_info["count"] = len(gpus)
                    
                    for gpu in gpus:
                        gpu_info["details"].append({
                            "id": gpu.id,
                            "name": gpu.name,
                            "memory_total": gpu.memoryTotal,
                            "memory_free": gpu.memoryFree,
                            "memory_used": gpu.memoryUsed,
                            "load": gpu.load * 100
                        })
            except Exception as e:
                logger.debug(f"Erro ao detectar GPU via GPUtil: {e}")
        
        # Detectar AMD ROCm (futuro)
        # TODO: Implementar detecção de ROCm
        
        return gpu_info
    
    def _detect_storage(self) -> Dict[str, Any]:
        """Detecta informações de armazenamento."""
        try:
            disk = psutil.disk_usage('/')
            
            return {
                "total_gb": disk.total / (1024**3),
                "used_gb": disk.used / (1024**3),
                "free_gb": disk.free / (1024**3),
                "percent": disk.percent
            }
        except Exception as e:
            logger.error(f"Erro ao detectar armazenamento: {e}")
            return {"error": str(e)}
    
    def _detect_os(self) -> Dict[str, Any]:
        """Detecta informações do sistema operacional."""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.machine()
        }
    
    def _calculate_score(self) -> float:
        """
        Calcula um score geral do sistema (0.0 a 1.0).
        Baseado em CPU, RAM e GPU.
        """
        score = 0.0
        
        # Score de CPU (máx 0.3)
        cpu_info = self.capabilities.get("cpu", {})
        cpu_cores = cpu_info.get("cores", 0)
        if cpu_cores >= 16:
            score += 0.3
        elif cpu_cores >= 8:
            score += 0.2
        elif cpu_cores >= 4:
            score += 0.1
        
        # Score de RAM (máx 0.3)
        memory_info = self.capabilities.get("memory", {})
        memory_total = memory_info.get("total_gb", 0)
        if memory_total >= 32:
            score += 0.3
        elif memory_total >= 16:
            score += 0.2
        elif memory_total >= 8:
            score += 0.1
        
        # Score de GPU (máx 0.4)
        gpu_info = self.capabilities.get("gpu", {})
        if gpu_info.get("cuda_available"):
            score += 0.4
        elif gpu_info.get("available"):
            score += 0.3
        
        return min(1.0, score)
    
    def _recommend_model(self) -> Dict[str, Any]:
        """
        Recomenda modelo LLM baseado nas capacidades.
        
        Returns:
            Dicionário com recomendação
        """
        memory_total = self.capabilities.get("memory", {}).get("total_gb", 0)
        gpu_available = self.capabilities.get("gpu", {}).get("cuda_available", False)
        cpu_cores = self.capabilities.get("cpu", {}).get("cores", 0)
        
        if gpu_available and memory_total >= 16:
            # Sistema robusto com GPU
            return {
                "model": "llama3:70b",
                "reason": "GPU disponível e RAM suficiente para modelo grande",
                "size": "large"
            }
        elif memory_total >= 16:
            # RAM boa, mas sem GPU
            return {
                "model": "llama3:13b",
                "reason": "RAM suficiente, mas sem GPU - modelo médio recomendado",
                "size": "medium"
            }
        elif memory_total >= 8:
            # RAM moderada
            return {
                "model": "llama3:8b",
                "reason": "RAM moderada - modelo pequeno recomendado",
                "size": "small"
            }
        else:
            # RAM limitada
            return {
                "model": "phi3:mini",
                "reason": "RAM limitada - modelo muito pequeno recomendado",
                "size": "tiny"
            }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Retorna todas as capacidades detectadas."""
        return self.capabilities.copy()
    
    def get_summary(self) -> str:
        """Retorna resumo textual das capacidades."""
        cpu = self.capabilities.get("cpu", {})
        memory = self.capabilities.get("memory", {})
        gpu = self.capabilities.get("gpu", {})
        recommended = self.capabilities.get("recommended_model", {})
        
        summary = f"""
 Capabilities Detected:

 CPU: {cpu.get('cores', 'N/A')} cores
🧠 RAM: {memory.get('total_gb', 0):.1f} GB total, {memory.get('available_gb', 0):.1f} GB disponível
 GPU: {' CUDA disponível' if gpu.get('cuda_available') else ' Sem GPU'}
 Score: {self.capabilities.get('overall_score', 0):.1%}
🤖 Modelo Recomendado: {recommended.get('model', 'N/A')} ({recommended.get('reason', '')})
        """
        return summary.strip()

