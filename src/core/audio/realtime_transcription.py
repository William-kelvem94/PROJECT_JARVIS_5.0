"""
JARVIS 5.0 - Real-time Audio Stream com Silero-VAD
===================================================
Sprint 1: Real-time Transcription
Pipeline: Ã¡udio stream â†’ Silero VAD â†’ buffer circular (3s) â†’ faster-whisper â†’ callback

DEPENDENCIES: pip install silero-vad
USAGE: from src.core.realtime_transcription import RealtimeTranscriber
"""

import sys
from pathlib import Path
import torch
import numpy as np
import threading
import time
import logging
from collections import deque
from typing import Callable, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import pyaudio

    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logger.warning("PyAudio not available. Real-time transcription disabled.")

try:
    from faster_whisper import WhisperModel

    FASTER_WHISPER_AVAILABLE = True
except (ImportError, AttributeError) as e:
    FASTER_WHISPER_AVAILABLE = False
    logger.warning(f"Faster-Whisper not available: {e}")


class AudioStream:
    """
    Real-time audio stream captor with circular buffer
    """

    def __init__(self, sample_rate=16000, chunk_size=512, channels=1):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.is_recording = False
        self.stream = None
        self.audio = None
        self.buffer = deque(maxlen=int(sample_rate * 10))  # 10s buffer

    def start(self):
        """Start audio stream"""
        if not PYAUDIO_AVAILABLE:
            logger.error("PyAudio not available")
            return False

        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback,
            )
            self.is_recording = True
            self.stream.start_stream()
            logger.info(f"âœ… Audio stream started (SR: {self.sample_rate}Hz)")
            return True
        except Exception as e:
            logger.error(f"Failed to start audio stream: {e}")
            return False

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback"""
        if status:
            logger.warning(f"Audio status: {status}")

        # Convert to numpy
        audio_data = np.frombuffer(in_data, dtype=np.float32)
        self.buffer.extend(audio_data)

        return (in_data, pyaudio.paContinue)

    def read_buffer(self, duration=3.0):
        """
        Read last N seconds from buffer

        Args:
            duration: Duration in seconds

        Returns:
            numpy array
        """
        num_samples = int(self.sample_rate * duration)
        if len(self.buffer) < num_samples:
            # Pad with zeros if not enough data
            audio_chunk = np.array(list(self.buffer))
            padding = np.zeros(num_samples - len(audio_chunk))
            return np.concatenate([padding, audio_chunk])
        else:
            # Get last N seconds
            return np.array(list(self.buffer)[-num_samples:])

    def stop(self):
        """Stop audio stream"""
        if self.stream:
            self.is_recording = False
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        logger.info("ðŸ›‘ Audio stream stopped")


class SileroVAD:
    """
    Silero Voice Activity Detection
    Detecta voz em tempo real usando modelo neural
    """

    def __init__(self, threshold=0.5, sample_rate=16000):
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.model = None
        self.utils = None

        try:
            # Load Silero VAD model
            model, utils = torch.hub.load(
                repo_or_dir="snakers4/silero-vad",
                model="silero_vad",
                force_reload=False,
                onnx=False,
            )
            self.model = model
            self.utils = utils
            self.get_speech_timestamps = utils[0]
            logger.info("âœ… Silero VAD loaded")
        except Exception as e:
            logger.error(f"Failed to load Silero VAD: {e}")

    def is_speech(self, audio_chunk):
        """
        Check if audio chunk contains speech

        Args:
            audio_chunk: numpy array (float32)

        Returns:
            bool: True if speech detected
        """
        if self.model is None:
            return False

        try:
            # Convert to tensor
            audio_tensor = torch.from_numpy(audio_chunk)

            # Get speech probability
            speech_prob = self.model(audio_tensor, self.sample_rate).item()

            return speech_prob > self.threshold
        except Exception as e:
            logger.error(f"VAD error: {e}")
            return False

    def get_speech_segments(self, audio_array):
        """
        Get speech segments from audio

        Args:
            audio_array: Full audio numpy array

        Returns:
            List of (start, end) tuples in samples
        """
        if self.model is None or self.get_speech_timestamps is None:
            return []

        try:
            audio_tensor = torch.from_numpy(audio_array)
            speech_timestamps = self.get_speech_timestamps(
                audio_tensor,
                self.model,
                sampling_rate=self.sample_rate,
                threshold=self.threshold,
            )
            return [(ts["start"], ts["end"]) for ts in speech_timestamps]
        except Exception as e:
            logger.error(f"Speech segmentation error: {e}")
            return []


class RealtimeTranscriber:
    """
    Real-time speech transcription system
    Pipeline: AudioStream â†’ Silero VAD â†’ Buffer â†’ Faster-Whisper â†’ Callback
    """

    def __init__(
        self,
        model_size="base",
        language="pt",
        vad_threshold=0.5,
        callback: Optional[Callable[[str], None]] = None,
        sample_rate=16000,
    ):
        """
        Args:
            model_size: Whisper model size ('tiny', 'base', 'small', 'medium')
            language: Language code ('pt', 'en', etc)
            vad_threshold: Voice activity detection threshold
            callback: Function called with transcribed text
            sample_rate: Audio sample rate
        """
        self.language = language
        self.callback = callback
        self.sample_rate = sample_rate
        self.is_running = False

        # Initialize components
        self.audio_stream = AudioStream(sample_rate=sample_rate)
        self.vad = SileroVAD(threshold=vad_threshold, sample_rate=sample_rate)

        # Initialize Whisper
        if FASTER_WHISPER_AVAILABLE:
            try:
                self.whisper = WhisperModel(
                    model_size,
                    device="cuda" if torch.cuda.is_available() else "cpu",
                    compute_type="float16" if torch.cuda.is_available() else "int8",
                )
                logger.info(f"âœ… Whisper {model_size} loaded")
            except Exception as e:
                logger.error(f"Failed to load Whisper: {e}")
                self.whisper = None
        else:
            self.whisper = None
            logger.warning("Faster-Whisper not available")

        # Processing thread
        self.processing_thread = None
        self.last_transcription_time = 0
        self.min_interval = 1.0  # Minimum interval between transcriptions

    def start(self):
        """Start real-time transcription"""
        if not PYAUDIO_AVAILABLE or not self.whisper:
            logger.error("Cannot start transcription: missing dependencies")
            return False

        logger.info("=" * 70)
        logger.info("ðŸŽ™ï¸  Starting Real-time Transcription")
        logger.info("=" * 70)

        # Start audio stream
        if not self.audio_stream.start():
            return False

        # Start processing thread
        self.is_running = True
        self.processing_thread = threading.Thread(
            target=self._processing_loop, daemon=True
        )
        self.processing_thread.start()

        logger.info("âœ… Real-time transcription active")
        return True

    def _processing_loop(self):
        """Main processing loop (runs in thread)"""
        while self.is_running:
            try:
                # ADJUST PERFORMANCE (Adaptive Scaling)
                try:
                    from src.core.management.hardware_manager import hardware_manager

                    is_throttled = hardware_manager.is_throttled
                except:
                    is_throttled = False

                interval = 2.0 if is_throttled else 1.0  # Menos scans se estiver pesado
                beam = 2 if is_throttled else 5  # Menos precisão, mais velocidade

                # Read audio buffer (last 3 seconds)
                audio_chunk = self.audio_stream.read_buffer(duration=3.0)

                # Check voice activity
                if self.vad.is_speech(audio_chunk):
                    # Throttle transcriptions
                    current_time = time.time()
                    if current_time - self.last_transcription_time < interval:
                        time.sleep(0.1)
                        continue

                    self.last_transcription_time = current_time

                    # Transcribe
                    try:
                        segments, info = self.whisper.transcribe(
                            audio_chunk,
                            language=self.language,
                            beam_size=beam,
                            vad_filter=False,  # Already filtered by Silero
                        )

                        # Extract text
                        text = " ".join([seg.text.strip() for seg in segments])

                        if text:
                            logger.info(f"🎯 {text}")

                            # Call callback
                            if self.callback:
                                self.callback(text)

                    except Exception as e:
                        logger.error(f"Transcription error: {e}")

                else:
                    # No speech detected, sleep longer if throttled
                    time.sleep(0.2 if is_throttled else 0.1)

            except Exception as e:
                logger.error(f"Processing loop error: {e}")
                time.sleep(0.5)

    def stop(self):
        """Stop real-time transcription"""
        logger.info("ðŸ›‘ Stopping transcription...")
        self.is_running = False

        if self.processing_thread:
            self.processing_thread.join(timeout=2.0)

        self.audio_stream.stop()
        logger.info("âœ… Transcription stopped")


# Example usage
if __name__ == "__main__":

    def on_transcription(text):
        """Callback for transcribed text"""
        print(f"\nðŸ“ Transcribed: {text}")

    # Create transcriber
    transcriber = RealtimeTranscriber(
        model_size="base", language="pt", vad_threshold=0.5, callback=on_transcription
    )

    # Start
    if transcriber.start():
        print("\nðŸŽ™ï¸  Speak now... (Ctrl+C to stop)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping...")
            transcriber.stop()
