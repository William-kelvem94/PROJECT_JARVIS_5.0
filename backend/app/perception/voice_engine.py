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
import asyncio
from dataclasses import dataclass, field
from typing import Optional, List, Callable

import numpy as np
from loguru import logger
from app.voice.tts_engine import tts_engine
from app.security.biometric_vault import biometric_vault


# ── Constants ──────────────────────────────────────────────────────────────────
SAMPLE_RATE = 16_000          # Hz — required by all models
CHUNK_DURATION = 0.5          # seconds per processing chunk
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)
ANALYSIS_WINDOW = 2.0         # Reduzido de 5s para 2s para resposta rápida
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
    is_validated: bool = False             # Blindagem Sensorial: Voice Validation



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


# ── Audio Processing (Sensory Shielding) ───────────────────────────────────────
try:
    import df.enhance as deepfilter  # type: ignore
    HAS_DEEPFILTER = True
    logger.info("[VoiceEngine] ✅ DeepFilterNet available for noise suppression")
except ImportError:
    HAS_DEEPFILTER = False
    logger.warning("[VoiceEngine] DeepFilterNet not installed — noise suppression disabled. Install: pip install deepfilternet")

def _apply_noise_suppression(audio_int16: np.ndarray) -> np.ndarray:
    """Removes ambient noise and music using DeepFilterNet."""
    if not HAS_DEEPFILTER:
        return audio_int16
    try:
        # DeepFilterNet expects float32
        audio_float = audio_int16.astype(np.float32) / 32768.0
        enhanced = deepfilter.enhance(audio_float)
        return (enhanced * 32767).astype(np.int16)
    except Exception as e:
        logger.debug(f"[VoiceEngine] Noise suppression failed: {e}")
        return audio_int16

_oww_model = None
_voice_encoder = None
_whisper_model = None


def _oww_list_available() -> list:
    """Return list of locally available .onnx wake word model paths."""
    import os, openwakeword # type: ignore
    pkg_dir = os.path.dirname(openwakeword.__file__)
    models_dir = os.path.join(pkg_dir, "resources", "models")
    if not os.path.isdir(models_dir):
        return []
    return [
        os.path.join(models_dir, f)
        for f in os.listdir(models_dir)
        if f.endswith(".onnx") and "embedding" not in f and "melspectrogram" not in f
    ]


def _get_oww(custom_models: List[str] = None):
    global _oww_model
    if _oww_model is None and HAS_WAKE_WORD:
        try:
            from openwakeword.model import Model  # type: ignore

            # 1. Carrega os modelos padrão + os customizados se fornecidos
            models_to_load = ["hey_jarvis_v0.1"]
            if custom_models:
                models_to_load.extend(custom_models)

            try:
                _oww_model = Model(wakeword_models=models_to_load, inference_framework="onnx")
                logger.success(f"[VoiceEngine] ✅ Wake words carregadas: {models_to_load}")
                return _oww_model
            except Exception as e:
                logger.warning(f"[VoiceEngine] Erro ao carregar modelos específicos: {e}. Tentando baixar modelos padrão...")
                try:
                    import openwakeword
                    openwakeword.utils.download_models()
                    _oww_model = Model(wakeword_models=models_to_load, inference_framework="onnx")
                    return _oww_model
                except:
                    pass

            # 2. Try any available .onnx wake word model found locally
            available = _oww_list_available()
            if available:
                _oww_model = Model(wakeword_models=available, inference_framework="onnx")
                names = [os.path.basename(p) for p in available]
                logger.success(f"[VoiceEngine] ✅ Wake word models carregados (Auto): {names}")
                return _oww_model

            # 3. No models found — disable wake word gracefully
            logger.warning(
                "[VoiceEngine] No wake word models found locally. "
                "Wake word disabled."
            )
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
    import os
    if _whisper_model is None and HAS_WHISPER:
        try:
            from faster_whisper import WhisperModel  # type: ignore
            import torch  # type: ignore
            # Device configuration
            device_env = os.environ.get("JARVIS_AI_DEVICE", "auto")
            if device_env == "auto":
                device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                device = device_env

            # Hardware Optimization
            if device == "cuda":
                compute_type = "int8_float16" # Optimized for NVIDIA GPUs (Tensor cores)
            elif device == "cpu":
                # OpenVINO logic: faster-whisper supports 'int8' on CPU.
                # If we wanted true OpenVINO, we'd use the openvino-whisper model,
                # but for faster-whisper, int8 is the standard CPU optimization.
                compute_type = "int8"
            else:
                compute_type = "float32"

            # Mudando de 'base' para 'tiny' para não travar sua CPU
            model_size = os.environ.get("JARVIS_WHISPER_MODEL", "tiny")
            _whisper_model = WhisperModel(model_size, device=device, compute_type=compute_type)
            logger.success(f"[VoiceEngine] ✅ faster-whisper '{model_size}' (Modo Veloz) carregado em {device.upper()} with {compute_type}")
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

        biometric_vault.save_voice_print(name, embedding)
        _enrolled_voices[name] = embedding
        logger.success(f"[VoiceEngine] ✅ Voice enrolled for '{name}' via BiometricVault")
        return f"Voice enrolled for '{name}'."
    except Exception as e:
        logger.error(f"[VoiceEngine] Voice enrolment failed: {e}")
        return f"Error enrolling voice: {e}"


