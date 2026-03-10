"""
JARVIS Gesture Engine — Adaptive gesture recognition.

Level A — Hand gestures via MediaPipe Hands
           Detects: fist, open_palm, point, peace, thumbs_up, thumbs_down, other.

Level B — Head/body gestures via MediaPipe Pose
           Detects: nod (yes), shake (no) — temporal analysis of landmark movement.

Level C — Pointing direction (builds on Level A when gesture == "point")
           Maps index finger direction to: left, right, up, down, center.
           Reports normalised (x, y) of finger tip for targeting.

Install: pip install mediapipe opencv-python
"""

import os
import time
import collections
from dataclasses import dataclass, field
from typing import Optional, Tuple, List

from loguru import logger


# ── Paths ───────────────────────────────────────────────────────────────────────
MODELS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "models"
)


# ── Result dataclass ───────────────────────────────────────────────────────────
@dataclass
class GestureResult:
    # Level A
    hand_gesture: Optional[str] = None    # fist|open_palm|point|peace|thumbs_up|thumbs_down
    hand_side: Optional[str] = None       # left | right
    # Level B
    head_gesture: Optional[str] = None    # nod | shake
    # Level C (subset of A — when hand_gesture == "point")
    pointing_direction: Optional[str] = None   # left|right|up|down|center
    pointing_xy: Optional[Tuple[float, float]] = None  # normalised (0‑1)
    active_levels: List[str] = field(default_factory=list)


# ── Capability detection ───────────────────────────────────────────────────────
HAS_GESTURE = False

try:
    import cv2  # type: ignore
    import mediapipe as mp  # type: ignore  # noqa: F401
    HAS_GESTURE = True
    logger.info("[GestureEngine] ✅ MediaPipe GestureRecognizer + PoseLandmarker available")
except ImportError:
    logger.warning("[GestureEngine] Unavailable — install: pip install mediapipe opencv-python")


# ── Gesture map: MediaPipe built-in names → our naming ────────────────────────
_GESTURE_MAP = {
    "Closed_Fist": "fist",
    "Open_Palm": "open_palm",
    "Pointing_Up": "point",
    "Victory": "peace",
    "Thumb_Up": "thumbs_up",
    "Thumb_Down": "thumbs_down",
    "ILoveYou": "open_palm",
}


# ── Lazy MediaPipe initialisation (Tasks API) ──────────────────────────────────
_gesture_rec = None
_pose_lm = None


