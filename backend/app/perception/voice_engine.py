"""
JARVIS Voice Engine — Adaptive voice recognition.

Level A — Wake word detection via openWakeWord (offline, free)
           Activates on "hey jarvis" without clicking anything.

Level B — Speaker identification via Resemblyzer (offline, voice embeddings)
           Recognises WHO is speaking and blocks unknown speakers.

Level C — Offline STT via faster-whisper (CPU, no internet required)
           Transcribes speech locally when Gemini is unavailable.

Audio input: sounddevice — 16 kHz mono int16 PCM stream.

Install:
  pip install sounddevice openwakeword            → Level A
  pip install resemblyzer                          → + Level B
  pip install faster-whisper                       → + Level C
"""

import os
import time
import queue
import threading
import collections
from dataclasses import dataclass, field
from typing import Optional, List, Callable

import numpy as np
from loguru import logger

# ── Constants ──────────────────────────────────────────────────────────────────
SAMPLE_RATE = 16_000          # Hz — required by all models
CHUNK_DURATION = 0.5          # seconds per processing chunk
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)
ANALYSIS_WINDOW = 5.0         # seconds of audio for Level B/C analysis
ANALYSIS_CHUNKS = int(ANALYSIS_WINDOW / CHUNK_DURATION)

VOICES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "voices",
)

# ── Result dataclass ───────────────────────────────────────────────────────────
@dataclass
class VoiceResult:
    wake_word_triggered: bool = False       # Level A
    speaker_identity: Optional[str] = None # Level B
    speaker_confidence: float = 0.0        # Level B
    offline_transcript: Optional[str] = None  # Level C
    active_levels: List[str] = field(default_factory=list)


# ── Capability detection ───────────────────────────────────────────────────────
HAS_SOUNDDEVICE = False
HAS_WAKE_WORD = False     # Level A
HAS_SPEAKER_ID = False    # Level B
HAS_WHISPER = False       # Level C

try:
    import sounddevice as sd  # noqa: F401
    HAS_SOUNDDEVICE = True
    logger.info("[VoiceEngine] ✅ sounddevice available")
except ImportError:
    logger.warning("[VoiceEngine] sounddevice not installed — all voice levels disabled. "
                   "Install: pip install sounddevice")

try:
    import openwakeword  # type: ignore  # noqa: F401
    HAS_WAKE_WORD = True
    logger.info("[VoiceEngine] ✅ Level A (openwakeword) available")
except ImportError:
    logger.warning("[VoiceEngine] Level A unavailable — install: pip install openwakeword")

try:
    from resemblyzer import VoiceEncoder, preprocess_wav  # type: ignore  # noqa: F401
    HAS_SPEAKER_ID = True
    logger.info("[VoiceEngine] ✅ Level B (resemblyzer speaker ID) available")
except ImportError:
    logger.warning("[VoiceEngine] Level B unavailable — install: pip install resemblyzer")

try:
    import faster_whisper  # type: ignore  # noqa: F401
    HAS_WHISPER = True
    logger.info("[VoiceEngine] ✅ Level C (faster-whisper offline STT) available")
except ImportError:
    logger.warning("[VoiceEngine] Level C unavailable — install: pip install faster-whisper")


# ── Lazy model instances ───────────────────────────────────────────────────────
_oww_model = None
_voice_encoder = None
_whisper_model = None


def _get_oww():
    global _oww_model
    if _oww_model is None and HAS_WAKE_WORD:
        try:
            from openwakeword.model import Model  # type: ignore
            # Try "hey_jarvis" first (built-in in openwakeword ≥ 0.6)
            try:
                _oww_model = Model(wakeword_models=["hey_jarvis_v0.1"], inference_framework="onnx")
                logger.success("[VoiceEngine] Wake word model 'hey_jarvis_v0.1' loaded")
            except Exception:
                # Fallback: load with default built-in models
                _oww_model = Model(inference_framework="onnx")
                logger.info("[VoiceEngine] openwakeword loaded with default models")
        except Exception as e:
            logger.error(f"[VoiceEngine] openwakeword init failed: {e}")
    return _oww_model


