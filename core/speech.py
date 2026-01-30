"""
JARVIS Speech - Sistema de Síntese de Voz (TTS)
Suporte para múltiplas engines: pyttsx3, Edge-TTS, ElevenLabs
"""

import os
import asyncio
import threading
import time
from typing import Optional, Dict, Any
from pathlib import Path

from config import config

class Speech:
    """
    Sistema de síntese de voz do JARVIS.
    Suporte para múltiplas engines com qualidade variável.
    """

    def __init__(self):
        self.is_speaking = False
        self.speech_queue = asyncio.Queue()
        self.engine = config.get("voice.tts_engine", "pyttsx3")
        self.language = config.get("voice.language", "pt-BR")
        self.volume = config.get("voice.voice_volume", 80) / 100.0  # 0-1

        # Engines disponíveis
        self.engines = {
            "pyttsx3": self._init_pyttsx3,
            "edge_tts": self._init_edge_tts,
            "elevenlabs": self._init_elevenlabs
        }

        # Inicializar engine
        self.current_engine = None
        self._init_engine()

    def _init_engine(self):
        """Inicializa a engine de TTS escolhida."""
        try:
            init_func = self.engines.get(self.engine, self._init_pyttsx3)
            self.current_engine = init_func()
            print(f"️ TTS Engine inicializada: {self.engine}")
        except Exception as e:
            print(f" Erro ao inicializar {self.engine}: {e}")
            # Fallback para pyttsx3
            try:
                self.current_engine = self._init_pyttsx3()
                self.engine = "pyttsx3"
                print(" Fallback para pyttsx3")
            except Exception as e2:
                print(f" Falha crítica no TTS: {e2}")
                self.current_engine = None

    def _init_pyttsx3(self):
        """Inicializa pyttsx3 (offline, mais rápido)."""
        try:
            import pyttsx3
            engine = pyttsx3.init()

            # Configurações de voz
            voices = engine.getProperty('voices')
            pt_voice = None

            # Procurar voz portuguesa
            for voice in voices:
                if 'portuguese' in voice.name.lower() or 'pt' in voice.name.lower():
                    pt_voice = voice
                    break

            if pt_voice:
                engine.setProperty('voice', pt_voice.id)
            else:
                # Usar primeira voz disponível
                engine.setProperty('voice', voices[0].id if voices else 'default')

            engine.setProperty('rate', 180)  # Velocidade
            engine.setProperty('volume', self.volume)

            return {
                "type": "pyttsx3",
                "engine": engine
            }
        except ImportError:
            raise Exception("pyttsx3 não instalado")

    def _init_edge_tts(self):
        """Inicializa Edge TTS (Microsoft, online)."""
        try:
            import edge_tts
            return {
                "type": "edge_tts",
                "voice": "pt-BR-AntonioNeural",  # Voz portuguesa
                "rate": "+0%",  # Velocidade normal
                "volume": "+0%"  # Volume normal
            }
        except ImportError:
            raise Exception("edge-tts não instalado")

    def _init_elevenlabs(self):
        """Inicializa ElevenLabs (premium, online)."""
        try:
            from elevenlabs import generate, set_api_key

            api_key = os.getenv('ELEVENLABS_API_KEY')
            if not api_key:
                raise Exception("ELEVENLABS_API_KEY não configurada")

            set_api_key(api_key)
            return {
                "type": "elevenlabs",
                "voice": "Antoni",  # Voz padrão (inglês)
                "model": "eleven_monolingual_v1"
            }
        except ImportError:
            raise Exception("elevenlabs não instalado")

    def speak(self, text: str, async_mode: bool = True) -> bool:
        """
        Fala o texto fornecido.

        Args:
            text: Texto a ser falado
            async_mode: Se True, fala em background

        Returns:
            True se iniciou com sucesso
        """
        if not self.current_engine or not text.strip():
            return False

        if async_mode:
            # Falar em background
            thread = threading.Thread(
                target=self._speak_sync,
                args=(text,),
                daemon=True
            )
            thread.start()
            return True
        else:
            # Falar sincronamente
            return self._speak_sync(text)

    def _speak_sync(self, text: str) -> bool:
        """
        Fala texto de forma síncrona.
        """
        try:
            self.is_speaking = True

            if self.engine == "pyttsx3":
                return self._speak_pyttsx3(text)
            elif self.engine == "edge_tts":
                return self._speak_edge_tts(text)
            elif self.engine == "elevenlabs":
                return self._speak_elevenlabs(text)

        except Exception as e:
            print(f" Erro na síntese de voz: {e}")
            return False
        finally:
            self.is_speaking = False

    def _speak_pyttsx3(self, text: str) -> bool:
        """Fala usando pyttsx3."""
        try:
            engine = self.current_engine["engine"]
            engine.say(text)
            engine.runAndWait()
            return True
        except Exception as e:
            print(f" Erro pyttsx3: {e}")
            return False

    def _speak_edge_tts(self, text: str) -> bool:
        """Fala usando Edge TTS."""
        try:
            import edge_tts
            import asyncio

            voice = self.current_engine["voice"]
            communicate = edge_tts.Communicate(text, voice)

            # Executar de forma síncrona
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                loop.run_until_complete(communicate.save("./temp_audio.mp3"))
                loop.run_until_complete(self._play_audio("./temp_audio.mp3"))
                return True
            finally:
                loop.close()
                # Limpar arquivo temporário
                if os.path.exists("./temp_audio.mp3"):
                    os.remove("./temp_audio.mp3")

        except Exception as e:
            print(f" Erro Edge TTS: {e}")
            return False

    async def _speak_edge_tts_async(self, text: str):
        """Versão assíncrona do Edge TTS."""
        try:
            import edge_tts
            voice = self.current_engine["voice"]
            communicate = edge_tts.Communicate(text, voice)

            await communicate.save("./temp_audio.mp3")
            await self._play_audio("./temp_audio.mp3")

        except Exception as e:
            print(f" Erro Edge TTS async: {e}")
        finally:
            if os.path.exists("./temp_audio.mp3"):
                os.remove("./temp_audio.mp3")

    def _speak_elevenlabs(self, text: str) -> bool:
        """Fala usando ElevenLabs."""
        try:
            from elevenlabs import generate, play

            audio = generate(
                text=text,
                voice=self.current_engine["voice"],
                model=self.current_engine["model"]
            )

            play(audio)
            return True

        except Exception as e:
            print(f" Erro ElevenLabs: {e}")
            return False

    async def _play_audio(self, file_path: str):
        """Toca arquivo de áudio."""
        try:
            if os.name == 'nt':  # Windows
                os.system(f'start /min "" "{file_path}"')
            else:  # Linux/Mac
                os.system(f'afplay "{file_path}"' if os.uname().sysname == 'Darwin' else f'mpg123 "{file_path}"')
        except Exception as e:
            print(f" Erro ao tocar áudio: {e}")

    def speak_file(self, file_path: str) -> bool:
        """
        Fala conteúdo de um arquivo de texto.

        Args:
            file_path: Caminho para o arquivo

        Returns:
            True se conseguiu falar
        """
        try:
            if not os.path.exists(file_path):
                return False

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return self.speak(content)

        except Exception as e:
            print(f" Erro ao falar arquivo: {e}")
            return False

    def set_volume(self, volume: int):
        """
        Define volume da voz (0-100).

        Args:
            volume: Volume de 0 a 100
        """
        self.volume = max(0, min(100, volume)) / 100.0

        if self.engine == "pyttsx3":
            engine = self.current_engine["engine"]
            engine.setProperty('volume', self.volume)

        # Salvar na config
        config.set("voice.voice_volume", volume)
        config.save()

    def set_voice(self, voice_name: str):
        """
        Define voz específica.

        Args:
            voice_name: Nome da voz
        """
        if self.engine == "pyttsx3":
            try:
                engine = self.current_engine["engine"]
                voices = engine.getProperty('voices')

                for voice in voices:
                    if voice_name.lower() in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            except Exception as e:
                print(f" Erro ao definir voz: {e}")

    def get_available_voices(self) -> list:
        """Retorna lista de vozes disponíveis."""
        if self.engine == "pyttsx3":
            try:
                engine = self.current_engine["engine"]
                voices = engine.getProperty('voices')
                return [voice.name for voice in voices]
            except:
                return []
        elif self.engine == "edge_tts":
            return ["pt-BR-AntonioNeural", "pt-BR-FranciscaNeural"]
        elif self.engine == "elevenlabs":
            return ["Antoni", "Arnold", "Bella", "Domi", "Elli", "Josh", "Rachel", "Sam"]
        return []

    def get_status(self) -> Dict[str, Any]:
        """Retorna status do sistema de speech."""
        return {
            "is_speaking": self.is_speaking,
            "engine": self.engine,
            "language": self.language,
            "volume": int(self.volume * 100),
            "engine_available": self.current_engine is not None
        }

    def stop_speaking(self):
        """Para de falar imediatamente."""
        if self.engine == "pyttsx3":
            try:
                engine = self.current_engine["engine"]
                engine.stop()
            except:
                pass

        self.is_speaking = False