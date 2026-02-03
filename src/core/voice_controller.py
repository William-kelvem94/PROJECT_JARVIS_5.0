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
import random
import re
from typing import Optional, Callable
try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

from src.utils.config import config

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

        # Flag de interrupção
        self.stop_requested = False
        self._is_speaking = False
        self.detected_tone = "normal"

    def _setup_voices(self):
        """Configura vozes locais"""
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "portuguese" in voice.name.lower() or "brazil" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        self.engine.setProperty('rate', 190) # Velocidade Jarvis levemente mais rápida
        
        # Frases de preenchimento (Fillers) para naturalidade
        self.fillers = [
            "Um momento, senhor.",
            "Deixe-me ver...",
            "Analisando os dados...",
            "Só um segundo, William.",
            "Estou verificando isso agora.",
            "Processando as informações..."
        ]

    def speak(self, text: str, mode: str = 'auto', wait: bool = False):
        """Fala um texto usando TTS híbrido (Online Fluido -> Offline Rápido)"""
        text = self.clean_text_for_speech(text)
        if not text: return
        
        if wait:
            self._speak_thread(text, mode)
        else:
            threading.Thread(target=self._speak_thread, args=(text, mode), daemon=True).start()

    def speak_filler(self):
        """Fala uma frase aleatória de preenchimento para manter a fluidez"""
        filler = random.choice(self.fillers)
        self.speak(filler, mode='auto')

    def clean_text_for_speech(self, text: str) -> str:
        """Limpa artefatos de IA (markdown, asteriscos, código) para voz natural"""
        if not text: return ""
        
        # Remover blocos de código
        text = re.sub(r'```[\s\S]*?```', '', text)
        # Remover negrito/itálico (asteriscos e underscores)
        text = re.sub(r'[*_]', '', text)
        # Remover crases (inline code)
        text = re.sub(r'`', '', text)
        # Remover emojis (opcional, mas evita que o TTS tente ler descrições estranhas)
        # text = text.encode('ascii', 'ignore').decode('ascii') 
        
        return text.strip()

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
        if not self.stop_requested:
            self._is_speaking = True
            self.engine.say(text)
            self.engine.runAndWait()
            self._is_speaking = False

    async def _speak_edge(self, text: str):
        """Usa a API do Microsoft Edge para fala natural gratuita"""
        voice = "pt-BR-AntonioNeural" # Voz masculina estilo assistente
        communicate = edge_tts.Communicate(text, voice)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp_path = tmp.name
            
        try:
            await communicate.save(tmp_path)
            
            if self.stop_requested: return
            
            self._is_speaking = True
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                if self.stop_requested:
                    pygame.mixer.music.stop()
                    break
                await asyncio.sleep(0.1)
        finally:
            self._is_speaking = False
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass

    def stop_speaking(self):
        """Interrompe a fala atual imediatamente"""
        logger.info("Interrupção solicitada pelo usuário.")
        self.stop_requested = True
        
        try:
            # Parar Pygame Mixer
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            
            # Parar Pyttsx3
            self.engine.stop()
        except Exception as e:
            logger.error(f"Erro ao parar fala: {e}")
        
        # Resetar flag após um curto delay
        threading.Timer(0.5, self._reset_stop_flag).start()

    def _reset_stop_flag(self):
        self.stop_requested = False

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
            
            # Analisar intensidade (Phase 14 - Tone Analysis)
            self._analyze_intensity(raw_data)

            if self.vosk_recognizer.AcceptWaveform(raw_data):
                result = json.loads(self.vosk_recognizer.Result())
                return result.get('text', '')
            return ""
        except Exception as e:
            logger.error(f"Erro no Vosk: {e}")
            return ""

    def _analyze_intensity(self, raw_data: bytes):
        """Calcula a intensidade do som para detectar urgência ou emoção"""
        try:
            audio_np = np.frombuffer(raw_data, dtype=np.int16)
            rms = np.sqrt(np.mean(audio_np**2))
            
            # Thresholds básicos (precisam de calibração)
            if rms > 5000:
                self.detected_tone = "urgente/alto"
            elif rms < 500:
                self.detected_tone = "calmo/baixo"
            else:
                self.detected_tone = "normal"
                
            logger.debug(f"Tom de voz detectado: {self.detected_tone} (RMS: {rms:.0f})")
        except:
            self.detected_tone = "normal"

    def check_internet(self) -> bool:
        """Verifica se há conexão com a internet"""
        try:
            # Tentar conectar ao DNS do Google
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            return True
        except OSError:
            return False

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


    def listen_for_wake_word(self, wake_word: str = "jarvis", on_wake: Optional[Callable[[], None]] = None):
        """
        Inicia escuta passiva pela palavra de ativação (Wake Word)
        Usa Vosk (Offline) para baixo consumo e privacidade.
        """
        if self.is_listening:
            logger.warning("Já estou ouvindo.")
            return

        self.is_listening = True
        threading.Thread(target=self._listen_for_wake_word_thread, args=(wake_word, on_wake), daemon=True).start()
        logger.info(f"Ouvindo pela palavra chave: '{wake_word}'")

    def _listen_for_wake_word_thread(self, wake_word: str, on_wake: Optional[Callable[[], None]]):
        """Thread de background para Wake Word"""
        if not VOSK_AVAILABLE:
            logger.warning("Vosk não disponível. Wake Word desativado.")
            return

        # Carregar modelo leve se necessário
        if not self.vosk_model:
            model_path = config.get_setting('voice.vosk_model_path', 'models/vosk-model-small-pt-0.22')
            if not os.path.exists(model_path):
                 logger.error(f"Modelo Vosk não encontrado em {model_path}")
                 return
            try:
                self.vosk_model = Model(model_path)
                self.vosk_recognizer = KaldiRecognizer(self.vosk_model, 16000)
            except Exception as e:
                logger.error(f"Erro ao carregar Vosk: {e}")
                return

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while self.is_listening:
                try:
                    # Captura pequenos chunks de áudio para processamento rápido
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                    
                    # Se JARVIS estiver falando, qualquer som detectado (ou palavra-chave) interrompe
                    # Nota: Em sistemas sem Echo Cancellation, isso pode ser sensível demais.
                    # Por isso, verificamos se o texto detectado não é vazio.
                    text = self._recognize_vosk(audio).lower()
                    
                    if self._is_speaking and len(text.strip()) > 1:
                        logger.info("Interrupção por voz detectada durante fala.")
                        self.stop_speaking()
                        continue

                    if wake_word in text:
                        logger.info(f"Wake Word detectada: {text}")
                        if on_wake:
                            on_wake()
                            # Pausa breve para evitar auto-trigger
                            time.sleep(1)
                            
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    logger.debug(f"Erro no loop Wake Word: {e}")


    def listen_once(self, on_command: Callable[[str], None]):
        """Escuta um único comando ativo após o despertar"""
        # Parar escuta passiva
        self.is_listening = False
        time.sleep(0.5)

        def _active_listen():
            with self.microphone as source:
                logger.info("Ouvindo comando ativo...")
                try:
                    # Feedback sonoro poderia ser adicionado aqui
                    self.speak("Pois não?")
                    time.sleep(1) # Esperar falar

                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    
                    is_online = self.check_internet()
                    text = ""
                    
                    if is_online:
                        text = self.recognizer.recognize_google(audio, language="pt-BR")
                    elif VOSK_AVAILABLE:
                        text = self._recognize_vosk(audio)
                        
                    if text:
                        logger.info(f"Comando recebido: {text}")
                        on_command(text)
                    else:
                        self.speak("Não entendi.")
                        
                except sr.WaitTimeoutError:
                    pass
                except Exception as e:
                    logger.error(f"Erro na escuta ativa: {e}")
            
            # Retomar Wake Word
            self.listen_for_wake_word()

        threading.Thread(target=_active_listen, daemon=True).start()

# Instância global
voice_controller = VoiceController()
