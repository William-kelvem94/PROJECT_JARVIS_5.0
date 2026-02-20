import time


class TTS:
    """Minimal offline TTS wrapper. Tries pyttsx3, falls back to print().

    - Best-effort: select a voice that matches the device language when available.
    """

    def __init__(self, rate: int = 150, lang: str = None):
        self.engine = None
        self.rate = rate
        try:
            import pyttsx3
            from .lang_utils import get_device_language

            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", rate)
            # select a voice matching device language (best-effort)
            desired = (lang or get_device_language() or "pt").lower()
            try:
                voices = self.engine.getProperty("voices")
                for v in voices:
                    info = (getattr(v, "name", "") + " " + getattr(v, "id", "")).lower()
                    if desired.startswith("pt") and ("pt" in info or "brazil" in info or "portuguese" in info):
                        self.engine.setProperty("voice", v.id)
                        break
                    if desired.startswith("en") and ("en_" in info or "english" in info):
                        self.engine.setProperty("voice", v.id)
                        break
            except Exception:
                pass
        except Exception:
            self.engine = None

    def speak(self, text: str):
        import time

        if not text:
            return
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                print("[TTS]", text)
        else:
            # fallback for environments without TTS
            print("[TTS]", text)
            time.sleep(min(0.25 * len(text.split()), 2.0))