def identify_speaker(audio_int16: np.ndarray) -> tuple:
    """Returns (name, confidence) or (None, 0.0). Uses BiometricVault."""
    _ensure_voices()
    encoder = _get_encoder()
    if encoder is None or not _enrolled_voices:
        return None, 0.0
    try:
        from resemblyzer import preprocess_wav  # type: ignore
        # Sensory Shielding: Noise suppression before identification
        audio_cleaned = _apply_noise_suppression(audio_int16)
        audio_float = audio_cleaned.astype(np.float32) / 32768.0
        wav = preprocess_wav(audio_float, source_sr=SAMPLE_RATE)
        if len(wav) < SAMPLE_RATE:  # need at least 1 second
            return None, 0.0
        embedding = encoder.embed_utterance(wav)
        _SPEAKER_THRESHOLD = float(os.environ.get("JARVIS_SPEAKER_THRESHOLD", "0.75"))
        best_name, best_sim = None, _SPEAKER_THRESHOLD
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
    if whisper is None or len(audio_int16) < 8000: # Aceita áudios a partir de 0.5s
        return None
    try:
        # Beam size 1 é o segredo para CPUs i3/Notebooks: 3x mais rápido!
        audio_float = audio_int16.astype(np.float32) / 32768.0
        _lang = os.environ.get("JARVIS_WHISPER_LANG", "pt")
        segments, info = whisper.transcribe(audio_float, beam_size=1, language=_lang)
        
        full_text = []
        for seg in segments:
            # Auditando: No speech prob > 0.5 indica alta chance de alucinação por ruído (Bug #15)
            if getattr(seg, "no_speech_prob", 0.0) > 0.5:
                continue
            full_text.append(seg.text.strip())
            
        text = " ".join(full_text).strip()
        
        # Filtro de fallback secundário
        _HALLUCINATIONS = {
            "e o que eu vou fazer?", "obrigado por assistir", "legendas",
            "inscreva-se no canal", "curta e compartilhe", "transcrição automática",
            "subtitles by", "legendas por", "thanks for watching",
            "please subscribe", "like and subscribe", "não se esqueça",
            "até a próxima", "caption by", "[música]", "[music]",
        }
        text_lower = text.lower().strip()
        if (text_lower in _HALLUCINATIONS
                or len(text_lower) < 3
                or text_lower.startswith("[")
                or all(c in ".,!? " for c in text_lower)):
            return None
            
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
_command_semaphore = threading.Semaphore(3)  # máximo 3 threads simultâneas

# Thread-safe queue for chunks coming from the sounddevice callback
_chunk_q: queue.Queue = queue.Queue(maxsize=200)


_active_listening = False
_silence_counter = 0
_voice_buffer = []
_noise_floor = 150.0  # baseline adaptativo de ruído ambiente
_NOISE_FLOOR_ALPHA = 0.05  # fator de suavização exponencial

