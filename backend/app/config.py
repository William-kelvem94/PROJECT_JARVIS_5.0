import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    livekit_url: str = os.getenv("LIVEKIT_URL", "")
    livekit_key: str = os.getenv("LIVEKIT_API_KEY", "")
    livekit_secret: str = os.getenv("LIVEKIT_API_SECRET", "")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))

settings = Settings()
