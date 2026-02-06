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

import logging
import threading
import queue
import time
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================================================
# CONDITIONAL IMPORTS (Graceful Degradation)
# ============================================================================
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False
    logger.warning("⚠️ faster-whisper not available - STT disabled")

try:
    import torch
    import torchaudio
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("⚠️ torch not available - advanced audio features disabled")

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    logger.warning("⚠️ soundfile not available - audio I/O limited")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logger.warning("⚠️ pyaudio not available - microphone input disabled")

# Fallback for speaker recognition
try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    RESEMBLYZER_AVAILABLE = True
except ImportError:
    RESEMBLYZER_AVAILABLE = False
    logger.warning("⚠️ resemblyzer not available - speaker verification disabled")


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
        self.whisper_model_size = "base"  # tiny, base, small, medium, large
        
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
        
        # Audio stream
        self.audio_stream = None
        self.audio_queue = queue.Queue()
        
        # Processing thread
        self._process_thread = None
        self._process_lock = threading.Lock()
        
        # Callbacks
        self.on_transcription: Optional[Callable[[TranscriptionResult], None]] = None
        self.on_speaker_detected: Optional[Callable[[str, float], None]] = None
        
        # Initialize components
        self._initialize_components()
        
        logger.info("✅ Enhanced Audio System initialized")
        logger.info(f"   Faster-Whisper: {'✅' if FASTER_WHISPER_AVAILABLE else '❌'}")
        logger.info(f"   PyAudio: {'✅' if PYAUDIO_AVAILABLE else '❌'}")
        logger.info(f"   Speaker Verification: {'✅' if RESEMBLYZER_AVAILABLE else '❌'}")
        
    def _initialize_components(self):
        """Initialize audio processing components"""
        # Initialize Faster-Whisper
        if FASTER_WHISPER_AVAILABLE:
            try:
                logger.info(f"Loading Faster-Whisper model ({self.whisper_model_size})...")
                
                # Use CPU or GPU based on availability
                device = "cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"
                compute_type = "float16" if device == "cuda" else "int8"
                
                self.whisper_model = WhisperModel(
                    self.whisper_model_size,
                    device=device,
                    compute_type=compute_type
                )
                
                logger.info(f"✅ Whisper model loaded ({device}, {compute_type})")
                
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                
        # Initialize Silero-VAD
        if TORCH_AVAILABLE:
            try:
                logger.info("Loading Silero-VAD model...")
                self.vad_model = torch.hub.load(
                    repo_or_dir='snakers4/silero-vad',
                    model='silero_vad',
                    force_reload=False,
                    onnx=False
                )
                logger.info("✅ Silero-VAD model loaded")
                
            except Exception as e:
                logger.warning(f"Failed to load VAD model: {e}")
                
        # Initialize speaker encoder
        if RESEMBLYZER_AVAILABLE:
            try:
                logger.info("Loading voice encoder...")
                self.voice_encoder = VoiceEncoder()
                logger.info("✅ Voice encoder loaded")
                
                # Load known speakers
                self._load_voice_signatures()
                
            except Exception as e:
                logger.warning(f"Failed to load voice encoder: {e}")
                
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
        silence_threshold = 0.5  # seconds
        silence_timer = 0
        
        while self.is_running:
            try:
                # Get audio chunk
                try:
                    chunk = self.audio_queue.get(timeout=0.1)
                    audio_buffer.append(chunk)
                except queue.Empty:
                    continue
                    
                # Check for voice activity
                if self.vad_model and len(audio_buffer) > 10:
                    # Concatenate buffer
                    audio = np.concatenate(audio_buffer)
                    
                    # Run VAD
                    has_voice = self._check_voice_activity(audio)
                    
                    if has_voice:
                        silence_timer = 0
                        self.state = AudioState.LISTENING
                    else:
                        silence_timer += 0.1
                        
                    # Process on silence end
                    if silence_timer > silence_threshold and len(audio_buffer) > 0:
                        self._process_audio_buffer(audio_buffer)
                        audio_buffer = []
                        silence_timer = 0
                        
            except Exception as e:
                logger.error(f"Error in audio processing loop: {e}")
                time.sleep(0.1)
                
    def _check_voice_activity(self, audio: np.ndarray) -> bool:
        """Check if audio contains voice using VAD"""
        if not self.vad_model:
            return True  # Assume voice if no VAD
            
        try:
            # Convert to float32 and normalize
            audio_float = audio.astype(np.float32) / 32768.0
            
            # Convert to tensor
            audio_tensor = torch.from_numpy(audio_float)
            
            # Get VAD probability
            with torch.no_grad():
                speech_prob = self.vad_model(audio_tensor, self.sample_rate).item()
                
            return speech_prob > self.vad_threshold
            
        except Exception as e:
            logger.error(f"VAD check failed: {e}")
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
                    logger.warning(f"⚠️ Unauthorized speaker detected")
                    
            # Transcribe audio
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
                language="en",
                confidence=0.0,
                segments=[],
                processing_time=0.0
            )
            
        try:
            start_time = time.time()
            
            # Transcribe
            segments, info = self.whisper_model.transcribe(
                audio,
                language="en",
                vad_filter=True,
                vad_parameters=dict(threshold=self.vad_threshold)
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
