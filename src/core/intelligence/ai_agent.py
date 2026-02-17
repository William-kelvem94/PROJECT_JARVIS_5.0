"""
Orquestrador do Agente de IA
Gerencia interação entre visão (OCR), decisão (LLM) e ação (PyAutoGUI)
"""

import logging
from typing import Dict, Any
from importlib import import_module

# Logger Setup
logger = logging.getLogger(__name__)

class DependencyManager:
    """Gerencia imports condicionais e dependências do sistema"""
    
    def __init__(self):
        self.http_clients = self._setup_http_clients()
        self.core_components = self._setup_core_components()
        
    def _setup_http_clients(self) -> Dict[str, Any]:
        """Configura clientes HTTP com fallback"""
        clients = {}
        try:
            clients['requests'] = import_module('requests')
            clients['aiohttp'] = import_module('aiohttp')
        except ImportError as e:
            logger.warning(f"HTTP client not available: {e}")
            clients['requests'] = None
            clients['aiohttp'] = None
        return clients
    
    def _setup_core_components(self) -> Dict[str, Any]:
        """Configura componentes principais com fallback"""
        components = {}
        
        # UI Signals (Safe Import)
        try:
            from src.interface.ui_signals import ui_signals
            components['ui_signals'] = ui_signals
        except ImportError:
            logger.debug("UI signals not available, using mock")
            components['ui_signals'] = MockSignals()
            
        return components

class MockSignal:
    def emit(self, *args):
        # args is intentionally unused
        pass

class MockSignals:
    update_status = MockSignal()

class AIAgentConfig:
    """Manipula as configurações do agente de forma isolada"""
    
    DEFAULT_SETTINGS = {
        "max_react_turns": 5,
        "screenshot_timeout": 5.0,
        "fallback_model": "gemma2:2b",
        "system_prompt_fallback": "You are JARVIS."
    }
    
    def __init__(self):
        self._load_configuration()
        
    def _load_configuration(self):
        """Carrega configurações com fallback para padrões"""
        try:
            from src.utils.env_manager import get_config
            
            config_obj = get_config()
            ollama_url_base = getattr(config_obj, 'ollama_url', 'http://localhost:11434')
            self.ollama_url = f"{ollama_url_base}/api/generate"
            
            # Use global config if available, otherwise fallback to empty dict
            try:
                from src.utils.config import config
                ai_config_data = getattr(config, 'AI_AGENT_CONFIG', {}) if hasattr(config, 'AI_AGENT_CONFIG') else {}
            except ImportError:
                ai_config_data = {}
            
            for key, default_value in self.DEFAULT_SETTINGS.items():
                clean_key = key.replace('fallback', '')
                setattr(self, clean_key, 
                        ai_config_data.get(f"ai_agent.{key}", default_value))
                
            if not hasattr(self, 'system_prompt'):
                self.system_prompt = self.DEFAULT_SETTINGS["system_prompt_fallback"]
                
        except ImportError as e:
            logger.error(f"Configuration loading failed: {e}")
            # Fallback para valores padrão
            for key, value in self.DEFAULT_SETTINGS.items():
                clean_key = key.replace('fallback', '')
                setattr(self, clean_key, value)
                
class AIAgentModuleLoader:
    """Carrega módulos avançados dinamicamente"""
    
    MODULES_MAP = {
        'advanced_action': ('actions', 'advanced_action_controller'),
        'advanced_speech': ('audio', 'advanced_speech_processor'),
        'workflow': ('actions', 'workflow_engine'),
        'security': ('security', 'security_manager')
    }
    
    @staticmethod
    def load_module(path: str):
        """Carrega um módulo dinamicamente"""
        try:
            module_path, _, class_name = path.rpartition('.')
            mod = import_module(module_path)
            return getattr(mod, class_name)
        except (ImportError, AttributeError) as e:
            logger.debug(f"Module {path} not available: {e}")
            return None
            
class AIAgent:
    """Classe principal do Agente Inteligente"""

CRITICAL_DEPENDENCIES = {
    # Example: "voice_controller": None,
    # Add actual dependency instances or leave as None/placeholders
    "voice_controller": None,
    "vision_enhancer": None,
    "screen_capture": None,
    "action_controller": None,
}

def __init__(self, provider: str = "ollama"):
    """Inicializa o agente com configurações padrão ou personalizadas."""
    self.provider = provider

    # Configurações iniciais centralizadas através da classe dedicada
    self.config = AIAgentConfig()

    # Dependências críticas e modo de segurança
    self.safe_mode = False

    # Histórico e componentes adicionais
    self.chat_history = []

    # Configuração dos módulos avançados em método separado usando o loader dedicado
    self._setup_additional_modules()

def _setup_additional_modules(self):
    """Configura módulos opcionais e avançados."""
    for attr_name, (module_prefix, module_name) in AIAgentModuleLoader.MODULES_MAP.items():
        full_path = f"src.core.{module_prefix}.{module_name}"
        setattr(
            self,
            f"{attr_name}_module",
            AIAgentModuleLoader.load_module(full_path)
        )

# Instâncias globais, se necessário
dependency_manager = DependencyManager()  # Gerenciador centralizado de dependências
ai_instance = AIAgent()  # Singleton pattern implícito mantido