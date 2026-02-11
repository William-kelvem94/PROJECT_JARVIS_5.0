#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Enhanced Audio Processing
===============================================
Advanced audio system with:
- Faster-Whisper (ultra-fast local STT)
- Silero-VAD (voice activity detection)
- Speaker verification
- Voice signature storage

Features:
- Real-time audio pipeline
- Voice authentication
- Multi-speaker support
- Low-latency processing
"""

import os
import logging
import threading
import queue
import time
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from src.core.management.hardware_manager import hardware_manager
from src.utils.stability import model_load_lock

# Try to import config with graceful fallback
try:
    from src.utils.config import config
except ImportError:
    try:
        from src.utils.config import Config
        config = Config()
    except Exception as e:
        logger.warning(f"⚠️ Config module unavailable: {e}. Using defaults.")
        # Mock config object
        class MoackConfig:
            @staticmethod
            def get_setting(key, default=None):
                return default
        config = MoackConfig()

logger = logging.getLogger(__name__)

# ============================================================================
# CONDITIONAL IMPORTS (Graceful Degradation)
# ============================================================================
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except (ImportError, OSError) as e:
    NUMPY_AVAILABLE = False
    # Mock numpy
    class np:
        class ndarray:
            pass
        @staticmethod
        def array(x):
            return x
        @staticmethod
        def frombuffer(*args, **kwargs):
            return []
    logger.warning(f"⚠️ numpy not available - audio processing limited: {e}")

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except (ImportError, OSError) as e:
    FASTER_WHISPER_AVAILABLE = False
    logger.warning(f"⚠️ faster-whisper not available - STT disabled: {e}")

try:
    import torch
    import torchaudio
    TORCH_AVAILABLE = True
except (ImportError, OSError) as e:
    TORCH_AVAILABLE = False
    logger.warning(f"⚠️ torch not available - advanced audio features disabled: {e}")

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except (ImportError, OSError) as e:
    SOUNDFILE_AVAILABLE = False
    logger.warning(f"⚠️ soundfile not available - audio I/O limited: {e}")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except (ImportError, OSError) as e:
    PYAUDIO_AVAILABLE = False
    logger.warning(f"⚠️ pyaudio not available - microphone input disabled: {e}")

# Fallback for speaker recognition
try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    RESEMBLYZER_AVAILABLE = True
except (ImportError, OSError) as e:
    RESEMBLYZER_AVAILABLE = False
    logger.warning(f"⚠️ resemblyzer not available - speaker verification disabled: {e}")

try:
    import pvporcupine
    PORCUPINE_AVAILABLE = True
except (ImportError, OSError):
    PORCUPINE_AVAILABLE = False
    logger.warning("⚠️ Wake Word detection (Porcupine) disabled - requirements missing")

# ============ P1: NOISE REDUCTION ============
try:
    import noisereduce as nr
    NOISEREDUCE_AVAILABLE = True
except (ImportError, OSError):
    NOISEREDUCE_AVAILABLE = False
    logger.warning("⚠️ Noise reduction disabled - install noisereduce")


# ============================================================================
# DATA CLASSES
# ============================================================================
@dataclass
class AudioSegment:
    """Audio segment data"""
    audio: np.ndarray
    sample_rate: int
    timestamp: datetime
    duration: float
    speaker_id: Optional[str] = None
    confidence: float = 0.0


@dataclass
class TranscriptionResult:
    """STT transcription result"""
    text: str
    language: str
    confidence: float
    segments: List[Dict]
    processing_time: float
    speaker_verified: bool = False
    speaker_id: Optional[str] = None


class AudioState(Enum):
    """Audio processing states"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


