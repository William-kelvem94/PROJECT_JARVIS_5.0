import time


class TTS:
    """Flexible TTS wrapper supporting multiple backends.

    Priority: try `edge-tts` (if available and preferred), then `pyttsx3` (local SAPI),
    otherwise fallback to console print. Both backends are optional and selected at
    runtime depending on installed packages and `config.TTS_BACKEND_PREFERENCE`.
    """

    def __init__(self, rate: int = None, lang: str = None):
        from .config import TTS_BACKEND_PREFERENCE, TTS_PYTTSX3_VOICE, TTS_EDGE_VOICE, TTS_RATE

        self.pref = TTS_BACKEND_PREFERENCE
        self.lang = lang
        self.rate = rate or TTS_RATE
        self.py_voice_preference = TTS_PYTTSX3_VOICE
        self.edge_voice = TTS_EDGE_VOICE
        self.engine = None
        self._use_edge = False

        # detect availability of edge-tts
        try:
            import importlib
            _ = importlib.import_module('edge_tts')
            self._edge_available = True
        except Exception:
            self._edge_available = False

        # initialize pyttsx3 engine if present
        try:
            import pyttsx3
            from .lang_utils import get_device_language

            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", self.rate)
            # set preferred local voice if configured
            try:
                voices = self.engine.getProperty("voices")
                chosen = None
                if self.py_voice_preference:
                    for v in voices:
                        if self.py_voice_preference.lower() in (getattr(v, "name", "").lower() + " " + getattr(v, "id", "").lower()):
                            chosen = v.id
                            break
                if not chosen:
                    desired = (lang or get_device_language() or "pt").lower()
                    for v in voices:
                        info = (getattr(v, "name", "") + " " + getattr(v, "id", "")).lower()
                        if desired.startswith("pt") and ("pt" in info or "brazil" in info or "portuguese" in info):
                            chosen = v.id
                            break
                        if desired.startswith("en") and ("en_" in info or "english" in info):
                            chosen = v.id
                            break
                if chosen:
                    self.engine.setProperty("voice", chosen)
            except Exception:
                pass
        except Exception:
            self.engine = None

    def list_voices(self):
        """Return installed pyttsx3 voices (name, id)."""
        try:
            if not self.engine:
                import pyttsx3
                eng = pyttsx3.init()
            else:
                eng = self.engine
            voices = eng.getProperty("voices")
            return [f"{getattr(v, 'name', '')} — {getattr(v, 'id', '')}" for v in voices]
        except Exception:
            return []

    def _speak_edge(self, text: str):
        """Use edge-tts (online) to synthesize and play audio (requires `playsound`)."""
        try:
            import edge_tts
            import asyncio
            import tempfile
            import os

            fname = tempfile.mktemp(suffix=".mp3")
            voice = self.edge_voice

            async def _save():
                communicate = edge_tts.Communicate(text, voice=voice)
                await communicate.save(fname)

            asyncio.run(_save())
            try:
                # Prefer Windows native player if available to avoid extra deps
                if hasattr(os, "startfile"):
                    os.startfile(fname)
                else:
                    # try playsound if installed
                    try:
                        from playsound import playsound

                        playsound(fname)
                    except Exception:
                        # last resort: print filename and let user play it
                        print(f"[TTS] arquivo de áudio gerado em: {fname}")
            finally:
                # do not remove immediately to allow playback; schedule removal if possible
                pass
            return True
        except Exception as e:
            # edge tts failed; fallthrough to other backends
            print("[TTS] edge-tts failed:", e)
            return False

    def speak(self, text: str):
        import time
        from .config import TTS_BACKEND_PREFERENCE

        if not text:
            return

        # Try backends in preference order
        for backend in (self.pref or TTS_BACKEND_PREFERENCE):
            if backend == "edge-tts":
                if self._edge_available:
                    ok = self._speak_edge(text)
                    if ok:
                        return
                    else:
                        continue
            if backend == "pyttsx3":
                if self.engine:
                    try:
                        self.engine.say(text)
                        self.engine.runAndWait()
                        return
                    except Exception as e:
                        print("[TTS] pyttsx3 failed:", e)
                        continue

        # fallback: print to console
        print("[TTS]", text)
        time.sleep(min(0.25 * len(text.split()), 2.0))
