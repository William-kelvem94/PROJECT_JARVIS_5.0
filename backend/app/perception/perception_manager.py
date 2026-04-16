"""
JARVIS Perception Manager — Orchestrates face, gesture and voice engines.

Responsibilities:
  • Runs a camera capture loop in a background thread → feeds face_engine + gesture_engine.
  • Starts voice_engine (manages its own background thread + audio stream).
  • Maintains a shared PerceptionSnapshot (thread-safe read via get_snapshot()).
  • Publishes perception events to the LiveKit room data channel (topic="perception").
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
from . import voice_engine
from .voice_engine import VoiceResult

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
    # Meta
    active_levels: List[str] = field(default_factory=list)
    timestamp: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["type"] = "perception_update"
        return d


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

    def set_room(self, room):
        self._room = room

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

    def _vision_analysis_process(self, input_queue: Queue, output_queue: Queue):
        """Process function for vision analysis in separate process."""
        import pickle
        while True:
            try:
                frame_bytes = input_queue.get()
                if frame_bytes is None:  # Sentinel to stop
                    break
                frame = pickle.loads(frame_bytes)

                # Run engines
                face: FaceResult = _face_analyze(frame)
                gesture: GestureResult = _gesture_analyze(frame)

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
                    'active_levels': all_levels,
                }
                output_queue.put(result)
                # Memory management
                if os.environ.get("JARVIS_ENABLE_GC", "true").lower() == "true":
                    gc.collect()
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
            except Exception as e:
                logger.error(f"[VisionProcess] Error: {e}")
                output_queue.put({})  # Send empty result to avoid blocking
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
            logger.info(f"[Perception] 🗣️ Recognised speaker: {result.speaker_identity} "
                        f"({result.speaker_confidence:.0%})")

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
            import pickle
            frame_bytes = pickle.dumps(frame)
            self._vision_input_queue.put(frame_bytes)

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

            # Controle Dinamico de FPS (Para Notebooks nao travarem a CPU em 100%)
            # Puxa 1.0 FPS por padrao (mais leve)
            import os
            try:
                fps_limit = float(os.environ.get("JARVIS_PERCEPTION_FPS", "1.0"))
                sleep_time = 1.0 / max(0.1, fps_limit)
            except:
                sleep_time = 1.0
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
            target=self._vision_analysis_process,
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
        # Stop vision process
        if self._vision_input_queue:
            self._vision_input_queue.put(None)  # Sentinel
        if self._vision_process:
            self._vision_process.join(timeout=3.0)
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
