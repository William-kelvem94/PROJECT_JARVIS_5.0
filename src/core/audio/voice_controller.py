import os
import sys
import logging
from pathlib import Path

# ============================================================================
# CRITICAL SYSTEM PATCHES (MUST BE AT THE VERY TOP)
# ============================================================================

# 1. COMTYPES FIX: Handled globally in main.py to prevent race conditions.
# Suppress comtypes logging
logging.getLogger('comtypes').setLevel(logging.ERROR)

# 2. QT DPI AWARENESS FIX: Suppresses "Access Denied" warnings in terminal
os.environ["QT_LOGGING_RULES"] = "qt.qpa.window=false"

# 3. COQUI TTS LICENSE FIX: Auto-agree to terms
os.environ["COQUI_TOS_AGREED"] = "1"

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
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
                logger.info("✅ Pygame mixer inicializado")
        except Exception as e:
            logger.warning(f"⚠️ Falha ao inicializar pygame mixer: {e}")
            global PYGAME_AVAILABLE
            PYGAME_AVAILABLE = False

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
        
        # Lock para evitar sobreposição de falas (Double Voice Fix)
        self.speech_lock = threading.RLock()
        
        self._warm_response_cache()  # Pre-generate on init

    def _setup_cloned_voice(self):
        """Inicializa o modelo XTTS-v2 para clonagem de voz"""
        global TTS_AVAILABLE
        if self.cloned_tts or not TTS_AVAILABLE:
            return
        
        try:
            logger.info("🧠 Carregando modelo de clonagem de voz (XTTS-v2)...")
            self.cloned_tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            if torch.cuda.is_available():
                self.cloned_tts.to("cuda")
            logger.info("✅ Modelo XTTS-v2 pronto")
        except ImportError as e:
            if "BeamSearchScorer" in str(e):
                logger.warning("⚠️ XTTS-v2 incompatível com versão atual do transformers (usando Edge-TTS)")
            else:
                logger.warning(f"⚠️ XTTS-v2 não disponível: {e}")
            TTS_AVAILABLE = False
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar XTTS-v2 (usando Edge-TTS como alternativa): {e}")
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
        
        # 🆕 CRÍTICO: Limpar SSML/XML ANTES de qualquer processamento
        text = self.strip_ssml(text)
        if not text or not text.strip(): return
        
        # LOGGING EXPLÍCITO DA FALA
        from src.utils.logger_reflection import reflect_logger
        reflect_logger.log_speech(text)  # Console visual
        logger.info(f"🗣️  SPEAKING: \"{text}\"")  # Arquivo de log detalhado
        
        # ============ P1: RESPONSE CACHING ============
        if PYGAME_AVAILABLE:
            text_lower = text.lower().strip()
            if text_lower in self.response_cache:
                cache_file = self.response_cache[text_lower]
                try:
                    pygame.mixer.music.load(cache_file)
                    pygame.mixer.music.play()
                    if wait:
                        while pygame.mixer.music.get_busy(): time.sleep(0.1)
                    return
                except: pass
        
        if wait:
            self._speak_thread(text, mode)
        else:
            threading.Thread(target=self._speak_thread, args=(text, mode), daemon=True).start()

    def speak_stream(self, text_chunk: str):
        """Consome chunks de texto e fala assim que possível (Streaming)"""
        if not text_chunk or len(text_chunk.strip()) < 2: return
        
        # Limpar texto
        clean_chunk = self.clean_text_for_speech(text_chunk)
        if not clean_chunk: return

        # Para streaming, usamos threads de background para cada chunk
        # Nota: Idealmente usaríamos uma fila para evitar sobreposição, 
        # mas para latência mínima, processamos o início imediatamente.
        threading.Thread(target=self._speak_thread, args=(clean_chunk, 'auto'), daemon=True).start()

    def speak_filler(self):
        """Fala uma frase aleatória de preenchimento para manter a fluidez"""
        filler = random.choice(self.fillers)
        self.speak(filler, mode='auto')

    def clean_text_for_speech(self, text: str) -> str:
        """Limpa artefatos de IA (markdown, asteriscos, código, CAMINHOS, URLs)"""
        if not text: return ""
        
        # 🔥 REMOVER MENSAGENS [SISTEMA] COMPLETAS (contém paths)
        text = re.sub(r'\[SISTEMA\].*?(?=\[|$)', '', text, flags=re.DOTALL)
        
        # 🔥 REMOVER BLOCOS DE CÓDIGO ANTES DE QUALQUER COISA (podem ter paths)
        text = re.sub(r'```[\s\S]*?```', '', text, flags=re.DOTALL)
        
        # 🔥 REMOVER URLs e www
        text = re.sub(r'https?://\S+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'www\.\S+', '', text, flags=re.IGNORECASE)
        
        # 🔥 REMOVER CAMINHOS - VERSÃO ULTRA AGRESSIVA
        # Qualquer coisa com \ (Windows paths)
        text = re.sub(r'[A-Za-z]:\\[^\s]+', '', text)  # C:\Users\...
        text = re.sub(r'\\[A-Za-z0-9_\.\\]+', '', text)  # \algo\path
        # Paths com forward slash (Unix/URL)
        text = re.sub(r'/[a-zA-Z0-9_\-\.\/]+', '', text)  # /usr/bin/...
        # Qualquer menção a diretórios comuns
        text = re.sub(r'\b(Users|Documents|GitHub|AppData|Program Files|Windows|System32|Desktop|Downloads)\b[^\s]*', '', text, flags=re.IGNORECASE)
        
        # 🔥 REMOVER EXTENSÕES DE ARQUIVO
        text = re.sub(r'\S+\.(exe|py|txt|log|json|yaml|yml|md|dll|bat|sh|png|jpg|jpeg|gif|mp3|mp4|wav|zip|rar|pdf|doc|docx|xls|xlsx|csv|db|sqlite|ini)', '', text, flags=re.IGNORECASE)
        
        # 🔥 REMOVER NOMES DE ARQUIVOS TÉCNICOS
        text = re.sub(r'\b(main\.py|config\.yaml|requirements\.txt|__init__\.py|setup\.py)\b', '', text, flags=re.IGNORECASE)
        
        # 🔥 FILTRAR TERMOS TÉCNICOS IRRITANTES
        tech_jargon = r'\b(spikes?|batch(es)?|processing|thread(s)?|worker(s)?|buffer|cache|heap|stack|node_modules|venv|virtualenv|conda|pip|npm)\b'
        text = re.sub(tech_jargon, '', text, flags=re.IGNORECASE)
        
        # Remover negrito/itálico
        text = re.sub(r'[*_]', '', text)
        # Remover crases e código inline
        text = re.sub(r'`[^`]+`', '', text)
        text = re.sub(r'`', '', text)
        
        # Reduzir espaços múltiplos e ponto-vírgula órfãos
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s*[,:;]\s*', ' ', text)  # Remove pontuação solta
        
        return text.strip()

    def strip_ssml(self, text: str) -> str:
        """Remove tags XML/SSML para que o TTS não as leia literalmente"""
        if not text:
            return ""
        # Remove tags XML/SSML completas
        text = re.sub(r'<[^>]+>', '', text)
        # Remove namespaces e atributos XML que ficaram soltos
        text = re.sub(r'xmlns\s*=\s*["\'][^"\'\']+["\']', '', text)
        text = re.sub(r'xml:lang\s*=\s*["\'][^"\'\']+["\']', '', text)
        text = re.sub(r'version\s*=\s*["\'][^"\'\']+["\']', '', text)
        # Limpar espaços múltiplos
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _speak_thread(self, text: str, mode: str):
        # 🆕 PROTEÇÃO EXTRA: Strip SSML mais uma vez
        text = self.strip_ssml(text)
        if not text or not text.strip():
            logger.warning("⚠️ Texto vazio após limpeza SSML, abortando speak")
            return
            
        # 🔒 SERIALIZAÇÃO DE FALA (Previne vozes sobrepostas)
        with self.speech_lock:
            # Re-check stop flag after acquiring lock in case it was set while waiting
            if self.stop_requested: return

            is_online = self.check_internet()
        
            # Get emotion mapping
            from src.core.intelligence.emotion_detector import emotion_detector
            emotion = getattr(emotion_detector, 'last_emotion', 'neutral')
            
            # ADAPTATIVE RATE
            base_rate = "+0%"
            if len(text) > 250: base_rate = "+18%"
            elif len(text) > 100: base_rate = "+10%"
            
            # --- PROVEDOR ONLINE (Primário) ---
            if is_online and mode != 'offline':
                try:
                    if self.tts_provider == 'edge' and EDGE_TTS_AVAILABLE:
                        logger.debug(f"🔊 TTS Edge: '{text[:50]}...'")
                        asyncio.run(self._speak_edge(text, emotion, base_rate))
                        return
                    elif GTTS_AVAILABLE:
                        logger.debug(f"🔊 TTS Google: '{text[:50]}...'")
                        self._speak_google(text)
                        return
                except Exception as e:
                    logger.error(f"❌ Erro no TTS Online ({self.tts_provider}): {e}. Usando fallback offline.")
                    import traceback
                    logger.error(traceback.format_exc())
            
            # --- PROVEDOR OFFLINE (Fallback / Forced) ---
            if not self.stop_requested:
                # 🆕 TENTATIVA DE FALLBACK HUMANO: XTTS-v2 (Local Neural)
                # Se a internet cair, tentamos usar o modelo neural local antes do robô
                if TTS_AVAILABLE:
                    try:
                        logger.info("⚠️ Modo Offline detectado: Tentando fallback para XTTS-v2 (Humano Local)...")
                        self.speak_cloned(text, wait=True)
                        return
                    except Exception as e:
                        logger.warning(f"❌ Falha no XTTS fallback: {e}")
                
                # 🆕 ÚLTIMO RECURSO: Pyttsx3 (Melhor que silêncio, mas evitado se possível)
                try:
                    self._is_speaking = True
                    
                    # 🆕 TRIPLA PROTEÇÃO: Remover SSML mais uma vez antes do offline
                    clean_text = self.strip_ssml(text)
                    if not clean_text or not clean_text.strip():
                        logger.warning("⚠️ Texto vazio após strip_ssml no offline, abortando")
                        return
                    
                    logger.debug(f"🔊 TTS Offline (pyttsx3 - Último Recurso): '{clean_text[:50]}...'")
                    
                    # Ajustar personalidade offline
                    modifier = emotion_detector.get_personality_modifier(emotion)
                    prefix = modifier.get('prefix', '') if random.random() > 0.7 else ''
                    
                    # Verificação de Saúde do Engine
                    if not hasattr(self, 'engine') or self.engine is None:
                        try:
                            self.engine = pyttsx3.init()
                            self.engine.setProperty('rate', 180)
                            self.engine.setProperty('volume', 1.0)
                        except Exception as e:
                            logger.error(f"❌ Impossível recriar engine pyttsx3: {e}")
                            return

                    try:
                        original_rate = self.engine.getProperty('rate')
                    except:
                        # Se falhar ao pegar propriedade, tenta reiniciar
                        try:
                            self.engine = pyttsx3.init()
                            original_rate = 180
                        except:
                            logger.error("❌ Falha terminal no pyttsx3")
                            return

                    # Ajustar rate baseado na emoção
                    if modifier.get('energy') in ['alta', 'máxima']:
                        self.engine.setProperty('rate', original_rate + 20)
                    elif modifier.get('energy') == 'baixa':
                        self.engine.setProperty('rate', original_rate - 20)

                    self.engine.say(prefix + clean_text)
                    self.engine.runAndWait()
                    
                    # Resetar rate
                    self.engine.setProperty('rate', original_rate)
                except Exception as e:
                    logger.error(f"❌ Falha crítica no motor de voz offline: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                finally:
                    self._is_speaking = False

    async def _speak_edge(self, text: str, emotion: str = "neutral", adaptive_rate: str = "+0%"):
        """TTS de Alta Qualidade via Edge-TTS com SSML"""
        if not EDGE_TTS_AVAILABLE:
            logger.warning("edge-tts não disponível")
            return
            
        # Mapeamento de vozes neurais para emoções
        voice_map = {
            "happy": "pt-BR-FranciscaNeural",
            "sad": "pt-BR-AntonioNeural",
            "angry": "pt-BR-AntonioNeural",
            "neutral": "pt-BR-AntonioNeural"
        }
        
        voice = voice_map.get(emotion, voice_map["neutral"])
        
        # --- PHASE: SSML PROSODY (Natural Speech) ---
        # Get emotion modifier for SSML
        from src.core.intelligence.emotion_detector import emotion_detector
        modifier = emotion_detector.get_personality_modifier(emotion)
        
        # Prosody parameters: pitch, rate, volume
        # Ex: <prosody pitch="+10Hz" rate="+20%" volume="loud">...
        pitch = "+0Hz"
        rate = adaptive_rate # Usar taxa adaptativa
        volume = "+0%"
        
        if emotion == "happy":
            pitch = "+15%"
            rate = "+10%"
        elif emotion == "sad":
            pitch = "-10%"
            rate = "-15%"
            volume = "-10%"
        elif emotion == "angry":
            pitch = "-5%"
            rate = "+15%"
            volume = "+20%"
        
                # 🔒 edge-tts NÃO suporta SSML raw - usar parâmetros nativos da API
        # A prosódia é aplicada via rate/pitch/volume do Communicate
        max_retries = 2
        retry_delay = 1.0
        
                # Sanitize parameters (Edge-TTS is strict)
                def sanitize_param(val, suffix="%"):
                    if not val or not isinstance(val, str): return "+0" + suffix
                    val = val.strip()
                    if val == "+0" + suffix: return val # Optimization
                    import re
                    # Must be +N% or -N%
                    if not re.match(r'^[+-]\d+' + suffix + r'$', val):
                         # Try to fix partial strings
                         if val.isdigit() or (val.startswith('-') and val[1:].isdigit()):
                             return ("+" if not val.startswith('-') else "") + val + suffix
                         return "+0" + suffix
                    return val

                safe_rate = sanitize_param(rate if rate != "+0%" else "+0%")
                safe_pitch = sanitize_param(pitch if pitch != "+0Hz" else "+0Hz", "Hz")
                safe_volume = sanitize_param(volume if volume != "+0%" else "+0%")
                
                communicate = edge_tts.Communicate(
                    text,  # 🔒 Texto puro, NÃO SSML
                    voice,
                    rate=safe_rate,
                    pitch=safe_pitch,
                    volume=safe_volume
                )
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    tmp_path = tmp.name
                    
                try:
                    # 🆕 TIMEOUT REDUZIDO para falhar mais rápido
                    import aiohttp
                    timeout = aiohttp.ClientTimeout(total=8, connect=3)  # 8s total, 3s connect for faster fallback
                    
                    await asyncio.wait_for(communicate.save(tmp_path), timeout=8.0)
                    
                    # 🔍 Log de confirmação do arquivo gerado
                    if os.path.exists(tmp_path):
                        file_size = os.path.getsize(tmp_path)
                        logger.info(f"✅ Edge-TTS: Arquivo MP3 gerado ({file_size} bytes) em {tmp_path}")
                    else:
                        logger.error(f"❌ Edge-TTS: Arquivo MP3 NÃO foi criado em {tmp_path}")
                        return # Não lançar exceção para evitar fallback duplo
                    
                    if self.stop_requested: return
                    
                    if not PYGAME_AVAILABLE:
                        logger.error("❌ pygame não disponível para reproduzir áudio")
                        return
                    
                    # 🆕 Verificar se mixer está initialized
                    if not pygame.mixer.get_init():
                        logger.warning("⚠️ Pygame mixer não inicializado, tentando reinicializar...")
                        try:
                            pygame.mixer.init()
                        except Exception as init_e:
                            logger.error(f"❌ Falha ao reinicializar pygame: {init_e}")
                            return
                        
                    self._is_speaking = True
                    
                    try:
                        logger.debug(f"🔊 Carregando MP3 no pygame.mixer: {tmp_path}")
                        pygame.mixer.music.load(tmp_path)
                        logger.info(f"✅ Edge-TTS: Arquivo carregado com sucesso no mixer")
                        
                        pygame.mixer.music.play()
                        logger.info(f"🎵 Edge-TTS: Reprodução iniciada (aguardando conclusão...)")
                        
                        while pygame.mixer.music.get_busy():
                            if self.stop_requested:
                                pygame.mixer.music.stop()
                                logger.info("🛑 Edge-TTS: Reprodução interrompida pelo usuário")
                                break
                            await asyncio.sleep(0.1)
                        
                        logger.info(f"✅ Edge-TTS: Reprodução concluída com sucesso")
                        return  # Sucesso, sair da função
                        
                    except pygame.error as pg_err:
                        logger.error(f"❌ Pygame error: {pg_err}")
                        raise  # Cair no fallback offline
                finally:
                    self._is_speaking = False
                    if os.path.exists(tmp_path):
                        try:
                            os.remove(tmp_path)
                        except:
                            pass
                            
            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    logger.debug(f"⏱️ Edge-TTS timeout (tentativa {attempt + 1}/{max_retries}), tentando novamente...")
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    logger.warning("⚠️ Edge-TTS timeout após múltiplas tentativas (usando fallback offline)")
                    raise  # Cair no fallback offline
                    
            except Exception as e:
                error_msg = str(e)
                # Reduzir verbosidade para timeouts conhecidos
                if "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                    if attempt < max_retries - 1:
                        logger.debug(f"⏱️ Edge-TTS conexão falhou (tentativa {attempt + 1}/{max_retries})")
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        logger.warning("⚠️ Edge-TTS indisponível (usando fallback offline)")
                else:
                    logger.warning(f"⚠️ Edge-TTS error: {error_msg}")
                raise  # Re-raise para cair no fallback offline

    def stop_speaking(self):
        """Interrompe a fala atual imediatamente"""
        logger.info("Interrupção solicitada pelo usuário.")
        self.stop_requested = True
        
        try:
            # Parar Pygame Mixer
            if PYGAME_AVAILABLE and pygame.mixer.get_init():
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
            
            # Parar Pyttsx3
            if hasattr(self, 'engine'):
                self.engine.stop()
        except Exception as e:
            logger.error(f"Erro ao parar fala: {e}")
        
        # Resetar flag após um curto delay
        threading.Timer(0.5, self._reset_stop_flag).start()

    def _reset_stop_flag(self):
        self.stop_requested = False

    def calibrate_vad_threshold(self, duration: float = 3.0):
        """Calibra o limiar de ruído ambiente (VAD)"""
        if not self.microphone:
            logger.error("❌ Calibração falhou: Microfone não disponível")
            return
            
        logger.info(f"🎤 Calibrando VAD por {duration} segundos... (Fique em silêncio)")
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            logger.info(f"✅ VAD calibrado: Energy Threshold = {self.recognizer.energy_threshold:.2f}")
        except Exception as e:
            logger.error(f"❌ Erro na calibração: {e}")

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
                model_path = config.get_setting('voice.vosk_model_path', 'models/speech/vosk-model-small-pt-0.3')
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
        """Verifica se há conexão com a internet (delegado ao BrainRouter)"""
        from src.core.intelligence.brain_router import brain_router
        return brain_router.check_connectivity()

    def confirm_with_voice(self, question: str, timeout: int = 5) -> bool:
        """
        Fala uma pergunta e aguarda uma confirmação por voz (Sim/Não).
        Retorna True se confirmado, False caso contrário.
        """
        self.speak(question, wait=True)
        
        if not self.microphone:
            return False
            
        logger.info(f"🎤 Aguardando confirmação: '{question}'")
        try:
            with self.microphone as source:
                # Pequena pausa para o usuário processar a pergunta
                time.sleep(0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=3)
                
                is_online = self.check_internet()
                text = ""
                if is_online:
                    text = self.recognizer.recognize_google(audio, language="pt-BR")
                elif VOSK_AVAILABLE:
                    text = self._recognize_vosk(audio)
                
                text = text.lower()
                logger.info(f"Resposta capturada: '{text}'")
                
                confirm_words = ["sim", "pode", "ok", "prosseguir", "confirmo", "afirmativo", "vai", "yes", "do it"]
                return any(word in text for word in confirm_words)
                
        except Exception as e:
            logger.debug(f"Falha na confirmação por voz: {e}")
            return False
        try:
            from src.core.intelligence.brain_router import brain_router
            return brain_router.check_connectivity()
        except:
            # Fallback se router não estiver disponível
            import socket
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=2)
                return True
            except:
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
        """Thread de background para Wake Word (Loop Infinito Robusto)"""
        if not VOSK_AVAILABLE:
            logger.warning("Vosk (biblioteca) não disponível. Wake Word desativado.")
            return

        # Carregar modelo leve se necessário
        if not self.vosk_model:
            # Tentar carregar modelo pequeno para wake word (rápido e leve)
            model_path = config.PROJECT_ROOT / "models" / "speech" / "vosk-model-small-pt-0.3"
            
            if not model_path.exists():
                logger.warning(f"Modelo Vosk Pequeno não encontrado em {model_path}. Tentando baixar...")
                # TODO: Implementar download automático se necessário
                logger.error("❌ Modelo VOSK não encontrado. Wake Word cancelado.")
                return

            try:
                self.vosk_model = vosk.Model(str(model_path))
                logger.info(f"✅ Modelo Vosk carregado: {model_path}")
            except Exception as e:
                logger.error(f"Erro fatal ao carregar Vosk: {e}")
                return

        # Configurar reconhecedor
        if not self.vosk_recognizer:
            self.vosk_recognizer = vosk.KaldiRecognizer(self.vosk_model, 16000)

        # Configurar stream de áudio PyAudio
        import pyaudio
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
        stream.start_stream()

        logger.info(f"👂 SENTINELA ATIVO: Aguardando '{wake_word}' ou 'computador'...")

        # Loop Infinito de Escuta
        triggers = [wake_word.lower(), "computador", "sistema", "assistente", "jarvis"]
        
        while self.is_listening:
            try:
                data = stream.read(4096, exception_on_overflow=False)
                
                if self.vosk_recognizer.AcceptWaveform(data):
                    result = json.loads(self.vosk_recognizer.Result())
                    text = result.get('text', '').lower()
                    
                    if any(t in text for t in triggers):
                        logger.info(f"⚡ WAKE WORD DETECTADA: '{text}'")
                        self._play_wake_sound()
                        
                        # Disparar callback de acordar (geralmente inicia listen_command)
                        if on_wake:
                            on_wake()
                            
                        # Limpar buffer após acordar
                        self.vosk_recognizer.Reset()
                        
                else:
                    # Partial result (opcional, para gatilho ultra-rápido)
                    pass

            except Exception as e:
                logger.error(f"Erro no loop de wake word: {e}")
                time.sleep(1.0) # Prevenir spam de erro em loop

        # Limpeza
        stream.stop_stream()
        stream.close()
        p.terminate()

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
                from src.core.intelligence.emotion_detector import emotion_detector
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