def _get_mp():
    """Return (GestureRecognizer, PoseLandmarker) or (None, None) if unavailable."""
    global _gesture_rec, _pose_lm
    if _gesture_rec is not None:
        return _gesture_rec, _pose_lm
    if not HAS_GESTURE:
        return None, None

    gest_path = os.path.join(MODELS_DIR, "gesture_recognizer.task")
    pose_path = os.path.join(MODELS_DIR, "pose_landmarker_lite.task")

    if not os.path.exists(gest_path):
        logger.warning("[GestureEngine] gesture_recognizer.task not found — run setup.py")
        return None, None

    try:
        from mediapipe.tasks import python as _mp_tasks
        from mediapipe.tasks.python import vision as _mp_vision

        base_opts = _mp_tasks.BaseOptions(model_asset_path=gest_path)
        opts = _mp_vision.GestureRecognizerOptions(
            base_options=base_opts,
            num_hands=2,
            min_hand_detection_confidence=0.7,
            min_tracking_confidence=0.5,
        )
        _gesture_rec = _mp_vision.GestureRecognizer.create_from_options(opts)
        logger.success("[GestureEngine] GestureRecognizer (tasks API) ready")
    except Exception as e:
        logger.error(f"[GestureEngine] GestureRecognizer init failed: {e}")
        return None, None

    if os.path.exists(pose_path):
        try:
            from mediapipe.tasks import python as _mp_tasks
            from mediapipe.tasks.python import vision as _mp_vision
            base_opts = _mp_tasks.BaseOptions(model_asset_path=pose_path)
            opts = _mp_vision.PoseLandmarkerOptions(
                base_options=base_opts,
                min_pose_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            _pose_lm = _mp_vision.PoseLandmarker.create_from_options(opts)
            logger.success("[GestureEngine] PoseLandmarker (tasks API) ready")
        except Exception as e:
            logger.warning(f"[GestureEngine] PoseLandmarker init failed (head gestures disabled): {e}")
    else:
        logger.warning("[GestureEngine] pose_landmarker_lite.task not found — head gestures disabled")

    return _gesture_rec, _pose_lm


# ── Temporal buffers for head gesture detection (Level B) ─────────────────────
_nose_x_buf: collections.deque = collections.deque(maxlen=20)   # ~2 s at 10 fps
_nose_y_buf: collections.deque = collections.deque(maxlen=20)
_last_head_gesture: Optional[str] = None
_head_gesture_ts: float = 0.0
_HEAD_COOLDOWN = 2.0   # seconds between head gesture events


# ── Hand gesture classifier ────────────────────────────────────────────────────
# Manual _classify_hand is no longer needed — GestureRecognizer handles this natively.


# ── Pointing direction (Level C) ──────────────────────────────────────────────
def _get_pointing(hand_lm) -> Tuple[str, Tuple[float, float]]:
    """
    Derive pointing direction and fingertip position from index finger.
    hand_lm is list[NormalizedLandmark] (tasks API — no .landmark attr needed).
    """
    tip = hand_lm[8]   # index fingertip
    mcp = hand_lm[5]   # index MCP (knuckle)

    dx = tip.x - mcp.x
    dy = tip.y - mcp.y

    if abs(dx) < 0.03 and abs(dy) < 0.03:
        direction = "center"
    elif abs(dx) >= abs(dy):
        direction = "right" if dx > 0 else "left"
    else:
        direction = "down" if dy > 0 else "up"

    return direction, (round(tip.x, 3), round(tip.y, 3))


# ── Head gesture detector (Level B) ───────────────────────────────────────────
def _detect_head_gesture() -> Optional[str]:
    global _last_head_gesture, _head_gesture_ts

    now = time.monotonic()
    if now - _head_gesture_ts < _HEAD_COOLDOWN:
        return None
    if len(_nose_y_buf) < 12:
        return None

    y_range = max(_nose_y_buf) - min(_nose_y_buf)
    x_range = max(_nose_x_buf) - min(_nose_x_buf)

    gesture = None
    if y_range > 0.04:       # Nod: significant vertical oscillation
        gesture = "nod"
    elif x_range > 0.05:     # Shake: significant horizontal oscillation
        gesture = "shake"

    if gesture:
        _last_head_gesture = gesture
        _head_gesture_ts = now
        # Clear buffers so same motion isn't re-reported
        _nose_x_buf.clear()
        _nose_y_buf.clear()

    return gesture


# ── Public API ─────────────────────────────────────────────────────────────────
def analyze_frame(frame_bgr) -> GestureResult:
    """
    Analyse one BGR camera frame for gestures.
    Call from a single background thread only.
    """
    result = GestureResult()
    if not HAS_GESTURE or frame_bgr is None:
        return result

    gesture_rec, pose_lm = _get_mp()
    if gesture_rec is None:
        return result

    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

    # ── Level A + C: Hand gestures via GestureRecognizer ─────────────────────
    gest_result = gesture_rec.recognize(mp_image)
    if gest_result.gestures:
        top = gest_result.gestures[0][0]  # first hand, top-ranked gesture
        mapped = _GESTURE_MAP.get(top.category_name)
        if mapped:
            result.hand_gesture = mapped
            result.active_levels.append("A")

            if gest_result.handedness:
                result.hand_side = gest_result.handedness[0][0].category_name.lower()

            # Level C: pointing direction
            if mapped == "point" and gest_result.hand_landmarks:
                direction, xy = _get_pointing(gest_result.hand_landmarks[0])
                result.pointing_direction = direction
                result.pointing_xy = xy
                result.active_levels.append("C")

    # ── Level B: Head/body gestures (PoseLandmarker) ──────────────────────────
    if pose_lm is not None:
        pose_result = pose_lm.detect(mp_image)
        # pose_result.pose_landmarks = list[list[NormalizedLandmark]]; [0][0] = nose
        if pose_result.pose_landmarks:
            nose = pose_result.pose_landmarks[0][0]
            _nose_x_buf.append(nose.x)
            _nose_y_buf.append(nose.y)

            head_gest = _detect_head_gesture()
            if head_gest:
                result.head_gesture = head_gest
                result.active_levels.append("B")

    return result
