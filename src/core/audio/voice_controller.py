import os
import sys
import asyncio
import threading
import hashlib
import time
import re
import json
import tempfile
from pathlib import Path
from typing import Optional, Callable
import logging

# ============================================================================
# CRITICAL SYSTEM PATCHES & ENVIRONMENT
# ============================================================================
os.environ["COQUI_TOS_AGREED"] = "1"
logging.getLogger('comtypes').setLevel(logging.ERROR)

# ============================================================================
# IMPORTS & DEPENDENCIES
# ============================================================================
import pyttsx3
import speech_recognition as sr
from src.utils.config import config

# Try to import ui_signals for status updates
try:
    from src.interface.ui_signals import ui_signals
except (ImportError, AttributeError):
    ui_signals = None

# Lazy import torch to avoid numpy conflicts
torch = None
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

# TTS will be imported lazily when needed
TTS_AVAILABLE = False

import logging
logger = logging.getLogger(__name__)

# ============================================================================
# CONDITIONAL IMPORTS (Graceful Degradation)
# ============================================================================

class VoiceController:
    """
    Stark Hybrid Voice Engine (JARVIS 5.0)
    Levels:
    1. Local XTTS-v2 (Cloning)
    2. Edge-TTS (Cloud Neural)
    3. pyttsx3 (Offline Fallback)
    """

    def __init__(self):
        # Paths & Cache
        self.cache_dir = Path("data/audio_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.reference_wav = Path("data/voice_signatures/jarvis_reference.wav")
        
        # Audio System Setup
        self._init_pygame()
        self.engine_offline = pyttsx3.init()
        self._setup_pyttsx3()
        
        # Microfone
        mic_index = config.get_setting('voice.mic_index', None)
        self.recognizer = sr.Recognizer()
        try:
            # 🔒 PERMISSÃO CHECK: Verificar acesso ao microfone
            try:
                # Tentar uma leitura rápida para verificar permissões
                test_mic = sr.Microphone(device_index=mic_index)
                with test_mic as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.1)
                logger.info("✅ Permissões de microfone verificadas")
            except Exception as perm_error:
                logger.error(f"❌ Sem permissão para acessar o microfone: {perm_error}")
                self.microphone = None
                return
            
            self.microphone = sr.Microphone(device_index=mic_index)
            logger.info(f"✅ Microfone inicializado (Index: {mic_index or 'Padrao'})")
        except Exception as e:
            logger.error(f"❌ Erro ao acessar microfone: {e}")
            self.microphone = None

        # State & Models
        self.xtts_model = None
        self.is_listening = False
        self.stop_requested = False
        self._is_speaking = False
        self.on_speech_recognized: Optional[Callable[[str], None]] = None
        
        # Lazy loading state
        self._xtts_loading = False
        self._xtts_ready = False
        
        # Load XTTS lazily (removed Thread from __init__)
        # Model will be loaded on the first speak() call that needs Level 1

    def _init_pygame(self):
        """Inicializa o mixer do pygame para reprodução de áudio."""
        if not PYGAME_AVAILABLE:
            logger.warning("⚠️ Pygame não disponível. Reprodução de áudio comprometida.")
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
                logger.info("✅ Pygame mixer inicializado")
        except Exception as e:
            logger.error(f"❌ Falha ao inicializar pygame mixer: {e}")

    def _setup_pyttsx3(self):
        """Configura o fallback básico."""
        try:
            voices = self.engine_offline.getProperty('voices')
            for voice in voices:
                if 'portuguese' in voice.name.lower() or 'brazil' in voice.name.lower():
                    self.engine_offline.setProperty('voice', voice.id)
                    break
            self.engine_offline.setProperty('rate', 180)
            self.engine_offline.setProperty('volume', 1.0)
        except Exception as e:
            logger.warning(f"⚠️ Erro ao configurar pyttsx3: {e}")

    def _init_xtts(self):
        """Inicializa o modelo XTTS-v2 localmente."""
        global TTS_AVAILABLE
        
        if self._xtts_ready or self._xtts_loading:
            return

        # Resource Guard: Don't load if system RAM is critically low (>85%)
        try:
            import psutil
            mem = psutil.virtual_memory()
            if mem.percent > 85.0:
                logger.warning(f"⚠️ Memory Guard: System RAM at {mem.percent}%. Skipping XTTS load.")
                return
        except ImportError:
            pass

        self._xtts_loading = True
        
        try:
            # Lazy import of TTS
            if not TTS_AVAILABLE:
                try:
                    # Patch BeamSearchScorer before importing TTS
                    import transformers
                    if not hasattr(transformers, 'BeamSearchScorer'):
                        from transformers.generation import BeamSearchScorer
                        transformers.BeamSearchScorer = BeamSearchScorer
                    
                    from TTS.api import TTS
                    TTS_AVAILABLE = True
                    logger.info("✅ TTS imported successfully")
                except Exception as e:
                    logger.warning(f"⚠️ TTS import failed: {e}")
                    TTS_AVAILABLE = False
                    self._xtts_loading = False
                    return

            if not TTS_AVAILABLE:
                self._xtts_loading = False
                return

            logger.info("🧠 Inicializando Stark Neural Engine (XTTS-v2)...")
            # Trava de Segurança Stark
            from src.utils.stability import model_load_lock
            model_load_lock.acquire("XTTS-v2 (Voice)")
            
            try:
                self.xtts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
                if TORCH_AVAILABLE and torch.cuda.is_available():
                    self.xtts_model.to("cuda")
                self._xtts_ready = True
                logger.info("✅ XTTS-v2 pronto para uso.")
            finally:
                model_load_lock.release()
                
        except Exception as e:
            logger.error(f"❌ Falha ao inicializar XTTS: {e}")
            self.xtts_model = None
        finally:
            self._xtts_loading = False

    def _get_cache_path(self, text: str) -> Path:
        """Gera o caminho do arquivo de cache baseado no hash do texto."""
        text_hash = hashlib.md5(text.lower().strip().encode('utf-8')).hexdigest()
        cache_path = self.cache_dir / f"{text_hash}.mp3"
        return cache_path

    def clean_text(self, text: str) -> str:
        """Limpa o texto para TTS mantendo a pontuação emocional."""
        if not text: return ""
        # Remove markdown e artefatos, mas mantém ! ? . ...
        text = re.sub(r'[*_#`]', '', text)
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'\(.*?\)', '', text)
        return text.strip()

    def speak(self, text: str, wait: bool = False):
        """Processo de fala com Motor Híbrido Estrito."""
        if not text: return
        
        clean_text = self.clean_text(text)
        if not clean_text: return
        
        # Log visual
        logger.info(f"🗣️ JARVIS: {clean_text}")
        if ui_signals:
            try:
                ui_signals.update_status.emit(clean_text)
            except Exception as e:
                logger.debug(f"UI signal error: {e}")

        # Cache check
        cache_path = self._get_cache_path(clean_text)
        if cache_path.exists():
            logger.debug(f"🎯 Cache hit: {cache_path.name}")
            self._play_audio(str(cache_path), wait=wait)
            return

        # Síntese (Asincrona ou Sincrona)
        if wait:
            self._synthesize_and_speak(clean_text, cache_path, wait=True)
        else:
            threading.Thread(target=self._synthesize_and_speak, args=(clean_text, cache_path, False), daemon=True).start()

    def _synthesize_and_speak(self, text: str, cache_path: Path, wait: bool):
        """Lógica de cascata de síntese (XTTS -> Edge -> pyttsx3)."""
        success = False
        
        # Nível 1: XTTS Local
        if self._xtts_ready:
            try:
                logger.info("🔊 [LEVEL 1] XTTS-v2 Synthesis (Cloning Mode)")
                self.xtts_model.tts_to_file(
                    text=text,
                    file_path=str(cache_path),
                    speaker_wav=str(self.reference_wav),
                    language="pt"
                )
                if cache_path.exists():
                    success = True
            except Exception as e:
                logger.warning(f"⚠️ XTTS falhou: {e}")
        elif not self._xtts_loading and not self._xtts_ready:
            # Trigger lazy load in background for NEXT time
            logger.info("🧠 [LAZY] Triggering XTTS background load for future use...")
            threading.Thread(target=self._init_xtts, daemon=True).start()

        # Nível 2: Edge-TTS
        if not success and EDGE_TTS_AVAILABLE:
            try:
                logger.info("🌐 [LEVEL 2] Edge-TTS Synthesis (Neural Cloud)")
                # Usar um loop específico para evitar conflito com loops já rodando
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self._edge_tts_to_file(text, cache_path))
                    if cache_path.exists():
                        success = True
                finally:
                    loop.close()
            except Exception as e:
                logger.warning(f"⚠️ Edge-TTS falhou: {e}")

        # Play or Fallback Nível 3
        if success and cache_path.exists():
            self._play_audio(str(cache_path), wait=wait)
        else:
            logger.error("🚨 [LEVEL 3] Fallback pyttsx3 (ROBOTIC MODE)")
            if not self.reference_wav.exists():
                logger.warning("💡 DICA: Adicione um arquivo .wav em 'data/voice_signatures/jarvis_reference.wav' para voz premium.")
            self.engine_offline.say(text)
            self.engine_offline.runAndWait()

    async def _edge_tts_to_file(self, text: str, path: Path):
        """Síntese via Edge-TTS com voz masculina neural."""
        voice = "pt-BR-AntonioNeural" # Voz masculina mais elegante
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(path))

    def _play_audio(self, file_path: str, wait: bool = False):
        """Reproduz áudio via pygame mixer com Antifeedback."""
        if not PYGAME_AVAILABLE: return
        
        from src.utils.hardware_control import hw_control
        
        try:
            self._is_speaking = True
            # BARGE-IN ENABLED: Microfone agora permanece aberto para permitir interrupções.
            
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            if wait:
                while pygame.mixer.music.get_busy() and not self.stop_requested:
                    time.sleep(0.05)
            else:
                # Async-like wait in thread
                while pygame.mixer.music.get_busy() and not self.stop_requested:
                    time.sleep(0.05)
        except Exception as e:
            logger.error(f"❌ Erro na reprodução: {e}")
        finally:
            self._is_speaking = False
            # O sistema agora confia no cancelamento de eco via software ou sensibilidade.
            
            if self.stop_requested:
                pygame.mixer.music.stop()
                self.stop_requested = False

    def stop_speaking(self):
        """Interrompe a fala atual."""
        self.stop_requested = True
        if PYGAME_AVAILABLE and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        self.engine_offline.stop()

    # --- Métodos de Escuta (Simplificados para manter integridade) ---
    
    def start_listening(self):
        if self.is_listening: return
        self.is_listening = True
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def stop_listening(self):
        self.is_listening = False

    def _listen_loop(self):
        if not self.microphone: return
        
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            while self.is_listening:
                try:
                    ui_signals.update_listening_state.emit(True)
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    ui_signals.update_listening_state.emit(False)
                    
                    # 🛡️ DATA VALIDATION: Verificar integridade do áudio
                    if audio is None or not hasattr(audio, 'frame_data') or len(audio.frame_data) == 0:
                        logger.warning("⚠️ Dados de áudio inválidos ou vazios, pulando...")
                        continue
                    
                    text = self.recognizer.recognize_google(audio, language="pt-BR")
                    if text and self.on_speech_recognized:
                        self.on_speech_recognized(text)
                except:
                    ui_signals.update_listening_state.emit(False)
                    continue

    def check_internet(self) -> bool:
        import socket
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            return True
        except:
            return False


# Module-level singleton instance (mandatory initialization)
try:
    voice_controller = VoiceController()
    logger.info("✅ VoiceController singleton created")
except Exception as e:
    logger.error(f"❌ Failed to initialize VoiceController: {e}")
    voice_controller = None

def get_voice_controller():
    """Return the singleton VoiceController instance.
    
    Now initialized at module load time since all features are mandatory.
    """
    return voice_controller
