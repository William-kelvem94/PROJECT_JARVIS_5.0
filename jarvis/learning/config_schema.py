# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger("JARVIS-CONFIG-SCHEMA")

@dataclass
class GeneralConfig:
    enabled: bool = True
    data_dir: str = "data"
    models_dir: str = "models"
    log_level: str = "INFO"

@dataclass
class IdleConditions:
    max_cpu_percent: float = 20.0
    max_memory_percent: float = 80.0
    min_idle_duration_seconds: int = 300
    check_interval_seconds: int = 60
    night_start_hour: int = 22
    night_end_hour: int = 6

@dataclass
class DreamCycleConfig:
    enabled: bool = True
    idle_conditions: IdleConditions = field(default_factory=IdleConditions)
    research_enabled: bool = True
    auto_fine_tune: bool = True  # NOVO: Habilita o treinamento automático
    max_research_topics_per_cycle: int = 2

@dataclass
class TrainingConfig:
    enabled: bool = True
    model_tier: str = "pro"
    max_length: int = 2048
    batch_size: int = 4
    learning_rate: float = 2e-4
    epochs: int = 3
    backend: str = "unsloth" # local, unsloth, ollama

@dataclass
class DatabaseConfig:
    enabled: bool = True
    backend: str = "sqlite"
    auto_migrate: bool = True

@dataclass
class LearningConfig:
    general: GeneralConfig = field(default_factory=GeneralConfig)
    dream_cycle: DreamCycleConfig = field(default_factory=DreamCycleConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningConfig':
        """Converte dicionário YAML em objeto tipado."""
        try:
            gen = data.get('general', {})
            dc = data.get('dream_cycle', {})
            ic = dc.get('idle_conditions', {})
            tr = data.get('training', {})
            db = data.get('database', {})

            return cls(
                general=GeneralConfig(**gen) if gen else GeneralConfig(),
                dream_cycle=DreamCycleConfig(
                    enabled=dc.get('enabled', True),
                    research_enabled=dc.get('research_enabled', True),
                    auto_fine_tune=dc.get('auto_fine_tune', True),
                    max_research_topics_per_cycle=dc.get('max_research_topics_per_cycle', 2),
                    idle_conditions=IdleConditions(**ic) if ic else IdleConditions()
                ),
                training=TrainingConfig(**tr) if tr else TrainingConfig(),
                database=DatabaseConfig(**db) if db else DatabaseConfig()
            )
        except Exception as e:
            logger.error(f"Erro ao converter config: {e}")
            return cls()
