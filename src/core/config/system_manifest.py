import os
import logging
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, SecretStr
from pathlib import Path
from dotenv import load_dotenv

# Configuração de logger básico para este módulo
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SYSTEM-MANIFEST")

# Carrega variáveis de ambiente (prioridade sobre defaults)
load_dotenv()

# --- Definições de Caminhos Base ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"
MEMORY_DIR = DATA_DIR / "memory"

class AIModelConfig(BaseModel):
    """Configuração para modelos de IA (Local e Nuvem)"""
    provider: str = Field(..., description="ollama, gemini, openai, local")
    model_name: str = Field(..., description="Nome técnico do modelo (ex: llama3:8b)")
    timeout: int = 30
    context_window: int = 4096
    temperature: float = 0.7

    # Ollama host/port (optional) — some modules reference these directly
    ollama_host: str = "localhost"
    ollama_port: int = 11434
    # Backwards-compatible alias for older modules that reference Ollama model
    ollama_model: str = Field(default_factory=lambda: os.getenv("AI_MODEL", "llama3:8b"))

class VisionConfig(BaseModel):
    """Configuração do Sistema de Visão (Heimdall)"""
    enabled: bool = True
    camera_index: int = 0
    resolution: tuple = (1280, 720)
    use_gpu: bool = True
    # Zero-Disk-IO: Define se salva capturas no disco (Falso por padrão para performance)
    save_captures_to_disk: bool = False 
    face_recognition_enabled: bool = True
    yolo_model_path: str = "yolov8n.pt"
    multiprocessing_enabled: bool = True
    # Use um 'mock' de câmera (black frame / noise) para CI/testes quando não houver hardware
    mock_camera: bool = False

class AudioConfig(BaseModel):
    """Configuração de Áudio e Voz"""
    input_device_index: Optional[int] = None
    output_device_index: Optional[int] = None
    wake_word: str = "jarvis"
    wake_word_sensitivity: float = 0.5
    tts_engine: str = "edge-tts" # edge-tts, coqui, pyttsx3
    voice_name: str = "pt-BR-AntonioNeural" # Exemplo para Edge-TTS
    # Executar o subsistema de áudio em processo separado para evitar bloqueios
    multiprocessing_enabled: bool = True

class SecurityConfig(BaseModel):
    """Configurações de Segurança e Permissões"""
    sandbox_mode: bool = True
    allowed_shell_commands: List[str] = ["echo", "dir", "ls", "whoami"]
    require_voice_auth: bool = False
    admin_users: List[str] = ["William"]

    # New flags used by orchestrator and security subsystems
    require_hardware_acceleration: bool = False
    allow_cpu_fallback: bool = True
    semantic_validation: bool = False


class NetworkConfig(BaseModel):
    """Configuração do Network Mesh (usada por Boot Manager e Network modules)"""
    enabled: bool = True
    discovery_port: int = 5000
    device_name: str = "JARVIS-PRIMARY"
    group_id: str = "STARK-CLUSTER-01"
    encryption_enabled: bool = True
    auth_token: Optional[SecretStr] = None
    sync_interval_seconds: int = 60
    sync_memory: bool = True
    sync_learning: bool = True


class SystemManifest(BaseModel):
    """
    O DNA do JARVIS. 
    Centraliza todas as configurações em um objeto validado.
    """
    system_name: str = "JARVIS"
    version: str = "5.0.0-Singularity"
    debug_mode: bool = True

    # Explicit project_root field for compatibility with older modules/tests
    project_root: Path = BASE_DIR
    
    # Sub-configurações
    ai: AIModelConfig
    vision: VisionConfig
    audio: AudioConfig
    security: SecurityConfig
    network: NetworkConfig
    
    # Caminhos Críticos
    paths: Dict[str, Path] = {
        "base": BASE_DIR,
        "logs": LOG_DIR,
        "memory": MEMORY_DIR,
        "vector_store": MEMORY_DIR / "vector_store"
    }

    # Backwards-compatible helpers expected by legacy modules/tests
    @property
    def system(self):
        from types import SimpleNamespace

        return SimpleNamespace(
            data_path=DATA_DIR,
            logs_path=self.paths.get("logs", LOG_DIR),
        )

    @property
    def database(self):
        from types import SimpleNamespace

        return SimpleNamespace(
            vector_store_path=self.paths.get("vector_store", MEMORY_DIR / "vector_store")
        )

    @classmethod
    def load_system(cls) -> "SystemManifest":
        """Carrega configurações do ambiente ou usa defaults seguros."""
        # Mesh auth token (opcional) lido do .env
        mesh_token = os.getenv("MESH_AUTH_TOKEN")

        return cls(
            ai=AIModelConfig(
                provider=os.getenv("AI_PROVIDER", "ollama"),
                model_name=os.getenv("AI_MODEL", "llama3:8b"),
            ),
            vision=VisionConfig(
                save_captures_to_disk=False,  # Forçando Zero-IO
                mock_camera=(os.getenv("JARVIS_VISION_MOCK", "0") == "1"),
            ),
            audio=AudioConfig(),
            security=SecurityConfig(),
            network=NetworkConfig(
                enabled=(os.getenv("NETWORK_ENABLED", "1") == "1"),
                auth_token=SecretStr(mesh_token) if mesh_token else None,
            ),
        )

# Instância Global (Singleton)
try:
    sys_config = SystemManifest.load_system()
    # Alias para compatibilidade se necessário
    system_manifest = sys_config

    # Backwards-compatible attributes expected in various modules/tests
    try:
        # project_root used in older modules — set via object.__setattr__ because
        # SystemManifest is a Pydantic model and disallows arbitrary attrs by default
        object.__setattr__(sys_config, "project_root", BASE_DIR)
    except Exception:
        pass

    # Cria diretórios essenciais se não existirem
    sys_config.paths["logs"].mkdir(parents=True, exist_ok=True)
    sys_config.paths["vector_store"].mkdir(parents=True, exist_ok=True)
    
    logger.info("✅ SystemManifest carregado com sucesso.")
except Exception as e:
    print(f"CRITICAL: Falha ao carregar SystemManifest: {e}")
    raise e
