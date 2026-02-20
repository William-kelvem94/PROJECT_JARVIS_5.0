import subprocess
import shlex
import json
from typing import Optional


def _try_cmd(cmd: list, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def query_ollama(model: str, prompt: str, timeout: int = 60) -> str:
    """Robust wrapper for local `ollama` CLI.

    Tries several CLI variants to support different Ollama versions:
      - `ollama chat <model> --prompt "..."`
      - `ollama run <model> --prompt "..."`
      - `ollama generate <model> --prompt "..."`

    Returns the CLI output or raises a RuntimeError with a helpful message.
    """
    cmds_to_try = [
        ["ollama", "chat", model, "--prompt", prompt],
        ["ollama", "run", model, "--prompt", prompt],
        ["ollama", "generate", model, "--prompt", prompt],
    ]

    for cmd in cmds_to_try:
        try:
            proc = _try_cmd(cmd, timeout=timeout)
        except FileNotFoundError:
            raise RuntimeError("`ollama` CLI not found. Ensure Ollama is installed and on PATH.")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Ollama request timed out")

        # success
        if proc.returncode == 0 and proc.stdout:
            return proc.stdout.strip()

        # specific 'unknown command' errors -> try next
        stderr = (proc.stderr or "").lower()
        if "unknown command" in stderr or "unrecognized command" in stderr:
            continue

        # if command executed but returned non-zero with stderr, return stderr
        if proc.stderr:
            return proc.stderr.strip()

    raise RuntimeError("Could not invoke Ollama CLI with known commands. Run `ollama --help` to inspect your installation.")


if __name__ == "__main__":
    try:
        out = query_ollama("llama", "Say hello from Ollama")
        print(out)
    except Exception as e:
        print("Ollama check failed:", e)
