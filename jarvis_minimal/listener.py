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
import time
from typing import Optional
from .config import LISTEN_TIMEOUT

import sounddevice as sd
import numpy as np

# Global flag used to temporarily suspend listening (e.g. when Jarvis is speaking)
_pause_listening = False

def set_pause_listening(value: bool):
    """Enable or disable the listening pause flag."""
    global _pause_listening
    _pause_listening = bool(value)


def is_paused() -> bool:
    return _pause_listening


# helper to locate vosk model path (shared with STT)
def _find_vosk_model() -> Optional[str]:
    import glob
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    candidates = []
    env_path = os.environ.get("VOSK_MODEL_PATH")
    if env_path:
        candidates.append(env_path)
    candidates += glob.glob(os.path.join(repo_root, "**", "vosk-model*"), recursive=True)
    candidates += glob.glob(os.path.join(repo_root, "models", "vosk-model*"))
    for p in candidates:
        if os.path.isdir(p):
            return p
    return None


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


# keep a persistent stream so the microphone device isn't opened/closed on every chunk.
_stream = None

def _get_stream(samplerate: int) -> sd.InputStream:
    global _stream
    if _stream is None:
        try:
            _stream = sd.InputStream(samplerate=samplerate, channels=1, dtype="int16")
            _stream.start()
        except Exception as e:
            print("[listener] erro ao abrir stream de audio:", e, file=sys.stderr)
            raise
    return _stream


def record_chunk(seconds: int = 4, samplerate: int = 16000) -> bytes:
    """Record a short chunk with visual feedback and watchdog."""
    try:
        stream = _get_stream(samplerate)
        num_frames = int(seconds * samplerate)
        
        # Incremental read for VU meter feedback
        chunk_size = 1024
        frames_list = []
        for _ in range(0, num_frames, chunk_size):
            if is_paused():
                break
            data, overflowed = stream.read(chunk_size)
            frames_list.append(data)
            
            # Simple VU meter
            rms = np.sqrt(np.mean(data**2))
            level = int(rms / 100) # scale factor
            meter = "[" + "#" * min(level, 20) + "-" * (20 - min(level, 20)) + "]"
            # Use carriage return to overwrite line
            sys.stdout.write(f"\r{meter} ouvindo..." if level > 2 else f"\r{meter}           ")
            sys.stdout.flush()

        if not frames_list:
            return b""
            
        frames = np.concatenate(frames_list)
        audio = frames.flatten().tobytes()
        
    except Exception as e:
        from .errors import errors
        errors.report("listener", e)
        # Attempt to restart stream
        global _stream
        _stream = None
        return b""

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
        if is_paused():
            # Jarvis is speaking; wait before trying to listen again
            time.sleep(0.1)
            continue
        try:
            data = record_chunk(seconds=chunk_seconds, samplerate=sample_rate)
            if not data:
                # recording failed; wait a bit then retry
                continue

            # 1) VOSK keyword detection (grammar) if available
            hotchain = hotword.lower()
            try:
                from vosk import Model, KaldiRecognizer
                model_path = _find_vosk_model()
                if model_path:
                    rec = KaldiRecognizer(Model(model_path), sample_rate, f"[\"{hotchain}\"]")
                    if rec.AcceptWaveform(data):
                        res = rec.Result()
                        j = json.loads(res)
                        if j.get("text", "").strip() == hotchain:
                            print("[listener] vosk grammar detectou hotword")
                            # capture follow-up command
                            follow = record_chunk(seconds=LISTEN_TIMEOUT, samplerate=sample_rate)
                            text = stt.transcribe_bytes(follow, sample_rate)
                            return (text or "").strip() or None
            except Exception:
                pass

            # 2) try wakeword neural detector (fast) if available
            try:
                from . import wakeword
                if wakeword.detect(data):
                    print("[listener] wakeword detector fired — ouvindo comando...")
                    follow = record_chunk(seconds=LISTEN_TIMEOUT, samplerate=sample_rate)
                    text = stt.transcribe_bytes(follow, sample_rate)
                    return (text or "").strip() or None
            except Exception:
                pass

            # 3) fallback: transcribe current chunk and look for hotword in text
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
            print("[listener] erro (loop):", e, file=sys.stderr)
            continue
