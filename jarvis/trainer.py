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
        # load local brain if available for fine-tuning
        try:
            from .local_brain import LocalBrain
            self.brain = LocalBrain()
        except Exception:
            self.brain = None

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
        # 1. run unit tests and collect suggestions
        out = self.run_tests()
        if "FAILED" not in out and "error" not in out.lower():
            print("[trainer] sem falhas detectadas nos testes.")
        else:
            suggestion = self.request_fix(out)
            saved = self.save_suggestion(suggestion)
            print(f"[trainer] sugestão salva em {saved}")
        # 2. fine-tune local brain on interactions (if available)
        if self.brain is not None:
            try:
                print("[trainer] treinando cérebro local com interações...")
                report = self.brain.train_from_file()
                if isinstance(report, dict):
                    ex = report.get("examples")
                    if ex is not None:
                        print(f"[trainer] fine-tuned on {ex} exemplos de interação.")
                    logs = report.get("log_history")
                    if logs:
                        print(f"[trainer] histórico de perda coletado ({len(logs)} registros).")
            except Exception as e:
                print("[trainer] erro ao treinar cérebro local:", e)

if __name__ == "__main__":
    import argparse, sys
    parser = argparse.ArgumentParser(description="Self‑trainer utility")
    parser.add_argument("--plot", action="store_true", help="mostrar gráfico do histórico de perda do cérebro local")
    args = parser.parse_args()
    if args.plot:
        try:
            import json
            import os
            import matplotlib.pyplot as plt
            path = os.path.join(os.path.dirname(__file__), "models", "local_brain", "training_log.json")
            with open(path, encoding="utf-8") as f:
                logs = json.load(f)
            epochs = [l.get("epoch") for l in logs if "epoch" in l]
            losses = [l.get("loss") for l in logs if "loss" in l]
            if epochs and losses:
                plt.plot(epochs, losses, marker="o")
                plt.xlabel("epoch")
                plt.ylabel("loss")
                plt.title("LocalBrain training loss")
                plt.show()
            else:
                print("Nenhum dado de perda disponível para plotagem.")
        except ImportError:
            print("matplotlib não está instalado; instale para visualizar gráficos.")
        except Exception as e:
            print("falha ao gerar gráfico:", e)
        sys.exit(0)
    t = SelfTrainer()
    t.nightly_job()
