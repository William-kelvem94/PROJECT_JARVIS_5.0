# Estrutura de plugins do Jarvis

# Todos os plugins devem implementar o método 'process(text: str) -> str'

import importlib
import os

class PluginManager:
    def __init__(self, plugins_folder="plugins"):
        self.plugins_folder = plugins_folder
        self.plugins = self.load_plugins()

    def load_plugins(self):
        plugins = []
        for file in os.listdir(self.plugins_folder):
            if file.endswith("_plugin.py"):
                module_name = file[:-3]
                module = importlib.import_module(f"plugins.{module_name}")
                plugin_class = [cls for cls in module.__dict__.values() if isinstance(cls, type) and cls.__name__.endswith("Plugin")]
                if plugin_class:
                    plugins.append(plugin_class[0]())
        return plugins

    def process_all(self, text: str):
        results = []
        for plugin in self.plugins:
            results.append(plugin.process(text))
        return results
