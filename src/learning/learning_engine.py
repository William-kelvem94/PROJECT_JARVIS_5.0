# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Central Learning Engine
===================================
A "Maestro" for the system's cognitive growth.
Orchestrates training, research, monitoring and self-improvement task deployment.
"""

import logging
import time
import os
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List

# Core Configuration
from .config_schema import LearningConfig

# Extracted Components
from .training_orchestrator import TrainingOrchestrator
from .model_registry_manager import ModelRegistryManager
from .health_monitor import HealthMonitor
from .dream_cycle import DreamCycle
from .dependency_manager import dependency_manager

# Utilities
from ..utils.safe_execute import safe_execute, safe_context

logger = logging.getLogger("JARVIS-LEARNING-ENGINE")


class LearningEngine:
    """
    Motor central de aprendizado do JARVIS.
    Orquestra treinamento, monitoramento e ciclos de evolução autônoma.
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.config_path = self.project_root / "config" / "ai_config.yaml"
        
        # Load typed config
        self.config = self._load_typed_config()
        
        # Data and Models paths (from config or defaults)
        self.data_dir = Path(self.config.general.data_dir)
        self.models_dir = Path(self.config.general.models_dir)
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # Components (Lazy initialized or during initialize())
        self.health_monitor = HealthMonitor(check_interval=120.0)
        self.training_orchestrator = TrainingOrchestrator(models_dir=self.models_dir)
        self.model_registry_manager = ModelRegistryManager(models_dir=self.models_dir)
        self.dream_cycle = None
        
        # Legacy/Internal objects (initialized on demand)
        self.scalable_database = None
        self.model_registry = None
        
        # Status tracking
        self.is_initialized = False
        self.components_status = {
            "health_monitor": False,
            "training_orchestrator": False,
            "model_registry": False,
            "dream_cycle": False
        }

    def _load_typed_config(self) -> LearningConfig:
        """Carrega e valida configuração usando esquemas tipados."""
        try:
            import yaml
            if not self.config_path.exists():
                logger.warning(f"⚠️ Config not found at {self.config_path}. Using defaults.")
                return LearningConfig()
                
            with open(self.config_path, 'r', encoding='utf-8') as f:
                raw_data = yaml.safe_load(f) or {}
                
            # Extrair seção 'continual_learning' se existir
            learning_data = raw_data.get('continual_learning', {})
            return LearningConfig.from_dict(learning_data)
            
        except Exception as e:
            logger.error(f"❌ Error loading typed config: {e}")
            return LearningConfig()

    @safe_execute(default=False)
    def initialize(self) -> bool:
        """Inicia todos os sistemas de aprendizado com configuração tipada."""
        if not self.config.general.enabled:
            logger.info("🔒 Learning Engine disabled by config")
            return False

        if self.is_initialized:
            return True

        logger.info("🚀 Initializing JARVIS Learning Engine...")

        with safe_context("health_monitor_init"):
            # Register essential components for monitoring
            self.health_monitor.register_component("training_orchestrator")
            self.health_monitor.register_component("model_registry")
            self.health_monitor.start()
            self.components_status["health_monitor"] = True

        # Initialize Dream Cycle (Orchestrator for background research/training)
        if self.config.dream_cycle.enabled:
            try:
                self.dream_cycle = DreamCycle(self.data_dir, self.config.dream_cycle)
                self.dream_cycle.start()
                self.components_status["dream_cycle"] = True
            except Exception as e:
                logger.error(f"Failed to start Dream Cycle: {e}")

        # Components are ready
        self.components_status["training_orchestrator"] = True
        self.components_status["model_registry"] = True
        
        self.is_initialized = True
        logger.info("✅ Learning Engine initialization complete")
        return True

    @safe_execute(default=False)
    def record_interaction(self, user_input: str, ai_response: str, metadata: Dict[str, Any] = None) -> bool:
        """Registra interação para aprendizado futuro (Gap Analysis)."""
        # This usually writes to interactions.jsonl used by GapAnalyzer
        interactions_file = self.data_dir / "logs" / "agent_interactions.jsonl"
        interactions_file.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        entry = {
            "timestamp": time.time(),
            "command": user_input,
            "response": ai_response,
            "metadata": metadata or {},
            "success": metadata.get("success", True) if metadata else True
        }
        
        with open(interactions_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            
        return True

    def add_training_task(self, **kwargs) -> bool:
        """Agenda uma nova tarefa de treinamento via orchestrator."""
        if not self.is_initialized:
            return False
        
        job_id = self.training_orchestrator.create_job(
            model_config=kwargs.get("config", {}),
            dataset_path=str(kwargs.get("dataset_path", "")),
            num_gpus=kwargs.get("num_gpus")
        )
        return bool(job_id)

    def get_status(self) -> Dict[str, Any]:
        """Retorna status unificado do motor cognitivo."""
        status = {
            "initialized": self.is_initialized,
            "components": self.components_status,
            "config": self.config.general.enabled,
        }
        
        if self.dream_cycle:
            status["dream_cycle"] = self.dream_cycle.get_status()
            
        if self.health_monitor:
            status["health"] = self.health_monitor.monitor_system()
            
        return status

    def shutdown(self):
        """Desliga graciosamente todos os componentes."""
        logger.info("🔄 Shutting down Learning Engine...")
        
        if self.dream_cycle:
            self.dream_cycle.stop()
            
        self.training_orchestrator.shutdown()
        self.health_monitor.stop()
        
        self.is_initialized = False
        logger.info("✅ Learning Engine shutdown OK")


# --- GLOBAL ACCESSORS (Singletons) ---

_learning_engine = None

def get_learning_engine() -> Optional[LearningEngine]:
    """Retorna a instância única do Learning Engine."""
    return _learning_engine

def initialize_learning_systems(project_root: str = "."):
    """Ponto de entrada oficial para inicialização do ecossistema de aprendizado."""
    global _learning_engine
    if _learning_engine is None:
        _learning_engine = LearningEngine(project_root)
        _learning_engine.initialize()
    return _learning_engine
