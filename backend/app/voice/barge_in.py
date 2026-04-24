import os
import torch
import numpy as np
import onnxruntime as ort
import sounddevice as sd
import threading
from loguru import logger

class BargeInManager:
    """
    Detecta voz humana durante a fala do JARVIS para permitir interrupção (Barge-in).
    Usa Silero VAD (ONNX) para máxima eficiência (CPU < 5%).
    """
    
    def __init__(self, model_path=None):
        self.model_path = model_path or os.path.expanduser("~/.jarvis/models/silero_vad.onnx")
        self.session = None
        self.is_listening = False
        self._stop_event = threading.Event()
        self.interrupt_callback = None
        self._initialize_model()

    def _initialize_model(self):
        """Inicializa a sessão ONNX do Silero VAD."""
        if not os.path.exists(self.model_path):
            logger.info("📥 Baixando modelo Silero VAD (ONNX)...")
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            import urllib.request
            url = "https://github.com/snakers4/silero-vad/raw/master/files/silero_vad.onnx"
            urllib.request.urlretrieve(url, self.model_path)
        
        # Carrega com provedor CPU para garantir compatibilidade multi-hardware (Book2/Desktop)
        self.session = ort.InferenceSession(self.model_path, providers=['CPUExecutionProvider'])
        logger.success("🎙️ Silero VAD (Barge-in) pronto para escuta ativa.")

    def start_vad_listener(self, callback):
        """Inicia a escuta em thread separada."""
        if self.is_listening: return
        self.is_listening = True
        self.interrupt_callback = callback
        self._stop_event.clear()
        self.thread = threading.Thread(target=self._vad_loop, daemon=True)
        self.thread.start()

    def stop_vad_listener(self):
        """Para a escuta."""
        self.is_listening = False
        self._stop_event.set()

    def _vad_loop(self):
        """Loop de captura e análise de áudio."""
        sample_rate = 16000
        window_size_samples = 512 # Recomendado para Silero VAD
        
        def audio_callback(indata, frames, time, status):
            if not self.is_listening: return
            
            # Converte para float32 conforme exigido pelo modelo
            audio_int16 = np.frombuffer(indata, dtype=np.int16)
            audio_float32 = audio_int16.astype(np.float32) / 32768.0
            
            # Prepara inputs para o ONNX
            ort_inputs = {
                'input': audio_float32.reshape(1, -1),
                'sr': np.array([sample_rate], dtype=np.int64)
            }
            
            # Inferência
            out = self.session.run(None, ort_inputs)[0]
            prob = out[0][0]
            
            if prob > 0.9:
                logger.warning(f"⚠️ [Barge-in] Voz detectada (prob: {prob:.2f}). Interrompendo JARVIS...")
                if self.interrupt_callback:
                    self.interrupt_callback()
                self.stop_vad_listener()

        try:
            with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16', 
                                blocksize=window_size_samples, callback=audio_callback):
                while not self._stop_event.is_set():
                    self._stop_event.wait(timeout=0.1)
        except Exception as e:
            logger.error(f"Erro no stream de áudio (Barge-in): {e}")

# Singleton para uso no sistema
barge_in = BargeInManager()
