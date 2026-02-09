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

try:
    from src.utils.config import config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    config = None

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
        
        # Carregar configurações do ai_config.yaml
        if CONFIG_AVAILABLE and config:
            try:
                self.ollama_url = config.get_ai_config('brain_router.ollama_url', 'http://localhost:11434')
                self.ollama_timeout = config.get_ai_config('brain_router.ollama_timeout', 2.0)
                self.tier_ultra = config.get_ai_config('brain_router.ollama_models.tier_ultra', [])
                self.tier_pro = config.get_ai_config('brain_router.ollama_models.tier_pro', [])
                self.tier_fast = config.get_ai_config('brain_router.ollama_models.tier_fast', [])
                self.hw_tier_ultra = config.get_ai_config('brain_router.hardware_requirements.tier_ultra', {})
                self.hw_tier_pro = config.get_ai_config('brain_router.hardware_requirements.tier_pro', {})
                self.hw_tier_fast = config.get_ai_config('brain_router.hardware_requirements.tier_fast', {})
                self.offline_mode = config.get_ai_config('brain_router.offline_mode', False)
                logger.info("✅ BrainRouter: Configurações carregadas de ai_config.yaml")
            except Exception as e:
                logger.warning(f"⚠️ BrainRouter: Erro ao carregar config, usando defaults: {e}")
                self._load_default_config()
        else:
            logger.warning("⚠️ BrainRouter: Config não disponível, usando defaults")
            self._load_default_config()
        
        # Discover Ollama models
        self._discover_ollama_models()
        
        if not self.cloud_available:
            logger.warning("⚠️ BrainRouter: Cloud (Gemini) desativado (Falta API Key).")
    
    def _load_default_config(self):
        """Carrega configurações padrão se ai_config.yaml não estiver disponível"""
        self.ollama_url = 'http://localhost:11434'
        self.ollama_timeout = 2.0
        self.tier_ultra = ["deepseek-r1:8b", "deepseek-r1:14b", "deepseek-r1", "llama3.3:70b"]
        self.tier_pro = ["llama3.3", "llama3.2", "llama3.1", "llama3", "qwen2.5:14b", "qwen2.5:7b"]
        self.tier_fast = ["qwen2.5:3b", "qwen2.5", "phi3.5", "phi3", "mistral", "gemma2:9b"]
        self.hw_tier_ultra = {"min_ram_gb": 6.0, "min_vram_gb": 4.0}
        self.hw_tier_pro = {"min_ram_gb": 4.0, "min_vram_gb": 2.0}
        self.hw_tier_fast = {"min_ram_gb": 1.5, "min_vram_gb": 0.0}
        self.offline_mode = False

    def _discover_ollama_models(self):
        """Detecta quais modelos estão instalados no Ollama localmente"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=self.ollama_timeout)
            if response.status_code == 200:
                models = response.json().get('models', [])
                self.ollama_available_models = [m['name'] for m in models]
                logger.info(f"✅ Ollama: {len(self.ollama_available_models)} modelos instalados.")
            else:
                self.ollama_available_models = []
        except Exception:
            self.ollama_available_models = []
            logger.debug("Ollama não está rodando no momento.")

    def choose_brain(
        self,
        task_complexity: float = 0.5,
        privacy_level: PrivacyLevel = PrivacyLevel.MEDIUM,
        latency_requirement: LatencyRequirement = LatencyRequirement.MODERATE
    ) -> str:
        """
        Versão Stark IQ 11.2 - Escolha adaptativa baseada em Memória e Tiers
        Retorna: 'ollama:<modelo>', 'local' (native), ou 'cloud'
        """
        # MODO OFFLINE: Força uso local
        if self.offline_mode:
            logger.info("🔒 MODO OFFLINE: Forçando uso de recursos locais")
            return self._choose_local_brain()
        
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
            # TIER ULTRA: Gênio (DeepSeek-R1) -> Alta Complexidade + Recursos Livres
            min_ram_ultra = self.hw_tier_ultra.get('min_ram_gb', 6.0)
            min_vram_ultra = self.hw_tier_ultra.get('min_vram_gb', 4.0)
            if task_complexity >= 0.7 and (free_ram > min_ram_ultra or free_vram > min_vram_ultra):
                for model_pattern in self.tier_ultra:
                    for available_model in self.ollama_available_models:
                        if model_pattern in available_model.lower():
                            logger.info(f"🧠 TIER ULTRA: {available_model}")
                            return f"ollama:{model_pattern}"

            # TIER PRO: Versátil (Llama 3.x) -> Média-Alta Complexidade
            min_ram_pro = self.hw_tier_pro.get('min_ram_gb', 4.0)
            min_vram_pro = self.hw_tier_pro.get('min_vram_gb', 2.0)
            if task_complexity >= 0.4 and (free_ram > min_ram_pro or free_vram > min_vram_pro):
                for model_pattern in self.tier_pro:
                    for available_model in self.ollama_available_models:
                        if model_pattern in available_model.lower():
                            logger.info(f"🎯 TIER PRO: {available_model}")
                            return f"ollama:{model_pattern}"
            
            # TIER FAST: Rápido (Qwen / Phi) -> Uso geral econômico
            min_ram_fast = self.hw_tier_fast.get('min_ram_gb', 1.5)
            if free_ram > min_ram_fast:
                for model_pattern in self.tier_fast:
                    for available_model in self.ollama_available_models:
                        if model_pattern in available_model.lower():
                            logger.info(f"⚡ TIER FAST: {available_model}")
                            return f"ollama:{model_pattern}"

        # ESCALONAMENTO PARA NUVEM (Último recurso para tarefas ultra-complexas)
        if task_complexity > 0.8 and self.cloud_available and not self.offline_mode:
            logger.info("☁️ Escalando para Cloud (Gemini)")
            return "cloud_flash"

        # FALLBACK: Native Micro-LLM (Qwen 0.5B/1.5B)
        logger.info("🏠 Usando LocalBrain nativo")
        return "local"
    
    def _choose_local_brain(self) -> str:
        """Escolhe o melhor modelo local disponível (Modo Offline)"""
        if not self.ollama_available_models:
            return "local"
        
        # Tentar tiers em ordem de preferência
        all_tiers = self.tier_ultra + self.tier_pro + self.tier_fast
        
        for model_pattern in all_tiers:
            for available_model in self.ollama_available_models:
                if model_pattern in available_model.lower():
                    logger.info(f"🔒 OFFLINE MODE: Usando {available_model}")
                    return f"ollama:{model_pattern}"
        
        # Se nenhum tier disponível, usar o primeiro modelo encontrado
        if self.ollama_available_models:
            first_model = self.ollama_available_models[0]
            logger.info(f"🔒 OFFLINE MODE: Usando {first_model} (primeiro disponível)")
            return f"ollama:{first_model}"
        
        return "local"
    
    def enable_offline_mode(self):
        """Ativa modo offline - força uso exclusivo de recursos locais"""
        self.offline_mode = True
        self.cloud_available = False
        logger.warning("🔒 MODO OFFLINE ATIVADO")
        logger.info("Usando apenas: LocalBrain + Ollama")
    
    def disable_offline_mode(self):
        """Desativa modo offline"""
        self.offline_mode = False
        self.cloud_available = True if self.api_key else False
        logger.info("🌐 MODO ONLINE ATIVADO")

    def update_status(self, local_load: float = None, cloud_quota: float = None):
        if local_load is not None:
            self.local_load = max(0.0, min(1.0, local_load))
        if cloud_quota is not None:
            self.cloud_quota_remaining = max(0.0, min(1.0, cloud_quota))

# Instância global
brain_router = BrainRouter()
