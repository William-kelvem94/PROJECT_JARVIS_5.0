"""
JARVIS 5.0 - Configuração Central com Maestria de Hardware
Detecta automaticamente CPU/GPU e ajusta perfis de performance.
"""

import os
import torch
from pathlib import Path
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # --- PROJETO ---
    PROJECT_NAME: str = "JARVIS 5.0"
    VERSION: str = "5.3-Engineering"
    BASE_DIR: Path = Path(__file__).resolve().parents[2]

    # --- HARDWARE ADAPTIVE ---
    DEVICE_TYPE: str = os.getenv("JARVIS_AI_DEVICE", "cpu")
    GPU_ENABLED: bool = False
    LOW_VRAM_MODE: bool = True
    CPU_THREADS: int = os.cpu_count() or 4
    
    # --- IA & BRAIN ---
    LM_STUDIO_URL: str = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")
    LM_STUDIO_MODEL: str = os.getenv("LM_STUDIO_MODEL", "local-model")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "local-model")
    LM_STUDIO_TIMEOUT: int = 5
    AI_TEMPERATURE: float = 0.2
    MAX_TOKENS: int = 4096

    # --- OLLAMA ---
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    OLLAMA_TIMEOUT: int = 60
    OLLAMA_ENABLED: bool = os.getenv("OLLAMA_ENABLED", "false").lower() == "true"

    # --- CLOUD FALLBACK (Gemini/OpenRouter) ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
    
    # --- PERCEPÇÃO ---
    VISION_DELEGATE: str = "CPU"
    JARVIS_WHISPER_MODEL: str = os.getenv("JARVIS_WHISPER_MODEL", "base")
    WHISPER_COMPUTE_TYPE: str = "int8"
    
    # --- MEMÓRIA & GC ---
    ENABLE_GC: bool = os.getenv("ENABLE_GC", "false").lower() == "true"
    AGGRESSIVE_GC_THRESHOLD: float = 85.0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._detect_hardware()

    def _detect_hardware(self):
        """Auto-detecção de GPU e ajuste de perfil."""
        env_device = os.getenv("JARVIS_AI_DEVICE")
        if env_device:
            self.DEVICE_TYPE = env_device.lower()
            self.GPU_ENABLED = self.DEVICE_TYPE == "cuda"
        elif torch.cuda.is_available():
            self.DEVICE_TYPE = "cuda"
            self.GPU_ENABLED = True
        else:
            self.DEVICE_TYPE = "cpu"
            self.GPU_ENABLED = False

        if self.GPU_ENABLED:
            try:
                vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                self.LOW_VRAM_MODE = vram_gb < 5.0
            except Exception:
                self.LOW_VRAM_MODE = True
        else:
            self.LOW_VRAM_MODE = False

        if self.GPU_ENABLED:
            self.JARVIS_WHISPER_MODEL = os.getenv("JARVIS_WHISPER_MODEL", "tiny")
        else:
            self.JARVIS_WHISPER_MODEL = os.getenv("JARVIS_WHISPER_MODEL", "base")


settings = Settings()
