
import logging
import torch
import os
from typing import Dict, Any, List, Optional
import platform

# Provedores de AceleraÃ§Ã£o
try:
    import openvino as ov
    OPENVINO_AVAILABLE = True
except ImportError:
    OPENVINO_AVAILABLE = False

try:
    import onnxruntime as ort
    ORT_AVAILABLE = True
except ImportError:
    ORT_AVAILABLE = False

logger = logging.getLogger(__name__)

class ComputeOrchestrator:
    """Maestro Universal de Hardware - Decide onde rodar cada parte da IA"""
    
    def __init__(self):
        self.available_providers = []
        self._detect_hardware()
        
    def _detect_hardware(self):
        """Varredura real de hardware e capacidades"""
        logger.info("ðŸ“¡ Iniciando varredura universal de hardware...")
        
        # 1. Verificar NVIDIA (CUDA)
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            logger.info(f"âœ… [CUDA] Detectada GPU NVIDIA: {gpu_name}")
            self.available_providers.append({
                "name": "nvidia_cuda",
                "backend": "torch",
                "device": "cuda",
                "score": 100 # Top performance
            })
            
        # 2. Verificar Intel (OpenVINO)
        if OPENVINO_AVAILABLE:
            try:
                core = ov.Core()
                devices = core.available_devices
                logger.info(f"âœ… [OpenVINO] Dispositivos detectados: {devices}")
                if "GPU" in devices:
                    self.available_providers.append({
                        "name": "intel_igpu",
                        "backend": "openvino",
                        "device": "GPU",
                        "score": 80
                    })
                if "CPU" in devices:
                    self.available_providers.append({
                        "name": "intel_cpu",
                        "backend": "openvino",
                        "device": "CPU",
                        "score": 40
                    })
            except Exception as e:
                logger.warning(f"âš ï¸ Erro ao inicializar OpenVINO: {e}")

        # 3. Verificar DirectML (Universal Windows)
        if ORT_AVAILABLE and hasattr(ort, 'get_available_providers'):
            try:
                providers = ort.get_available_providers()
                if 'DmlExecutionProvider' in providers:
                    logger.info("âœ… [DirectML] AceleraÃ§Ã£o universal DirectX 12 disponÃ­vel.")
                    self.available_providers.append({
                        "name": "windows_directml",
                        "backend": "onnx",
                        "device": "DML",
                        "score": 70
                    })
            except Exception as e:
                logger.warning(f"âš ï¸ Erro ao verificar DirectML: {e}")

        # 4. Fallback CPU Otimizada
        self.available_providers.append({
            "name": "generic_cpu",
            "backend": "torch",
            "device": "cpu",
            "score": 10
        })
        
        # Ordenar provedores por score (melhor primeiro)
        self.available_providers.sort(key=lambda x: x["score"], reverse=True)

    def get_best_provider(self, task_type: str = "inference") -> Dict[str, Any]:
        """Retorna o melhor dispositivo disponÃ­vel para uma tarefa especÃ­fica"""
        # Se estivermos em um jogo, podemos querer evitar a GPU principal
        # Futuramente incluiremos lÃ³gica de monitoramento de carga aqui
        return self.available_providers[0]

    def get_execution_strategy(self):
        """Retorna a estratégia de distribuição de carga HETEROGÊNEA"""
        # Exemplo real de estratégia Iris Xe + CPU
        primary = self.get_best_provider()
        
        if primary["name"] == "intel_igpu" and OPENVINO_AVAILABLE:
            return "HETERO:GPU,CPU" 
        
        if primary["name"] == "nvidia_cuda":
            return "cuda"
            
        return "cpu"

    def verify_acceleration(self) -> bool:
        """
        Verifica se a aceleração de hardware (OpenVINO/CUDA) está funcional.
        Se falhar e não houver fallback, retorna False.
        """
        if torch.cuda.is_available():
            return True
            
        if OPENVINO_AVAILABLE:
            try:
                core = ov.Core()
                if "GPU" in core.available_devices or "CPU" in core.available_devices:
                    return True
            except Exception:
                pass
                
        return False

# InstÃ¢ncia global
compute_orchestrator = ComputeOrchestrator()
