import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

# Chain load: root .env → env/.env (override)
base_dir = Path(__file__).resolve().parents[1]  # PROJECT_JARVIS_5.0 root
load_dotenv(base_dir / '.env')
load_dotenv(base_dir / 'env' / '.env', override=True)

class Settings(BaseSettings):
    # API Keys
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")

    # Ports
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")

    # Frontend
    frontend_url: str = Field(default="http://localhost:3000", alias="FRONTEND_URL")

    # Knowledge Base Paths
    jarvis_kb_path: str = Field(default="", alias="JARVIS_KB_PATH")
    jarvis_api_url: str = Field(default="http://localhost:8000", alias="JARVIS_API_URL")
    jarvis_vault_root: str = Field(default="", alias="JARVIS_VAULT_ROOT")

    # Toggles
    debug_mode: bool = Field(default=False, alias="DEBUG_MODE")
    enable_perception: bool = Field(default=True)

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("google_api_key", mode="before")
    @classmethod
    def fallback_google_api_key(cls, v):
        if v:
            return v
        return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or v

    @field_validator("google_api_key")
    @classmethod
    def validate_keys(cls, v):
        if not v or v.startswith("YOUR_"):
            # Apenas avisa mas não bloqueia o carregamento para não travar o sistema totalmente se o usuário ainda for configurar
            print(f"AVISO: Chave API Google inválida ou não configurada: {v}")
            return v
        return v

settings = Settings()

