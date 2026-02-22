import os
import yaml
import logging
from pathlib import Path
from dotenv import load_dotenv

# Initialize Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger("JARVIS-CONFIG")

class Config:
    """Professional Configuration Manager for JARVIS 5.0"""
    
    def __init__(self, project_root: str):
        self.root = Path(project_root)
        load_dotenv(self.root / ".env")
        
        # Default Settings
        self.defaults = {
            "name": "Jarvis",
            "ollama_url": os.getenv("OLLAMA_URL", "http://localhost:11434"),
            "ollama_model": os.getenv("OLLAMA_MODEL", "llama3"),
            "evolution_model": os.getenv("EVOLUTION_MODEL", "deepseek-coder"),
            "language": "pt-BR",
            "voice_enabled": True,
            "research_enabled": True,
            "auto_repair": True
        }
        
        self.settings = self.defaults.copy()
        self._load_from_yaml()

    def _load_from_yaml(self):
        yaml_path = self.root / "config" / "settings.yaml"
        if yaml_path.exists():
            try:
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    user_settings = yaml.safe_load(f)
                    if user_settings:
                        self.settings.update(user_settings)
                logger.info("Settings loaded from YAML.")
            except Exception as e:
                logger.error(f"Error loading YAML settings: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default or self.defaults.get(key))

# Global Instance
config = Config(os.getcwd())
