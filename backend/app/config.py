import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator

load_dotenv()

class Settings(BaseSettings):
    # API Keys & Sensitive Data
    google_api_key: str = Field(alias="GOOGLE_API_KEY")
    livekit_url: str = Field(alias="LIVEKIT_URL")
    livekit_api_key: str = Field(alias="LIVEKIT_API_KEY")
    livekit_api_secret: str = Field(alias="LIVEKIT_API_SECRET")
    
    # Optional Configurations (with defaults)
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    frontend_url: str = Field(default="*", alias="FRONTEND_URL")
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    
    # Technical Toggles
    enable_vanta: bool = Field(default=True)
    debug_mode: bool = Field(default=False)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @validator("google_api_key", "livekit_url", "livekit_api_key", "livekit_api_secret")
    def validate_required_keys(cls, v):
        if not v or v.startswith("YOUR_"):
            raise ValueError(f"A chave '{v}' não parece ser uma credencial válida. Configure seu arquivo .env corretamente.")
        return v

try:
    settings = Settings()
except Exception as e:
    print(f"\n[🚨 CRITICAL] Erro de configuracao detectado: {e}")
    print("[💡 TIP] Certifique-se de que o arquivo env/.env contenha todas as chaves necessarias.")
    # Em produção, poderíamos interromper o processo, mas aqui vamos permitir 
    # para debug inicial se necessário, ou criar um objeto vazio seguro.
    class FakeSettings:
        def __getattr__(self, name): return ""
    settings = FakeSettings()
