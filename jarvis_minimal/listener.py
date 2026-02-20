"""Minimal listener with hotword detection + modular STT backends.

Behavior (MVP):
- continuously record short chunks
- transcribe chunk using available backend (whisper -> vosk -> speech_recognition)
- if transcription contains HOTWORD -> return the spoken command
"""
import os
import tempfile
import wave
import sys
import json
from typing import Optional
from .config import LISTEN_TIMEOUT

import sounddevice as sd
import numpy as np


class STT:
    """Speech-to-text wrapper.

    - Lazy-loads Whisper once (if available) to avoid repeated downloads/loads.
    - Falls back to SpeechRecognition (Google) only if Whisper isn't available.
    """

    def __init__(self):
        self.whisper_model = None
        # lazy: only load Whisper if explicitly enabled in config to avoid
        # unexpected large downloads during startup.
        try:
            from . import config as _cfg
            self._use_whisper = getattr(_cfg, "USE_WHISPER", False)
        except Exception:
            self._use_whisper = False

    def transcribe_bytes(self, data: bytes, sample_rate: int = 16000) -> str:
        """Transcribe WAV bytes. Returns empty string on failure."""
        # If Whisper is enabled in config, load it lazily on first use
        if getattr(self, "_use_whisper", False):
            try:
                if self.whisper_model is None:
                    import whisper
                    self.whisper_model = whisper.load_model("small")
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    f.write(data)
                    fname = f.name
                res = self.whisper_model.transcribe(fname)
                os.remove(fname)
                return res.get("text", "").strip()
            except Exception:
                # fall-through to other backends
                pass

        # try VOSK (offline) if installed and a model exists
        try:
            from vosk import Model, KaldiRecognizer
            import glob
            # search common model locations in repo
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            candidates = []
            env_path = os.environ.get("VOSK_MODEL_PATH")
            if env_path:
                candidates.append(env_path)
            candidates += glob.glob(os.path.join(repo_root, "**", "vosk-model*"), recursive=True)
            candidates += glob.glob(os.path.join(repo_root, "models", "vosk-model*"))
            model_path = None
            for p in candidates:
                if os.path.isdir(p):
                    model_path = p
                    break
            if model_path:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    f.write(data)
                    fname = f.name
                wf = wave.open(fname, "rb")
                model = Model(model_path)
                rec = KaldiRecognizer(model, wf.getframerate())
                results = []
                while True:
                    chunk = wf.readframes(4000)
                    if len(chunk) == 0:
                        break
                    if rec.AcceptWaveform(chunk):
                        results.append(rec.Result())
                results.append(rec.FinalResult())
                wf.close()
                os.remove(fname)
                text = " ".join([json.loads(r).get("text", "") for r in results if r])
                return text.strip()
        except Exception:
            pass

        # Fallback to SpeechRecognition (requires internet)
        try:
            import speech_recognition as sr
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(data)
                fname = f.name
            r = sr.Recognizer()
            with sr.AudioFile(fname) as source:
                audio = r.record(source)
            os.remove(fname)
            return r.recognize_google(audio)
        except Exception:
            return ""


def record_chunk(seconds: int = 4, samplerate: int = 16000) -> bytes:
    """Record a short chunk from default input and return WAV bytes."""
    frames = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=1, dtype="int16")
    sd.wait()
    audio = frames.flatten().tobytes()
    # write WAV header
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wf = wave.open(f.name, "wb")
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio)
        wf.close()
        with open(f.name, "rb") as rf:
            data = rf.read()
    os.remove(f.name)
    return data


def listen_for_hotword(hotword: str, chunk_seconds: int = 4, sample_rate: int = 16000, stt: Optional[STT] = None) -> Optional[str]:
    """Loop until hotword detected. Returns the raw transcribed text that contained the hotword.

    Logic:
    - Prefer a trained `wakeword` detector (if present).
    - If detector fires, perform a short follow-up recording for the command.
    - Otherwise fall back to full STT-based hotword matching.
    """
    if stt is None:
        stt = STT()
    hot = hotword.lower()
    print(f"[listener] aguardando hotword '{hotword}'...")
    while True:
        try:
            data = record_chunk(seconds=chunk_seconds, samplerate=sample_rate)

            # 1) try wakeword neural detector (fast) if available
            try:
                from . import wakeword
                if wakeword.detect(data):
                    # heard wakeword — capture the following short command
                    print("[listener] wakeword detector fired — ouvindo comando...")
                    follow = record_chunk(seconds=LISTEN_TIMEOUT, samplerate=sample_rate)
                    text = stt.transcribe_bytes(follow, sample_rate)
                    return (text or "").strip() or None
            except Exception:
                # detector not available or failed — continue to STT fallback
                pass

            # 2) fallback: transcribe current chunk and look for hotword in text
            txt = stt.transcribe_bytes(data, sample_rate)
            txt_l = (txt or "").lower()
            if not txt_l:
                continue
            print("[listener] transcribed:", txt_l)
            if hot in txt_l:
                idx = txt_l.find(hot)
                cmd = txt_l[idx + len(hot) :].strip()
                return cmd or None
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print("[listener] erro:", e, file=sys.stderr)
            continue
