import os
import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_SETTINGS = {
    "HOTWORD": "jarvis",
    "OLLAMA_MODEL": "llama",
    "CONTEXT_WINDOW": 10,
    "SYSTEM_PROMPT": "Você é Jarvis — assistente pessoal que responde de forma útil, sucinta e segura.",
    "DEVICE_LANGUAGE": None,
    "LANGUAGE_VALIDATION": True,
    "TTS_BACKEND_PREFERENCE": ["edge-tts", "pyttsx3"],
    "TTS_EDGE_VOICE": "pt-BR-AntonioNeural",
    "TTS_RATE": 150,
    "TTS_VOLUME": 1.0,
    "TTS_PITCH": "+0Hz",
    "USE_WHISPER": False,
    "USE_LOCAL_BRAIN": True,
    "AUTO_TRAIN": True,
}

class ConfigManager:
    def __init__(self, config_path: str = "data/settings.json"):
        self.config_path = config_path
        self.settings = DEFAULT_SETTINGS.copy()
        self._load()

    def _load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    user_settings = json.load(f)
                    self.settings.update(user_settings)
                logger.info(f"Configuração carregada de {self.config_path}")
            except Exception as e:
                logger.error(f"Erro ao carregar configurações: {e}")
        else:
            self.save() # save defaults

    def save(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            logger.info(f"Configuração salva em {self.config_path}")
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        self.settings[key] = value
        self.save()

# Global instance
config = ConfigManager()
