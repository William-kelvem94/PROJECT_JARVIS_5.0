import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from threading import Lock


class SystemManifest:
    """
    JARVIS 5.0 System Manifest (A Constituição)

    Singleton responsável por carregar, validar e fornecer acesso centralizado
    às configurações do sistema (ai_config.yaml).
    """

    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SystemManifest, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.config_path = self._find_config_path()
        self.config: Dict[str, Any] = {}
        self._load_config()
        self._initialized = True

    def _find_config_path(self) -> Path:
        """Localiza o arquivo AI Config."""
        # Tenta localizar relativo ao arquivo atual ou na raiz do projeto
        current_dir = Path(__file__).resolve().parent
        # src/core/infrastructure -> src/core -> src -> root
        root_dir = current_dir.parent.parent.parent

        config_file = root_dir / "config" / "ai_config.yaml"
        if not config_file.exists():
            # Fallback: tenta buscar subindo diretórios
            potential_path = Path("config/ai_config.yaml").resolve()
            if potential_path.exists():
                return potential_path
            raise FileNotFoundError(f"AI Config not found at {config_file}")

        return config_file

    def _load_config(self):
        """Carrega e valida o arquivo YAML."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)

            self._validate_manifest()
            print(f"[SystemManifest] Constitution loaded from {self.config_path}")

        except Exception as e:
            print(f"[SystemManifest] CRITICAL ERROR: Failed to load constitution: {e}")
            # Em caso de erro crítico na constituição, o sistema não deve
            # operar
            self.config = {}
            raise

    def _validate_manifest(self):
        """Valida se as seções críticas existem."""
        required_sections = [
            "ai_agent",
            "brain_router",
            "continual_learning",
            "security",
        ]

        missing = [s for s in required_sections if s not in self.config]
        if missing:
            raise ValueError(
                f"System Constitution incomplete. Missing sections: {missing}"
            )

    def get(self, key: str, default: Any = None) -> Any:
        """Recupera um valor da configuração (suporta dot.notation para nested keys)."""
        keys = key.split(".")
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    @property
    def tiers(self) -> Dict[str, Any]:
        """Atalho para tiers de modelos."""
        return self.get("brain_router.ollama_models", {})

    @property
    def complexity_limits(self) -> Dict[str, float]:
        """Atalho para limites de complexidade."""
        return self.get("ai_agent.complexity_thresholds", {})


# Global Accessor
manifest = SystemManifest()
