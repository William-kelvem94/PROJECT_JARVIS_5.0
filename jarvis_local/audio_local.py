#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - MÓDULO DE PROCESSAMENTO DE ÁUDIO LOCAL
Processamento 100% local: STT (Whisper), TTS (Piper), Speaker Diarization
"""

import os
import sys
import numpy as np
import soundfile as sf
import time
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
import queue
import threading
import json

# Verificar disponibilidade de bibliotecas
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️ Whisper não disponível. Reconhecimento de voz limitado.")

try:
    from piper.voice import PiperVoice
    from piper.download import ensure_voice_exists
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False
    print("⚠️ Piper TTS não disponível. Síntese de voz limitada.")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("⚠️ PyAudio não disponível. Captura de áudio limitada.")

try:
    from pyannote.audio import Pipeline
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False
    print("⚠️ PyAnnote não disponível. Diarização limitada.")


class LocalSpeechRecognition:
    """Reconhecimento de voz 100% local usando Whisper"""

    def __init__(self, models_dir="./models", model_size="base"):
        self.models_dir = Path(models_dir)
        self.model_size = model_size

        # Carregar modelo Whisper local
        self.model = None
        self._load_whisper_model()

        # Estatísticas
        self.stats = {
            'transcriptions': 0,
            'total_audio_seconds': 0.0,
            'avg_processing_time': 0.0,
            'errors': 0
        }

    def _load_whisper_model(self):
        """Carregar modelo Whisper local"""
        if not WHISPER_AVAILABLE:
            print("❌ Whisper não disponível")
            return

        try:
            # Verificar se modelo existe localmente
            model_path = self.models_dir / f"whisper_{self.model_size}.pt"

            if model_path.exists():
                print(f"✅ Carregando Whisper {self.model_size} do disco local")
                self.model = whisper.load_model(str(model_path))
            else:
                print(f"📥 Baixando Whisper {self.model_size}...")
                self.model = whisper.load_model(self.model_size)
                print(f"💾 Modelo salvo em: {model_path}")

            print(f"🎤 Whisper {self.model_size} carregado com sucesso")

        except Exception as e:
            print(f"❌ Erro ao carregar Whisper: {e}")

    def transcribe_audio(self, audio_path: str, language: str = "pt") -> Dict[str, Any]:
        """Transcrever áudio para texto"""
        if not self.model:
            return {"text": "", "error": "Modelo não carregado"}

        try:
            start_time = time.time()

            # Transcrição
            result = self.model.transcribe(
                audio_path,
                language=language,
                task="transcribe",
                verbose=False
            )

            processing_time = time.time() - start_time

            # Estatísticas
            self.stats['transcriptions'] += 1
            audio_duration = result.get('duration', 0)
            self.stats['total_audio_seconds'] += audio_duration
            self.stats['avg_processing_time'] = (
                (self.stats['avg_processing_time'] * (self.stats['transcriptions'] - 1)) +
                processing_time
            ) / self.stats['transcriptions']

            return {
                "text": result["text"].strip(),
                "language": result.get("language", language),
                "duration": audio_duration,
                "processing_time": processing_time,
                "segments": result.get("segments", [])
            }

        except Exception as e:
            self.stats['errors'] += 1
            return {"text": "", "error": str(e)}

    def transcribe_array(self, audio_array: np.ndarray, sample_rate: int = 16000,
                        language: str = "pt") -> Dict[str, Any]:
        """Transcrever array de áudio numpy"""
        if not self.model:
            return {"text": "", "error": "Modelo não carregado"}

        try:
            start_time = time.time()

            # Transcrição
            result = self.model.transcribe(
                audio_array,
                language=language,
                task="transcribe",
                verbose=False
            )

            processing_time = time.time() - start_time

            # Estatísticas
            self.stats['transcriptions'] += 1
            audio_duration = len(audio_array) / sample_rate
            self.stats['total_audio_seconds'] += audio_duration
            self.stats['avg_processing_time'] = (
                (self.stats['avg_processing_time'] * (self.stats['transcriptions'] - 1)) +
                processing_time
            ) / self.stats['transcriptions']

            return {
                "text": result["text"].strip(),
                "language": result.get("language", language),
                "duration": audio_duration,
                "processing_time": processing_time,
                "segments": result.get("segments", [])
            }

        except Exception as e:
            self.stats['errors'] += 1
            return {"text": "", "error": str(e)}

    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do reconhecimento"""
        return self.stats.copy()


