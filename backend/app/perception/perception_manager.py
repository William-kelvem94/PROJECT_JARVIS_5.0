"""
JARVIS Perception Manager — Orchestrates face, gesture and voice engines.

Responsibilities:
  • Runs a camera capture loop in a background thread → feeds face_engine + gesture_engine.
  • Starts voice_engine (manages its own background thread + audio stream).
  • Maintains a shared PerceptionSnapshot (thread-safe read via get_snapshot()).
  • Exposes a wake-word callback so the agent session can react immediately.
"""

import asyncio
import json
import time
import threading
import os
import datetime
import multiprocessing
from multiprocessing import Queue, Process
from dataclasses import dataclass, asdict, field
from typing import Optional, Callable, List
import gc
import torch

from loguru import logger

from .face_engine import analyze_frame as _face_analyze, FaceResult
from .gesture_engine import analyze_frame as _gesture_analyze, GestureResult
from .object_engine import object_engine as _object_engine
from . import voice_engine
from .voice_engine import VoiceResult
from ..config import settings

# ── Shared snapshot ────────────────────────────────────────────────────────────

@dataclass
class PerceptionSnapshot:
    # Face
    face_present: bool = False
    face_count: int = 0
    face_emotion: str = "neutral"
    face_emotion_score: float = 0.0
    face_identity: Optional[str] = None
    face_identity_confidence: float = 0.0
    # Gestures
    hand_gesture: Optional[str] = None
    hand_side: Optional[str] = None
    head_gesture: Optional[str] = None
    pointing_direction: Optional[str] = None
    pointing_xy: Optional[tuple] = None
    # Voice
    wake_word_triggered: bool = False
    speaker_identity: Optional[str] = None
    offline_transcript: Optional[str] = None
    # Spatial
    detected_objects: List[dict] = field(default_factory=list)
    # Meta
    active_levels: List[str] = field(default_factory=list)
    timestamp: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["type"] = "perception_update"
        return d


# ── Vision Analysis Worker (Standalone for Windows compatibility) ──────────────

def _vision_worker(input_queue: Queue, output_queue: Queue):
    """
    Process function for vision analysis. 
    Standalone to avoid pickling 'self' (PerceptionManager) on Windows.
    """
    import pickle
    import os
    import gc
    import torch
    from loguru import logger
    
    # Imports locais para evitar circular dependency ou problemas de pickling
    from .face_engine import analyze_frame as _face_analyze
    from .gesture_engine import analyze_frame as _gesture_analyze

    logger.info("[VisionProcess] Motor de visão iniciado em processo independente.")

    while True:
        try:
            frame_bytes = input_queue.get()
            if frame_bytes is None:  # Sentinel to stop
                break
            frame = pickle.loads(frame_bytes)

            # Executa os motores de visão (Face + Gestos + Objetos)
            face = _face_analyze(frame)
            gesture = _gesture_analyze(frame)
            objects = _object_engine.analyze_frame(frame)

            all_levels = list(set(face.active_levels + gesture.active_levels))

            result = {
                'face_present': face.present,
                'face_count': face.count,
                'face_emotion': face.emotion,
                'face_emotion_score': face.emotion_score,
                'face_identity': face.identity,
                'face_identity_confidence': face.identity_confidence,
                'hand_gesture': gesture.hand_gesture,
                'hand_side': gesture.hand_side,
                'head_gesture': gesture.head_gesture,
                'pointing_direction': gesture.pointing_direction,
                'pointing_xy': gesture.pointing_xy,
                "detected_objects": objects,
                'active_levels': all_levels,
            }
            output_queue.put(result)

            # Gerenciamento de Memória (Especialmente importante no processo de visão)
            del frame
            del frame_bytes
            
            if settings.ENABLE_GC:
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    
        except Exception as e:
            logger.error(f"[VisionProcess] Erro crítico no loop de visão: {e}")
            output_queue.put({})  # Envia resultado vazio para não bloquear


# ── Manager ────────────────────────────────────────────────────────────────────

