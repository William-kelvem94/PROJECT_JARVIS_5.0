#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Democratic Intelligence Configuration
========================================================
Configuração central para todos os sistemas democráticos
"""

from enum import Enum
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from pathlib import Path
import json

class DemocraticFeature(Enum):
    """Features disponíveis do sistema democrático"""
    NETWORK_MESH = "network_mesh"
    AUTO_RECOVERY = "auto_recovery"
    PREDICTIVE_ANALYTICS = "predictive_analytics"
    TASK_DISTRIBUTION = "task_distribution"
    ENERGY_OPTIMIZATION = "energy_optimization"
    PERFORMANCE_MONITORING = "performance_monitoring"

@dataclass
class DemocraticConfig:
    """📋 Configuração do sistema democrático"""
    
    # === IDENTIFICAÇÃO ===
    target_microsoft_account: str = "williamkelvem64@gmail.com"
    device_trust_network: Set[str] = field(default_factory=set)  # Device IDs autorizados
    enable_auto_discovery: bool = True
    
    # === FEATURES HABILITADAS ===
    enabled_features: Set[DemocraticFeature] = field(default_factory=set)
    
    # === NETWORK CONFIGURATION ===
    # Configurações da rede democrática
    max_connected_devices: int = 10
    heartbeat_interval_sec: int = 30
    election_timeout_sec: int = 60
    task_redistribution_threshold: float = 0.8  # 80% CPU/Memory
    
    # === AUTO-RECOVERY CONFIGURATION ===
    # Configurações do auto-recovery
    health_check_interval_sec: int = 15
    failure_threshold_count: int = 3
    emergency_timeout_sec: int = 300  # 5 minutos
    enable_automatic_takeover: bool = True
    takeover_confirmation_required: bool = False  # Para FULL_AUTO
    
    # === PREDICTIVE ANALYTICS CONFIGURATION ===
    # Configurações da análise preditiva
    metrics_collection_interval_sec: int = 30
    prediction_interval_sec: int = 300  # 5 minutos
    metrics_retention_hours: int = 168  # 1 semana
    ml_training_min_samples: int = 100
    anomaly_detection_sensitivity: float = 0.1  # 10% outliers
    
    # === OPTIMIZATION CONFIGURATION ===
    # Configurações das otimizações
    auto_optimization_enabled: bool = True
    optimization_interval_sec: int = 300  # 5 minutos
    energy_save_priority: bool = True
    performance_priority: bool = True
    max_optimization_per_hour: int = 12
    
    # === AUTOMATION LEVELS ===
    # Nível padrão de automação
    default_automation_level: str = "SUPERVISED"  # MANUAL, SUPERVISED, SEMI_AUTO, FULL_AUTO
    emergency_automation_override: bool = True  # AUTO em emergência
    
    # === SECURITY CONFIGURATION ===
    # Configurações de segurança
    require_device_authentication: bool = True
    encrypted_communication: bool = False  # Placeholder
    audit_all_actions: bool = True
    max_failed_authentications: int = 3
    
    # === PERFORMANCE LIMITS ===
    # Limites de performance
    max_cpu_usage_percent: float = 85.0
    max_memory_usage_percent: float = 80.0
    max_network_bandwidth_mbps: float = 100.0
    max_concurrent_tasks: int = 5
    
    # === DATA STORAGE ===
    # Configurações de storage
    data_retention_days: int = 30
    backup_rotation_count: int = 5
    compress_old_data: bool = True
    google_drive_integration: bool = True
    
    def __post_init__(self):
        """Inicialização pós-criação"""
        if self.device_trust_network is None:
            self.device_trust_network = set()
        
        if self.enabled_features is None:
            # Habilitar todas features por padrão
            self.enabled_features = set(DemocraticFeature)
    
    def is_feature_enabled(self, feature: DemocraticFeature) -> bool:
        """🔍 Verifica se feature está habilitada"""
        return feature in self.enabled_features
    
    def add_trusted_device(self, device_id: str):
        """➕ Adiciona dispositivo confiável"""
        self.device_trust_network.add(device_id)
    
    def remove_trusted_device(self, device_id: str):
        """➖ Remove dispositivo confiável"""
        self.device_trust_network.discard(device_id)
    
    def is_device_trusted(self, device_id: str) -> bool:
        """🔍 Verifica se dispositivo é confiável"""
        return device_id in self.device_trust_network
    
    def to_dict(self) -> Dict[str, Any]:
        """📋 Converte para dicionário"""
        data = {}
        for key, value in self.__dict__.items():
            if isinstance(value, set):
                if key == 'enabled_features':
                    data[key] = [f.value for f in value]
                else:
                    data[key] = list(value)
            elif isinstance(value, Enum):
                data[key] = value.value
            else:
                data[key] = value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DemocraticConfig':
        """📁 Carrega de dicionário"""
        # Converter features de volta
        if 'enabled_features' in data:
            features = set()
            for feature_name in data['enabled_features']:
                try:
                    features.add(DemocraticFeature(feature_name))
                except ValueError:
                    pass
            data['enabled_features'] = features
        
        # Converter device trust network
        if 'device_trust_network' in data:
            data['device_trust_network'] = set(data['device_trust_network'])
        
        return cls(**data)

class DemocraticConfigManager:
    """⚙️ Gerenciador de configuração democrática"""
    
    DEFAULT_CONFIG_PATH = "config/democratic_config.json"
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.config_path = self.base_path / self.DEFAULT_CONFIG_PATH
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._config: Optional[DemocraticConfig] = None
    
    def load_config(self) -> DemocraticConfig:
        """📁 CARREGA CONFIGURAÇÃO"""
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self._config = DemocraticConfig.from_dict(data)
                print(f"📁 Configuração democrática carregada: {self.config_path}")
                
            except Exception as e:
                print(f"❌ Erro carregando configuração: {e}")
                self._config = DemocraticConfig()
                self._save_default_config()
        else:
            # Criar configuração padrão
            self._config = self._create_default_config()
            self.save_config()
        
        return self._config
    
    def save_config(self):
        """💾 SALVA CONFIGURAÇÃO"""
        
        if not self._config:
            return
        
        try:
            data = self._config.to_dict()
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Configuração salva: {self.config_path}")
            
        except Exception as e:
            print(f"❌ Erro salvando configuração: {e}")
    
    def get_config(self) -> DemocraticConfig:
        """📋 OBTEM CONFIGURAÇÃO ATUAL"""
        if not self._config:
            return self.load_config()
        return self._config
    
    def update_config(self, **kwargs):
        """🔄 ATUALIZA CONFIGURAÇÃO"""
        
        if not self._config:
            self.load_config()
        
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        
        self.save_config()
    
    def _create_default_config(self) -> DemocraticConfig:
        """⚙️ Cria configuração padrão"""
        
        config = DemocraticConfig()
        
        # Configurações específicas para williamkelvem64@gmail.com
        config.target_microsoft_account = "williamkelvem64@gmail.com"
        config.enabled_features = {
            DemocraticFeature.NETWORK_MESH,
            DemocraticFeature.AUTO_RECOVERY,
            DemocraticFeature.PREDICTIVE_ANALYTICS,
            DemocraticFeature.TASK_DISTRIBUTION,
            DemocraticFeature.PERFORMANCE_MONITORING
        }
        
        # Configurações otimizadas para pequenas redes locais
        config.max_connected_devices = 5
        config.heartbeat_interval_sec = 30
        config.enable_automatic_takeover = True
        config.takeover_confirmation_required = False
        
        # Configurações de análise preditiva
        config.ml_training_min_samples = 50  # Reduzido para redes pequenas
        config.metrics_retention_hours = 72  # 3 dias
        
        # Configurações de automação
        config.default_automation_level = "SEMI_AUTO"
        config.emergency_automation_override = True
        
        return config
    
    def _save_default_config(self):
        """💾 Salva configuração padrão"""
        if not self._config:
            self._config = self._create_default_config()
        self.save_config()
    
    def reset_to_defaults(self):
        """🔄 RESETA PARA CONFIGURAÇÕES PADRÃO"""
        self._config = self._create_default_config()
        self.save_config()
        print("🔄 Configuração resetada para padrão")

# ===== CONFIGURAÇÕES PRÉ-DEFINIDAS =====

PROFILE_CONFIGS = {
    "conservative": {
        "default_automation_level": "MANUAL",
        "enable_automatic_takeover": False,
        "takeover_confirmation_required": True,
        "max_optimization_per_hour": 3,
        "emergency_automation_override": False
    },
    
    "balanced": {
        "default_automation_level": "SUPERVISED",
        "enable_automatic_takeover": True,
        "takeover_confirmation_required": True,
        "max_optimization_per_hour": 6,
        "emergency_automation_override": True
    },
    
    "aggressive": {
        "default_automation_level": "FULL_AUTO",
        "enable_automatic_takeover": True,
        "takeover_confirmation_required": False,
        "max_optimization_per_hour": 12,
        "emergency_automation_override": True,
        "optimization_interval_sec": 180  # 3 minutos
    },
    
    "development": {
        "default_automation_level": "SEMI_AUTO",
        "metrics_collection_interval_sec": 10,
        "prediction_interval_sec": 60,
        "health_check_interval_sec": 5,
        "audit_all_actions": True,
        "metrics_retention_hours": 24  # 1 dia apenas
    },
    
    "production": {
        "default_automation_level": "SUPERVISED",
        "require_device_authentication": True,
        "audit_all_actions": True,
        "max_failed_authentications": 2,
        "backup_rotation_count": 10,
        "data_retention_days": 90
    }
}

def apply_config_profile(config: DemocraticConfig, profile_name: str) -> bool:
    """🎭 APLICA PERFIL DE CONFIGURAÇÃO PRÉ-DEFINIDO"""
    
    if profile_name not in PROFILE_CONFIGS:
        print(f"❌ Perfil '{profile_name}' não encontrado")
        return False
    
    profile = PROFILE_CONFIGS[profile_name]
    
    for key, value in profile.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    print(f"✅ Perfil '{profile_name}' aplicado")
    return True

# ===== VALIDAÇÕES =====

def validate_democratic_config(config: DemocraticConfig) -> List[str]:
    """✅ VALIDA CONFIGURAÇÃO DEMOCRÁTICA"""
    
    issues = []
    
    # Validar conta Microsoft
    if not config.target_microsoft_account or "@" not in config.target_microsoft_account:
        issues.append("target_microsoft_account deve ser um email válido")
    
    # Validar intervalos
    if config.heartbeat_interval_sec < 10:
        issues.append("heartbeat_interval_sec deve ser >= 10")
    
    if config.health_check_interval_sec < 5:
        issues.append("health_check_interval_sec deve ser >= 5")
    
    if config.prediction_interval_sec < 60:
        issues.append("prediction_interval_sec deve ser >= 60")
    
    # Validar limites de performance
    if config.max_cpu_usage_percent > 95:
        issues.append("max_cpu_usage_percent deve ser <= 95")
    
    if config.max_memory_usage_percent > 90:
        issues.append("max_memory_usage_percent deve ser <= 90")
    
    # Validar retenção de dados
    if config.metrics_retention_hours < 24:
        issues.append("metrics_retention_hours deve ser >= 24")
    
    if config.data_retention_days < 7:
        issues.append("data_retention_days deve ser >= 7")
    
    # Validar automação
    valid_automation = ["MANUAL", "SUPERVISED", "SEMI_AUTO", "FULL_AUTO"]
    if config.default_automation_level not in valid_automation:
        issues.append(f"default_automation_level deve ser um de: {valid_automation}")
    
    return issues

# ===== EXEMPLE DE USO =====

def create_william_config() -> DemocraticConfig:
    """👤 CRIA CONFIGURAÇÃO ESPECÍFICA PARA WILLIAM"""
    
    config = DemocraticConfig()
    
    # Configurações específicas
    config.target_microsoft_account = "williamkelvem64@gmail.com"
    
    # Habilitar todas features
    config.enabled_features = set(DemocraticFeature)
    
    # Configurações otimizadas para desenvolvimento
    config.default_automation_level = "SEMI_AUTO"
    config.enable_automatic_takeover = True
    config.takeover_confirmation_required = False
    config.emergency_automation_override = True
    
    # Intervalos otimizados
    config.health_check_interval_sec = 15
    config.metrics_collection_interval_sec = 30
    config.optimization_interval_sec = 300
    
    # Retenção de dados
    config.metrics_retention_hours = 168  # 1 semana
    config.data_retention_days = 30
    config.backup_rotation_count = 5
    
    # Features avançadas
    config.google_drive_integration = True
    config.audit_all_actions = True
    config.energy_save_priority = True
    
    return config

# Para uso:
# config_manager = DemocraticConfigManager("/path/to/jarvis")
# config = config_manager.load_config()
# 
# # Ou aplicar perfil
# apply_config_profile(config, "development")
# config_manager.save_config()