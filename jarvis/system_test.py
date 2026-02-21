"""Run a comprehensive system test for Jarvis Minimal.

Checks performed:
- Startup checks (bootstrap) with auto-install of core packages when possible
- TTS test (edge-tts then pyttsx3)
- List local voices
- Audio input/output checks and short STT test
- Ollama CLI presence test
- Run smoke test (agent.handle_command)

Designed to be safe: heavy packages (torch/whisper) are NOT auto-installed.
"""
import time
import os
import json

from .bootstrap import run_startup_checks
from .tts import TTS
from .listener import record_chunk, STT
from .ollama_client import query_ollama


def run_all():
    report = run_startup_checks(autoinstall=True)
    print("--- Startup report ---")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    print("\n--- Instantiate agent (aplica configuração) ---")
    from .agent import JarvisAgent
    agent = JarvisAgent()
    print("Agent model:", agent.model)
    print("Startup report accessible via agent.startup_report")

    print("\n--- TTS tests ---")
    tts = agent.tts
    voices = tts.list_voices()
    print("Local voices found:", voices)
    print("TTS speak (teste curto)...")
    tts.speak("Teste de fala do Jarvis. Se você ouvir isso, a TTS está funcionando.")

    print("\n--- Audio input test (via agent.stt) ---")
    try:
        data = record_chunk(seconds=2)
        print("Gravado bytes:", len(data))
        text = agent.stt.transcribe_bytes(data)
        print("Transcrição (via agent.stt):", repr(text))
    except Exception as e:
        print("Falha no teste de áudio:", e)

    print("\n--- Ollama CLI test ---")
    try:
        out = query_ollama("llama", "Diga oi")
        print("Ollama responded (truncated):", (out or "").strip()[:200])
    except Exception as e:
        print("Ollama test falhou:", e)

    print("\n--- Smoke tests (agent) ---")
    try:
        from ._smoke_test import agent
        print("Executando smoke test...")
        agent.handle_command('teste: diga olá')
        time.sleep(0.5)
        agent.handle_command('teste: repetir')
    except Exception as e:
        print("Smoke test falhou:", e)

    print("\n--- System test complete ---")


if __name__ == "__main__":
    run_all()
