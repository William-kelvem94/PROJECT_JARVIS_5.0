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
        """Use edge-tts (online) to synthesize and play audio."""
        try:
            import edge_tts
            import asyncio
            import tempfile
            import os
            import subprocess

            from .config_manager import config
            # Use a slightly more robust temp file handling
            fd, fname = tempfile.mkstemp(suffix=".mp3")
            os.close(fd) 
            
            voice = self.edge_voice
            pitch = config.get("TTS_PITCH", "+0Hz")

            async def _save():
                communicate = edge_tts.Communicate(text, voice=voice, pitch=pitch)
                await communicate.save(fname)

            # 1. Sintetiza (Online)
            try:
                asyncio.run(_save())
            except Exception as e:
                print(f"[TTS] Falha na síntese Edge: {e}")
                if os.path.exists(fname): os.remove(fname)
                return False

            # 2. Reproduz (Local)
            try:
                if os.name == 'nt':
                    # Reduzindo o overhead do PowerShell e adicionando timeout de segurança
                    ps_cmd = f"$m = New-Object -ComObject WMPlayer.OCX; $m.url = '{fname}'; $m.controls.play(); $start = Get-Date; while($m.playState -ne 1 -and (Get-Date) -lt $start.AddSeconds(15)){{Start-Sleep -m 100}}"
                    subprocess.run(["powershell", "-WindowStyle", "Hidden", "-Command", ps_cmd], 
                                   capture_output=True, timeout=20)
                else:
                    try:
                        from playsound import playsound
                        playsound(fname)
                    except Exception:
                        subprocess.run(["ffplay", "-nodisp", "-autoexit", fname], capture_output=True, timeout=20)
            except subprocess.TimeoutExpired:
                print("[TTS] Timeout na reprodução de áudio.")
            except Exception as e:
                print(f"[TTS] Erro na reprodução: {e}")
            finally:
                if os.path.exists(fname):
                    try: os.remove(fname)
                    except: pass
            return True
        except Exception as e:
            print("[TTS] Erro crítico no motor Edge:", e)
            return False

    def speak(self, text: str):
        import time
        from .config_manager import config

        if not text:
            return

        pref = config.get("TTS_BACKEND_PREFERENCE")

        # Try backends in preference order
        for backend in pref:
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
