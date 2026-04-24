import os
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # --- PROJETO ---
    PROJECT_NAME: str = "JARVIS 5.0"
    VERSION: str = "5.3-Engineering"
    BASE_DIR: Path = Path(__file__).resolve().parents[2]
    
    # --- IA & BRAIN ---
    LM_STUDIO_URL: str = os.getenv("LM_STUDIO_URL", "http://127.0.0.1:1234/v1/chat/completions")
    DEFAULT_MODEL: str = os.getenv("LM_STUDIO_MODEL", "llama-3.2-3b-instruct")
    AI_TEMPERATURE: float = 0.2
    MAX_TOKENS: int = 4096
    
    # --- PERCEPÇÃO VISUAL ---
    FACE_CONFIDENCE: float = 0.5
    FACE_ENROLLED_THRESHOLD: float = 0.6 # dlib distance (lower = stricter)
    GESTURE_CONFIDENCE: float = 0.7
    
    # --- PERCEPÇÃO DE VOZ ---
    SAMPLE_RATE: int = 16000
    WAKE_WORD_THRESHOLD: float = 0.45
    STT_MODEL: str = os.getenv("JARVIS_WHISPER_MODEL", "tiny") # tiny, base, small
    
    # --- SEGURANÇA & CLOUD FALLBACK ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    
    # --- FRONTEND ---
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    class Config:
        env_file = ".env"

settings = Settings()
