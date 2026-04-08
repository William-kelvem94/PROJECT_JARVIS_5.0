import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Chain load: root .env → env/.env (override)
base_dir = Path(__file__).resolve().parents[3]  # PROJECT_JARVIS_5.0 root
load_dotenv(base_dir / '.env')
load_dotenv(base_dir / 'env' / '.env', override=True)

class Settings(BaseSettings):
    # API Keys
    google_api_key: str = Field(alias="GOOGLE_API_KEY")
    livekit_url: str = Field(alias="LIVEKIT_URL")
    livekit_api_key: str = Field(alias="LIVEKIT_API_KEY")
    livekit_api_secret: str = Field(alias="LIVEKIT_API_SECRET")
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    
    # Ports
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    
    # Frontend
    frontend_url: str = Field(default="http://localhost:3000", alias="FRONTEND_URL")
    
    # Toggles
    debug_mode: bool = Field(default=False, alias="DEBUG_MODE")
    enable_perception: bool = Field(default=True)
    
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore"
    )

from pydantic import field_validator\n\n@field_validator("google_api_key", "livekit_url", "livekit_api_key", "livekit_api_secret")\n@classmethod\ndef validate_keys(cls, v):\n    if not v or v.startswith("YOUR_"):\n        raise ValueError(f"Chave inválida: {v}. Configure .env corretamente.")\n    return v

settings = Settings()

# Next.js compat: Prefix for client-side
NEXT_PUBLIC_LIVEKIT_URL = os.getenv("NEXT_PUBLIC_LIVEKIT_URL", livekit_url)

