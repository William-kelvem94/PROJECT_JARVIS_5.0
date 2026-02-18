# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Unified Learning Configuration Schema
==================================================
Centralized, typed, and validated configuration for all learning subsystems.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from pathlib import Path

@dataclass
class GeneralConfig:
    """Configurações gerais do sistema de aprendizado."""
    enabled: bool = True
    project_root: str = "."
    data_dir: str = "data"
    models_dir: str = "models"
    log_level: str = "INFO"

@dataclass
class IdleConditions:
    """Condições para detecção de ociosidade."""
    max_cpu_percent: float = 20.0
    max_memory_percent: float = 80.0
    min_idle_duration_seconds: int = 300
    check_interval_seconds: int = 60
    night_start_hour: int = 22
    night_end_hour: int = 6

@dataclass
class DreamCycleConfig:
    """Configuração do Dream Cycle."""
    enabled: bool = True
    idle_conditions: IdleConditions = field(default_factory=IdleConditions)
    research_enabled: bool = True
    max_research_topics_per_cycle: int = 2

@dataclass
class TrainingConfig:
    """Configuração de treinamento para LoRA/QLoRA."""
    enabled: bool = True
    model_tier: str = "pro"  # ultra, pro, fast
    max_length: int = 2048
    batch_size: int = 4
    learning_rate: float = 2e-4
    epochs: int = 3
    gradient_accumulation_steps: int = 4
    backend: str = "distributed"  # local, distributed

@dataclass
class DatabaseConfig:
    """Configuração de banco de dados e persistência."""
    enabled: bool = True
    backend: str = "sqlite"  # sqlite, postgresql, chromadb
    auto_migrate: bool = True
    max_connections: int = 10
    sqlite_path: str = "data/learning.db"

@dataclass
class MonitoringConfig:
    """Configuração de monitoramento e dashboard."""
    enabled: bool = True
    collection_interval: float = 1.0
    web_port: int = 8080
    log_level: str = "INFO"

@dataclass
class LearningConfig:
    """Configuração principal (Master) do sistema de aprendizado."""
    general: GeneralConfig = field(default_factory=GeneralConfig)
    dream_cycle: DreamCycleConfig = field(default_factory=DreamCycleConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LearningConfig":
        """Reconstrói a configuração a partir de um dicionário (YAML)."""
        if not data:
            return cls()

        def _get_sub_config(section: str, SubCls: Any, sub_sections: Optional[Dict] = None):
            section_data = data.get(section, {})
            # Map sub-sections if needed (e.g. idle_conditions inside dream_cycle)
            if sub_sections:
                for target_key, sub_cls in sub_sections.items():
                    sub_data = section_data.get(target_key, {})
                    section_data[target_key] = sub_cls(**sub_data) if isinstance(sub_data, dict) else sub_data
            
            # Filter only valid fields for the dataclass
            valid_fields = {f.name for f in SubCls.__dataclass_fields__.values()}
            filtered = {k: v for k, v in section_data.items() if k in valid_fields}
            return SubCls(**filtered)

        return cls(
            general=_get_sub_config("general", GeneralConfig),
            dream_cycle=_get_sub_config("dream_cycle", DreamCycleConfig, {"idle_conditions": IdleConditions}),
            training=_get_sub_config("training", TrainingConfig),
            database=_get_sub_config("database", DatabaseConfig),
            monitoring=_get_sub_config("monitoring", MonitoringConfig)
        )