def _get_encoder():
    global _voice_encoder
    if _voice_encoder is None and HAS_SPEAKER_ID:
        try:
            from resemblyzer import VoiceEncoder  # type: ignore
            _voice_encoder = VoiceEncoder()
            logger.success("[VoiceEngine] Resemblyzer encoder loaded")
        except Exception as e:
            logger.error(f"[VoiceEngine] Resemblyzer init failed: {e}")
    return _voice_encoder


def _get_whisper():
    global _whisper_model
    if _whisper_model is None and HAS_WHISPER:
        try:
            from faster_whisper import WhisperModel  # type: ignore
            _whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
            logger.success("[VoiceEngine] faster-whisper tiny model loaded")
        except Exception as e:
            logger.error(f"[VoiceEngine] faster-whisper init failed: {e}")
    return _whisper_model


# ── Enrolled voice embeddings (Level B) ───────────────────────────────────────
_enrolled_voices: dict = {}
_voices_loaded = False


def _ensure_voices():
    global _enrolled_voices, _voices_loaded
    if _voices_loaded or not HAS_SPEAKER_ID:
        return
    _voices_loaded = True
    if not os.path.isdir(VOICES_DIR):
        return
    for fn in os.listdir(VOICES_DIR):
        if fn.endswith(".npy"):
            name = fn[:-4]
            try:
                emb = np.load(os.path.join(VOICES_DIR, fn))
                _enrolled_voices[name] = emb
                logger.info(f"[VoiceEngine] Enrolled voice: '{name}'")
            except Exception as e:
                logger.warning(f"[VoiceEngine] Could not load voice '{name}': {e}")


def enroll_voice(name: str, audio_int16: np.ndarray) -> str:
    """Enrol a speaker from a 16 kHz int16 numpy audio array."""
    encoder = _get_encoder()
    if encoder is None:
        return "Level B (resemblyzer) not installed — enrolment not possible."
    try:
        from resemblyzer import preprocess_wav  # type: ignore
        audio_float = audio_int16.astype(np.float32) / 32768.0
        wav = preprocess_wav(audio_float, source_sr=SAMPLE_RATE)
        embedding = encoder.embed_utterance(wav)
        os.makedirs(VOICES_DIR, exist_ok=True)
        path = os.path.join(VOICES_DIR, f"{name}.npy")
        np.save(path, embedding)
        _enrolled_voices[name] = embedding
        logger.success(f"[VoiceEngine] ✅ Voice enrolled for '{name}' → {path}")
        return f"Voice enrolled for '{name}'."
    except Exception as e:
        logger.error(f"[VoiceEngine] Voice enrolment failed: {e}")
        return f"Error enrolling voice: {e}"


def identify_speaker(audio_int16: np.ndarray) -> tuple:
    """Returns (name, confidence) or (None, 0.0)."""
    _ensure_voices()
    encoder = _get_encoder()
    if encoder is None or not _enrolled_voices:
        return None, 0.0
    try:
        from resemblyzer import preprocess_wav  # type: ignore
        audio_float = audio_int16.astype(np.float32) / 32768.0
        wav = preprocess_wav(audio_float, source_sr=SAMPLE_RATE)
        if len(wav) < SAMPLE_RATE:  # need at least 1 second
            return None, 0.0
        embedding = encoder.embed_utterance(wav)
        best_name, best_sim = None, 0.65  # similarity threshold
        for name, ref_emb in _enrolled_voices.items():
            sim = float(np.dot(embedding, ref_emb))
            if sim > best_sim:
                best_sim, best_name = sim, name
        return best_name, round(best_sim, 2)
    except Exception as e:
        logger.debug(f"[VoiceEngine] Speaker ID error: {e}")
        return None, 0.0


def transcribe_offline(audio_int16: np.ndarray) -> Optional[str]:
    """Offline transcription via faster-whisper (Level C). Returns text or None."""
    whisper = _get_whisper()
    if whisper is None or len(audio_int16) < SAMPLE_RATE:
        return None
    try:
        audio_float = audio_int16.astype(np.float32) / 32768.0
        segments, _ = whisper.transcribe(audio_float, beam_size=3, language="pt")
        text = " ".join(seg.text.strip() for seg in segments).strip()
        return text if text else None
    except Exception as e:
        logger.debug(f"[VoiceEngine] Offline STT error: {e}")
        return None