def _audio_loop():
    """Background thread: opens audio input and processes chunks."""
    global _active_listening, _silence_counter, _voice_buffer, _noise_floor
    if not HAS_SOUNDDEVICE:
        return

    oww = _get_oww()
    
    def _sd_callback(indata, frames, time_info, status):
        """Called by PortAudio thread — mantém o mais leve possível."""
        try:
            if status:
                pass 
            chunk_int16 = (indata[:, 0] * 32767).astype(np.int16)
            if _chunk_q.qsize() < 100: 
                _chunk_q.put_nowait(chunk_int16)
        except Exception:
            pass

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

                # ── Modo de Escuta Ativa (Pós Wake Word ou PTT) ──────────────
                if _active_listening:
                    _voice_buffer.append(chunk)
                    
                    # VAD Adaptativo (Energia do Áudio)
                    energy = float(np.abs(chunk).mean())
                    # Threshold adaptativo: 2x o ruído de fundo estimado, mínimo 150
                    _silence_threshold = max(150.0, _noise_floor * 2.0)
                    if energy < _silence_threshold:
                        _silence_counter += 1
                        # Atualiza noise floor apenas em silêncio (EMA)
                        _noise_floor = _noise_floor * (1 - _NOISE_FLOOR_ALPHA) + energy * _NOISE_FLOOR_ALPHA
                    else:
                        _silence_counter = 0
                        
                    # 6 chunks de silêncio = 1.5 segundos. Mínimo 4 chunks = 1 segundo
                    if len(_voice_buffer) > 4 and _silence_counter > 6:
                        segment = np.concatenate(_voice_buffer)
                        _active_listening = False
                        
                        _notify_hud("thinking")
                        
                        text = transcribe_offline(segment) if HAS_WHISPER else ""
                        if text and len(text.strip()) > 2:
                            logger.success(f"[VoiceEngine] 📝 Comando Ouvido: {text}")
                            def _run_with_semaphore(t):
                                with _command_semaphore:
                                    _process_command_sync(t)
                            threading.Thread(target=_run_with_semaphore, args=(text,), daemon=True).start()
                        else:
                            _notify_hud("idle")

                # ── Modo de Espera (Aguardando Wake Word) ────────────────────
                else:
                    if oww is not None:
                        try:
                            # Sensory Shielding: Noise suppression before Wake Word detection
                            chunk_cleaned = _apply_noise_suppression(chunk)
                            chunk_float = chunk_cleaned.astype(np.float32) / 32768.0
                            pred = oww.predict(chunk_float)
                            for model_name, score_data in pred.items():
                                try:
                                    if isinstance(score_data, (int, float)): score = float(score_data)
                                    elif isinstance(score_data, dict): score = max(score_data.values()) if score_data else 0.0
                                    elif hasattr(score_data, "__iter__"): score = max(score_data) if len(score_data) > 0 else 0.0
                                    else: score = 0.0
                                except: score = 0.0

                                if score > 0.45:
                                    # Sensory Shielding: Validate Voice Print before activation
                                    # Use the current buffer/chunk to check if it's the owner
                                    # (In a real scenario, we'd use a slightly larger window)
                                    speaker, conf = identify_speaker(chunk_cleaned)

                                    if speaker:
                                        logger.success(f"[VoiceEngine] 🎙️ Wake word '{model_name}' VALIDATED for {speaker}")
                                        _active_listening = True
                                        _silence_counter = 0
                                        _voice_buffer = []
                                        _notify_hud("listening")
                                    else:
                                        logger.warning(f"[VoiceEngine] ⚠️ Wake word '{model_name}' detected but VOICE UNVALIDATED. Blocking.")
                        except Exception as e:
                            logger.debug(f"[VoiceEngine] Wake word check: {e}")


    except Exception as e:
        logger.error(f"[VoiceEngine] Audio loop crashed: {e}")

def _notify_hud(status: str, transcript: str = "", response: str = ""):
    """Envia status para o HUD de forma segura para não travar a thread de áudio."""
    try:
        from app.voice_websocket import broadcast_state
        # Cria um novo event loop temporário para rodar a corrotina
        loop = asyncio.new_event_loop()
        loop.run_until_complete(broadcast_state(status, transcript, response))
        loop.close()
    except Exception as e:
        pass

def _process_command_sync(text: str):
    """Executa o chat_pipeline e tts localmente."""
    try:
        from app.chat_pipeline import chat_stream
        from app.voice.tts_engine import tts_engine
        from app.voice.barge_in import barge_in

        _notify_hud("thinking", transcript=text)

        async def run_chat():
            # Inicia a escuta de Barge-in enquanto o JARVIS processa/fala
            barge_in.start_vad_listener(callback=tts_engine.stop_speaking)

            full_reply = ""
            async for chunk in chat_stream("Chefe", text):
                full_reply += chunk
                from app.voice_websocket import broadcast_chunk
                await broadcast_chunk(chunk)

            _notify_hud("speaking", response=full_reply)
            # Toca o áudio nas caixas locais
            await tts_engine.speak(full_reply, play_local=True)

            barge_in.stop_vad_listener()
            _notify_hud("idle")

        loop = asyncio.new_event_loop()
        loop.run_until_complete(run_chat())
        loop.close()
    except Exception as e:
        logger.error(f"[VoiceEngine] Falha ao processar comando: {e}")
        _notify_hud("idle")

def force_listen():
    """Gatilho manual acionado pelo HUD."""
    global _active_listening, _silence_counter, _voice_buffer
    _active_listening = True
    _silence_counter = 0
    _voice_buffer = []
    _notify_hud("listening")

def start(custom_models: List[str] = None):
    """Start the voice engine background thread."""
    global _running, _audio_thread
    if _running:
        return
    
    # Se não houver custom_models via argumento, tenta carregar do ambiente
    if not custom_models:
        env_models = os.environ.get("JARVIS_CUSTOM_WAKE_WORDS")
        if env_models:
            custom_models = [m.strip() for m in env_models.split(",") if m.strip()]

    # Eagerly initialise so models are ready before audio starts
    _ensure_voices()
    _get_oww(custom_models)
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
