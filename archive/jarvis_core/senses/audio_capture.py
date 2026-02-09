"""
Senses - Audio Capture
Captura de áudio real do microfone
"""

import logging
import numpy as np
from typing import Optional
from pathlib import Path
import wave

logger = logging.getLogger(__name__)

class AudioCapture:
    """Captura de áudio do microfone"""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.pyaudio = None
        self.stream = None
        self.is_recording = False
        
        try:
            import pyaudio
            self.pyaudio = pyaudio.PyAudio()
            logger.info(f"✅ Audio Capture inicializado ({sample_rate}Hz)")
        except ImportError:
            logger.error("❌ pyaudio não instalado: pip install pyaudio")
    
    def start_recording(self) -> bool:
        """Inicia gravação"""
        if not self.pyaudio:
            return False
        
        try:
            import pyaudio
            
            self.stream = self.pyaudio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=1024
            )
            
            self.is_recording = True
            logger.info("🎤 Gravação iniciada")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar gravação: {e}")
            return False
    
    def stop_recording(self) -> bool:
        """Para gravação"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.is_recording = False
            logger.info("🛑 Gravação parada")
            return True
        return False
    
    def record_audio(self, duration: float, output_path: Optional[str] = None) -> Optional[str]:
        """Grava áudio por X segundos"""
        if not self.pyaudio:
            return None
        
        output_path = output_path or "data/temp/audio_input.wav"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            import pyaudio
            
            # Abrir stream
            stream = self.pyaudio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=1024
            )
            
            logger.info(f"🎤 Gravando {duration}s...")
            
            frames = []
            num_frames = int(self.sample_rate / 1024 * duration)
            
            for _ in range(num_frames):
                data = stream.read(1024)
                frames.append(data)
            
            # Parar stream
            stream.stop_stream()
            stream.close()
            
            # Salvar WAV
            with wave.open(output_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.pyaudio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(frames))
            
            logger.info(f"✅ Áudio salvo: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Erro ao gravar: {e}")
            return None
    
    def get_audio_level(self) -> float:
        """Retorna nível de áudio atual (0-1)"""
        if not self.stream or not self.is_recording:
            return 0.0
        
        try:
            data = self.stream.read(1024, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            level = np.abs(audio_data).mean() / 32768.0
            return float(level)
        except:
            return 0.0
    
    def cleanup(self):
        """Limpa recursos"""
        if self.stream:
            self.stream.close()
        if self.pyaudio:
            self.pyaudio.terminate()


# Instância global
audio_capture = AudioCapture()
