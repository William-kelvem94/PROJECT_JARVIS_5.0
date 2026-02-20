import subprocess
import shlex
import json
from typing import Optional


def _try_cmd(cmd: list, timeout: int = 60) -> subprocess.CompletedProcess:
    # use bytes mode and decode ourselves to avoid Windows codepage issues
    return subprocess.run(cmd, capture_output=True, timeout=timeout)


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
        ["ollama", "run", model, prompt],
        ["ollama", "run", model],
        ["ollama", "generate", model, "--prompt", prompt],
    ]

    for cmd in cmds_to_try:
        try:
            # special-case: if `ollama run MODEL` without inline prompt, send prompt via stdin
            if cmd[1] == "run" and len(cmd) == 3:
                proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout)
            else:
                proc = _try_cmd(cmd, timeout=timeout)
        except FileNotFoundError:
            raise RuntimeError("`ollama` CLI not found. Ensure Ollama is installed and on PATH.")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Ollama request timed out")

        # normalize output (decode bytes safely)
        out = proc.stdout.decode("utf-8", errors="replace") if isinstance(proc.stdout, bytes) else proc.stdout or ""
        err = proc.stderr.decode("utf-8", errors="replace") if isinstance(proc.stderr, bytes) else proc.stderr or ""
        # success
        if proc.returncode == 0 and out:
            return out.strip()

        stderr = err.lower()
        # try next if CLI reports unknown command or unknown flag
        if "unknown command" in stderr or "unrecognized command" in stderr or "unknown flag" in stderr:
            continue

        # return error text if present
        if err:
            return err.strip()

    raise RuntimeError("Could not invoke Ollama CLI with known commands. Run `ollama --help` to inspect your installation.")


if __name__ == "__main__":
    try:
        out = query_ollama("llama", "Say hello from Ollama")
        print(out)
    except Exception as e:
        print("Ollama check failed:", e)
