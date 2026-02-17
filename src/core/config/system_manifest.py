#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - System Manifest (Central Configuration Hub)
========================================================
FUNDAÇÃO DO SISTEMA - Unifica todas as configurações em um único barramento.
Define as "leis da física" do sistema JARVIS.

Philosophy:
- Single Source of Truth para configurações (Pydantic)
- Hierarquia clara de precedência
- Fallbacks inteligentes
- Validação automática (Hardware rules, Security, Priorities)
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Literal, ClassVar
from pydantic import BaseModel, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIConfig(BaseModel):
    """Configurações de IA e providers"""

    provider: Literal["gemini", "openai", "anthropic", "ollama", "local"] = Field(
        default="gemini", description="Provedor de IA principal"
    )
    fallback_provider: str = Field(default="ollama", description="Provedor de fallback")
    max_react_turns: int = Field(default=5, ge=1, le=20)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=128)
    timeout_seconds: int = Field(default=30, ge=5)

    # API Keys (sensíveis)
    openai_api_key: Optional[SecretStr] = Field(default=None, alias="OPENAI_API_KEY")
    gemini_api_key: Optional[SecretStr] = Field(default=None, alias="GEMINI_API_KEY")
    anthropic_api_key: Optional[SecretStr] = Field(
        default=None, alias="ANTHROPIC_API_KEY"
    )

    # Configurações do Ollama
    ollama_host: str = Field(default="localhost", description="Host do Ollama")
    ollama_port: int = Field(default=11434, description="Porta do Ollama")
    ollama_model: str = Field(default="llama3", description="Modelo padrão do Ollama")

    @model_validator(mode="after")
    def check_api_keys(self) -> "AIConfig":
        if self.provider == "openai" and not self.openai_api_key:
            raise ValueError("OpenAI API key required for OpenAI provider")
        # Gemini is often used via vertex ai or default credentials too, but warning is good practice
        if self.provider == "gemini" and not self.gemini_api_key:
            logger.warning(
                "Gemini API key not configured explicitly (using environment fallback?)"
            )
        return self


class SystemConfig(BaseModel):
    """Configurações do sistema operacional"""

    debug_mode: bool = Field(default=False, description="Modo de debug")
    safe_mode: bool = Field(default=False, description="Modo de segurança")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    max_workers: int = Field(default=4, ge=1)
    startup_timeout: int = Field(default=60, ge=10)
    shutdown_timeout: int = Field(default=30, ge=5)

    # Paths críticos (resolvidos dinamicamente)
    project_root: Path = Field(default_factory=lambda: Path(os.getcwd()))
    data_path: Path = Field(default_factory=lambda: Path(os.getcwd()) / "data")
    logs_path: Path = Field(default_factory=lambda: Path(os.getcwd()) / "data" / "logs")
    config_path: Path = Field(default_factory=lambda: Path(os.getcwd()) / "config")

    # Performance
    async_enabled: bool = True
    multiprocessing_enabled: bool = True
    memory_limit_mb: int = Field(default=4096, ge=512)

    # Evolution Layer - Protected Files
    core_protected_files: List[str] = Field(
        default_factory=lambda: [
            "main.py",
            "src/core/infrastructure/*",
            "src/core/config/system_manifest.py",
            "src/core/config/blackbox_logger.py",
            "src/core/engine/*",
            "src/evolution/evolution_manager.py",
            "src/evolution/authorization_manager.py",
            "src/evolution/safe_executor.py",
        ]
    )


class NetworkConfig(BaseModel):
    """Configurações de rede"""

    enabled: bool = False
    mesh_enabled: bool = False
    port: int = Field(default=8765, ge=1024, le=65535)
    max_connections: int = 10
    timeout_seconds: int = 10
    encryption_enabled: bool = True

    # Google Drive
    google_drive_enabled: bool = False
    google_drive_sync_interval: int = 300

    # Local Network
    local_network_enabled: bool = False
    broadcast_enabled: bool = False


class VisionConfig(BaseModel):
    """Configurações de visão"""

    enabled: bool = True
    ocr_enabled: bool = True
    face_detection_enabled: bool = True
    screenshot_timeout: float = 5.0
    zero_disk_io: bool = True

    # Modelos
    yolo_enabled: bool = True
    yolo_model_path: Optional[str] = None

    # Performance
    max_fps: int = Field(default=1, ge=1, le=60)
    resize_factor: float = Field(default=0.5, ge=0.1, le=1.0)


class AudioConfig(BaseModel):
    """Configurações de áudio"""

    enabled: bool = True
    input_device: Optional[str] = None
    output_device: Optional[str] = None
    sample_rate: int = 16000
    chunk_size: int = 1024

    # Voice Recognition
    speech_recognition_enabled: bool = True
    wake_word_enabled: bool = True
    wake_word: str = "jarvis"

    # Text-to-Speech
    tts_enabled: bool = True
    tts_voice: str = "default"
    tts_speed: float = 1.0

    # Hardware Lock Override (Force headless behavior)
    force_headless: bool = False


class DatabaseConfig(BaseModel):
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


class SecurityConfig(BaseModel):
    """Configurações de segurança"""

    hitl_enabled: bool = Field(default=True, description="Human-In-The-Loop Protocol")
    semantic_validation: bool = True
    max_risk_score: float = 0.8

    # Hardware Lock Rules
    require_hardware_acceleration: bool = True
    allow_cpu_fallback: bool = False  # Strict Hardware Lock by default


class SystemManifest(BaseSettings):
    """
    Manifesto Central do Sistema JARVIS (Pydantic Edition)
    Consolida todas as configurações do sistema.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    ai: AIConfig = Field(default_factory=AIConfig)
    system: SystemConfig = Field(default_factory=SystemConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    vision: VisionConfig = Field(default_factory=VisionConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    _instance: ClassVar[Optional["SystemManifest"]] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._post_init_setup()

    def _post_init_setup(self):
        """Setup paths and logging after initialization"""
        # Ensure critical directories exist
        self.system.data_path.mkdir(parents=True, exist_ok=True)
        self.system.logs_path.mkdir(parents=True, exist_ok=True)
        self.system.config_path.mkdir(parents=True, exist_ok=True)

        # Configure logging level based on config
        logger.setLevel(getattr(logging, self.system.log_level))

    @classmethod
    def get_instance(cls):
        """Singleton Accessor"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def validate_hardware_requirements(self) -> Dict[str, bool]:
        """Verifica se os requisitos de hardware estão alinhados com o manifesto"""
        report = {"acceleration": False, "vector_db": False, "compatible": False}

        # Placeholder for actual checks - usually delegate to HardwareManager
        # Here we just reflect the strictness of the config
        if (
            self.security.require_hardware_acceleration
            and not self.security.allow_cpu_fallback
        ):
            logger.info("🔒 Strict Hardware Lock Active: Acceleration Required")

        return report

    # ------------------------------------------------------------------
    # Backward-compatibility aliases (legacy code expects flat attributes)
    # ------------------------------------------------------------------
    @property
    def project_root(self) -> Path:
        return self.system.project_root

    @property
    def data_path(self) -> Path:
        return self.system.data_path

    @property
    def logs_path(self) -> Path:
        return self.system.logs_path

# Global instance
system_manifest = SystemManifest.get_instance()

if __name__ == "__main__":
    print("🧪 System Manifest Validation")
    print("=" * 50)
    print(system_manifest.model_dump_json(indent=2))
