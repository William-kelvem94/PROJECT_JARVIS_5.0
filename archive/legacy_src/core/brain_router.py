"""
Sistema de Decisão Inteligente para Roteamento Local vs Nuvem
Decide automaticamente onde processar cada tarefa baseado em:
- Complexidade da tarefa
- Nível de privacidade requerido
- Requisitos de latência
- Disponibilidade de recursos
"""

import logging
from typing import Dict, Any, Literal
from enum import Enum

logger = logging.getLogger(__name__)

class TaskComplexity(Enum):
    """Níveis de complexidade de tarefas"""
    TRIVIAL = 0.1      # Comandos simples, UI detection
    SIMPLE = 0.3       # OCR básico, classificação
    MODERATE = 0.5     # Análise de contexto, NLU
    COMPLEX = 0.7      # Raciocínio multi-step
    ADVANCED = 0.9     # Análise profunda, criação

class PrivacyLevel(Enum):
    """Níveis de privacidade"""
    PUBLIC = 0         # Pode ir para nuvem
    LOW = 1            # Preferência local mas aceita nuvem
    MEDIUM = 2         # Apenas local exceto se crítico
    HIGH = 3           # Sempre local
    CRITICAL = 4       # Local + criptografia

class LatencyRequirement(Enum):
    """Requisitos de latência"""
    ULTRA_LOW = 0.1    # <100ms (UI responsiveness)
    LOW = 0.5          # <500ms (conversação)
    MODERATE = 2.0     # <2s (análise)
    HIGH = 5.0         # <5s (processamento complexo)
    FLEXIBLE = 10.0    # >5s (background tasks)

class BrainRouter:
    """Roteador inteligente de tarefas entre cérebros local e nuvem"""
    
    def __init__(self):
        self.local_available = True
        self.cloud_available = True
        self.local_load = 0.0  # 0-1
        self.cloud_quota_remaining = 1.0  # 0-1
        
    def choose_brain(
        self,
        task_complexity: float,
        privacy_level: PrivacyLevel,
        latency_requirement: LatencyRequirement,
        task_type: str = "general"
    ) -> Literal["local", "cloud_flash", "cloud_pro", "hybrid"]:
        """
        Decide qual cérebro usar para processar a tarefa
        
        Returns:
            - "local": Qwen local (CPU/GPU)
            - "cloud_flash": Gemini Flash (rápido, barato)
            - "cloud_pro": Gemini Pro / Claude (preciso, caro)
            - "hybrid": Combina local + nuvem
        """
        
        # REGRA 1: Privacidade alta = sempre local
        if privacy_level.value >= PrivacyLevel.HIGH.value:
            logger.info(f"🔒 Roteamento: LOCAL (privacidade alta)")
            return "local"
        
        # REGRA 2: Latência ultra-baixa = sempre local
        if latency_requirement.value <= LatencyRequirement.ULTRA_LOW.value:
            logger.info(f"⚡ Roteamento: LOCAL (latência crítica)")
            return "local"
        
        # REGRA 3: Complexidade muito alta + latência flexível = nuvem pro
        if task_complexity > 0.8 and latency_requirement.value >= LatencyRequirement.MODERATE.value:
            if self.cloud_available and self.cloud_quota_remaining > 0.1:
                logger.info(f"🧠 Roteamento: CLOUD_PRO (complexidade alta)")
                return "cloud_pro"
        
        # REGRA 4: Complexidade moderada + latência ok = nuvem flash
        if task_complexity > 0.4 and latency_requirement.value >= LatencyRequirement.LOW.value:
            if self.cloud_available and self.cloud_quota_remaining > 0.3:
                logger.info(f"☁️ Roteamento: CLOUD_FLASH (balanceado)")
                return "cloud_flash"
        
        # REGRA 5: Local sobrecarregado = nuvem
        if self.local_load > 0.8 and self.cloud_available:
            logger.info(f"📊 Roteamento: CLOUD_FLASH (local sobrecarregado)")
            return "cloud_flash"
        
        # REGRA 6: Tarefas específicas otimizadas
        if task_type == "vision" and task_complexity > 0.6:
            # Visão complexa = híbrido (local filtra, nuvem analisa)
            logger.info(f"👁️ Roteamento: HYBRID (visão complexa)")
            return "hybrid"
        
        # PADRÃO: Local para tudo que não se encaixa acima
        logger.info(f"💻 Roteamento: LOCAL (padrão)")
        return "local"
    
    def update_status(self, local_load: float = None, cloud_quota: float = None):
        """Atualiza status dos recursos disponíveis"""
        if local_load is not None:
            self.local_load = max(0.0, min(1.0, local_load))
        if cloud_quota is not None:
            self.cloud_quota_remaining = max(0.0, min(1.0, cloud_quota))
    
    def get_recommended_model(self, brain_choice: str) -> str:
        """Retorna o modelo recomendado para cada tipo de cérebro"""
        models = {
            "local": "Qwen/Qwen2.5-0.5B-Instruct",
            "cloud_flash": "gemini-2.0-flash-exp",
            "cloud_pro": "gemini-exp-1206",
            "hybrid": "local+gemini-flash"
        }
        return models.get(brain_choice, "local")


# Instância global
brain_router = BrainRouter()


# Exemplos de uso
if __name__ == "__main__":
    router = BrainRouter()
    
    # Teste 1: Comando simples
    choice = router.choose_brain(
        task_complexity=0.2,
        privacy_level=PrivacyLevel.PUBLIC,
        latency_requirement=LatencyRequirement.ULTRA_LOW
    )
    print(f"Comando simples → {choice}")
    
    # Teste 2: Análise de documento sensível
    choice = router.choose_brain(
        task_complexity=0.6,
        privacy_level=PrivacyLevel.HIGH,
        latency_requirement=LatencyRequirement.MODERATE
    )
    print(f"Documento sensível → {choice}")
    
    # Teste 3: Raciocínio complexo
    choice = router.choose_brain(
        task_complexity=0.9,
        privacy_level=PrivacyLevel.LOW,
        latency_requirement=LatencyRequirement.FLEXIBLE
    )
    print(f"Raciocínio complexo → {choice}")
    
    # Teste 4: Visão complexa
    choice = router.choose_brain(
        task_complexity=0.7,
        privacy_level=PrivacyLevel.MEDIUM,
        latency_requirement=LatencyRequirement.MODERATE,
        task_type="vision"
    )
    print(f"Visão complexa → {choice}")
