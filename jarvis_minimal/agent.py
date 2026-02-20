import os
import sys
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
from . import web_utils
from . import trainer_ui
from .local_brain import LocalBrain



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
            # adapt Ollama model if configured one is missing
            models = report.get("ollama_models") or []
            if models and (_cfg.OLLAMA_MODEL not in models):
                # prefer a non-cloud model (no ':cloud' suffix) if possible
                local_models = [m for m in models if ":cloud" not in m]
                choice = local_models[0] if local_models else models[0]
                _cfg.OLLAMA_MODEL = choice
                self.model = choice
            # if whisper package is available, enable its use for STT
            heavy = report.get("heavy_packages", {})
            if heavy.get("whisper"):
                _cfg.USE_WHISPER = True
        except Exception:
            pass

        # create runtime components
        self.tts = TTS(lang=self.device_lang)
        self.stt = STT()
        self.memory = ConversationMemory(path=INTERACTIONS_LOG, window=CONTEXT_WINDOW)
        os.makedirs(os.path.dirname(INTERACTIONS_LOG), exist_ok=True)
        self.debug = False
        self._interactions_since_train = 0
        self._auto_train_interval = 50  # fine-tune after this many interactions

        # local brain (pode ser None se falhar)
        from .config import USE_LOCAL_BRAIN
        self.local_brain = LocalBrain() if USE_LOCAL_BRAIN else None

        # expose startup report for debugging/inspection
        self.startup_report = report
        # perform a lightweight self-test after initialization
        try:
            self.self_test()
        except Exception as e:
            print("[agent] self-test falhou:", e)

    def self_test(self):
        """Run some quick checks and print outcomes to console.

        The TTS portion now uses a friendly, context-aware greeting instead of a
        hard-coded "teste" string.  This makes startup feel less mechanical.
        """
        print("[self_test] iniciando diagnóstico completo...")
        # TTS test with smarter greeting
        try:
            self._speak(self._startup_greeting())
        except Exception as e:
            print("[self_test] erro TTS:", e)
        # STT test
        try:
            data = record_chunk(seconds=1)
            txt = self.stt.transcribe_bytes(data)
            print("[self_test] transcrição STT:", repr(txt))
        except Exception as e:
            print("[self_test] erro STT:", e)

    def _log_interaction(self, user_text: str, assistant_text: str):
        entry = {"ts": time.time(), "user": user_text, "assistant": assistant_text}
        with open(INTERACTIONS_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        # also store in memory for conversational prompting
        try:
            self.memory.add(user_text, assistant_text)
        except Exception:
            pass

    def _speak(self, text: str):
        """Speak through TTS while pausing the listener to avoid feedback loops."""
        from . import listener
        try:
            listener.set_pause_listening(True)
            self.tts.speak(text)
        finally:
            listener.set_pause_listening(False)

    def _startup_greeting(self) -> str:
        """Generate a friendly greeting for startup.

        Chooses a salutation based on local time and device language.
        """
        import datetime
        hour = datetime.datetime.now().hour
        if hour < 12:
            part = "Bom dia"
        elif hour < 18:
            part = "Boa tarde"
        else:
            part = "Boa noite"
        # If device language isn't Portuguese, fall back to generic English
        if self.device_lang and not self.device_lang.startswith("pt"):
            if hour < 12:
                part = "Good morning"
            elif hour < 18:
                part = "Good afternoon"
            else:
                part = "Good evening"
        return f"{part}! Eu sou o Jarvis, seu assistente pessoal. Como posso ajudar?"

    def handle_command(self, text: str) -> None:
        print("[agent] user:", text)
        if self.debug:
            print("[agent-debug] device_lang=", self.device_lang)
        # language validation: detect language of input and compare with device language

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
            self._speak(resp)
            return

        # built-in voice/text commands
        cmd_l = (text or "").strip().lower()
        # online search shortcuts
        if cmd_l.startswith("pesquisar ") or cmd_l.startswith("buscar ") or cmd_l.startswith("procure "):
            parts = text.split(" ",1)
            query = parts[1] if len(parts) > 1 else ""
            resp = web_utils.search_online(query)
            print("[agent] jarvis (search):", resp)
            self._log_interaction(text, resp)
            self._speak(resp)
            if self.local_brain and resp:
                self._log_interaction(f"[web]: {query}", resp)
            return
        # train on a topic via web search
        if cmd_l.startswith("treinar sobre "):
            topic = text.split(" ",2)[2] if len(text.split(" ",2))>2 else ""
            if topic:
                info = web_utils.search_online(topic)
                self._log_interaction(f"[web {topic}]", info)
                self._speak(f"Busquei informações sobre {topic} e agora vou treinar.")
                if self.local_brain:
                    self.local_brain.train_from_file()
                    self._speak("Treinamento concluído sobre esse tema.")
                else:
                    self._speak("Cérebro local não disponível para treinar.")
            else:
                self._speak("Qual assunto você quer que eu pesquise e treine?")
            return
        # show training interface
        if cmd_l in ("mostrar treinamento", "ver treinamento"):
            url = trainer_ui.start_server()
            resp = f"Interface de treino aberta em {url}"
            self._speak(resp)
            return
        if cmd_l in ("limpar memória", "clear memory", "reset context", "reiniciar contexto"):
            self.memory.clear()
            resp = "Contexto limpo. Memória reiniciada."
            print("[agent] jarvis:", resp)
            self._log_interaction(text, resp)
            self._speak(resp)
            return
        if cmd_l.startswith("treinar hotword"):
            # to handle hotword training, expect files under wake_data already present
            resp = "Iniciando treinamento do hotword, aguarde."
            print("[agent] jarvis:", resp)
            self._speak(resp)
            try:
                import subprocess
                subprocess.run([sys.executable, "-m", "jarvis_minimal.wakeword_trainer"], check=True)
                resp2 = "Treinamento do hotword concluído."
            except Exception as e:
                resp2 = f"Falha no treinamento do hotword: {e}"
            self._log_interaction(text, resp2)
            self._speak(resp2)
            return
        if cmd_l.startswith("treinar cerebro") or cmd_l.startswith("treinar cérebro"):
            resp = "Treinando cérebro local com interações..."
            print("[agent] jarvis:", resp)
            self._speak(resp)
            try:
                if self.local_brain:
                    self.local_brain.train_from_file()
                    resp2 = "Treinamento do cérebro local finalizado."
                else:
                    resp2 = "Cérebro local não disponível. Instale transformers/datasets."
            except Exception as e:
                resp2 = f"Falha ao treinar cérebro: {e}"
            self._log_interaction(text, resp2)
            self._speak(resp2)
            return

        # compose a conversational prompt using system prompt + recent history
        history_prompt = self.memory.as_prompt(SYSTEM_PROMPT, max_items=CONTEXT_WINDOW)
        lang_directive = f"\n(Responda em {code_to_name(self.device_lang)}.)"
        prompt_body = (
            history_prompt + "\nUsuário: " + text + "\nJarvis:" if history_prompt else f"{SYSTEM_PROMPT}\nUsuário: {text}\nJarvis:"
        )
        prompt = prompt_body + lang_directive

        resp = None
        # try local brain first
        if self.local_brain is not None:
            try:
                resp = self.local_brain.reply(text, history_prompt)
            except Exception as e:
                print("[agent] LocalBrain error:", e)
                resp = None
        if not resp:
            try:
                resp = query_ollama(self.model, prompt)
            except Exception as e:
                resp = f"Erro ao contatar o modelo: {e}"

        print("[agent] jarvis:", resp)
        self._log_interaction(text, resp)
        self._speak(resp)
        if self.debug:
            self._interactions_since_train += 1
            if self._interactions_since_train >= self._auto_train_interval:
                print("[agent-debug] auto-treinando cérebro...")
                if self.local_brain:
                    try:
                        self.local_brain.train_from_file()
                    except Exception as e:
                        print("[agent-debug] erro auto-treinamento:", e)
                self._interactions_since_train = 0

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
