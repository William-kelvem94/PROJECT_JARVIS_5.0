# -*- coding: utf-8 -*-
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from .config_schema import LearningConfig
from .dream_cycle import DreamCycle

logger = logging.getLogger("JARVIS-LEARNING-ENGINE")

class LearningEngine:
    """
    O Coração do Aprendizado do JARVIS 5.0.
    Coordena Pesquisa, Ciclo de Sonho e Auto-Fine-Tuning Local.
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.config_path = self.project_root / "config" / "ai_config.yaml"
        self.data_dir = self.project_root / "data"
        
        # Load Config
        self.config = self._load_config()
        
        # Components
        self.dream_cycle = DreamCycle(self.data_dir, self.config.dream_cycle)
        self.is_initialized = False

    def _load_config(self) -> LearningConfig:
        try:
            import yaml
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    return LearningConfig.from_dict(data.get("continual_learning", {}))
            return LearningConfig()
        except Exception as e:
            logger.error(f"Falha ao carregar configuração de aprendizado: {e}")
            return LearningConfig()

    def initialize(self):
        """Ativa os sistemas de aprendizado."""
        if not self.config.general.enabled:
            logger.info("🔒 Sistemas de aprendizado desativados pela configuração.")
            return

        if self.dream_cycle.start():
            self.is_initialized = True
            logger.info("🧠 Cérebro Evolutivo (Fase 2+) ativo e monitorando.")

    def record_interaction(self, user_text: str, assistant_text: str):
        """Registra interação para futura análise de gaps."""
        # A gravação física já acontece no agent.py (interactions.jsonl)
        # O ResearchEngine do DreamCycle lerá esse arquivo.
        pass

    def get_status(self) -> Dict[str, Any]:
        return {
            "initialized": self.is_initialized,
            "dream_cycle": self.dream_cycle.get_status()
        }

# --- Singleton Pattern ---
_engine = None

def initialize_learning_systems(project_root: str = ".") -> LearningEngine:
    global _engine
    if _engine is None:
        _engine = LearningEngine(project_root)
        _engine.initialize()
    return _engine

def get_learning_engine() -> Optional[LearningEngine]:
    return _engine
