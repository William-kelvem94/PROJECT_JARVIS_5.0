import os
import sys
import logging

# ============================================================================
# CRITICAL SYSTEM PATCHES (MUST BE AT THE VERY TOP)
# ============================================================================

# 1. COMTYPES FIX: Resolves AttributeError: 'MessageFactory' object has no attribute 'GetPrototype'
# This occurs on Windows 11 due to cache generation issues.
try:
    import comtypes.client
    import comtypes.client._code_cache
    import shutil
    from pathlib import Path
    
    # Nuke cache programmatically on every init to ensure stability
    gen_dir = Path(comtypes.client._code_cache._get_gen_dir())
    if gen_dir.exists():
        shutil.rmtree(gen_dir, ignore_errors=True)
    os.makedirs(gen_dir, exist_ok=True)
    
    comtypes.client._code_cache._enable_cache = False
    logging.getLogger('comtypes').setLevel(logging.ERROR)
except Exception:
    pass

# 2. QT DPI AWARENESS FIX: Suppresses "Access Denied" warnings in terminal
os.environ["QT_LOGGING_RULES"] = "qt.qpa.window=false"

# ============================================================================
# STANDARD IMPORTS
# ============================================================================
import speech_recognition as sr
import pyttsx3
import asyncio
import threading
import tempfile
import json
import socket
import random
import re
from typing import Optional, Callable

# Imports opcionais
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logging.warning("edge-tts não disponível. Instale com: pip install edge-tts")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logging.warning("gTTS não disponível")

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    logging.warning("pygame não disponível")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logging.warning("numpy não disponível")

try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    logging.warning("TTS (Coqui) não disponível. Voice cloning desativado.")

from src.utils.config import config

logger = logging.getLogger(__name__)

