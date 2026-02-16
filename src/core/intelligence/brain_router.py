"""
JARVIS 5.0 - Brain Router (Stark IQ Tiers)
==========================================
Sistema de DecisÃ£o Inteligente para Roteamento Local vs Nuvem.
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

try:
    from src.utils.env_manager import get_config
    ENV_MANAGER_AVAILABLE = True
except ImportError:
    ENV_MANAGER_AVAILABLE = False

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
    """Roteador inteligente de tarefas entre cÃ©rebros local e nuvem"""
    
    def __init__(self):
        self.api_key = os.environ.get('GOOGLE_API_KEY')
        self.local_available = True
        self.cloud_available = True 
        self.local_load = 0.0  # 0-1
        self.cloud_quota_remaining = 0.0
        self.ollama_available_models = []
        self._is_online = True
        self._last_conn_check = 0
        self._last_model_check = 0
        self.discovery_interval = 60  # Recarregar lista de modelos a cada 60s
        
        # Carregar configuraÃ§Ãµes do ai_config.yaml
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
                logger.info("âœ… BrainRouter: ConfiguraÃ§Ãµes carregadas de ai_config.yaml")
            except Exception as e:
                logger.warning(f"âš ï¸ BrainRouter: Erro ao carregar config, usando defaults: {e}")
                self._load_default_config()
        else:
            logger.warning("âš ï¸ BrainRouter: Config nÃ£o disponÃ­vel, usando defaults")
            self._load_default_config()
        
        # Discover Ollama models
        self._discover_ollama_models()
        
        self.cloud_available = self._check_cloud_availability()
        logger.info(f"âœ… BrainRouter: Cloud integration initialized (Available: {self.cloud_available})")
    
    def _load_default_config(self):
        """Carrega configuraÃ§Ãµes padrÃ£o se ai_config.yaml nÃ£o estiver disponÃ­vel"""
        self.ollama_url = 'http://localhost:11434'
        self.ollama_timeout = 2.0
        
        # ðŸ†• FASE 2: Tiers otimizados para 16GB RAM com quantizaÃ§Ã£o GGUF
        # tier_ultra: Especialista Pesado (8B-14B) - Tarefas complexas
        self.tier_ultra = ["deepseek-r1:8b", "deepseek-r1:14b", "llama3.3:70b"]
        
        # tier_pro: Especialista MÃ©dio (7B-8B) - Tarefas versÃ¡teis
        self.tier_pro = ["llama3.1:8b", "llama3.3:8b", "qwen2.5:7b", "mistral:7b"]
        
        # tier_fast: Sentinela (1.5B-3B) - Respostas rÃ¡pidas e cache
        self.tier_fast = ["qwen2.5:3b", "qwen2.5:1.5b", "llama3.2:3b", "phi3.5", "gemma2:2b"]
        
        import psutil
        ram_percent = psutil.virtual_memory().percent
        # Se RAM estiver cheia (>75%), descarta modelos imediatamente (0).
        # Se tiver sobra, mantÃ©m por 5 minutos ("5m") para resposta rÃ¡pida.
        self.dynamic_keep_alive = 0 if ram_percent > 75 else "5m"
        
        # ðŸ†• FASE 2: Thresholds de RAM + Keep-Alive DinÃ¢mico
        self.hw_tier_ultra = {"min_ram_gb": 10.0, "min_vram_gb": 4.0, "keep_alive": self.dynamic_keep_alive}  # DinÃ¢mico
        self.hw_tier_pro = {"min_ram_gb": 6.0, "min_vram_gb": 2.0, "keep_alive": 0}     # Descarte imediato
        self.hw_tier_fast = {"min_ram_gb": 2.0, "min_vram_gb": 0.0, "keep_alive": "15m"}  # Cache 15min
        
        self.offline_mode = False
        
        # ðŸ†• FASE 2: Callback para UX Masking
        self.on_heavy_model_loading = None


    def _discover_ollama_models(self):
        """Detecta quais modelos estÃ£o instalados no Ollama localmente"""
        try:
            # Aumentar timeout para descoberta inicial
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5.0)  # 5 segundos
            if response.status_code == 200:
                models = response.json().get('models', [])
                self.ollama_available_models = [m['name'] for m in models]
                logger.info(f"âœ… Ollama: {len(self.ollama_available_models)} modelos instalados.")
            else:
                self.ollama_available_models = []
                logger.warning(f"âš ï¸ Ollama respondeu com status {response.status_code}")
        except requests.exceptions.Timeout:
            self.ollama_available_models = []
            logger.warning("âš ï¸ Ollama nÃ£o respondeu dentro do timeout (5s) - serÃ¡ detectado posteriormente")
        except requests.exceptions.ConnectionError:
            self.ollama_available_models = []
            logger.warning("âš ï¸ Ollama nÃ£o estÃ¡ acessÃ­vel - serÃ¡ detectado posteriormente")
        except Exception as e:
            self.ollama_available_models = []
            logger.warning(f"âš ï¸ Erro ao detectar modelos Ollama: {e}")
        except Exception:
            self.ollama_available_models = []
            logger.debug("Ollama nÃ£o estÃ¡ rodando no momento.")


    def choose_brain(
        self,
        task_complexity: float = 0.5,
        privacy_level: PrivacyLevel = PrivacyLevel.MEDIUM,
        latency_requirement: LatencyRequirement = LatencyRequirement.MODERATE
    ) -> dict:
        """
        VersÃ£o Stark IQ 11.2 - Escolha adaptativa baseada em MemÃ³ria e Tiers
        Retorna: {'brain': 'ollama:<modelo>'|'local'|'cloud', 'keep_alive': 0|'15m', 'is_heavy': bool}
        """
        # Periodic Re-discovery of models (perfeito para downloads em background)
        import time
        if time.time() - self._last_model_check > self.discovery_interval:
            self._discover_ollama_models()
            self._last_model_check = time.time()

        # MODO OFFLINE FORÃ‡ADO OU SEM INTERNET: ForÃ§a uso local
        if self.offline_mode or not self.check_connectivity():
            if self.offline_mode:
                logger.debug("ðŸ”’ Modo Offline ForÃ§ado (Config)")
            else:
                logger.info("ðŸ“¡ Sem internet: Usando recursos locais")
            return self._choose_local_brain()
        
        # PRIVACIDADE CRÃTICA -> NATIVO (Sem rede)
        if privacy_level.value >= PrivacyLevel.HIGH.value:
            return {"brain": "local", "keep_alive": "15m", "is_heavy": False}

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
            # TIER ULTRA: GÃªnio (DeepSeek-R1) -> Alta Complexidade + Recursos Livres
            min_ram_ultra = self.hw_tier_ultra.get('min_ram_gb', 10.0)
            min_vram_ultra = self.hw_tier_ultra.get('min_vram_gb', 4.0)
            if task_complexity >= 0.7 and (free_ram > min_ram_ultra or free_vram > min_vram_ultra):
                for model_pattern in self.tier_ultra:
                    for available_model in self.ollama_available_models:
                        if model_pattern in available_model.lower():
                            logger.info(f"ðŸ§  TIER ULTRA: {available_model}")
                            # ðŸ†• FASE 2: UX Masking para modelo pesado
                            if self.on_heavy_model_loading:
                                self.on_heavy_model_loading(
                                    "Isso Ã© um pouco mais complexo, senhor. "
                                    "Deixe-me alocar mais recursos para analisar..."
                                )
                            return {
                                "brain": f"ollama:{available_model}",
                                "keep_alive": self.hw_tier_ultra.get('keep_alive', 0),
                                "is_heavy": True
                            }

            # TIER PRO: VersÃ¡til (Llama 3.x) -> MÃ©dia-Alta Complexidade
            min_ram_pro = self.hw_tier_pro.get('min_ram_gb', 6.0)
            min_vram_pro = self.hw_tier_pro.get('min_vram_gb', 2.0)
            if task_complexity >= 0.4 and (free_ram > min_ram_pro or free_vram > min_vram_pro):
                for model_pattern in self.tier_pro:
                    for available_model in self.ollama_available_models:
                        if model_pattern in available_model.lower():
                            logger.info(f"ðŸŽ¯ TIER PRO: {available_model}")
                            # ðŸ†• FASE 2: UX Masking para modelo pesado
                            if self.on_heavy_model_loading:
                                self.on_heavy_model_loading(
                                    "Analisando com recursos avanÃ§ados, senhor..."
                                )
                            return {
                                "brain": f"ollama:{available_model}",
                                "keep_alive": self.hw_tier_pro.get('keep_alive', 0),
                                "is_heavy": True
                            }
            
            
            # TIER FAST: RÃ¡pido (Qwen / Phi) -> Uso geral econÃ´mico
            min_ram_fast = self.hw_tier_fast.get('min_ram_gb', 2.0)
            if free_ram > min_ram_fast:
                for model_pattern in self.tier_fast:
                    for available_model in self.ollama_available_models:
                        if model_pattern in available_model.lower():
                            logger.info(f"âš¡ TIER FAST: {available_model}")
                            return {
                                "brain": f"ollama:{available_model}",
                                "keep_alive": self.hw_tier_fast.get('keep_alive', "15m"),
                                "is_heavy": False
                            }

        # CLOUD ESCALATION: Se local nÃ£o for suficiente e internet disponÃ­vel
        if self.cloud_available and task_complexity >= 0.8:
            cloud_tier = "tier_ultra" if task_complexity >= 0.9 else "tier_pro"
            cloud_models = config.get_ai_config(f'brain_router.cloud_models.{cloud_tier}', []) if CONFIG_AVAILABLE else []
            
            if cloud_models:
                # Filtrar Gemini (SeguranÃ§a redundante)
                safe_models = [m for m in cloud_models if "gemini" not in m.lower()]
                if safe_models:
                    model = safe_models[0]
                    logger.info(f"â˜ï¸ CLOUD ESCALATION ({cloud_tier}): {model}")
                    return {"brain": f"cloud:{model}", "keep_alive": 0, "is_heavy": True}


        # FALLBACK: Native Micro-LLM (Qwen 0.5B/1.5B)
        logger.info("ðŸ  Usando LocalBrain nativo")
        return {"brain": "local", "keep_alive": "15m", "is_heavy": False}
    
    
    def _choose_local_brain(self) -> str:
        """Escolhe o melhor modelo local disponÃ­vel (Modo Offline)"""
        if not self.ollama_available_models:
            return "local"
        
        # Tentar tiers em ordem de preferÃªncia
        all_tiers = self.tier_ultra + self.tier_pro + self.tier_fast
        
        for model_pattern in all_tiers:
            for available_model in self.ollama_available_models:
                if model_pattern in available_model.lower():
                    logger.info(f"ðŸ”’ OFFLINE MODE: Usando {available_model}")
                    return f"ollama:{available_model}"
        
        # Se nenhum tier disponÃ­vel, usar o primeiro modelo encontrado
        if self.ollama_available_models:
            first_model = self.ollama_available_models[0]
            logger.info(f"ðŸ”’ OFFLINE MODE: Usando {first_model} (primeiro disponÃ­vel)")
            return f"ollama:{first_model}"
        
        return "local"
    
    def enable_offline_mode(self):
        """Ativa modo offline - forÃ§a uso exclusivo de recursos locais"""
        self.offline_mode = True
        self.cloud_available = False
        logger.warning("ðŸ”’ MODO OFFLINE ATIVADO")
        logger.info("Usando apenas: LocalBrain + Ollama")
    
    def disable_offline_mode(self):
        """Desativa modo offline"""
        self.offline_mode = False
        self.cloud_available = self._check_cloud_availability()
        logger.info(f"ðŸŒ MODO ONLINE ATIVADO (Cloud Available: {self.cloud_available})")

    def check_connectivity(self) -> bool:
        """Verifica conexÃ£o com a internet (cache de 30s)"""
        import time
        import socket
        
        now = time.time()
        if now - self._last_conn_check < 30:
            return self._is_online
            
        self._last_conn_check = now
        try:
            # Tentar conectar ao DNS do Google
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            self._is_online = True
        except (OSError, socket.timeout):
            self._is_online = False
            
        return self._is_online

    def _check_cloud_availability(self) -> bool:
        """Verifica se existem provedores de nuvem ativos (Exceto Gemini)"""
        if not CONFIG_AVAILABLE: return False
        
        # Verificar DeepSeek (exemplo de outro provedor)
        ds_key = os.environ.get('DEEPSEEK_API_KEY')
        if ds_key: return True
        
        # Verificar outros provedores genÃ©ricos se configurados
        return False

    def update_status(self, local_load: float = None, cloud_quota: float = None):
        if local_load is not None:
            self.local_load = max(0.0, min(1.0, local_load))
        if cloud_quota is not None:
            self.cloud_quota_remaining = max(0.0, min(1.0, cloud_quota))

# InstÃ¢ncia global
brain_router = BrainRouter()