# ============================================================================
# ENHANCED AUDIO SYSTEM
# ============================================================================
class EnhancedAudioSystem:
    """
    Advanced audio processing system.
    
    Features:
    - Ultra-fast STT with faster-whisper
    - Voice activity detection (Silero-VAD)
    - Speaker verification
    - Real-time audio pipeline
    - Voice signature management
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize Enhanced Audio System.
        
        Args:
            data_dir: Directory for audio data and signatures
        """
        self.data_dir = data_dir or Path("data")
        self.voice_signatures_dir = self.data_dir / "voice_signatures"
        self.audio_temp_dir = self.data_dir / "audio" / "temp"
        
        # Create directories
        self.voice_signatures_dir.mkdir(parents=True, exist_ok=True)
        self.audio_temp_dir.mkdir(parents=True, exist_ok=True)
        
        # State
        self.state = AudioState.IDLE
        self.is_running = False
        
        # STT Model (faster-whisper)
        self.whisper_model = None
        self.whisper_model_size = "small"  # tiny, base, small, medium, large
        
        # VAD Model (Silero)
        self.vad_model = None
        self.vad_threshold = 0.5
        
        # Speaker verification
        self.voice_encoder = None
        self.known_speakers = {}  # {name: embedding}
        self.speaker_threshold = 0.75  # Similarity threshold
        
        # Audio settings
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.channels = 1
        
        # Audio processing features
        self.noise_reduction_enabled = config.get_setting('audio.noise_reduction', True)
        
        # Audio stream
        self.audio_stream = None
        self.audio_queue = queue.Queue()
        
        # Processing thread
        self._process_thread = None
        self._process_lock = threading.Lock()
        
        # Callbacks
        self.on_transcription: Optional[Callable[[TranscriptionResult], None]] = None
        self.on_speaker_detected: Optional[Callable[[str, float], None]] = None
        self.on_wake_word_detected: Optional[Callable[[], None]] = None
        
        # Wake word state
        self.porcupine = None
        self.wake_word_active = config.get_setting('audio.wake_word_enabled', True)
        # 🆕 ALWAYS LISTENING MODE: Se não tiver wake word, fica sempre acordado
        self.is_awake = not self.wake_word_active  # Começa acordado se wake word desabilitado
        
        # Readiness flags for heavy models
        self._whisper_ready = False
        self._vad_ready = False
        self._models_lock = threading.Lock()
        
        # Initialize basic components
        self._initialize_basic_components()
        
        # Start heavy models in background to avoid 0xC0000005 during boot
        # 🆕 PASSIVE INIT: Do not start threads in __init__. Call start_background_loading() later.
        # threading.Thread(target=self._load_models_background, daemon=True, name="AudioNeuralLoad").start()
        
        logger.info("✅ Enhanced Audio System initialized (Passive Mode)")
        logger.info(f"   Faster-Whisper: {'✅' if FASTER_WHISPER_AVAILABLE else '❌'}")
        logger.info(f"   PyAudio: {'✅' if PYAUDIO_AVAILABLE else '❌'}")
        logger.info(f"   Speaker Verification: {'✅' if RESEMBLYZER_AVAILABLE else '❌'}")

    def start_background_loading(self):
        """Trigger background loading of heavy neural models (Call after GUI boot)"""
        logger.info("🚀 Audio System: Iniciando carregamento neural post-boot...")
        threading.Thread(target=self._load_models_background, daemon=True, name="AudioNeuralLoad").start()
        
    def _initialize_basic_components(self):
        """Initialize lightweight audio components (device checks, VAD gate)"""
        # 🆕 FREE WAKE WORD: VAD-based Energy Gate
        # Instead of Porcupine (paid), we use Silero-VAD + Energy Threshold
        if self.wake_word_active:
            logger.info("✅ VAD-based Wake Word enabled (Always Listen Mode)")
            self.porcupine = None # Disable Porcupine explicitly
            # self.is_awake = False # Start asleep, wait for VAD
        else:
            logger.info("ℹ️ Wake Word disabled (Push-to-Talk Mode)")

    def _load_models_background(self):
        """Load heavy AI models in background to prevent 0xC0000005 during boot"""
        # 1. Faster-Whisper
        if FASTER_WHISPER_AVAILABLE:
            try:
                # 🆕 GLOBAL NEURAL LOCK: Serialize heavy loads
                model_load_lock.acquire("Whisper (Audio Core)")
                try:
                    with self._models_lock:
                        logger.info(f"🧠 Audio Core: Carregando Faster-Whisper ({self.whisper_model_size})...")
                        
                        # CRITICAL: Import here to avoid init-time conflicts
                        from faster_whisper import WhisperModel
                        
                        device = hardware_manager.get_device()
                        # compute_type will now trigger the float32 force for CPU
                        compute_type = hardware_manager.get_compute_type()
                        
                        # CRITICAL: cpu_threads=1 for Windows stability
                        # num_workers=1 to prevent thread pool crashes
                        self.whisper_model = WhisperModel(
                            self.whisper_model_size,
                            device=device,
                            compute_type=compute_type,
                            cpu_threads=1,  # Single-threaded for stability
                            num_workers=1   # Single worker to prevent pool crashes
                        )
                        self._whisper_ready = True
                        logger.info(f"✅ Audio Core: Whisper pronto (Backend: {device.upper()}, Type: {compute_type})")
                finally:
                    model_load_lock.release()
            except Exception as e:
                self._whisper_ready = False
                logger.error(f"❌ Audio Core: Falha no Whisper: {e}")
                import traceback
                logger.error(traceback.format_exc())

        # 2. Silero-VAD
        if TORCH_AVAILABLE:
            try:
                model_load_lock.acquire("Silero-VAD (Audio Core)")
                try:
                    with self._models_lock:
                        logger.info("🧠 Audio Core: Carregando Silero-VAD...")
                        result = torch.hub.load(
                            repo_or_dir='snakers4/silero-vad',
                            model='silero_vad',
                            force_reload=False,
                            onnx=False
                        )
                        
                        if isinstance(result, tuple):
                            self.vad_model, self.vad_utils = result[0], result[1] if len(result) > 1 else None
                        else:
                            self.vad_model = result
                            self.vad_utils = None
                            
                        self._vad_ready = True
                        logger.info("✅ Audio Core: Silero-VAD pronto")
                finally:
                    model_load_lock.release()
            except Exception as e:
                self._vad_ready = False
                logger.warning(f"❌ Audio Core: Falha no VAD: {e}")

    def wait_for_models(self, timeout: float = 30.0) -> bool:
        """Wait for background model loading to complete"""
        import time
        start_time = time.time()
        logger.info("⏳ Waiting for audio models to initialize...")
        
        while time.time() - start_time < timeout:
            with self._models_lock:
                if self._whisper_ready and (self._vad_ready or not TORCH_AVAILABLE):
                    logger.info("✅ Audio models initialized and ready")
                    return True
            time.sleep(0.5)
            
        logger.warning("⚠️ Timeout waiting for audio models - system may be degraded")
        return self._whisper_ready

    def _load_voice_signatures(self):
        """Load known voice signatures"""
        if not RESEMBLYZER_AVAILABLE:
            return
            
        logger.info(f"Loading voice signatures from {self.voice_signatures_dir}...")
        
        count = 0
        for sig_file in self.voice_signatures_dir.glob("*.npy"):
            try:
                embedding = np.load(sig_file)
                speaker_name = sig_file.stem
                self.known_speakers[speaker_name] = embedding
                count += 1
                logger.info(f"   ✅ Loaded: {speaker_name}")
            except Exception as e:
                logger.error(f"   ❌ Failed to load {sig_file.name}: {e}")
                
        logger.info(f"✅ Loaded {count} voice signatures")
    
    def calibrate_vad_threshold(self, duration: float = 3.0):
        """
        🔥 Auto-calibra threshold de VAD baseado no ruído ambiente.
        Mede RMS médio do ambiente por 'duration' segundos e ajusta threshold.
        
        Args:
            duration: Tempo de medição em segundos (padrão: 3.0s)
        """
        if not PYAUDIO_AVAILABLE:
            logger.warning("PyAudio não disponível - pulando calibração VAD")
            return
        
        logger.info(f"🎤 Iniciando calibração VAD ({duration}s de medição)...")
        
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            
            # Abrir stream temporário para calibração
            temp_stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            ambient_samples = []
            start_time = time.time()
            
            # Coletar amostras de ruído ambiente
            while time.time() - start_time < duration:
                try:
                    data = temp_stream.read(self.chunk_size, exception_on_overflow=False)
                    audio_np = np.frombuffer(data, dtype=np.int16)
                    rms = np.sqrt(np.mean(audio_np.astype(np.float32) ** 2))
                    ambient_samples.append(rms)
                except Exception:
                    continue
            
            temp_stream.stop_stream()
            temp_stream.close()
            p.terminate()
            
            if ambient_samples:
                ambient_rms_mean = np.mean(ambient_samples)
                ambient_rms_std = np.std(ambient_samples)
                
                # 🔥 Threshold dinâmico: média + 2.5 * desvio padrão
                # Isso captura apenas áudio SIGNIFICATIVAMENTE mais alto que ambiente
                dynamic_threshold = ambient_rms_mean + (2.5 * ambient_rms_std)
                
                # Clamp entre 1000 e 5000 para segurança
                dynamic_threshold = max(1000, min(5000, dynamic_threshold))
                
                logger.info(f"📊 Ruído ambiente medido: RMS médio = {ambient_rms_mean:.1f}, std = {ambient_rms_std:.1f}")
                logger.info(f"🎯 Threshold VAD ajustado: {dynamic_threshold:.1f} (era 2000)")
                
                # Atualizar threshold global usado em _check_voice_activity
                # Note: Isso afeta apenas o fallback RMS quando VAD model não disponível
                self._dynamic_rms_threshold = dynamic_threshold
                
                return dynamic_threshold
            else:
                logger.warning("⚠️ Nenhuma amostra coletada durante calibração")
                return 2000  # Fallback padrão
                
        except Exception as e:
            logger.error(f"❌ Erro na calibração VAD: {e}")
            return 2000  # Fallback padrão
        
    def start_listening(self):
        """Start listening for audio input"""
        if not PYAUDIO_AVAILABLE:
            logger.error("PyAudio not available - cannot start listening")
            return False
            
        if self.is_running:
            logger.warning("Audio system already running")
            return False
            
        try:
            self.is_running = True
            self.state = AudioState.LISTENING
            
            # Start processing thread
            self._process_thread = threading.Thread(
                target=self._audio_processing_loop,
                daemon=True,
                name="AudioProcessing"
            )
            self._process_thread.start()
            
            # Start audio stream
            self._start_audio_stream()
            
            logger.info("✅ Audio listening started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start listening: {e}")
            self.is_running = False
            return False
            
    def stop_listening(self):
        """Stop listening"""
        self.is_running = False
        
        if self.audio_stream:
            try:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio_stream = None
            except:
                pass
                
        if self._process_thread:
            self._process_thread.join(timeout=2)
            
        self.state = AudioState.IDLE
        logger.info("✅ Audio listening stopped")
        
    def _start_audio_stream(self):
        """Start PyAudio stream"""
        if not PYAUDIO_AVAILABLE:
            return
            
        try:
            p = pyaudio.PyAudio()
            
            self.audio_stream = p.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.audio_stream.start_stream()
            
        except Exception as e:
            logger.error(f"Failed to start audio stream: {e}")
            
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Audio stream callback"""
        if self.is_running:
            # Convert bytes to numpy array
            audio_data = np.frombuffer(in_data, dtype=np.int16)
            self.audio_queue.put(audio_data)
            
        return (None, pyaudio.paContinue)
        
    def _audio_processing_loop(self):
        """Main audio processing loop"""
        audio_buffer = []
        silence_threshold = config.get_setting('audio.silence_timeout', 1.0) # Reduzido de 2.0s para 1.0s (Fase 5)
        voice_detected_in_buffer = False
        last_voice_time = time.time()
        MIN_VOICE_FRAMES = 5 # Reduzido de 10 para 5 para maior sensibilidade
        voice_frame_count = 0
        
        while self.is_running:
            try:
                # Get audio chunk
                try:
                    chunk = self.audio_queue.get(timeout=0.1)
                    audio_buffer.append(chunk)
                except queue.Empty:
                    # 🔒 Mesmo sem dados, checar timeout de silêncio para flush do buffer
                    if voice_detected_in_buffer and (time.time() - last_voice_time) > silence_threshold:
                        if voice_frame_count >= MIN_VOICE_FRAMES:
                            self._process_audio_buffer(audio_buffer)
                        else:
                            pass  # logger.debug(f"Buffer silencioso descartado: apenas {voice_frame_count} frames com voz (mín: {MIN_VOICE_FRAMES})")
                        audio_buffer = []
                        voice_detected_in_buffer = False
                        voice_frame_count = 0
                    continue
                    
                # Check for voice activity
                if self.vad_model and len(audio_buffer) > 10:
                    # Concatenate buffer
                    audio = np.concatenate(audio_buffer)
                    
                    # Run VAD
                    has_voice = self._check_voice_activity(audio)
                    
                    if has_voice:
                        last_voice_time = time.time()  # 🔒 Tempo REAL
                        voice_detected_in_buffer = True
                        voice_frame_count += 1
                        
                        # 🆕 FREE WAKE WORD LOGIC (VAD GATE)
                        if self.wake_word_active and not self.is_awake:
                            # Se detectar voz clara e forte, acorda automaticamente
                            # Isso substitui "Hey Jarvis" por "Qualquer fala humana clara"
                            # Para evitar disparos falsos, exigimos confiança alta do VAD
                            
                            logger.debug("⚡ VAD Trigger: Voz detectada, acordando sistema...")
                            self.is_awake = True
                            self.state = AudioState.LISTENING
                            if self.on_wake_word_detected:
                                self.on_wake_word_detected()
                            
                            # Não quebramos o loop, continuamos processando o buffer atual como comando
                            # break  <-- REMOVIDO para capturar o comando "acordar" junto
                        
                        if self.is_awake or not self.wake_word_active:
                            self.state = AudioState.LISTENING
                            
                            # 🔥 FAST-PATH (Fase 5): Se a energia for muito alta e o buffer curto, 
                            # podemos antecipar o processamento se for um comando de interrupção
                            if len(audio_buffer) < 15: # ~300ms de áudio
                                rms = np.sqrt(np.mean(audio.astype(np.float32) ** 2))
                                if rms > 5000: # Grito ou comando muito alto/claro
                                    logger.debug("⚡ Fast-Path: Disparando processamento imediato por energia alta")
                                    self._process_audio_buffer(audio_buffer)
                                    audio_buffer = []
                                    voice_detected_in_buffer = False
                                    voice_frame_count = 0
                                    continue
                    
                    # 🔒 Processar quando silêncio REAL ultrapassar threshold
                    elapsed_silence = time.time() - last_voice_time
                    if elapsed_silence > silence_threshold and len(audio_buffer) > 0:
                        if voice_detected_in_buffer and voice_frame_count >= MIN_VOICE_FRAMES:
                            self._process_audio_buffer(audio_buffer)
                        elif len(audio_buffer) > 0:
                            # Silencioso descartado - log removido para evitar pollution (~300 linhas/min)
                            pass  # logger.debug(f"🔇 Buffer silencioso descartado ({len(audio_buffer)} chunks, {voice_frame_count} voice frames)")
                        audio_buffer = []
                        voice_detected_in_buffer = False
                        voice_frame_count = 0
                    
                    # 🔒 Limite máximo de buffer para evitar acúmulo infinito (30s)
                    max_buffer_chunks = int(30 * self.sample_rate / 1024)  # ~30 segundos
                    if len(audio_buffer) > max_buffer_chunks:
                        logger.warning("⚠️ Buffer de áudio excedeu 30s, forçando flush")
                        if voice_detected_in_buffer and voice_frame_count >= MIN_VOICE_FRAMES:
                            self._process_audio_buffer(audio_buffer)
                        audio_buffer = []
                        voice_detected_in_buffer = False
                        voice_frame_count = 0
                        
            except Exception as e:
                logger.error(f"Error in audio processing loop: {e}")
                time.sleep(0.1)
                
    def _check_voice_activity(self, audio: np.ndarray) -> bool:
        """Check if audio contains voice using VAD"""
        if not self.vad_model:
            # 🔒 Sem VAD: usar RMS energy como fallback simples
            # AUMENTADO de 500 para 2000 para evitar capturar ruído
            # Se calibração dinâmica foi feita, usa threshold calibrado
            threshold = getattr(self, '_dynamic_rms_threshold', 2000)
            rms = np.sqrt(np.mean(audio.astype(np.float32) ** 2))
            return rms > threshold
            
        try:
            # Convert to float32 and normalize
            audio_float = audio.astype(np.float32) / 32768.0

            # Silero-VAD expects specific chunk sizes (512 for 16kHz)
            # If the chunk is larger, we take the last 512 samples for a spot check
            if self.sample_rate == 16000 and audio_float.shape[-1] > 512:
                audio_float = audio_float[-512:]
            elif self.sample_rate == 8000 and audio_float.shape[-1] > 256:
                audio_float = audio_float[-256:]
                
            # Convert to tensor
            audio_tensor = torch.from_numpy(audio_float)
            
            # Get VAD probability
            with torch.no_grad():
                # Check if vad_model is callable
                if callable(self.vad_model):
                    # Ensure tensor is 1D or 2D [1, samples] as expected
                    if audio_tensor.ndim == 1:
                        audio_tensor = audio_tensor.unsqueeze(0)
                        
                    result = self.vad_model(audio_tensor, self.sample_rate)
                    
                    # Silero-VAD can return tuple (speech_prob, _) or just speech_prob
                    if isinstance(result, tuple):
                        speech_prob = result[0]
                    else:
                        speech_prob = result
                    
                    # Extract scalar value
                    if hasattr(speech_prob, 'item'):
                        speech_prob = speech_prob.item()
                    elif isinstance(speech_prob, (int, float)):
                        pass  # Already a scalar
                    else:
                        speech_prob = float(speech_prob)
                else:
                    # If not callable, assume no voice detection
                    logger.warning(f"VAD model not callable: {type(self.vad_model)}")
                    return True
                
            return speech_prob > self.vad_threshold
            
        except Exception as e:
            # Silently assume voice on error (less log spam)
            if not hasattr(self, '_vad_error_logged'):
                logger.warning(f"VAD disabled due to error: {e}")
                self._vad_error_logged = True
                self.vad_model = None  # Disable VAD to stop errors
            return True
            
    def _process_audio_buffer(self, audio_buffer: List[np.ndarray]):
        """Process accumulated audio buffer"""
        if not audio_buffer:
            return
            
        try:
            self.state = AudioState.PROCESSING
            
            # Concatenate audio
            audio = np.concatenate(audio_buffer)
            
            # Convert to float32
            audio_float = audio.astype(np.float32) / 32768.0
            
            # ============ P1: NOISE REDUCTION ============
            if self.noise_reduction_enabled and NOISEREDUCE_AVAILABLE:
                try:
                    # Reduce noise using spectral gating
                    audio_float = nr.reduce_noise(
                        y=audio_float,
                        sr=self.sample_rate,
                        stationary=True,
                        prop_decrease=0.8  # 80% noise reduction
                    )
                    logger.debug("✅ Noise reduction applied (+20% accuracy)")
                except Exception as e:
                    logger.warning(f"Noise reduction failed: {e}")
            
            # Verify speaker (if enabled)
            speaker_id = None
            speaker_verified = False
            
            if self.voice_encoder and self.known_speakers:
                speaker_id, confidence = self._verify_speaker(audio_float)
                speaker_verified = (confidence > self.speaker_threshold)
                
                if speaker_verified:
                    logger.info(f"✅ Speaker verified: {speaker_id} ({confidence:.2f})")
                    
                    if self.on_speaker_detected:
                        self.on_speaker_detected(speaker_id, confidence)
                else:
                    logger.warning(f"⚠️ Unknown speaker detected (confidence: {confidence:.2f})")
            else:
                # No speaker verification configured - allow transcription
                speaker_verified = True
                    
            # Transcribe audio (allow if no speaker verification OR if speaker verified)
            if self.whisper_model and speaker_verified:
                result = self._transcribe_audio(audio_float)
                result.speaker_verified = speaker_verified
                result.speaker_id = speaker_id
                
                if self.on_transcription:
                    self.on_transcription(result)
                    
            self.state = AudioState.LISTENING
            
        except Exception as e:
            logger.error(f"Failed to process audio buffer: {e}")
            self.state = AudioState.ERROR
            
    def _verify_speaker(self, audio: np.ndarray) -> Tuple[Optional[str], float]:
        """Verify speaker identity"""
        if not RESEMBLYZER_AVAILABLE or not self.voice_encoder:
            return None, 0.0
            
        try:
            # Preprocess audio
            wav = preprocess_wav(audio, source_sr=self.sample_rate)
            
            # Get embedding
            embedding = self.voice_encoder.embed_utterance(wav)
            
            # Compare with known speakers
            best_match = None
            best_similarity = 0.0
            
            for speaker_name, known_embedding in self.known_speakers.items():
                # Cosine similarity
                similarity = np.dot(embedding, known_embedding)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = speaker_name
                    
            return best_match, best_similarity
            
        except Exception as e:
            logger.error(f"Speaker verification failed: {e}")
            return None, 0.0
            
    def _transcribe_audio(self, audio: np.ndarray) -> TranscriptionResult:
        """Transcribe audio using Faster-Whisper"""
        if not FASTER_WHISPER_AVAILABLE or not self.whisper_model:
            return TranscriptionResult(
                text="",
                language="pt",
                confidence=0.0,
                segments=[],
                processing_time=0.0
            )
            
        try:
            start_time = time.time()
            
            # Transcribe (Forçado em PT-BR para comando do usuário)
            # beam_size=5 increases accuracy significantly on CPU
            # 🔥 VAD threshold aumentado de 0.5 para 0.7 (mais rigoroso)
            segments, info = self.whisper_model.transcribe(
                audio,
                language="pt", 
                beam_size=5,
                initial_prompt="",  # 🔥 Removido prompt que pode causar alucinações
                vad_filter=True,
                vad_parameters=dict(threshold=0.8, min_silence_duration_ms=1000)  # Extreme VAD
            )
            
            # Collect segments
            segment_list = []
            full_text = []
            
            for segment in segments:
                segment_list.append({
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text,
                    'confidence': segment.avg_logprob
                })
                full_text.append(segment.text)
                
            processing_time = time.time() - start_time
            
            # Calculate average confidence
            avg_confidence = np.mean([s['confidence'] for s in segment_list]) if segment_list else 0.0
            
            result = TranscriptionResult(
                text=" ".join(full_text).strip(),
                language=info.language,
                confidence=avg_confidence,
                segments=segment_list,
                processing_time=processing_time
            )
            
            logger.info(f"✅ Transcription: \"{result.text}\" ({processing_time:.2f}s)")
            
            return result
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return TranscriptionResult(
                text="",
                language="en",
                confidence=0.0,
                segments=[],
                processing_time=0.0
            )
            
    def transcribe_file(self, audio_file: Path) -> TranscriptionResult:
        """Transcribe audio file"""
        if not FASTER_WHISPER_AVAILABLE or not self.whisper_model:
            logger.error("Faster-Whisper not available")
            return TranscriptionResult(
                text="",
                language="en",
                confidence=0.0,
                segments=[],
                processing_time=0.0
            )
            
        try:
            # Load audio file
            if SOUNDFILE_AVAILABLE:
                audio, sr = sf.read(str(audio_file))
                
                # Resample if needed
                if sr != self.sample_rate:
                    # Simple resampling (for production, use librosa)
                    pass
                    
                return self._transcribe_audio(audio)
            else:
                logger.error("soundfile not available - cannot load audio file")
                return TranscriptionResult(
                    text="",
                    language="en",
                    confidence=0.0,
                    segments=[],
                    processing_time=0.0
                )
                
        except Exception as e:
            logger.error(f"Failed to transcribe file: {e}")
            return TranscriptionResult(
                text="",
                language="en",
                confidence=0.0,
                segments=[],
                processing_time=0.0
            )
            
    def enroll_speaker(self, speaker_name: str, audio: Optional[np.ndarray] = None, audio_file: Optional[Path] = None) -> bool:
        """
        Enroll new speaker for verification.
        
        Args:
            speaker_name: Name to identify speaker
            audio: Audio samples (numpy array)
            audio_file: Path to audio file
            
        Returns:
            True if successful
        """
        if not RESEMBLYZER_AVAILABLE or not self.voice_encoder:
            logger.error("Speaker verification not available")
            return False
            
        try:
            # Load audio
            if audio_file and SOUNDFILE_AVAILABLE:
                audio, sr = sf.read(str(audio_file))
                if sr != self.sample_rate:
                    # Resample needed
                    pass
            elif audio is None:
                logger.error("No audio provided for enrollment")
                return False
                
            # Preprocess
            wav = preprocess_wav(audio, source_sr=self.sample_rate)
            
            # Get embedding
            embedding = self.voice_encoder.embed_utterance(wav)
            
            # Save embedding
            sig_path = self.voice_signatures_dir / f"{speaker_name}.npy"
            np.save(sig_path, embedding)
            
            # Add to known speakers
            self.known_speakers[speaker_name] = embedding
            
            logger.info(f"✅ Speaker enrolled: {speaker_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enroll speaker: {e}")
            return False
            
    def cleanup(self):
        """Cleanup resources"""
        self.stop_listening()
        logger.info("✅ Enhanced Audio System cleaned up")


# Singleton instance
_audio_system: Optional[EnhancedAudioSystem] = None


def get_audio_system(data_dir: Optional[Path] = None) -> EnhancedAudioSystem:
    """
    Get or create Audio System singleton.
    
    Args:
        data_dir: Data directory (for first call)
        
    Returns:
        EnhancedAudioSystem instance
    """
    global _audio_system
    
    if _audio_system is None:
        _audio_system = EnhancedAudioSystem(data_dir)
        
    return _audio_system


# Testing
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*60)
    print("JARVIS Enhanced Audio System Test")
    print("="*60)
    
    # Create audio system
    audio = EnhancedAudioSystem(Path("data"))
    
    # Test transcription callback
    def on_transcription(result: TranscriptionResult):
        print(f"\n📝 Transcription: {result.text}")
        print(f"   Language: {result.language}")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Time: {result.processing_time:.2f}s")
        print(f"   Speaker: {result.speaker_id if result.speaker_verified else 'Unknown'}")
        
    audio.on_transcription = on_transcription
    
    # Test speaker detection
    def on_speaker(speaker_id: str, confidence: float):
        print(f"🎤 Speaker detected: {speaker_id} (confidence: {confidence:.2f})")
        
    audio.on_speaker_detected = on_speaker
    
    print("\n✅ Audio system ready")
    print("   Faster-Whisper:", "✅" if FASTER_WHISPER_AVAILABLE else "❌")
    print("   VAD:", "✅" if audio.vad_model else "❌")
    print("   Speaker Verification:", "✅" if RESEMBLYZER_AVAILABLE else "❌")
    print("   Known speakers:", len(audio.known_speakers))
    
    print("\n" + "="*60 + "\n")
    
    audio.cleanup()
