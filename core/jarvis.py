# Estrutura de inicialização do Jarvis

from core.config import Config
from core.logger import logger
from core.plugins_manager import PluginManager

class Jarvis:
    def __init__(self):
        self.config = Config()
        self.plugins = PluginManager()
        logger.info("Jarvis inicializado.")

    def process(self, text: str):
        logger.info(f"Processando: {text}")
        responses = self.plugins.process_all(text)
        return responses
