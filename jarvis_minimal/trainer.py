"""Minimal self‑training / self‑improvement scaffolding.

- Collects interactions (already saved by agent)
- Can run a nightly job to attempt self-improvement (placeholder):
  - runs `pytest` and captures failures
  - asks Ollama for suggested fixes and writes them to ./autofix/
  - (does NOT modify `BACKUP` or commit by default)

This is intentionally conservative: suggestions are stored for review or for later auto-apply.
"""
import os
import subprocess
import json
import time
from typing import List

from .ollama_client import query_ollama
from .config import AUTO_TRAIN


AUTOFIX_DIR = "autofix"
os.makedirs(AUTOFIX_DIR, exist_ok=True)


class SelfTrainer:
    def __init__(self, model: str = "llama"):
        self.model = model

    def run_tests(self) -> str:
        '''Run pytest (if available) and return stdout/stderr.'''
        try:
            proc = subprocess.run(["pytest", "-q"], capture_output=True, text=True, timeout=600)
            return proc.stdout + "\n" + proc.stderr
        except Exception as e:
            return f"pytest failed to run: {e}"

    def request_fix(self, test_output: str) -> str:
        prompt = (
            "Há falhas nos testes. Apresente uma sugestão sucinta de correção de código "
            "(patch) que possa resolver os erros abaixo. Forneça o patch no formato unified diff e explique brevemente.\n\n"
            "Falhas:\n" + test_output
        )
        return query_ollama(self.model, prompt)

    def save_suggestion(self, suggestion: str) -> str:
        ts = int(time.time())
        path = os.path.join(AUTOFIX_DIR, f"suggestion_{ts}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(suggestion)
        return path

    def nightly_job(self):
        if not AUTO_TRAIN:
            return
        print("[trainer] iniciando rotina noturna de auto‑treino...")
        out = self.run_tests()
        if "FAILED" not in out and "error" not in out.lower():
            print("[trainer] sem falhas detectadas.")
            return
        suggestion = self.request_fix(out)
        saved = self.save_suggestion(suggestion)
        print(f"[trainer] sugestão salva em {saved}")


if __name__ == "__main__":
    t = SelfTrainer()
    t.nightly_job()