class VoiceController:
    """Classe para processamento de voz (Jarvis Style)"""

    def __init__(self):
        # Configurar microfone com index opcional do config
        mic_index = config.get_setting('voice.mic_index', None)
        self.recognizer = sr.Recognizer()
        try:
            self.microphone = sr.Microphone(device_index=mic_index)
            logger.info(f"✅ Microfone inicializado (Index: {mic_index or 'Padrão'})")
        except Exception as e:
            logger.error(f"❌ Erro ao acessar microfone: {e}")
            self.microphone = None
        
        # TTS Offline (fallback)
        self.engine = pyttsx3.init()
        
        # Configurar voz em português se disponível
        try:
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'portuguese' in voice.name.lower() or 'brazil' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
            self.engine.setProperty('rate', 180)  # Velocidade
            self.engine.setProperty('volume', 0.9)  # Volume
        except Exception as e:
            logger.warning(f"Não foi possível configurar voz: {e}")
        
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

        # XTTS-v2 Cloned Voice (Lazy Setup)
        self.cloned_tts = None
        self.speaker_wav = config.get_setting('voice.speaker_wav', 'data/voice_signatures/william.wav')
        
        # ============ P1: RESPONSE CACHING ============
        # Cache common phrases ("ok", "entendi", etc) as pre-generated audio
        self.response_cache = {}  # text -> audio_file_path
        self.common_phrases = [
            "OK", "Entendi", "Claro", "Pode deixar", "Estou trabalhando nisso",
            "Pronto", "Concluído", "Sim", "Não", "Como posso ajudar?"
        ]
        self._warm_response_cache()  # Pre-generate on init

    def _setup_cloned_voice(self):
        """Inicializa o modelo XTTS-v2 para clonagem de voz"""
        if self.cloned_tts or not TTS_AVAILABLE:
            return
        
        try:
            logger.info("🧠 Carregando modelo de clonagem de voz (XTTS-v2)...")
            self.cloned_tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            if torch.cuda.is_available():
                self.cloned_tts.to("cuda")
            logger.info("✅ Modelo XTTS-v2 pronto")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar XTTS-v2: {e}")
            TTS_AVAILABLE = False
    
    def _warm_response_cache(self):
        """Pre-generate common phrases for instant response"""
        if not EDGE_TTS_AVAILABLE or not PYGAME_AVAILABLE:
            return
        
        cache_dir = Path("data/audio/response_cache")
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("🔥 Warming response cache (common phrases)...")
        
        for phrase in self.common_phrases:
            cache_file = cache_dir / f"{phrase.lower().replace(' ', '_')}.mp3"
            
            if cache_file.exists():
                self.response_cache[phrase.lower()] = str(cache_file)
        
        logger.info(f"✅ Response cache ready ({len(self.response_cache)} phrases loaded)")
    
    async def _generate_cached_response(self, phrase: str, cache_file: Path):
        """Generate and cache a common phrase"""
        try:
            communicate = edge_tts.Communicate(phrase, "pt-BR-FranciscaNeural")
            await communicate.save(str(cache_file))
            self.response_cache[phrase.lower()] = str(cache_file)
            logger.debug(f"📦 Cached: {phrase}")
        except Exception as e:
            logger.warning(f"Failed to cache '{phrase}': {e}")

    def speak(self, text: str, mode: str = 'auto', wait: bool = False):
        """Fala um texto usando TTS híbrido (Online Fluido -> Offline Rápido)"""
        text = self.clean_text_for_speech(text)
        if not text: return
        
        # ============ P1: RESPONSE CACHING ============
        # Check if text is a cached common phrase
        if PYGAME_AVAILABLE:
            text_lower = text.lower().strip()
            if text_lower in self.response_cache:
                cache_file = self.response_cache[text_lower]
                try:
                    pygame.mixer.music.load(cache_file)
                    pygame.mixer.music.play()
                    
                    if wait:
                        while pygame.mixer.music.get_busy():
                            time.sleep(0.1)
                    
                    logger.debug(f"📦 Used cached response: {text}")
                    return
                except Exception as e:
                    logger.warning(f"Cache playback failed: {e}")
        
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
        
        # Get emotion for prosody
        from core.emotion_detector import emotion_detector
        emotion = getattr(emotion_detector, 'last_emotion', 'neutral')
        modifier = emotion_detector.get_personality_modifier(emotion)
        
        # Adjust rate based on emotion
        original_rate = self.engine.getProperty('rate')
        if modifier['energy'] == 'alta' or modifier['energy'] == 'máxima':
            self.engine.setProperty('rate', original_rate + 20)
        elif modifier['energy'] == 'baixa':
            self.engine.setProperty('rate', original_rate - 20)

        if (mode == 'online' or mode == 'auto') and is_online:
            try:
                if self.tts_provider == 'edge' and EDGE_TTS_AVAILABLE:
                    asyncio.run(self._speak_edge(text, emotion))
                elif GTTS_AVAILABLE:
                    self._speak_google(text)
                else:
                    logger.warning("Nenhum TTS online disponível, usando fallback offline")
                return
            except Exception as e:
                logger.warning(f"TTS Online ({self.tts_provider}) falhou: {e}")
        
        # Fallback Offline
        if not self.stop_requested:
            self._is_speaking = True
            prefix = modifier.get('prefix', '') if random.random() > 0.7 else ''
            self.engine.say(prefix + text)
            self.engine.runAndWait()
            self._is_speaking = False
            self.engine.setProperty('rate', original_rate) # Reset

    async def _speak_edge(self, text: str, emotion: str = "neutral"):
        """Usa a API do Microsoft Edge com seleção de voz baseada em emoção"""
        if not EDGE_TTS_AVAILABLE:
            logger.warning("edge-tts não disponível")
            return
            
        # Mapeamento de vozes neurais para emoções
        # Vozes do Edge por enquanto são limitadas em variação emocional direta, 
        # mas podemos simular trocando o "pitch" ou a voz se disponível.
        voice_map = {
            "happy": "pt-BR-FranciscaNeural",   # Mais leve/feminina
            "sad": "pt-BR-AntonioNeural",       # Mais profunda/masculina
            "angry": "pt-BR-AntonioNeural",     # Mais firme
            "neutral": "pt-BR-AntonioNeural"
        }
        
        voice = voice_map.get(emotion, voice_map["neutral"])
        communicate = edge_tts.Communicate(text, voice)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp_path = tmp.name
            
        try:
            await communicate.save(tmp_path)
            
            if self.stop_requested: return
            
            if not PYGAME_AVAILABLE:
                logger.warning("pygame não disponível para reproduzir áudio")
                return
                
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
                model_path = config.get_setting('voice.vosk_model_path', 'models/vosk-model-small-pt-0.3')
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
            logger.warning("Vosk (biblioteca) não disponível. Wake Word desativado.")
            return

        # Carregar modelo leve se necessário
        if not self.vosk_model:
            model_path = config.get_setting('voice.vosk_model_path', 'models/vosk-model-small-pt-0.3')
            if not os.path.exists(model_path):
                 
                 # Tentar caminho relativo se o absoluto falhar
                 abs_model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', model_path))
                 if os.path.exists(abs_model_path):
                     model_path = abs_model_path
                 else:
                     logger.warning(f"Modelo Vosk não encontrado em {model_path}. Wake Word Offline desativado.")
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

    def speak_cloned(self, text: str, wait: bool = False):
        """Fala usando a voz clonada (XTTS-v2) com refinamento emocional"""
        if not TTS_AVAILABLE:
            self.speak(text, wait=wait)
            return

        def _cloned_speak():
            try:
                self._setup_cloned_voice()
                self._is_speaking = True
                
                # Get emotion context
                from core.emotion_detector import emotion_detector
                emotion = getattr(emotion_detector, 'last_emotion', 'neutral')
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp_path = tmp.name
                
                logger.info(f"🎙️ Generating cloned voice (Emotion: {emotion})")
                self.cloned_tts.tts_to_file(
                    text=text, 
                    speaker_wav=self.speaker_wav, 
                    language="pt", 
                    file_path=tmp_path,
                    emotion=emotion # XTTS-v2 supports basic emotion conditioning
                )
                
                if self.stop_requested: return
                
                pygame.mixer.music.load(tmp_path)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    if self.stop_requested:
                        pygame.mixer.music.stop()
                        break
                    time.sleep(0.1)
                
                self._is_speaking = False
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception as e:
                logger.error(f"Erro na voz clonada: {e}")
                self._is_speaking = False
                self.speak(text, wait=True)

        if wait:
            _cloned_speak()
        else:
            threading.Thread(target=_cloned_speak, daemon=True).start()

# Instância global
voice_controller = VoiceController()
