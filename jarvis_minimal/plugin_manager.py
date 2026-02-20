import os
import importlib.util
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PluginManager:
    def __init__(self, plugin_dir: str = "src/plugins"):
        self.plugin_dir = plugin_dir
        self.plugins = {}

    def load_plugins(self, agent: Any):
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir, exist_ok=True)
            return

        for root, dirs, files in os.walk(self.plugin_dir):
            for file in files:
                if file.endswith("_plugin.py") or (file.endswith(".py") and root != self.plugin_dir):
                    plugin_path = os.path.join(root, file)
                    self._load_plugin(plugin_path, agent)

    def _load_plugin(self, path: str, agent: Any):
        try:
            module_name = os.path.basename(path)[:-3]
            spec = importlib.util.spec_from_file_location(module_name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, "setup"):
                module.setup(agent)
                self.plugins[module_name] = module
                logger.info(f"Plugin carregado: {module_name}")
        except Exception as e:
            logger.error(f"Erro ao carregar plugin {path}: {e}")

# Global instance
plugin_manager = PluginManager()