# ── Callback registry ──────────────────────────────────────────────────────────
_callbacks: List[Callable[[VoiceResult], None]] = []


def add_callback(fn: Callable[[VoiceResult], None]):
    """Register a function to be called when a voice event is detected."""
    _callbacks.append(fn)


def _fire(result: VoiceResult):
    for cb in _callbacks:
        try:
            cb(result)
        except Exception as e:
            logger.error(f"[VoiceEngine] Callback error: {e}")


# ── Background audio thread ────────────────────────────────────────────────────
_running = False
_audio_thread: Optional[threading.Thread] = None

# Thread-safe queue for chunks coming from the sounddevice callback
_chunk_q: queue.Queue = queue.Queue(maxsize=200)


def _audio_loop():
    """Background thread: opens audio input and processes chunks."""
    if not HAS_SOUNDDEVICE:
        return

    oww = _get_oww()
    analysis_buffer: List[np.ndarray] = []

    def _sd_callback(indata, frames, time_info, status):
        """Called by PortAudio thread — keep minimal, just enqueue."""
        if status:
            logger.debug(f"[VoiceEngine] Audio status: {status}")
        chunk_int16 = (indata[:, 0] * 32767).astype(np.int16)
        try:
            _chunk_q.put_nowait(chunk_int16)
        except queue.Full:
            pass  # drop silently under load

    try:
        import sounddevice as sd
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=CHUNK_SIZE,
            callback=_sd_callback,
        ):
            logger.success("[VoiceEngine] 🎤 Audio input stream started")

            while _running:
                try:
                    chunk = _chunk_q.get(timeout=1.0)
                except queue.Empty:
                    continue

                analysis_buffer.append(chunk)

                # ── Level A: Wake word ─────────────────────────────────────
                if oww is not None:
                    try:
                        pred = oww.predict(chunk)
                        for model_name, scores in pred.items():
                            score = float(max(scores)) if isinstance(scores, list) else float(scores)
                            if score > 0.5:
                                logger.success(
                                    f"[VoiceEngine] 🎙️ Wake word '{model_name}' "
                                    f"score={score:.2f}"
                                )
                                _fire(VoiceResult(wake_word_triggered=True, active_levels=["A"]))
                    except Exception as e:
                        logger.debug(f"[VoiceEngine] Wake word check: {e}")

                # ── Level B + C: Periodic buffer analysis ─────────────────
                if len(analysis_buffer) >= ANALYSIS_CHUNKS:
                    segment = np.concatenate(analysis_buffer)
                    analysis_buffer.clear()

                    result = VoiceResult()

                    # Level B: Speaker ID
                    if HAS_SPEAKER_ID and _enrolled_voices:
                        name, conf = identify_speaker(segment)
                        if name:
                            result.speaker_identity = name
                            result.speaker_confidence = conf
                            result.active_levels.append("B")

                    # Level C: Offline STT
                    if HAS_WHISPER:
                        text = transcribe_offline(segment)
                        if text:
                            result.offline_transcript = text
                            result.active_levels.append("C")
                            logger.info(f"[VoiceEngine] 📝 Offline STT: {text}")

                    if result.active_levels:
                        _fire(result)

    except Exception as e:
        logger.error(f"[VoiceEngine] Audio loop crashed: {e}")


def start():
    """Start the voice engine background thread."""
    global _running, _audio_thread
    if _running:
        return
    # Eagerly initialise so models are ready before audio starts
    _ensure_voices()
    _get_oww()
    _running = True
    _audio_thread = threading.Thread(
        target=_audio_loop, daemon=True, name="jarvis-voice-engine"
    )
    _audio_thread.start()
    logger.info("[VoiceEngine] Started")


def stop():
    """Stop the voice engine background thread."""
    global _running
    _running = False
    if _audio_thread:
        _audio_thread.join(timeout=3.0)
    logger.info("[VoiceEngine] Stopped")


def get_audio_buffer_seconds() -> float:
    """Return how many seconds are currently queued (useful for diagnostics)."""
    return _chunk_q.qsize() * CHUNK_DURATION