class LocalTextToSpeech:
    """Síntese de voz 100% local usando Piper"""

    def __init__(self, models_dir="./models", voice_name="en_US-lessac-medium"):
        self.models_dir = Path(models_dir)
        self.voice_name = voice_name

        # Carregar voz Piper local
        self.voice = None
        self._load_piper_voice()

        # Estatísticas
        self.stats = {
            'syntheses': 0,
            'total_chars': 0,
            'avg_processing_time': 0.0,
            'errors': 0
        }

    def _load_piper_voice(self):
        """Carregar voz Piper local"""
        if not PIPER_AVAILABLE:
            print("❌ Piper TTS não disponível")
            return

        try:
            # Caminho da voz
            voice_path = self.models_dir / "piper_voices" / f"{self.voice_name}.onnx"
            config_path = self.models_dir / "piper_voices" / f"{self.voice_name}.onnx.json"

            if voice_path.exists() and config_path.exists():
                print(f"✅ Carregando voz Piper: {self.voice_name}")
                self.voice = PiperVoice.load(str(voice_path))
            else:
                print(f"📥 Baixando voz Piper: {self.voice_name}")
                # Piper faz download automático se não existir
                self.voice = PiperVoice.load(self.voice_name)

            print(f"🗣️ Voz Piper carregada: {self.voice_name}")

        except Exception as e:
            print(f"❌ Erro ao carregar voz Piper: {e}")

    def synthesize(self, text: str, output_path: str) -> bool:
        """Sintetizar texto para áudio"""
        if not self.voice:
            print("❌ Voz não carregada")
            return False

        try:
            start_time = time.time()

            # Síntese
            with open(output_path, "wb") as f:
                self.voice.synthesize(text, f)

            processing_time = time.time() - start_time

            # Estatísticas
            self.stats['syntheses'] += 1
            self.stats['total_chars'] += len(text)
            self.stats['avg_processing_time'] = (
                (self.stats['avg_processing_time'] * (self.stats['syntheses'] - 1)) +
                processing_time
            ) / self.stats['syntheses']

            print(f"🗣️ Áudio sintetizado: {output_path}")
            return True

        except Exception as e:
            self.stats['errors'] += 1
            print(f"❌ Erro na síntese: {e}")
            return False

    def synthesize_to_array(self, text: str) -> Optional[np.ndarray]:
        """Sintetizar para array numpy (para playback direto)"""
        if not self.voice:
            return None

        try:
            import io
            buffer = io.BytesIO()
            with buffer:
                self.voice.synthesize(text, buffer)
                buffer.seek(0)
                audio_data, sample_rate = sf.read(buffer)

            return audio_data

        except Exception as e:
            print(f"❌ Erro na síntese para array: {e}")
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas da síntese"""
        return self.stats.copy()


class LocalSpeakerDiarization:
    """Diarização de locutor 100% local"""

    def __init__(self, models_dir="./models"):
        self.models_dir = Path(models_dir)

        # Carregar pipeline PyAnnote local
        self.pipeline = None
        self._load_diarization_pipeline()

        # Estatísticas
        self.stats = {
            'diarizations': 0,
            'total_audio_seconds': 0.0,
            'speakers_found': 0,
            'avg_processing_time': 0.0,
            'errors': 0
        }

    def _load_diarization_pipeline(self):
        """Carregar pipeline de diarização local"""
        if not PYANNOTE_AVAILABLE:
            print("❌ PyAnnote não disponível")
            return

        try:
            # Usar modelo gratuito (não requer token)
            print("✅ Carregando pipeline de diarização...")
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=False  # Versão gratuita
            )
            print("🎙️ Diarização de locutor carregada")

        except Exception as e:
            print(f"❌ Erro ao carregar diarização: {e}")

    def diarize_audio(self, audio_path: str) -> List[Dict[str, Any]]:
        """Realizar diarização de locutor"""
        if not self.pipeline:
            return [{"error": "Pipeline não carregado"}]

        try:
            start_time = time.time()

            # Diarização
            diarization = self.pipeline(audio_path)

            # Processar resultados
            speakers = []
            speaker_count = {}

            for turn, _, speaker in diarization.itertracks(yield_label=True):
                speaker_id = speaker
                if speaker_id not in speaker_count:
                    speaker_count[speaker_id] = 0
                speaker_count[speaker_id] += 1

                speakers.append({
                    'speaker': speaker_id,
                    'start': turn.start,
                    'end': turn.end,
                    'duration': turn.end - turn.start
                })

            processing_time = time.time() - start_time

            # Estatísticas
            self.stats['diarizations'] += 1
            total_duration = sum(s['duration'] for s in speakers)
            self.stats['total_audio_seconds'] += total_duration
            self.stats['speakers_found'] += len(speaker_count)
            self.stats['avg_processing_time'] = (
                (self.stats['avg_processing_time'] * (self.stats['diarizations'] - 1)) +
                processing_time
            ) / self.stats['diarizations']

            return speakers

        except Exception as e:
            self.stats['errors'] += 1
            return [{"error": str(e)}]

    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas da diarização"""
        return self.stats.copy()


