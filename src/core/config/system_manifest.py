#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - System Manifest (Central Configuration Hub)
========================================================
FUNDAÇÃO DO SISTEMA - Unifica todas as configurações em um único barramento.
Define as "leis da física" do sistema JARVIS.

Este módulo centraliza:
- Variáveis de ambiente (.env)
- Configurações JSON
- Configurações YAML
- Configurações runtime dinâmicas
- Hierarquia de prioridades

Philosophy:
- Single Source of Truth para configurações
- Hierarquia clara de precedência
- Fallbacks inteligentes
- Validação automática
- Hot-reload quando possível

Usage:
    from src.core.config.system_manifest import system_manifest
    
    # Acesso direto às configurações
    ai_provider = system_manifest.ai.provider
    debug_mode = system_manifest.system.debug_mode
    
    # Acesso com fallback
    api_key = system_manifest.get('api.openai.key', fallback='default_key')
    
    # Validação de integridade
    health = system_manifest.validate_system()
"""

import os
import json
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union, List
from dataclasses import dataclass, field
from datetime import datetime
import threading

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    """Raised when there's a configuration error"""
    pass

@dataclass
class AIConfig:
    """Configurações de IA e providers"""
    provider: str = "gemini"
    fallback_provider: str = "ollama"
    max_react_turns: int = 5
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout_seconds: int = 30
    
    # API Keys (sensíveis)
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Configurações do Ollama
    ollama_host: str = "localhost"
    ollama_port: int = 11434
    ollama_model: str = "llama2"

@dataclass
class SystemConfig:
    """Configurações do sistema operacional"""
    debug_mode: bool = False
    safe_mode: bool = False
    log_level: str = "INFO"
    max_workers: int = 4
    startup_timeout: int = 60
    shutdown_timeout: int = 30
    
    # Paths críticos
    project_root: Path = None
    data_path: Path = None
    logs_path: Path = None
    config_path: Path = None
    
    # Performance
    async_enabled: bool = True
    multiprocessing_enabled: bool = True
    memory_limit_mb: int = 4096
    
    # Evolution Layer - Protected Files
    # These files cannot be auto-modified without explicit human authorization
    core_protected_files: List[str] = field(default_factory=lambda: [
        "main.py",
        "src/core/infrastructure/*",
        "src/core/config/system_manifest.py",
        "src/core/config/blackbox_logger.py",
        "src/core/engine/*",
        "src/evolution/evolution_manager.py",
        "src/evolution/authorization_manager.py",
        "src/evolution/safe_executor.py"
    ])

@dataclass
class NetworkConfig:
    """Configurações de rede"""
    enabled: bool = False
    mesh_enabled: bool = False
    port: int = 8765
    max_connections: int = 10
    timeout_seconds: int = 10
    encryption_enabled: bool = True
    
    # Google Drive
    google_drive_enabled: bool = False
    google_drive_sync_interval: int = 300
    
    # Local Network
    local_network_enabled: bool = False
    broadcast_enabled: bool = False

@dataclass
class VisionConfig:
    """Configurações de visão"""
    enabled: bool = True
    ocr_enabled: bool = True
    face_detection_enabled: bool = True
    screenshot_timeout: float = 5.0
    zero_disk_io: bool = True  # Não salvar PNGs por padrão
    
    # Modelos
    yolo_enabled: bool = False
    yolo_model_path: Optional[str] = None
    
    # Performance
    max_fps: int = 1
    resize_factor: float = 0.5

@dataclass
class AudioConfig:
    """Configurações de áudio"""
    enabled: bool = True
    input_device: Optional[str] = None
    output_device: Optional[str] = None
    sample_rate: int = 16000
    chunk_size: int = 1024
    
    # Voice Recognition
    speech_recognition_enabled: bool = True
    wake_word_enabled: bool = False
    wake_word: str = "jarvis"
    
    # Text-to-Speech
    tts_enabled: bool = True
    tts_voice: str = "default"
    tts_speed: float = 1.0

