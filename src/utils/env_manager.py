"""
JARVIS 5.0 - Environment Manager
=================================

Centraliza o carregamento e validaÃ§Ã£o de variÃ¡veis de ambiente.
Prioriza variÃ¡veis de sistema (JARVIS_*) antes de valores padrÃ£o.
Garante seguranÃ§a e flexibilidade para diferentes ambientes.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import json
import yaml

logger = logging.getLogger("JARVIS-ENV-MANAGER")

@dataclass
class JarvisConfig:
    """ConfiguraÃ§Ã£o centralizada do JARVIS via environment."""

    # === CORE PATHS ===
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent)
    data_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent / "data")
    config_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent / "config")
    models_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent / "models")

    # === EXTERNAL SERVICES ===
    ollama_url: str = "http://localhost:11434"
    ollama_timeout: int = 30
    web_host: str = "0.0.0.0"
    web_port: int = 5000
    ha_url: str = "http://homeassistant.local:8123"

    # === AI/ML SETTINGS ===
    default_model_tier: str = "pro"  # ultra, pro, fast
    max_tokens: int = 4096
    temperature: float = 0.7

    # === SECURITY ===
    enable_security: bool = True
    allowed_paths: List[str] = field(default_factory=lambda: [])
    blocked_commands: List[str] = field(default_factory=lambda: [])

    # === PERFORMANCE ===
    gpu_memory_fraction: float = 0.8
    cpu_threads: int = 4
    enable_cache: bool = True

    # === DEBUG/DEVELOPMENT ===
    debug_mode: bool = False
    log_level: str = "INFO"
    enable_metrics: bool = True

    def __post_init__(self):
        """ValidaÃ§Ã£o pÃ³s-inicializaÃ§Ã£o."""
        # Garantir que paths sejam Path objects
        for attr in ['project_root', 'data_dir', 'config_dir', 'models_dir']:
            value = getattr(self, attr)
            if isinstance(value, str):
                setattr(self, attr, Path(value))

        # Criar diretÃ³rios se nÃ£o existirem
        for path_attr in ['data_dir', 'config_dir', 'models_dir']:
            path = getattr(self, path_attr)
            path.mkdir(parents=True, exist_ok=True)

class EnvironmentManager:
    """Gerenciador centralizado de configuraÃ§Ã£o via ambiente."""

    # Mapeamento de variÃ¡veis de ambiente para atributos da config
    ENV_MAPPING = {
        # Core paths
        'JARVIS_PROJECT_ROOT': 'project_root',
        'JARVIS_DATA_DIR': 'data_dir',
        'JARVIS_CONFIG_DIR': 'config_dir',
        'JARVIS_MODELS_DIR': 'models_dir',

        # External services
        'JARVIS_OLLAMA_URL': 'ollama_url',
        'JARVIS_OLLAMA_TIMEOUT': 'ollama_timeout',
        'JARVIS_WEB_HOST': 'web_host',
        'JARVIS_WEB_PORT': 'web_port',
        'JARVIS_HA_URL': 'ha_url',

        # AI/ML
        'JARVIS_MODEL_TIER': 'default_model_tier',
        'JARVIS_MAX_TOKENS': 'max_tokens',
        'JARVIS_TEMPERATURE': 'temperature',

        # Security
        'JARVIS_ENABLE_SECURITY': 'enable_security',
        'JARVIS_ALLOWED_PATHS': 'allowed_paths',
        'JARVIS_BLOCKED_COMMANDS': 'blocked_commands',

        # Performance
        'JARVIS_GPU_MEMORY_FRACTION': 'gpu_memory_fraction',
        'JARVIS_CPU_THREADS': 'cpu_threads',
        'JARVIS_ENABLE_CACHE': 'enable_cache',

        # Debug
        'JARVIS_DEBUG_MODE': 'debug_mode',
        'JARVIS_LOG_LEVEL': 'log_level',
        'JARVIS_ENABLE_METRICS': 'enable_metrics',
    }

    # Valores padrÃ£o seguros
    DEFAULTS = {
        'ollama_url': 'http://localhost:11434',
        'ollama_timeout': 30,
        'web_host': '0.0.0.0',
        'web_port': 5000,
        'ha_url': 'http://homeassistant.local:8123',
        'default_model_tier': 'pro',
        'max_tokens': 4096,
        'temperature': 0.7,
        'enable_security': True,
        'gpu_memory_fraction': 0.8,
        'cpu_threads': 4,
        'enable_cache': True,
        'debug_mode': False,
        'log_level': 'INFO',
        'enable_metrics': True,
    }

    def __init__(self):
        self.config = None
        self._load_dotenv_if_available()

    def _load_dotenv_if_available(self):
        """Carrega .env se disponÃ­vel (opcional)."""
        try:
            from dotenv import load_dotenv
            project_root = Path(__file__).parent.parent.parent
            env_file = project_root / '.env'

            if env_file.exists():
                load_dotenv(env_file)
                logger.info(f"Carregado arquivo .env: {env_file}")
            else:
                logger.debug("Arquivo .env nÃ£o encontrado, usando variÃ¡veis de ambiente do sistema")
        except ImportError:
            logger.debug("python-dotenv nÃ£o disponÃ­vel, usando apenas variÃ¡veis de ambiente do sistema")

    def load_config(self) -> JarvisConfig:
        """Carrega e valida configuraÃ§Ã£o completa."""
        if self.config is not None:
            return self.config

        # Inicializar com defaults
        config_dict = self.DEFAULTS.copy()

        # Override com variÃ¡veis de ambiente
        for env_var, config_key in self.ENV_MAPPING.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                config_dict[config_key] = self._parse_env_value(env_value, config_key)
                logger.debug(f"Configurado {config_key} = {config_dict[config_key]} (via {env_var})")

        # Processar paths especiais
        self._process_paths(config_dict)

        # Criar objeto de configuraÃ§Ã£o
        self.config = JarvisConfig(**config_dict)

        # ValidaÃ§Ã£o final
        self._validate_config()

        logger.info("ConfiguraÃ§Ã£o JARVIS carregada com sucesso")
        return self.config

    def _parse_env_value(self, value: str, key: str) -> Any:
        """Parse valor de string da environment para tipo correto."""
        # Booleans
        if key in ['enable_security', 'enable_cache', 'debug_mode', 'enable_metrics']:
            return value.lower() in ('true', '1', 'yes', 'on')

        # Integers
        if key in ['ollama_timeout', 'web_port', 'max_tokens', 'cpu_threads']:
            try:
                return int(value)
            except ValueError:
                logger.warning(f"Valor invÃ¡lido para {key}: {value}, usando padrÃ£o")
                return self.DEFAULTS.get(key, 0)

        # Floats
        if key in ['temperature', 'gpu_memory_fraction']:
            try:
                return float(value)
            except ValueError:
                logger.warning(f"Valor invÃ¡lido para {key}: {value}, usando padrÃ£o")
                return self.DEFAULTS.get(key, 0.0)

        # Lists (JSON)
        if key in ['allowed_paths', 'blocked_commands']:
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # Se nÃ£o for JSON, tratar como lista separada por vÃ­rgula
                return [item.strip() for item in value.split(',') if item.strip()]

        # Strings (default)
        return value

    def _process_paths(self, config_dict: Dict[str, Any]):
        """Processa caminhos especiais."""
        project_root = Path(__file__).parent.parent.parent

        # Paths relativos ao projeto
        path_mappings = {
            'data_dir': project_root / "data",
            'config_dir': project_root / "config",
            'models_dir': project_root / "models",
        }

        for key, default_path in path_mappings.items():
            if key in config_dict:
                path_value = config_dict[key]
                if isinstance(path_value, str):
                    # Se for caminho relativo, resolver relativo ao projeto
                    if not Path(path_value).is_absolute():
                        config_dict[key] = project_root / path_value
                    else:
                        config_dict[key] = Path(path_value)

    def _validate_config(self):
        """Valida configuraÃ§Ã£o carregada."""
        # Validar URLs
        import re
        url_pattern = re.compile(r'^https?://.+$')

        for url_key in ['ollama_url', 'ha_url']:
            url = getattr(self.config, url_key, '')
            if url and not url_pattern.match(url):
                logger.warning(f"URL potencialmente invÃ¡lida para {url_key}: {url}")

        # Validar portas
        if self.config and hasattr(self.config, 'web_port') and not (1 <= self.config.web_port <= 65535):
            logger.warning(f"Porta invÃ¡lida: {self.config.web_port}, usando 5000")
            self.config.web_port = 5000

        # Validar tiers de modelo
        valid_tiers = ['ultra', 'pro', 'fast']
        if self.config and hasattr(self.config, 'default_model_tier') and self.config.default_model_tier not in valid_tiers:
            logger.warning(f"Tier invÃ¡lido: {self.config.default_model_tier}, usando 'pro'")
            self.config.default_model_tier = 'pro'

    def get_model_for_tier(self, tier: str) -> str:
        """Retorna modelo apropriado para o tier."""
        # Carregar do ai_config.yaml se disponÃ­vel
        try:
            if self.config and hasattr(self.config, 'config_dir'):
                config_file = self.config.config_dir / "ai_config.yaml"
                if config_file.exists():
                    with open(config_file, 'r', encoding='utf-8') as f:
                        ai_config = yaml.safe_load(f)

                    tier_models = ai_config.get('brain_router', {}).get('ollama_models', {}).get(f'tier_{tier}', [])
                    if tier_models:
                        return tier_models[0]  # Retorna o primeiro modelo do tier
        except Exception as e:
            logger.debug(f"Erro ao carregar modelos do tier: {e}")

        # Fallback para modelos hardcoded (por seguranÃ§a)
        fallback_models = {
            'ultra': 'deepseek-r1:8b',
            'pro': 'gemma3:4b',
            'fast': 'llama3.2'
        }

        return fallback_models.get(tier, 'gemma3:4b')

    def save_config_template(self, output_path: Optional[Path] = None):
        """Salva template de configuraÃ§Ã£o .env."""
        if output_path is None:
            if self.config and hasattr(self.config, 'project_root'):
                output_path = self.config.project_root / '.env.template'
            else:
                output_path = Path.cwd() / '.env.template'

        template = """# JARVIS 5.0 - Environment Configuration Template
