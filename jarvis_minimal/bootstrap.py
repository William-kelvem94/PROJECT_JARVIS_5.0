"""Startup checks and adaptive auto-configuration for Jarvis Minimal.

Responsibilities:
- Check internet, audio devices, ollama CLI, and required Python packages.
- Auto-install a small set of "core" packages when internet is available.
- Adapt runtime configuration (TTS/STT backend preference) based on availability.
- Provide a concise report for logging and tests.

Design notes:
- Does NOT auto-install heavy packages (torch/whisper); these remain opt-in.
- Safe: failures are non-fatal and reported so Jarvis can fall back.
"""
from __future__ import annotations

import importlib
import subprocess
import sys
import shutil
import socket
from typing import Dict, List, Tuple

CORE_PACKAGES = [
    "pyttsx3",
    "sounddevice",
    "numpy",
    "speechrecognition",
    "playsound",
    "langdetect",
    "vosk",
    "soundfile",
    "edge-tts",
]

AUTO_INSTALL = set([
    "pyttsx3",
    "sounddevice",
    "numpy",
    "speechrecognition",
    "playsound",
    "langdetect",
    "soundfile",
    "edge-tts",
    # don't auto-install 'vosk' models here (models are large)
])

HEAVY_PACKAGES = set(["torch", "whisper"])  # won't be auto-installed


def has_internet(host: str = "8.8.8.8", port: int = 53, timeout: float = 2.0) -> bool:
    try:
        socket.setdefaulttimeout(timeout)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sock.close()
        return True
    except Exception:
        return False


def is_command_available(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def is_package_installed(pkg: str) -> bool:
    try:
        importlib.import_module(pkg)
        return True
    except Exception:
        return False


def pip_install(pkg: str) -> Tuple[bool, str]:
    """Install a package using the active Python interpreter's pip."""
    try:
        proc = subprocess.run([sys.executable, "-m", "pip", "install", pkg], capture_output=True, text=True, timeout=600)
        ok = proc.returncode == 0
        out = proc.stdout + "\n" + proc.stderr
        return ok, out
    except Exception as e:
        return False, str(e)


def _check_audio_devices() -> Dict[str, bool]:
    res = {"input": False, "output": False}
    try:
        import sounddevice as sd
        devs = sd.query_devices()
        # check if there is any device with input channels > 0 and output >0
        for d in devs:
            if d.get("max_input_channels", 0) > 0:
                res["input"] = True
            if d.get("max_output_channels", 0) > 0:
                res["output"] = True
        return res
    except Exception:
        return res


def run_startup_checks(autoinstall: bool = True) -> Dict[str, object]:
    """Run a full startup validation and optionally install missing core packages.

    Returns a report dict with status for each check.
    """
    report: Dict[str, object] = {}

    report["internet"] = has_internet()
    report["ollama_cli"] = is_command_available("ollama")

    # list ollama models if CLI available
    ollama_models: List[str] = []
    if report["ollama_cli"]:
        try:
            proc = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
            lines = (proc.stdout or "").splitlines()
            for line in lines[1:]:
                parts = line.strip().split()
                if parts:
                    ollama_models.append(parts[0])
        except Exception:
            pass
    report["ollama_models"] = ollama_models

    # packages
    pkgs_status: Dict[str, bool] = {}
    for pkg in CORE_PACKAGES:
        pkgs_status[pkg] = is_package_installed(pkg)

    report["packages"] = pkgs_status

    # try to auto-install missing core packages when allowed
    install_log: Dict[str, Tuple[bool, str]] = {}
    if autoinstall and report["internet"]:
        for pkg, installed in list(pkgs_status.items()):
            if not installed and pkg in AUTO_INSTALL:
                ok, out = pip_install(pkg)
                install_log[pkg] = (ok, out)
                pkgs_status[pkg] = ok
    report["install_log"] = install_log

    # audio devices
    report["audio"] = _check_audio_devices()

    # choose best TTS backend: prefer edge-tts if internet & installed; else pyttsx3 if installed
    tts_pref = []
    if report["internet"] and pkgs_status.get("edge-tts"):
        tts_pref.append("edge-tts")
    if pkgs_status.get("pyttsx3"):
        tts_pref.append("pyttsx3")
    if not tts_pref:
        tts_pref = ["pyttsx3"]  # fallback; may not be installed
    report["recommended_tts_pref"] = tts_pref

    # STT availability (vosk or speech_recognition)
    stt_backends = []
    if pkgs_status.get("vosk"):
        stt_backends.append("vosk")
    if pkgs_status.get("speechrecognition"):
        stt_backends.append("speechrecognition")
    report["stt_backends"] = stt_backends

    # heavy packages presence
    heavy_status = {p: is_package_installed(p) for p in HEAVY_PACKAGES}
    report["heavy_packages"] = heavy_status

    return report


if __name__ == "__main__":
    import json

    r = run_startup_checks(autoinstall=False)
    print(json.dumps(r, indent=2, ensure_ascii=False))
