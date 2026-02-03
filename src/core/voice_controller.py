"""
Controlador de Voz (STT & TTS)
Responsável por ouvir comandos e falar com o usuário
"""

import speech_recognition as sr
import pyttsx3
import asyncio
import edge_tts
from gtts import gTTS
import pygame
import threading
import logging
import os
import tempfile
import json
import socket
from typing import Optional, Callable
try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

logger = logging.getLogger(__name__)

class VoiceController:
    """Classe para processamento de voz (Jarvis Style)"""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # TTS Offline (fallback)
        self.engine = pyttsx3.init()
        self._setup_voices()
        
        # Configurar provedor padrão
        self.tts_provider = config.get_setting('voice.tts_provider', 'edge')
        self.stt_provider = config.get_setting('voice.stt_provider', 'auto') # 'google', 'vosk', 'auto'
        
        # Vosk Model (será carregado sob demanda se offline)
        self.vosk_model = None
        self.vosk_recognizer = None
        
        # Estado
        self.is_listening = False
        self.on_speech_recognized: Optional[Callable[[str], None]] = None
        
        # Inicializar pygame para áudio (edge-tts)
        pygame.mixer.init()

    def _setup_voices(self):
        """Configura vozes locais"""
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "portuguese" in voice.name.lower() or "brazil" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        self.engine.setProperty('rate', 180) # Velocidade Jarvis

    def speak(self, text: str, mode: str = 'auto'):
        """Fala um texto usando TTS híbrido (Online Fluido -> Offline Rápido)"""
        threading.Thread(target=self._speak_thread, args=(text, mode), daemon=True).start()

    def _speak_thread(self, text: str, mode: str):
        is_online = self.check_internet()
        
        if (mode == 'online' or mode == 'auto') and is_online:
            try:
                if self.tts_provider == 'edge':
                    asyncio.run(self._speak_edge(text))
                else:
                    self._speak_google(text)
                return
            except Exception as e:
                logger.warning(f"TTS Online ({self.tts_provider}) falhou: {e}")
        
        # Fallback Offline
        self.engine.say(text)
        self.engine.runAndWait()

    async def _speak_edge(self, text: str):
        """Usa a API do Microsoft Edge para fala natural gratuita"""
        voice = "pt-BR-AntonioNeural" # Voz masculina estilo assistente
        communicate = edge_tts.Communicate(text, voice)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp_path = tmp.name
            
        try:
            await communicate.save(tmp_path)
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass

    def start_listening(self):
        """Inicia escuta em background"""
        if self.is_listening:
            return
        self.is_listening = True
        threading.Thread(target=self._listen_thread, daemon=True).start()

    def stop_listening(self):
        """Para escuta"""
        self.is_listening = False

    def _listen_thread(self):
        """Thread de reconhecimento de fala híbrida"""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while self.is_listening:
                is_online = self.check_internet()
                
                try:
                    logger.info(f"Ouvindo ({'Online' if is_online else 'Offline'})...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    
                    text = ""
                    if self.stt_provider == 'google' or (self.stt_provider == 'auto' and is_online):
                        # Usar Google (Online)
                        text = self.recognizer.recognize_google(audio, language="pt-BR")
                    elif VOSK_AVAILABLE:
                        # Usar Vosk (Offline)
                        text = self._recognize_vosk(audio)
                    
                    if text:
                        logger.info(f"Voz reconhecida: {text}")
                        if self.on_speech_recognized:
                            self.on_speech_recognized(text)
                        
                except sr.WaitTimeoutError:
                    continue
                except (sr.UnknownValueError, Exception) as e:
                    logger.debug(f"Não entendi ou erro: {e}")

    def _recognize_vosk(self, audio_data) -> str:
        """Reconhecimento via Vosk (Offline)"""
        try:
            if not self.vosk_model:
                model_path = config.get_setting('voice.vosk_model_path', 'models/vosk-model-small-pt-0.22')
                if not os.path.exists(model_path):
                    logger.warning(f"Modelo Vosk não encontrado em {model_path}. Fala offline desabilitada.")
                    return ""
                self.vosk_model = Model(model_path)
                self.vosk_recognizer = KaldiRecognizer(self.vosk_model, 16000)

            # Converter audio para formato compatível com Vosk
            raw_data = audio_data.get_raw_data(convert_rate=16000, convert_width=2)
            if self.vosk_recognizer.AcceptWaveform(raw_data):
                result = json.loads(self.vosk_recognizer.Result())
                return result.get('text', '')
            return ""
        except Exception as e:
            logger.error(f"Erro no Vosk: {e}")
            return ""

    def check_internet(self) -> bool:
        """Verifica se há conexão com a internet"""
        try:
            # Tentar conectar ao DNS do Google
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            return True
        except OSError:
            return False

    def _speak_google(self, text: str):

    def _speak_google(self, text: str):
        """Usa Google TTS (gTTS)"""
        tts = gTTS(text=text, lang='pt', tld='com.br')
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp_path = tmp.name
            
        try:
            tts.save(tmp_path)
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass

# Instância global
voice_controller = VoiceController()
