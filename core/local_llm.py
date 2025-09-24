# Integração local com modelos LLM (Llama.cpp, GPT4All, DeepSeek)

import subprocess
import os

class LocalLLM:
    def __init__(self, model_path: str, backend: str = "llama.cpp"):
        self.model_path = model_path
        self.backend = backend

    def generate(self, prompt: str) -> str:
        # Resposta fixa para testes locais sem modelo/binário
        return f"Jarvis (simulado): Recebi sua mensagem: '{prompt}'"