class PerceptionManager:
    def __init__(self):
        self._snapshot = PerceptionSnapshot()
        self._lock = threading.Lock()
        self._running = False
        self._camera_thread: Optional[threading.Thread] = None
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        self._wake_callbacks: List[Callable] = []
        self._gesture_callbacks: List[Callable] = []
        self._last_gesture = None
        # Multiprocessing for vision analysis
        self._vision_input_queue: Optional[Queue] = None
        self._vision_output_queue: Optional[Queue] = None
        self._vision_process: Optional[Process] = None

    # ── Configuration ──────────────────────────────────────────────────────────

    def on_wake_word(self, callback: Callable):
        """Register a (zero-arg) callable invoked when the wake word fires."""
        self._wake_callbacks.append(callback)

    def on_gesture(self, callback: Callable):
        """Register a (gesture_name, side) callable invoked when a gesture is detected."""
        self._gesture_callbacks.append(callback)

    # ── State access (thread-safe) ─────────────────────────────────────────────

    def _update(self, **kwargs):
        with self._lock:
            for k, v in kwargs.items():
                setattr(self._snapshot, k, v)
            self._snapshot.timestamp = datetime.datetime.now().isoformat()

    def get_snapshot(self) -> dict:
        with self._lock:
            return self._snapshot.to_dict()

    def _on_voice_event(self, result: VoiceResult):
        updates: dict = {}

        if result.wake_word_triggered:
            updates["wake_word_triggered"] = True
            logger.success("[Perception] 🎙️ Wake word detected — activating agent!")
            for cb in self._wake_callbacks:
                try:
                    cb()
                except Exception as e:
                    logger.warning(f"[Perception] Wake callback error: {e}")

        if result.speaker_identity:
            updates["speaker_identity"] = result.speaker_identity
            logger.info(f"[Perception] 🗣️ Recognised speaker: {result.speaker_identity}")

        if result.offline_transcript:
            updates["offline_transcript"] = result.offline_transcript

        if updates:
            self._update(**updates)

    # ── Camera loop (background thread) ───────────────────────────────────────

    def _find_camera(self, cv2_module) -> Optional[object]:
        """
        Try camera indices from env var JARVIS_CAMERA_INDEX (default: auto-detect 0,1,2).
        Returns an open VideoCapture or None if no camera is available.
        """
        import os
        forced = os.getenv("JARVIS_CAMERA_INDEX", "auto")
        if forced.lstrip("-").isdigit():
            indices = [int(forced)]
        else:
            indices = [0, 1, 2]

        for idx in indices:
            try:
                cam = cv2_module.VideoCapture(idx)
                if not cam.isOpened():
                    cam.release()
                    continue
                # Warm test: read one frame to confirm it's not a black/dead device
                ret, frame = cam.read()
                if not ret or frame is None:
                    cam.release()
                    continue
                cam.set(cv2_module.CAP_PROP_FRAME_WIDTH, 640)
                cam.set(cv2_module.CAP_PROP_FRAME_HEIGHT, 480)
                cam.set(cv2_module.CAP_PROP_FPS, 15)
                logger.success(f"[Perception] 📷 Camera opened (index {idx})")
                return cam
            except Exception as e:
                logger.debug(f"[Perception] Camera index {idx} failed: {e}")

        return None

    def _camera_loop(self):
        try:
            import cv2
        except ImportError:
            logger.warning("[Perception] opencv not installed — camera loop disabled")
            return

        cam = None
        retry_delay = 10.0   # wait longer before retrying a busy camera
        consecutive_failures = 0
        MAX_FAILURES = 3     # give up trying to open after this many failures

        logger.info("[Perception] Starting camera detection...")

        while self._running:
            # Open camera if needed
            if cam is None or not cam.isOpened():
                if consecutive_failures >= MAX_FAILURES:
                    logger.warning(
                        "[Perception] Camera unavailable after multiple attempts. "
                        "This may be because the browser already has exclusive access. "
                        "Set JARVIS_CAMERA_INDEX=1 (or 2) in .env to try another camera. "
                        "Face/Gesture perception disabled — Voice perception still active."
                    )
                    # Don't retry camera — just keep voice running
                    while self._running:
                        time.sleep(5.0)
                    break

                cam = self._find_camera(cv2)
                if cam is None:
                    consecutive_failures += 1
                    msg = (
                        f"[Perception] Câmera não encontrada ou ocupada "
                        f"(tentativa {consecutive_failures}/{MAX_FAILURES}). "
                    )
                    if os.name == 'nt':
                        msg += "Dica: Verifique se outro app (como o navegador ou Teams) está usando a webcam."
                    
                    logger.warning(msg)
                    time.sleep(retry_delay)
                    continue
                else:
                    consecutive_failures = 0

            ret, frame = cam.read()
            if not ret or frame is None:
                logger.warning("[Perception] Failed to read frame — reopening camera")
                cam.release()
                cam = None
                time.sleep(1.0)
                continue

            # ── Send frame to vision process ─────────────────────────────────────
            # Convert frame to bytes for multiprocessing
            # Verifica se a fila já está cheia para evitar leak de memória se o processo de visão travar
            if self._vision_input_queue.qsize() < 2:
                import pickle
                frame_bytes = pickle.dumps(frame)
                self._vision_input_queue.put(frame_bytes)
            
            # Limpa frame local da thread para liberar RAM
            del frame

            # ── Get result from vision process ─────────────────────────────────
            if not self._vision_output_queue.empty():
                result = self._vision_output_queue.get_nowait()
                if result:
                    self._update(**result)

                    # ── Proactive Gesture Trigger ────────────────────────────────────
                    hand_gesture = result.get('hand_gesture')
                    hand_side = result.get('hand_side')
                    if hand_gesture and hand_gesture != self._last_gesture:
                        if hand_gesture not in ("other", None):
                            logger.info(f"[Perception] ⚡ Proactive Gesture Trigger: {hand_gesture}")
                            for cb in self._gesture_callbacks:
                                try:
                                    cb(hand_gesture, hand_side)
                                except Exception as e:
                                    logger.warning(f"[Perception] Gesture callback error: {e}")
                        self._last_gesture = hand_gesture

                    # Log interesting events
                    if result.get('face_identity'):
                        logger.info(
                            f"[Perception] 👤 Identity: {result['face_identity']} "
                            f"({result['face_identity_confidence']:.0%})"
                        )
                    if result.get('face_present') and result.get('face_emotion') not in ("neutral", ""):
                        logger.debug(f"[Perception] 😐→ {result['face_emotion']} ({result['face_emotion_score']:.0%})")
                    if hand_gesture and hand_gesture not in ("other", None):
                        logger.info(f"[Perception] ✋ Gesture: {hand_gesture} ({hand_side})")
                    if result.get('head_gesture'):
                        logger.info(f"[Perception] 🫡 Head: {result['head_gesture']}")
            else:
                # If no result yet, skip update this frame
                pass

            # Controle Dinamico de FPS (Maestria de Hardware)
            # Desktop (GPU) -> FPS maior | Book2 (CPU) -> FPS balanceado
            fps_limit = 2.0 if settings.DEVICE_TYPE == "cuda" else 1.0
            sleep_time = 1.0 / fps_limit
            time.sleep(sleep_time)

        if cam:
            cam.release()
        logger.info("[Perception] Camera loop stopped")

    # ── Async LiveKit publish ──────────────────────────────────────────────────



    # ── Lifecycle ──────────────────────────────────────────────────────────────

    def start(self):
        import os # Import local de segurança para evitar NameError em reloads
        if self._running:
            return
        self._running = True

        # Initialize vision multiprocessing
        self._vision_input_queue = Queue()
        self._vision_output_queue = Queue()
        self._vision_process = Process(
            target=_vision_worker,
            args=(self._vision_input_queue, self._vision_output_queue),
            daemon=True,
            name="jarvis-vision-analysis"
        )
        self._vision_process.start()

        # Camera thread (skip if disabled)
        # Se sua CPU/GPU estiver lenta, desative a camera no .env com JARVIS_DISABLE_CAMERA=true
        if os.environ.get("JARVIS_DISABLE_CAMERA", "false").lower() == "true":
            logger.info("[PerceptionManager] 📷 Camera desativada por configuracao. Apenas Voz Ativa.")
        else:
            self._camera_thread = threading.Thread(
                target=self._camera_loop,
                daemon=True,
                name="jarvis-perception-camera",
            )
            self._camera_thread.start()

        # Voice engine
        voice_engine.add_callback(self._on_voice_event)
        voice_engine.start()

        logger.success("[PerceptionManager] 🧠 All perception engines started")

    def stop(self):
        self._running = False
        voice_engine.stop()
        if self._camera_thread:
            self._camera_thread.join(timeout=3.0)
        
        # Finalização robusta do processo de visão
        try:
            if self._vision_input_queue:
                self._vision_input_queue.put(None)  # Sentinel
            if self._vision_process:
                self._vision_process.join(timeout=2.0)
                if self._vision_process.is_alive():
                    logger.warning("[PerceptionManager] Forçando encerramento do processo de visão...")
                    self._vision_process.terminate()
        except: pass
        logger.info("[PerceptionManager] Stopped")

    def capture_frame(self):
        """
        Capture a single frame from the camera (for enrolment workflows).
        Returns a BGR numpy array or None.
        """
        try:
            import cv2
            cam = self._find_camera(cv2)
            if cam is None:
                return None
            # Warm-up: discard a few frames so autofocus settles
            for _ in range(5):
                cam.read()
            ret, frame = cam.read()
            cam.release()
            return frame if ret else None
        except Exception as e:
            logger.error(f"[Perception] Frame capture failed: {e}")
            return None

    def get_audio_sample(self, seconds: float = 5.0) -> Optional[object]:
        """
        Record `seconds` of audio from the microphone for enrolment.
        Returns int16 numpy array at 16 kHz, or None on error.
        """
        if not voice_engine.HAS_SOUNDDEVICE:
            return None
        try:
            import sounddevice as sd
            import numpy as np
            logger.info(f"[Perception] 🎤 Recording {seconds}s for voice enrolment...")
            audio = sd.rec(
                int(seconds * voice_engine.SAMPLE_RATE),
                samplerate=voice_engine.SAMPLE_RATE,
                channels=1,
                dtype="float32",
            )
            sd.wait()
            audio_int16 = (audio[:, 0] * 32767).astype(np.int16)
            logger.info("[Perception] Recording complete")
            return audio_int16
        except Exception as e:
            logger.error(f"[Perception] Audio recording failed: {e}")
            return None


# ── Singleton ──────────────────────────────────────────────────────────────────
perception_manager = PerceptionManager()