@dataclass
class DatabaseConfig:
    """Configurações de banco de dados"""
    vector_store_enabled: bool = True
    vector_store_path: str = "data/memory/vector_store"
    
    # SQLite para logs
    log_database_enabled: bool = True
    log_database_path: str = "data/logs/blackbox.db"
    
    # ChromaDB
    chromadb_enabled: bool = True
    chromadb_telemetry: bool = False
    
    # Backup
    auto_backup: bool = True
    backup_interval_hours: int = 24
    max_backup_versions: int = 5

class SystemManifest:
    """
    Manifesto Central do Sistema JARVIS
    
    Consolida todas as configurações do sistema em uma única interface,
    definindo as "leis da física" do JARVIS.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Discover project root
        self.project_root = self._discover_project_root()
        
        # Initialize configuration objects
        self.ai = AIConfig()
        self.system = SystemConfig()
        self.network = NetworkConfig()
        self.vision = VisionConfig()
        self.audio = AudioConfig()
        self.database = DatabaseConfig()
        
        # Configuration sources priority (ordered)
        self._config_sources = []
        
        # Load configurations in order of priority
        self._load_all_configurations()
        
        # Post-process and validate
        self._post_process_config()
        self._validate_critical_config()
        
        self._initialized = True
        logger.info("✅ System Manifest initialized - Configuration hierarchy established")
    
    def _discover_project_root(self) -> Path:
        """Discover project root directory"""
        current = Path(__file__).resolve()
        
        # Look for main.py or other markers
        for parent in current.parents:
            if (parent / "main.py").exists() or (parent / "jarvis.bat").exists():
                return parent
                
        # Fallback
        return current.parent.parent.parent.parent
    
    def _load_all_configurations(self):
        """Load all configuration sources in priority order"""
        logger.info("📂 Loading configuration hierarchy...")
        
        # 1. Load defaults (already done in dataclass definitions)
        
        # 2. Load .env file
        self._load_env_config()
        
        # 3. Load YAML config files
        self._load_yaml_configs()
        
        # 4. Load JSON config files
        self._load_json_configs()
        
        # 5. Apply environment variable overrides
        self._apply_env_overrides()
        
        logger.info(f"📊 Loaded {len(self._config_sources)} configuration sources")
    
    def _load_env_config(self):
        """Load .env file"""
        env_file = self.project_root / ".env"
        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
                self._config_sources.append(f".env ({env_file})")
                logger.debug("✅ .env file loaded")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load .env: {e}")
    
    def _load_yaml_configs(self):
        """Load YAML configuration files"""
        config_dir = self.project_root / "config"
        if not config_dir.exists():
            return
            
        yaml_files = [
            "network_mesh_config.yaml",
            "vector_store_config.yaml",
            "system_config.yaml",
            "ai_config.yaml"
        ]
        
        for yaml_file in yaml_files:
            yaml_path = config_dir / yaml_file
            if yaml_path.exists():
                try:
                    with open(yaml_path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f) or {}
                        self._apply_yaml_config(data, yaml_file)
                        self._config_sources.append(f"YAML ({yaml_file})")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load {yaml_file}: {e}")
    
    def _apply_yaml_config(self, data: Dict, source_file: str):
        """Apply YAML configuration data to appropriate config objects"""
        
        # Network configuration
        if 'network_mesh' in data:
            nm = data['network_mesh']
            self.network.enabled = nm.get('enabled', self.network.enabled)
            self.network.port = nm.get('port', self.network.port)
            self.network.encryption_enabled = nm.get('privacy', {}).get('encrypt_packets', self.network.encryption_enabled)
            
            if 'google_drive' in nm:
                gd = nm['google_drive']
                self.network.google_drive_enabled = gd.get('enabled', self.network.google_drive_enabled)
                self.network.google_drive_sync_interval = gd.get('sync_interval', self.network.google_drive_sync_interval)
        
        # Vector store configuration
        if 'vector_store' in data:
            vs = data['vector_store']
            self.database.vector_store_enabled = vs.get('enabled', self.database.vector_store_enabled)
            self.database.vector_store_path = vs.get('path', self.database.vector_store_path)
            
            if 'chromadb' in vs:
                cdb = vs['chromadb']
                self.database.chromadb_telemetry = cdb.get('anonymized_telemetry', self.database.chromadb_telemetry)
        
        # System configuration
        if 'system' in data:
            sys_cfg = data['system']
            self.system.debug_mode = sys_cfg.get('debug_mode', self.system.debug_mode)
            self.system.log_level = sys_cfg.get('log_level', self.system.log_level)
        
        # AI configuration
        if 'ai' in data:
            ai_cfg = data['ai']
            self.ai.provider = ai_cfg.get('provider', self.ai.provider)
            self.ai.temperature = ai_cfg.get('temperature', self.ai.temperature)
            self.ai.max_tokens = ai_cfg.get('max_tokens', self.ai.max_tokens)
    
    def _load_json_configs(self):
        """Load JSON configuration files"""
        config_dir = self.project_root / "config"
        if not config_dir.exists():
            return
            
        json_files = list(config_dir.glob("*.json"))
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Apply JSON config similar to YAML
                    self._config_sources.append(f"JSON ({json_file.name})")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load {json_file.name}: {e}")
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides"""
        env_mappings = {
            # AI Configuration
            'JARVIS_AI_PROVIDER': ('ai', 'provider'),
            'JARVIS_AI_TEMPERATURE': ('ai', 'temperature', float),
            'JARVIS_AI_MAX_TOKENS': ('ai', 'max_tokens', int),
            'OPENAI_API_KEY': ('ai', 'openai_api_key'),
            'GEMINI_API_KEY': ('ai', 'gemini_api_key'),
            
            # System Configuration
            'JARVIS_DEBUG_MODE': ('system', 'debug_mode', bool),
            'JARVIS_LOG_LEVEL': ('system', 'log_level'),
            'JARVIS_SAFE_MODE': ('system', 'safe_mode', bool),
            
            # Network Configuration
            'JARVIS_NETWORK_PORT': ('network', 'port', int),
            'JARVIS_NETWORK_ENABLED': ('network', 'enabled', bool),
            
            # Vision Configuration
            'JARVIS_VISION_ENABLED': ('vision', 'enabled', bool),
            'JARVIS_ZERO_DISK_IO': ('vision', 'zero_disk_io', bool),
        }
        
        for env_var, config_path in env_mappings.items():
            if env_var in os.environ:
                try:
                    section = config_path[0]
                    attr = config_path[1]
                    converter = config_path[2] if len(config_path) > 2 else str
                    
                    value = os.environ[env_var]
                    if converter == bool:
                        value = value.lower() in ('true', '1', 'yes', 'on')
                    elif converter != str:
                        value = converter(value)
                    
                    config_obj = getattr(self, section)
                    setattr(config_obj, attr, value)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to apply env override {env_var}: {e}")
    
    def _post_process_config(self):
        """Post-process configuration after loading"""
        
        # Set critical paths
        self.system.project_root = self.project_root
        self.system.data_path = self.project_root / "data"
        self.system.logs_path = self.project_root / "data" / "logs"
        self.system.config_path = self.project_root / "config"
        
        # Ensure directories exist
        self.system.data_path.mkdir(parents=True, exist_ok=True)
        self.system.logs_path.mkdir(parents=True, exist_ok=True)
        self.system.config_path.mkdir(parents=True, exist_ok=True)
        
        # Convert relative paths to absolute
        if not Path(self.database.vector_store_path).is_absolute():
            self.database.vector_store_path = str(self.project_root / self.database.vector_store_path)
        
        if not Path(self.database.log_database_path).is_absolute():
            self.database.log_database_path = str(self.project_root / self.database.log_database_path)
    
    def _validate_critical_config(self):
        """Validate critical configuration requirements"""
        errors = []
        warnings = []
        
        # AI Provider validation
        supported_providers = ['gemini', 'openai', 'anthropic', 'ollama', 'local']
        if self.ai.provider not in supported_providers:
            errors.append(f"Unsupported AI provider: {self.ai.provider}")
        
        # API Key validation for cloud providers
        if self.ai.provider == 'openai' and not self.ai.openai_api_key:
            errors.append("OpenAI API key required for OpenAI provider")
        elif self.ai.provider == 'gemini' and not self.ai.gemini_api_key:
            warnings.append("Gemini API key not configured, will use fallback")
        
        # Path validation
        if not self.system.project_root.exists():
            errors.append(f"Project root does not exist: {self.system.project_root}")
        
        # Log critical issues
        for error in errors:
            logger.error(f"❌ Configuration Error: {error}")
            
        for warning in warnings:
            logger.warning(f"⚠️ Configuration Warning: {warning}")
        
        if errors:
            raise ConfigurationError(f"Critical configuration errors: {errors}")
    
    def get(self, key_path: str, fallback: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Examples:
            get('ai.provider')
            get('system.debug_mode')
            get('network.port', 8080)
        """
        try:
            parts = key_path.split('.')
            obj = self
            
            for part in parts:
                obj = getattr(obj, part)
            
            return obj
        except AttributeError:
            return fallback
    
    def set(self, key_path: str, value: Any) -> bool:
        """
        Set configuration value using dot notation (runtime only)
        
        Examples:
            set('ai.temperature', 0.8)
            set('system.debug_mode', True)
        """
        try:
            parts = key_path.split('.')
            obj = self
            
            # Navigate to parent object
            for part in parts[:-1]:
                obj = getattr(obj, part)
            
            # Set the final attribute
            setattr(obj, parts[-1], value)
            return True
        except AttributeError:
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        return {
            "project_root": str(self.system.project_root),
            "config_sources": self._config_sources,
            "ai_provider": self.ai.provider,
            "debug_mode": self.system.debug_mode,
            "network_enabled": self.network.enabled,
            "vision_enabled": self.vision.enabled,
            "audio_enabled": self.audio.enabled,
            "vector_store_enabled": self.database.vector_store_enabled,
            "log_database_enabled": self.database.log_database_enabled,
            "initialized_at": datetime.now().isoformat()
        }
    
    def validate_system(self) -> Dict[str, Any]:
        """Perform system validation and health check"""
        validation_result = {
            "status": "healthy",
            "errors": [],
            "warnings": [],
            "checks": {}
        }
        
        try:
            # Check project structure
            validation_result["checks"]["project_root"] = self.system.project_root.exists()
            validation_result["checks"]["data_directory"] = self.system.data_path.exists()
            validation_result["checks"]["config_directory"] = self.system.config_path.exists()
            
            # Check AI configuration
            validation_result["checks"]["ai_provider_configured"] = bool(self.ai.provider)
            
            # Check database paths
            vector_store_parent = Path(self.database.vector_store_path).parent
            validation_result["checks"]["vector_store_path"] = vector_store_parent.exists()
            
            log_db_parent = Path(self.database.log_database_path).parent
            validation_result["checks"]["log_database_path"] = log_db_parent.exists()
            
            # Overall health
            failed_checks = [k for k, v in validation_result["checks"].items() if not v]
            if failed_checks:
                validation_result["status"] = "degraded"
                validation_result["warnings"].extend([f"Failed check: {check}" for check in failed_checks])
            
        except Exception as e:
            validation_result["status"] = "error"
            validation_result["errors"].append(str(e))
        
        return validation_result
    
    def reload_configuration(self) -> bool:
        """Reload configuration from files (hot-reload)"""
        try:
            logger.info("🔄 Reloading system configuration...")
            
            # Reset configuration sources
            self._config_sources = []
            
            # Reload all configurations
            self._load_all_configurations()
            self._post_process_config()
            self._validate_critical_config()
            
            logger.info("✅ Configuration reloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Configuration reload failed: {e}")
            return False

# Global instance
system_manifest = SystemManifest()

if __name__ == "__main__":
    # Test the system manifest
    print("🧪 Testing System Manifest")
    print("=" * 50)
    
    info = system_manifest.get_system_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    
    print("\n🔍 Validation Results:")
    validation = system_manifest.validate_system()
    print(f"Status: {validation['status']}")
    if validation['warnings']:
        print(f"Warnings: {validation['warnings']}")
    if validation['errors']:
        print(f"Errors: {validation['errors']}")