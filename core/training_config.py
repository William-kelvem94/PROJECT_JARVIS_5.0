"""
Training Configuration - Sistema de Configuração de Treinamento
Gerencia todas as configurações relacionadas ao treinamento de modelos
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path
from core.logger import logger


@dataclass
class ModelConfig:
    """Configuração de modelo para treinamento."""
    base_model: str = "codellama:7b"
    custom_model_name: str = "jarvis-custom"
    model_type: str = "conversational"  # conversational, code, general
    context_length: int = 4096
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1


@dataclass
class DatasetConfig:
    """Configuração de dataset para treinamento."""
    min_interactions: int = 50
    min_quality_score: float = 0.5
    max_samples: int = 10000
    include_code_examples: bool = True
    include_conversations: bool = True
    include_documents: bool = False
    train_test_split: float = 0.8
    validation_split: float = 0.1


@dataclass
class TrainingConfig:
    """Configuração de treinamento."""
    # Hiperparâmetros
    learning_rate: float = 0.0001
    batch_size: int = 32
    num_epochs: int = 10
    warmup_steps: int = 100
    gradient_accumulation_steps: int = 1
    
    # Otimização
    optimizer: str = "adamw"  # adamw, sgd, adam
    scheduler: str = "linear"  # linear, cosine, constant
    weight_decay: float = 0.01
    max_grad_norm: float = 1.0
    
    # Early stopping
    early_stopping_patience: int = 3
    early_stopping_threshold: float = 0.01
    
    # Checkpointing
    save_steps: int = 500
    eval_steps: int = 100
    logging_steps: int = 10
    save_total_limit: int = 3


@dataclass
class AutoTrainingConfig:
    """Configuração de auto-treinamento."""
    enabled: bool = True
    quality_threshold: float = 0.6
    retrain_interval_hours: int = 24
    min_interactions_for_training: int = 50
    min_interactions_for_incremental: int = 20
    max_training_time_minutes: int = 60
    auto_switch_to_custom_model: bool = True


@dataclass
class ResourceConfig:
    """Configuração de recursos computacionais."""
    use_gpu: bool = True
    gpu_memory_fraction: float = 0.8
    num_workers: int = 4
    mixed_precision: bool = False  # fp16
    distributed_training: bool = False


@dataclass
class ComprehensiveTrainingConfig:
    """Configuração completa do sistema de treinamento."""
    model: ModelConfig = field(default_factory=ModelConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    auto_training: AutoTrainingConfig = field(default_factory=AutoTrainingConfig)
    resources: ResourceConfig = field(default_factory=ResourceConfig)
    
    # Metadados
    version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    description: str = "Configuração de treinamento JARVIS"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte configuração para dicionário."""
        return {
            "model": self.model.__dict__,
            "dataset": self.dataset.__dict__,
            "training": self.training.__dict__,
            "auto_training": self.auto_training.__dict__,
            "resources": self.resources.__dict__,
            "version": self.version,
            "created_at": self.created_at,
            "description": self.description
        }
    
    def save(self, path: str):
        """Salva configuração em arquivo JSON."""
        config_dict = self.to_dict()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        logger.info(f"Configuração salva: {path}")
    
    @classmethod
    def load(cls, path: str) -> 'ComprehensiveTrainingConfig':
        """Carrega configuração de arquivo JSON."""
        with open(path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        
        config = cls()
        
        # Model config
        if "model" in config_dict:
            for key, value in config_dict["model"].items():
                if hasattr(config.model, key):
                    setattr(config.model, key, value)
        
        # Dataset config
        if "dataset" in config_dict:
            for key, value in config_dict["dataset"].items():
                if hasattr(config.dataset, key):
                    setattr(config.dataset, key, value)
        
        # Training config
        if "training" in config_dict:
            for key, value in config_dict["training"].items():
                if hasattr(config.training, key):
                    setattr(config.training, key, value)
        
        # Auto-training config
        if "auto_training" in config_dict:
            for key, value in config_dict["auto_training"].items():
                if hasattr(config.auto_training, key):
                    setattr(config.auto_training, key, value)
        
        # Resources config
        if "resources" in config_dict:
            for key, value in config_dict["resources"].items():
                if hasattr(config.resources, key):
                    setattr(config.resources, key, value)
        
        # Metadata
        config.version = config_dict.get("version", "1.0.0")
        config.created_at = config_dict.get("created_at", datetime.now().isoformat())
        config.description = config_dict.get("description", "")
        
        logger.info(f"Configuração carregada: {path}")
        return config
    
    @classmethod
    def create_default(cls) -> 'ComprehensiveTrainingConfig':
        """Cria configuração padrão."""
        return cls()
    
    @classmethod
    def create_for_conversation(cls) -> 'ComprehensiveTrainingConfig':
        """Cria configuração otimizada para conversação."""
        config = cls()
        config.model.model_type = "conversational"
        config.model.base_model = "llama2:7b"
        config.model.temperature = 0.8
        config.dataset.include_conversations = True
        config.dataset.include_code_examples = False
        config.training.learning_rate = 0.00005
        return config
    
    @classmethod
    def create_for_code(cls) -> 'ComprehensiveTrainingConfig':
        """Cria configuração otimizada para código."""
        config = cls()
        config.model.model_type = "code"
        config.model.base_model = "codellama:7b"
        config.model.temperature = 0.2
        config.dataset.include_code_examples = True
        config.dataset.include_conversations = False
        config.training.learning_rate = 0.0001
        return config
    
    @classmethod
    def create_for_general(cls) -> 'ComprehensiveTrainingConfig':
        """Cria configuração otimizada para uso geral."""
        config = cls()
        config.model.model_type = "general"
        config.model.base_model = "mistral:7b"
        config.model.temperature = 0.7
        config.dataset.include_conversations = True
        config.dataset.include_code_examples = True
        config.dataset.include_documents = True
        return config


class TrainingConfigManager:
    """Gerenciador de configurações de treinamento."""
    
    def __init__(self, config_dir: str = "./config/training"):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            config_dir: Diretório para armazenar configurações
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.current_config: Optional[ComprehensiveTrainingConfig] = None
        logger.info(f"TrainingConfigManager inicializado: {self.config_dir}")
    
    def create_default_config(self) -> ComprehensiveTrainingConfig:
        """Cria e salva configuração padrão."""
        config = ComprehensiveTrainingConfig.create_default()
        self.save_config(config, "default")
        return config
    
    def save_config(self, config: ComprehensiveTrainingConfig, name: str = "default"):
        """Salva configuração com nome específico."""
        config_path = self.config_dir / f"{name}.json"
        config.save(str(config_path))
        self.current_config = config
    
    def load_config(self, name: str = "default") -> ComprehensiveTrainingConfig:
        """Carrega configuração por nome."""
        config_path = self.config_dir / f"{name}.json"
        
        if not config_path.exists():
            logger.warning(f"Configuração {name} não encontrada, criando padrão")
            return self.create_default_config()
        
        config = ComprehensiveTrainingConfig.load(str(config_path))
        self.current_config = config
        return config
    
    def list_configs(self) -> List[str]:
        """Lista todas as configurações disponíveis."""
        configs = [f.stem for f in self.config_dir.glob("*.json")]
        return configs
    
    def get_current_config(self) -> ComprehensiveTrainingConfig:
        """Retorna configuração atual ou cria padrão."""
        if self.current_config is None:
            self.current_config = self.load_config("default")
        return self.current_config
    
    def update_config(self, updates: Dict[str, Any], name: str = "default"):
        """Atualiza configuração existente."""
        config = self.load_config(name)
        
        # Atualizar campos baseado no dicionário
        for section, values in updates.items():
            if hasattr(config, section):
                section_obj = getattr(config, section)
                for key, value in values.items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)
        
        self.save_config(config, name)
        logger.info(f"Configuração {name} atualizada")
