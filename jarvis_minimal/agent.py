import os
import json
import time
import threading
from typing import Optional

from .config import (
    HOTWORD,
    OLLAMA_MODEL,
    INTERACTIONS_LOG,
    LISTEN_TIMEOUT,
    CONTEXT_WINDOW,
    SYSTEM_PROMPT,
    DEVICE_LANGUAGE,
    LANGUAGE_VALIDATION,
)
from .listener import listen_for_hotword, record_chunk, STT
from .ollama_client import query_ollama
from .tts import TTS
from .conversation import ConversationMemory
from .lang_utils import get_device_language, detect_language, code_to_name



class JarvisAgent:
    def __init__(self, model: str = OLLAMA_MODEL, auto_setup: bool = True):
        self.model = model
        # detect device language (fallback to config DEVICE_LANGUAGE if provided)
        self.device_lang = DEVICE_LANGUAGE or get_device_language()
        self.lang_validate = LANGUAGE_VALIDATION

        # Run adaptive startup checks / auto-setup
        from . import bootstrap
        try:
            report = bootstrap.run_startup_checks(autoinstall=auto_setup)
        except Exception as e:
            report = {"error": str(e)}

        # apply recommended TTS preference at runtime
        try:
            from . import config as _cfg
            pref = report.get("recommended_tts_pref")
            if pref:
                _cfg.TTS_BACKEND_PREFERENCE = pref
        except Exception:
            pass

        # create runtime components
        self.tts = TTS(lang=self.device_lang)
        self.stt = STT()
        self.memory = ConversationMemory(path=INTERACTIONS_LOG, window=CONTEXT_WINDOW)
        os.makedirs(os.path.dirname(INTERACTIONS_LOG), exist_ok=True)

        # expose startup report for debugging/inspection
        self.startup_report = report

    def _log_interaction(self, user_text: str, assistant_text: str):
        entry = {"ts": time.time(), "user": user_text, "assistant": assistant_text}
        with open(INTERACTIONS_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        # also store in memory for conversational prompting
        try:
            self.memory.add(user_text, assistant_text)
        except Exception:
            pass

    def handle_command(self, text: str) -> None:
        print("[agent] user:", text)

        # language validation: detect language of input and compare with device language
        try:
            detected = detect_language(text)
        except Exception:
            detected = "unknown"

        if self.lang_validate and detected not in ("unknown", self.device_lang):
            # ask for confirmation to continue in a different language
            device_name = code_to_name(self.device_lang)
            detected_name = code_to_name(detected)
            resp = (
                f"Detectei que você está falando em {detected_name}. "
                f"Meu idioma nativo do dispositivo é {device_name}. Deseja continuar em {detected_name} ou prefere que eu responda em {device_name}?"
            )
            print("[agent] jarvis (lang validate):", resp)
            self._log_interaction(text, resp)
            self.tts.speak(resp)
            return

        # built-in voice commands
        cmd_l = (text or "").strip().lower()
        if cmd_l in ("limpar memória", "clear memory", "reset context", "reiniciar contexto"):
            self.memory.clear()
            resp = "Contexto limpo. Memória reiniciada."
            print("[agent] jarvis:", resp)
            self._log_interaction(text, resp)
            self.tts.speak(resp)
            return

        # compose a conversational prompt using system prompt + recent history
        history_prompt = self.memory.as_prompt(SYSTEM_PROMPT, max_items=CONTEXT_WINDOW)
        lang_directive = f"\n(Responda em {code_to_name(self.device_lang)}.)"
        prompt_body = (
            history_prompt + "\nUsuário: " + text + "\nJarvis:" if history_prompt else f"{SYSTEM_PROMPT}\nUsuário: {text}\nJarvis:"
        )
        prompt = prompt_body + lang_directive

        try:
            resp = query_ollama(self.model, prompt)
        except Exception as e:
            resp = f"Erro ao contatar o modelo: {e}"

        print("[agent] jarvis:", resp)
        self._log_interaction(text, resp)
        self.tts.speak(resp)

    def run(self):
        print("Jarvis minimal iniciado — aguardando hotword para conversar.")
        while True:
            cmd = listen_for_hotword(HOTWORD, stt=self.stt)
            if cmd is None:
                # if hotword detected but no command, listen again for a short time
                try:
                    print("[agent] ouvindo comando (push)...")
                    data = record_chunk(seconds=LISTEN_TIMEOUT)
                    text = self.stt.transcribe_bytes(data)
                    if text:
                        self.handle_command(text)
                    continue
                except Exception as e:
                    print("[agent] erro curto:", e)
                    continue
            else:
                # hotword + inline command
                self.handle_command(cmd)


if __name__ == "__main__":
    a = JarvisAgent()
    a.run()