# Copie este arquivo para .env e ajuste os valores conforme necessÃ¡rio

# === CORE PATHS ===
# JARVIS_PROJECT_ROOT=./
# JARVIS_DATA_DIR=./data
# JARVIS_CONFIG_DIR=./config
# JARVIS_MODELS_DIR=./models

# === EXTERNAL SERVICES ===
# JARVIS_OLLAMA_URL=http://localhost:11434
# JARVIS_OLLAMA_TIMEOUT=30
# JARVIS_WEB_HOST=0.0.0.0
# JARVIS_WEB_PORT=5000
# JARVIS_HA_URL=http://homeassistant.local:8123

# === AI/ML SETTINGS ===
# JARVIS_MODEL_TIER=pro
# JARVIS_MAX_TOKENS=4096
# JARVIS_TEMPERATURE=0.7

# === SECURITY ===
# JARVIS_ENABLE_SECURITY=true
# JARVIS_ALLOWED_PATHS=["/home/user", "/tmp"]
# JARVIS_BLOCKED_COMMANDS=["rm -rf", "sudo"]

# === PERFORMANCE ===
# JARVIS_GPU_MEMORY_FRACTION=0.8
# JARVIS_CPU_THREADS=4
# JARVIS_ENABLE_CACHE=true

# === DEBUG/DEVELOPMENT ===
# JARVIS_DEBUG_MODE=false
# JARVIS_LOG_LEVEL=INFO
# JARVIS_ENABLE_METRICS=true
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template)

        logger.info(f"Template de configuraÃ§Ã£o salvo em: {output_path}")

# InstÃ¢ncia global
env_manager = EnvironmentManager()

def get_config() -> JarvisConfig:
    """FunÃ§Ã£o de conveniÃªncia para obter configuraÃ§Ã£o."""
    return env_manager.load_config()

def get_model_for_tier(tier: str) -> str:
    """FunÃ§Ã£o de conveniÃªncia para obter modelo por tier."""
    return env_manager.get_model_for_tier(tier)
