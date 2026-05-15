import asyncio
import os
import subprocess
import time
from pathlib import Path

import edge_tts
from loguru import logger

try:
    import pygame
    pygame.mixer.init()
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
    logger.warning("[TTS] pygame não instalado. Playback local desativado.")

try:
    _r = subprocess.run(["piper", "--version"], capture_output=True, timeout=3)
    HAS_PIPER = _r.returncode == 0
    if HAS_PIPER:
        logger.info("[TTS] ✅ Piper TTS disponível (fallback offline)")
except Exception:
    HAS_PIPER = False


class TTSEngine:
    # Circuit breaker: abre após _CB_THRESHOLD falhas consecutivas
    _CB_THRESHOLD = 3
    _CB_COOLDOWN = 60.0  # segundos

    def __init__(self):
        self.temp_dir = Path("temp_audio")
        self.temp_dir.mkdir(exist_ok=True)
        self.default_voice = os.environ.get("JARVIS_TTS_VOICE", "pt-BR-AntonioNeural")
        self._stop_requested = False
        self._cb_failures = 0        # contagem de falhas consecutivas Edge-TTS
        self._cb_open_until = 0.0   # timestamp até quando o circuito está aberto

    # ── Circuit Breaker helpers ────────────────────────────────────────────────
    def _cb_is_open(self) -> bool:
        if self._cb_failures >= self._CB_THRESHOLD:
            if time.time() < self._cb_open_until:
                return True
            # Cooldown expirou: half-open, reseta contador
            self._cb_failures = 0
        return False

    def _cb_record_success(self):
        self._cb_failures = 0

    def _cb_record_failure(self):
        self._cb_failures += 1
        if self._cb_failures >= self._CB_THRESHOLD:
            self._cb_open_until = time.time() + self._CB_COOLDOWN
            logger.warning(f"[TTS] ⚡ Circuit breaker aberto por {self._CB_COOLDOWN}s (Edge-TTS inacessível)")

    # ── Controle de reprodução ─────────────────────────────────────────────────
    def stop_speaking(self):
        """Interrompe fala imediatamente (Barge-in)."""
        self._stop_requested = True
        if HAS_PYGAME:
            pygame.mixer.music.stop()
        logger.info("[TTS] 🛑 Fala interrompida por Barge-in.")

    # ── Backends de síntese ────────────────────────────────────────────────────
    async def _speak_edge(self, text: str, voice: str) -> str | None:
        """Síntese via Edge-TTS (Microsoft, online). Com retry e circuit breaker."""
        if self._cb_is_open():
            logger.warning("[TTS] Circuit breaker ABERTO — pulando Edge-TTS.")
            return None

        filename = self.temp_dir / f"jarvis_{int(time.time() * 1000)}.mp3"
        for attempt in range(2):
            try:
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(str(filename))
                self._cb_record_success()
                return str(filename)
            except Exception as e:
                logger.warning(f"[TTS] Edge-TTS falhou (tentativa {attempt + 1}/2): {e}")
                if attempt == 0:
                    await asyncio.sleep(1.0)

        self._cb_record_failure()
        return None

    async def _speak_piper(self, text: str) -> str | None:
        """Síntese offline via Piper TTS (fallback)."""
        if not HAS_PIPER:
            return None
        try:
            model_path = os.environ.get("JARVIS_PIPER_MODEL", "")
            filename = self.temp_dir / f"jarvis_piper_{int(time.time() * 1000)}.wav"
            cmd = ["piper", "--output_file", str(filename)]
            if model_path:
                cmd += ["--model", model_path]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.communicate(input=text.encode("utf-8"))
            if proc.returncode == 0 and filename.exists():
                logger.info("[TTS] ✅ Piper TTS (offline) usado com sucesso.")
                return str(filename)
            return None
        except Exception as e:
            logger.debug(f"[TTS] Piper error: {e}")
            return None

    # ── API pública ────────────────────────────────────────────────────────────
    async def speak(self, text: str, voice: str = None, play_local: bool = True) -> str | None:
        """Sintetiza texto com fallback: Edge-TTS → Piper TTS."""
        if not text or not text.strip():
            return None
        self._stop_requested = False
        voice = voice or self.default_voice

        filename = await self._speak_edge(text, voice)
        if filename is None and HAS_PIPER:
            logger.info("[TTS] Tentando Piper TTS como fallback offline...")
            filename = await self._speak_piper(text)

        if filename is None:
            logger.error("[TTS] Todos os backends falharam. Sem áudio.")
            return None

        if play_local and HAS_PYGAME:
            await self.play_audio_async(filename)

        return filename

    async def play_audio_async(self, file_path: str):
        """Reproduz áudio sem bloquear o event loop."""
        if not HAS_PYGAME:
            return
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                if self._stop_requested:
                    pygame.mixer.music.stop()
                    break
                await asyncio.sleep(0.05)
        except Exception as e:
            logger.error(f"[TTS] Erro ao tocar áudio: {e}")

    def cleanup(self):
        """Remove arquivos temporários de áudio com mais de 5 minutos."""
        now = time.time()
        for pattern in ("*.mp3", "*.wav"):
            for f in list(self.temp_dir.glob(pattern)):
                try:
                    if (now - f.stat().st_mtime) > 300:
                        if HAS_PYGAME and pygame.mixer.music.get_busy():
                            continue
                        f.unlink(missing_ok=True)
                except Exception:
                    pass


tts_engine = TTSEngine()
