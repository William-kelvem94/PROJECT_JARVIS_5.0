import os
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # --- PROJETO ---
    PROJECT_NAME: str = "JARVIS 5.0"
    VERSION: str = "5.3-Engineering"
    BASE_DIR: Path = Path(__file__).resolve().parents[2]
    # --- HARDWARE ADAPTIVE (Book2 vs Desktop) ---
    DEVICE_TYPE: str = "auto" # auto, cuda, cpu
    LOW_VRAM_MODE: bool = True # Ativa se < 6GB VRAM (como a 1050Ti)
    CPU_THREADS: int = os.cpu_count() or 4
    
    # --- IA & BRAIN ---
    LM_STUDIO_URL: str = os.getenv("LM_STUDIO_URL", "http://127.0.0.1:1234/v1/chat/completions")
    DEFAULT_MODEL: str = os.getenv("LM_STUDIO_MODEL", "llama-3.2-3b-instruct")
    AI_TEMPERATURE: float = 0.2
    MAX_TOKENS: int = 4096
    LM_STUDIO_TIMEOUT: int = 15 # Aumentado para o i3 lidar com a carga
    
    # --- PERCEPÇÃO VISUAL ---
    # No Desktop (1050Ti), usamos GPU. No Book2, usamos CPU (OpenVINO/CPU)
    VISION_DELEGATE: str = "CPU" # Será ajustado dinamicamente
    
    # --- PERCEPÇÃO DE VOZ ---
    # No i3 (Desktop), usamos 'tiny' para não travar o sistema. No i7 (Book2), podemos usar 'base'.
    STT_MODEL: str = os.getenv("JARVIS_WHISPER_MODEL", "tiny")
    WHISPER_COMPUTE_TYPE: str = "int8" # Crucial para 16GB de RAM e SSD DRAM-less
    
    # --- MEMÓRIA & GC ---
    ENABLE_GC: bool = True
    AGGRESSIVE_GC_THRESHOLD: float = 85.0 # Porcentagem de RAM
    
    # --- SEGURANÇA & CLOUD FALLBACK ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    
    # --- FRONTEND ---
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    TTS_VOICE: str = "pt-BR-FranciscaNeural"
    
    class Config:
        env_file = ".env"

settings = Settings()

# Lógica de Maestria de Hardware
import torch
if settings.DEVICE_TYPE == "auto":
    if torch.cuda.is_available():
        # Perfil Desktop (1050Ti)
        vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        if vram < 5:
             settings.LOW_VRAM_MODE = True
             settings.STT_MODEL = "tiny" # Poupa VRAM para a visão
        settings.DEVICE_TYPE = "cuda"
        settings.VISION_DELEGATE = "GPU"
    else:
        # Perfil Book2 (i7)
        settings.DEVICE_TYPE = "cpu"
        settings.VISION_DELEGATE = "CPU"
        settings.STT_MODEL = "base" # O i7 de 12th aguenta o modelo base com folga
