# Integração local com modelos LLM (Llama.cpp, GPT4All, DeepSeek)

import subprocess
import os

class LocalLLM:
    def __init__(self, model_path: str, backend: str = "llama.cpp"):
        self.model_path = model_path
        self.backend = backend

    def generate(self, prompt: str) -> str:
        # Exemplo para Llama.cpp (ajuste conforme o backend/modelo)
        if self.backend == "llama.cpp":
            result = subprocess.run([
                "llama.cpp", "--model", self.model_path, "--prompt", prompt, "--n_predict", "128"
            ], capture_output=True, text=True)
            return result.stdout
        # Adicione outros backends aqui
        return "[LLM local não configurado]"
