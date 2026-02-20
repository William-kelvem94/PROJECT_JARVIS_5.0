import subprocess
import shlex
import json
from typing import Optional


def query_ollama(model: str, prompt: str, timeout: int = 60) -> str:
    """Minimal wrapper that calls the local `ollama` CLI.

    Falls back to an informative error if the CLI isn't available.
    """
    try:
        # Use `ollama chat <model> --prompt "..."` if available
        cmd = ["ollama", "chat", model, "--prompt", prompt]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if proc.returncode == 0 and proc.stdout:
            return proc.stdout.strip()
        # sometimes ollama prints to stderr
        if proc.stderr:
            return proc.stderr.strip()
        raise RuntimeError("'ollama' returned empty output")
    except FileNotFoundError as e:
        raise RuntimeError("`ollama` CLI not found. Ensure Ollama is installed and on PATH.") from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError("Ollama request timed out") from e


if __name__ == "__main__":
    # quick sanity check (manual run)
    try:
        out = query_ollama("llama", "Say hello from Ollama")
        print(out)
    except Exception as e:
        print("Ollama check failed:", e)
