"""
JARVIS Hearing - Sistema de Reconhecimento de Voz (STT)
Suporte para múltiplas engines: Whisper, SpeechRecognition, Vosk
"""

import os
import time
import threading
import queue
from typing import Optional, Callable, Dict, Any
from pathlib import Path

from config import config

class Hearing:
    """
    Sistema de reconhecimento de voz do JARVIS.
    Suporte para múltiplas engines com fallback automático.
    """

    def __init__(self):
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.result_callback = None

        # Configurações de voz
        self.engine = config.get("voice.stt_engine", "speech_recognition")
        self.language = config.get("voice.language", "pt-BR")
        self.wake_word = config.get("voice.wake_word", "jarvis").lower()

        # Engines disponíveis
        self.engines = {
            "speech_recognition": self._init_speech_recognition,
            "whisper": self._init_whisper,
            "vosk": self._init_vosk
        }

        # Inicializar engine escolhida
        self.current_engine = None
        self._init_engine()

    def _init_engine(self):
        """Inicializa a engine de STT escolhida."""
        try:
            init_func = self.engines.get(self.engine, self._init_speech_recognition)
            self.current_engine = init_func()
            print(f" STT Engine inicializada: {self.engine}")
        except Exception as e:
            print(f" Erro ao inicializar {self.engine}: {e}")
            # Fallback para speech_recognition
            try:
                self.current_engine = self._init_speech_recognition()
                self.engine = "speech_recognition"
                print(" Fallback para SpeechRecognition")
            except Exception as e2:
                print(f" Falha crítica no STT: {e2}")
                self.current_engine = None

    def _init_speech_recognition(self):
        """Inicializa SpeechRecognition (Google Speech API)."""
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            # Ajustar para ambiente (notebook pode ter mais ruído)
            if config.get("hardware.is_laptop"):
                recognizer.energy_threshold = 300
                recognizer.dynamic_energy_threshold = True
            else:
                recognizer.energy_threshold = 400

            return {
                "type": "speech_recognition",
                "recognizer": recognizer,
                "source": None
            }
        except ImportError:
            raise Exception("SpeechRecognition não instalado")

    def _init_whisper(self):
        """Inicializa Whisper (OpenAI)."""
        try:
            import whisper
            model = whisper.load_model("base")  # Modelo leve
            return {
                "type": "whisper",
                "model": model
            }
        except ImportError:
            raise Exception("OpenAI Whisper não instalado")

    def _init_vosk(self):
        """Inicializa Vosk (offline)."""
        try:
            from vosk import Model, KaldiRecognizer
            import json

            # Baixar modelo português se não existir
            model_path = Path("./models/vosk-model-pt")
            if not model_path.exists():
                print(" Baixando modelo Vosk português...")
                # Nota: seria necessário implementar download automático

            model = Model(str(model_path))
            return {
                "type": "vosk",
                "model": model,
                "recognizer": None  # Inicializado por áudio
            }
        except ImportError:
            raise Exception("Vosk não instalado")

    def start_listening(self, callback: Optional[Callable] = None):
        """
        Inicia escuta contínua.

        Args:
            callback: Função chamada quando reconhecer fala
        """
        if self.is_listening:
            return

        self.result_callback = callback
        self.is_listening = True

        # Iniciar thread de escuta
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()

        print(" JARVIS está ouvindo...")

    def stop_listening(self):
        """Para de ouvir."""
        self.is_listening = False
        print(" JARVIS parou de ouvir")

    def listen_once(self, timeout: int = 5) -> Optional[str]:
        """
        Escuta uma única vez.

        Args:
            timeout: Tempo limite em segundos

        Returns:
            Texto reconhecido ou None
        """
        if not self.current_engine:
            return None

        try:
            if self.engine == "speech_recognition":
                return self._listen_speech_recognition(timeout)
            elif self.engine == "whisper":
                return self._listen_whisper(timeout)
            elif self.engine == "vosk":
                return self._listen_vosk(timeout)
        except Exception as e:
            print(f" Erro na escuta: {e}")
            return None

    def _listen_loop(self):
        """Loop principal de escuta contínua."""
        while self.is_listening:
            try:
                text = self.listen_once(timeout=3)
                if text and self.result_callback:
                    # Verificar wake word
                    if self.wake_word in text.lower():
                        # Remover wake word e processar
                        clean_text = text.lower().replace(self.wake_word, "").strip()
                        if clean_text:
                            self.result_callback(clean_text)
                    elif not self.wake_word:  # Se não usar wake word
                        self.result_callback(text)

                time.sleep(0.1)  # Pequena pausa

            except Exception as e:
                print(f"Erro no loop de escuta: {e}")
                time.sleep(1)

    def _listen_speech_recognition(self, timeout: int) -> Optional[str]:
        """Escuta usando SpeechRecognition."""
        try:
            import speech_recognition as sr

            engine = self.current_engine
            recognizer = engine["recognizer"]

            with sr.Microphone() as source:
                print(" Ouvindo...")
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=10)

                print(" Processando...")
                text = recognizer.recognize_google(audio, language=self.language)
                return text

        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            print(" Não entendi o áudio")
            return None
        except sr.RequestError as e:
            print(f" Erro na API do Google: {e}")
            return None

    def _listen_whisper(self, timeout: int) -> Optional[str]:
        """Escuta usando Whisper."""
        try:
            import whisper
            import numpy as np
            import sounddevice as sd

            engine = self.current_engine
            model = engine["model"]

            # Configurações de áudio
            sample_rate = 16000
            duration = min(timeout, 10)  # Máximo 10 segundos

            print(" Gravando áudio...")
            audio = sd.rec(int(sample_rate * duration),
                          samplerate=sample_rate,
                          channels=1,
                          dtype=np.float32)
            sd.wait()

            print(" Transcrevendo...")
            result = model.transcribe(audio, language="pt")
            text = result["text"].strip()

            return text if text else None

        except ImportError:
            print(" sounddevice não instalado para Whisper")
            return None
        except Exception as e:
            print(f" Erro no Whisper: {e}")
            return None

    def _listen_vosk(self, timeout: int) -> Optional[str]:
        """Escuta usando Vosk."""
        try:
            from vosk import KaldiRecognizer
            import sounddevice as sd
            import json

            engine = self.current_engine
            model = engine["model"]

            # Configurações
            sample_rate = 16000
            device = None  # Default microphone

            recognizer = KaldiRecognizer(model, sample_rate)
            recognizer.SetWords(True)

            print(" Ouvindo (Vosk)...")

            def callback(indata, frames, time, status):
                if recognizer.AcceptWaveform(bytes(indata)):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "")
                    if text:
                        self.audio_queue.put(text)

            with sd.RawInputStream(samplerate=sample_rate,
                                 blocksize=8000,
                                 device=device,
                                 dtype='int16',
                                 channels=1,
                                 callback=callback):

                # Aguardar resultado ou timeout
                try:
                    text = self.audio_queue.get(timeout=timeout)
                    return text
                except queue.Empty:
                    return None

        except Exception as e:
            print(f" Erro no Vosk: {e}")
            return None

    def calibrate_microphone(self):
        """Calibra o microfone para o ambiente."""
        if self.engine == "speech_recognition":
            try:
                import speech_recognition as sr
                recognizer = self.current_engine["recognizer"]

                with sr.Microphone() as source:
                    print(" Calibrando microfone... Fique em silêncio")
                    recognizer.adjust_for_ambient_noise(source, duration=2)
                    print(f" Calibrado. Threshold: {recognizer.energy_threshold}")

            except Exception as e:
                print(f" Erro na calibração: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Retorna status do sistema de hearing."""
        return {
            "is_listening": self.is_listening,
            "engine": self.engine,
            "language": self.language,
            "wake_word": self.wake_word,
            "engine_available": self.current_engine is not None
        }