"""
Application Configuration Management
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
import secrets


class Settings(BaseSettings):
    """
    Application settings with validation
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Application
    APP_NAME: str = "Jarvis AI Assistant"
    VERSION: str = "3.0.0"
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
    DEBUG: bool = True
    LOG_LEVEL: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    
    # Security
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    POSTGRES_USER: str = "jarvis"
    POSTGRES_PASSWORD: str = "jarvis_secret"
    POSTGRES_DB: str = "jarvis_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = None
    
    @validator("DATABASE_URL", pre=True, always=True)
    def assemble_db_connection(cls, v, values):
        if v:
            return v
        return (
            f"postgresql+asyncpg://{values.get('POSTGRES_USER')}:"
            f"{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_HOST')}:"
            f"{values.get('POSTGRES_PORT')}/{values.get('POSTGRES_DB')}"
        )
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = None
    
    @validator("REDIS_URL", pre=True, always=True)
    def assemble_redis_connection(cls, v, values):
        if v:
            return v
        return f"redis://{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}/{values.get('REDIS_DB')}"
    
    # Ollama
    OLLAMA_URL: str = "http://ollama:11434"
    OLLAMA_DEFAULT_MODEL: str = "llama2"
    OLLAMA_TIMEOUT: int = 120
    
    # External APIs (Optional)
    OPENAI_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    ALEXA_CLIENT_ID: str = ""
    ALEXA_CLIENT_SECRET: str = ""
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:80"]
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    # Voice
    WHISPER_MODEL: str = "base"
    TTS_ENGINE: str = "pyttsx3"
    
    # Application Limits
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    SESSION_TIMEOUT: int = 3600  # 1 hour
    MAX_CONNECTIONS_PER_USER: int = 5
    MAX_MESSAGE_LENGTH: int = 4096
    MAX_HISTORY_SIZE: int = 100
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MESSAGE_QUEUE_SIZE: int = 100
    
    # Plugins
    PLUGINS_DIR: str = "app/plugins"
    ENABLE_PLUGIN_HOT_RELOAD: bool = True
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    SENTRY_DSN: str = ""
    
    class Config:
        case_sensitive = True


# Global settings instance
settings = Settings()