class LocalAudioProcessor:
    """Processador de áudio integrado 100% local"""

    def __init__(self, models_dir="./models"):
        self.models_dir = Path(models_dir)

        # Inicializar módulos
        self.speech_recognition = LocalSpeechRecognition(models_dir)
        self.text_to_speech = LocalTextToSpeech(models_dir)
        self.speaker_diarization = LocalSpeakerDiarization(models_dir)

        # Controle de áudio
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.audio_thread = None

        # Configuração de captura
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = 1024

        # Estatísticas gerais
        self.stats = {
            'start_time': time.time(),
            'audio_captured_seconds': 0.0,
            'processing_errors': 0
        }

        print("🔊 Processador de Áudio Local inicializado")

    def start_listening(self):
        """Iniciar captura de áudio contínua"""
        if self.is_listening:
            return

        self.is_listening = True
        self.audio_thread = threading.Thread(target=self._audio_capture_loop, daemon=True)
        self.audio_thread.start()

        print("🎤 Captura de áudio iniciada")

    def stop_listening(self):
        """Parar captura de áudio"""
        self.is_listening = False

        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=2)

        print("🎤 Captura de áudio parada")

    def _audio_capture_loop(self):
        """Loop de captura de áudio"""
        if not PYAUDIO_AVAILABLE:
            print("❌ PyAudio não disponível para captura")
            return

        try:
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )

            print("🎤 Loop de captura iniciado")

            audio_buffer = []

            while self.is_listening:
                try:
                    # Capturar chunk
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    audio_buffer.extend(np.frombuffer(data, dtype=np.int16))

                    # Verificar se há silêncio (fim da fala)
                    if self._is_silence(audio_buffer[-self.chunk_size*2:]):
                        if len(audio_buffer) > self.sample_rate:  # Pelo menos 1 segundo
                            # Processar áudio capturado
                            audio_array = np.array(audio_buffer, dtype=np.float32) / 32768.0
                            self._process_audio_chunk(audio_array)

                            # Limpar buffer
                            audio_buffer = []

                except Exception as e:
                    print(f"❌ Erro na captura: {e}")
                    time.sleep(0.1)

            stream.stop_stream()
            stream.close()
            audio.terminate()

        except Exception as e:
            print(f"❌ Erro no loop de áudio: {e}")

    def _is_silence(self, audio_chunk, threshold=500):
        """Verificar se chunk é silêncio"""
        if len(audio_chunk) == 0:
            return True

        # Calcular RMS
        rms = np.sqrt(np.mean(audio_chunk.astype(np.float64) ** 2))

        return rms < threshold

    def _process_audio_chunk(self, audio_array: np.ndarray):
        """Processar chunk de áudio capturado"""
        try:
            # Transcrever
            transcription = self.speech_recognition.transcribe_array(
                audio_array, self.sample_rate
            )

            if transcription.get('text'):
                print(f"🎤 Você disse: {transcription['text']}")

                # Adicionar à fila para processamento
                self.audio_queue.put({
                    'type': 'speech',
                    'text': transcription['text'],
                    'audio_duration': transcription.get('duration', 0),
                    'timestamp': time.time()
                })

        except Exception as e:
            print(f"❌ Erro no processamento de áudio: {e}")
            self.stats['processing_errors'] += 1

    def get_next_audio_event(self, timeout: float = 0.1) -> Optional[Dict[str, Any]]:
        """Obter próximo evento de áudio da fila"""
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def speak_text(self, text: str) -> bool:
        """Falar texto usando TTS local"""
        try:
            # Sintetizar para arquivo temporário
            temp_file = f"temp_speech_{int(time.time())}.wav"
            success = self.text_to_speech.synthesize(text, temp_file)

            if success:
                # Reproduzir áudio
                self._play_audio_file(temp_file)

                # Limpar arquivo temporário
                try:
                    os.remove(temp_file)
                except:
                    pass

                return True

            return False

        except Exception as e:
            print(f"❌ Erro na fala: {e}")
            return False

    def _play_audio_file(self, file_path: str):
        """Reproduzir arquivo de áudio"""
        try:
            # Usar playsound ou pygame se disponível
            import playsound
            playsound.playsound(file_path, block=True)
        except ImportError:
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

            except ImportError:
                print("⚠️ Nenhum player de áudio disponível")

    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do processador de áudio"""
        uptime = time.time() - self.stats['start_time']

        stats = {
            'uptime': uptime,
            'audio_captured_seconds': self.stats['audio_captured_seconds'],
            'processing_errors': self.stats['processing_errors'],
            'speech_recognition': self.speech_recognition.get_stats(),
            'text_to_speech': self.text_to_speech.get_stats(),
            'speaker_diarization': self.speaker_diarization.get_stats()
        }

        return stats


# Função de teste
def test_audio_system():
    """Testar sistema de áudio local"""
    print("🧪 Testando sistema de áudio local...")

    audio_processor = LocalAudioProcessor()

    # Teste de TTS
    print("🗣️ Testando síntese de voz...")
    success = audio_processor.speak_text("Olá! Este é um teste do sistema de áudio local.")
    if success:
        print("✅ TTS funcionando!")
    else:
        print("❌ TTS com problemas")

    # Teste de STT (se houver arquivo de áudio)
    test_audio_file = "test_audio.wav"
    if os.path.exists(test_audio_file):
        print("🎤 Testando reconhecimento de voz...")
        result = audio_processor.speech_recognition.transcribe_audio(test_audio_file)
        if result.get('text'):
            print(f"✅ STT: '{result['text']}'")
        else:
            print("❌ STT falhou ou arquivo não encontrado")

    stats = audio_processor.get_stats()
    print("📊 Estatísticas do teste:")
    print(f"  - Uptime: {stats['uptime']:.1f}s")
    print("✅ Teste concluído!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Processador de Áudio Local JARVIS")
    parser.add_argument("--test", action="store_true", help="Executar teste do sistema")
    parser.add_argument("--speak", type=str, help="Sintetizar texto para fala")
    parser.add_argument("--transcribe", type=str, help="Transcrever arquivo de áudio")

    args = parser.parse_args()

    if args.test:
        test_audio_system()
    elif args.speak:
        processor = LocalAudioProcessor()
        processor.speak_text(args.speak)
    elif args.transcribe:
        processor = LocalAudioProcessor()
        result = processor.speech_recognition.transcribe_audio(args.transcribe)
        print(f"Transcrição: {result.get('text', 'Erro')}")
    else:
        print("🔊 Processador de Áudio Local JARVIS 5.0")
        print("Use --test para testar ou --speak/--transcribe para operações específicas")
