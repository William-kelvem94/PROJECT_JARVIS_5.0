"""
JARVIS 5.0 - Brain Router (Stark IQ Tiers)
==========================================
Sistema de Decisão Inteligente para Roteamento Local vs Nuvem.
Detecta modelos Ollama e escala o QI baseado em hardware (RAM/VRAM).
"""

import logging
import os
import requests
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class PrivacyLevel(Enum):
    PUBLIC = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class LatencyRequirement(Enum):
    ULTRA_LOW = 0.1
    LOW = 0.5
    MODERATE = 2.0
    HIGH = 5.0
    FLEXIBLE = 10.0

class BrainRouter:
    """Roteador inteligente de tarefas entre cérebros local e nuvem"""
    
    def __init__(self):
        self.api_key = os.environ.get('GOOGLE_API_KEY')
        self.local_available = True
        self.cloud_available = True if self.api_key else False
        self.local_load = 0.0  # 0-1
        self.cloud_quota_remaining = 1.0 if self.cloud_available else 0.0
        self.ollama_available_models = []
        
        # Discover Ollama models
        self._discover_ollama_models()
        
        if not self.cloud_available:
            logger.warning("⚠️ BrainRouter: Cloud (Gemini) desativado (Falta API Key).")

    def _discover_ollama_models(self):
        """Detecta quais modelos estão instalados no Ollama localmente"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                self.ollama_available_models = [m['name'] for m in models]
                logger.info(f"Ollama descoberto: {len(self.ollama_available_models)} modelos instalados.")
            else:
                self.ollama_available_models = []
        except Exception:
            self.ollama_available_models = []
            logger.debug("Ollama não está rodando no momento.")

    def choose_brain(
        self,
        task_complexity: float = 0.5,
        privacy_level: PrivacyLevel = PrivacyLevel.MEDIUM,
        latency_requirement: LatencyRequirement = LatencyRequirement.MEDIUM
    ) -> str:
        """
        Versão Stark IQ 11.2 - Escolha adaptativa baseada em Memória e Tiers
        Retorna: 'ollama:<modelo>', 'local' (native), ou 'cloud'
        """
        # PRIVACIDADE CRÍTICA -> NATIVO (Sem rede)
        if privacy_level.value >= PrivacyLevel.HIGH.value:
            return "local"

        # Capturar Hardware em tempo real
        try:
            from src.core.management.hardware_manager import hardware_manager
            mem = hardware_manager.get_memory_status()
            free_ram = mem["ram_free_gb"]
            free_vram = mem["vram_free_gb"]
        except Exception as e:
            logger.warning(f"Erro ao ler hardware info: {e}")
            free_ram, free_vram = 4.0, 0.0

        # ROTEAMENTO OLLAMA (TIERS)
        if self.ollama_available_models:
            # TIER S: Gênio (DeepSeek-R1) -> Alta Complexidade + Recursos Livres
            if task_complexity >= 0.7 and (free_ram > 6.0 or free_vram > 4.0):
                for m in ["deepseek-r1:8b", "deepseek-r1:14b", "deepseek-r1"]:
                    if any(m in name.lower() for name in self.ollama_available_models):
                        return f"ollama:{m}"

            # TIER A: Versátil (Llama 3.1) -> Média-Alta Complexidade
            if task_complexity >= 0.4 and (free_ram > 4.0 or free_vram > 2.0):
                for m in ["llama3.1", "llama3.2", "llama3"]:
                    if any(m in name.lower() for name in self.ollama_available_models):
                        return f"ollama:{m}"
            
            # TIER B: Rápido (Qwen / Phi) -> Uso geral econômico
            if free_ram > 1.5:
                for m in ["qwen2.5:3b", "qwen2.5", "phi3.5", "phi3"]:
                    if any(m in name.lower() for name in self.ollama_available_models):
                        return f"ollama:{m}"

        # ESCALONAMENTO PARA NUVEM (Último recurso para tarefas ultra-complexas)
        if task_complexity > 0.8 and self.cloud_available:
            return "cloud_flash"

        # FALLBACK: Native Micro-LLM (Qwen 0.5B/1.5B)
        return "local"

    def update_status(self, local_load: float = None, cloud_quota: float = None):
        if local_load is not None:
            self.local_load = max(0.0, min(1.0, local_load))
        if cloud_quota is not None:
            self.cloud_quota_remaining = max(0.0, min(1.0, cloud_quota))

# Instância global
brain_router = BrainRouter()
