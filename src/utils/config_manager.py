"""
JARVIS 5.0 - Configuration Manager
===================================
Sistema de configuração hierárquico com fallback automático.
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import threading

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Gerenciador de configuração hierárquico.
    Hierarquia: runtime -> user -> system -> defaults
    """

    _instance: Optional["ConfigManager"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "ConfigManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return

        with self._lock:
            if hasattr(self, "_initialized"):
                return

            self._initialized = True
            self.configs: Dict[str, Dict[str, Any]] = {
                "defaults": self._get_defaults(),
                "system": {},
                "user": {},
                "runtime": {},
            }
            self._config_files = {
                "system": self._get_system_config_path(),
                "user": self._get_user_config_path(),
            }

            self._load_configs()
            logger.info("Configuration Manager initialized")

    def _get_defaults(self) -> Dict[str, Any]:
        """Retorna configurações padrão"""
        return {
            "system": {
                "max_memory_mb": 1024,
                "max_cpu_percent": 80,
                "log_level": "INFO",
                "timeout_seconds": 30,
            },
            "ai": {"max_tokens": 4096, "temperature": 0.7, "model": "gpt-3.5-turbo"},
            "interface": {
                "theme": "dark",
                "opacity": 0.9,
                "position": {"x": 100, "y": 100},
            },
            "security": {
                "enable_encryption": True,
                "max_file_size_mb": 100,
                "allowed_domains": ["google.com", "openai.com"],
            },
        }

    def _get_system_config_path(self) -> Path:
        """Retorna caminho do arquivo de configuração do sistema"""
        return Path(__file__).parent.parent.parent / "config" / "system_config.yaml"

    def _get_user_config_path(self) -> Path:
        """Retorna caminho do arquivo de configuração do usuário"""
        home = Path.home()
        return home / ".jarvis" / "user_config.yaml"

    def _load_configs(self) -> None:
        """Carrega configurações dos arquivos"""
        # Carrega config do sistema
        system_path = self._config_files["system"]
        if system_path.exists():
            try:
                with open(system_path, "r", encoding="utf-8") as f:
                    if system_path.suffix == ".yaml":
                        self.configs["system"] = yaml.safe_load(f) or {}
                    else:
                        self.configs["system"] = json.load(f)
                logger.info(f"Loaded system config from {system_path}")
            except Exception as e:
                logger.error(f"Failed to load system config: {e}")

        # Carrega config do usuário
        user_path = self._config_files["user"]
        if user_path.exists():
            try:
                with open(user_path, "r", encoding="utf-8") as f:
                    if user_path.suffix == ".yaml":
                        self.configs["user"] = yaml.safe_load(f) or {}
                    else:
                        self.configs["user"] = json.load(f)
                logger.info(f"Loaded user config from {user_path}")
            except Exception as e:
                logger.error(f"Failed to load user config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retorna valor de configuração com hierarquia.

        Args:
            key: Chave de configuração (pode usar notação com pontos)
            default: Valor padrão se não encontrado

        Returns:
            Valor da configuração
        """
        keys = key.split(".")

        # Procura em ordem: runtime -> user -> system -> defaults
        for level in ["runtime", "user", "system", "defaults"]:
            config = self.configs[level]
            value = self._get_nested_value(config, keys)
            if value is not None:
                return value

        return default

    def _get_nested_value(self, config: Dict[str, Any], keys: list) -> Any:
        """Busca valor aninhado em dicionário"""
        current = config
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    def set(self, key: str, value: Any, level: str = "runtime") -> None:
        """
        Define valor de configuração.

        Args:
            key: Chave de configuração
            value: Valor a definir
            level: Nível da configuração ('runtime', 'user', 'system')
        """
        if level not in self.configs:
            raise ValueError(f"Invalid config level: {level}")

        keys = key.split(".")
        config = self.configs[level]

        # Cria estrutura aninhada se necessário
        current = config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value
        logger.debug(f"Set config {key} = {value} at level {level}")

    def save_user_config(self) -> bool:
        """
        Salva configuração do usuário no arquivo.

        Returns:
            True se salvo com sucesso
        """
        user_path = self._config_files["user"]
        user_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(user_path, "w", encoding="utf-8") as f:
                yaml.dump(self.configs["user"], f, default_flow_style=False)
            logger.info(f"Saved user config to {user_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save user config: {e}")
            return False

    def reload_configs(self) -> None:
        """Recarrega todas as configurações dos arquivos"""
        self._load_configs()
        logger.info("Reloaded all configurations")

    def get_all(self, level: Optional[str] = None) -> Dict[str, Any]:
        """
        Retorna todas as configurações de um nível ou merged.

        Args:
            level: Nível específico ou None para merged

        Returns:
            Dicionário com configurações
        """
        if level:
            return self.configs.get(level, {}).copy()

        # Merge all levels
        merged = {}
        for level_name in ["defaults", "system", "user", "runtime"]:
            self._deep_merge(merged, self.configs[level_name])
        return merged

    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Merge profundo de dicionários"""
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                self._deep_merge(target[key], value)
            else:
                target[key] = value


# Singleton instance
config_manager = ConfigManager()


# Convenience functions
def get_config(key: str, default: Any = None) -> Any:
    """Função de conveniência para obter configuração"""
    return config_manager.get(key, default)


def set_config(key: str, value: Any, level: str = "runtime") -> None:
    """Função de conveniência para definir configuração"""
    config_manager.set(key, value, level)
