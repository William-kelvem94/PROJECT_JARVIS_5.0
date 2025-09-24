# Estrutura de configuração do Jarvis

import json

class Config:
    def __init__(self, path="config/config.json"):
        with open(path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def get(self, key, default=None):
        return self.data.get(key, default)
