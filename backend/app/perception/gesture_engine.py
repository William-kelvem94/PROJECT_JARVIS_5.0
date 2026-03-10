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

import time
import collections
from dataclasses import dataclass, field
from typing import Optional, Tuple, List

from loguru import logger


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
    logger.info("[GestureEngine] ✅ MediaPipe Hands + Pose available")
except ImportError:
    logger.warning("[GestureEngine] Unavailable — install: pip install mediapipe opencv-python")


# ── Lazy MediaPipe initialisation ──────────────────────────────────────────────
_mp_hands = None
_mp_pose = None


def _get_mp():
    global _mp_hands, _mp_pose
    if _mp_hands is None and HAS_GESTURE:
        try:
            _mp_hands = mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5,
            )
            _mp_pose = mp.solutions.pose.Pose(
                static_image_mode=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
        except Exception as e:
            logger.error(f"[GestureEngine] MediaPipe init failed: {e}")
    return _mp_hands, _mp_pose


# ── Temporal buffers for head gesture detection (Level B) ─────────────────────
_nose_x_buf: collections.deque = collections.deque(maxlen=20)   # ~2 s at 10 fps
_nose_y_buf: collections.deque = collections.deque(maxlen=20)
_last_head_gesture: Optional[str] = None
_head_gesture_ts: float = 0.0
_HEAD_COOLDOWN = 2.0   # seconds between head gesture events


# ── Hand gesture classifier ────────────────────────────────────────────────────
def _classify_hand(landmarks) -> str:
    """
    Classify hand gesture from 21 MediaPipe hand landmarks.
    Returns one of: fist, open_palm, point, peace, thumbs_up, thumbs_down, other.
    """
    lm = landmarks.landmark

    # Reference points
    wrist = lm[0]
    index_mcp = lm[5]

    # Determine handedness from geometry (right hand: wrist.x < index_mcp.x in mirror image)
    is_right = wrist.x < index_mcp.x

    # Thumb extended: tip further from centre than base, along hand axis
    thumb_tip = lm[4]
    thumb_ip = lm[3]
    thumb_extended = (thumb_tip.x > thumb_ip.x) if is_right else (thumb_tip.x < thumb_ip.x)

    # Non-thumb fingers: tip.y < pip.y means extended (image y increases downward)
    idx_ext = lm[8].y < lm[6].y    # index
    mid_ext = lm[12].y < lm[10].y  # middle
    rng_ext = lm[16].y < lm[14].y  # ring
    pnk_ext = lm[20].y < lm[18].y  # pinky

    extended = [thumb_extended, idx_ext, mid_ext, rng_ext, pnk_ext]
    count = sum(extended)

    if count == 0:
        return "fist"
    if count == 5:
        return "open_palm"
    if idx_ext and not mid_ext and not rng_ext and not pnk_ext and not thumb_extended:
        return "point"
    if idx_ext and mid_ext and not rng_ext and not pnk_ext and not thumb_extended:
        return "peace"
    # Thumbs up: thumb extended, all others curled, thumb tip above wrist
    if thumb_extended and not idx_ext and not mid_ext and not rng_ext and not pnk_ext:
        if thumb_tip.y < wrist.y:
            return "thumbs_up"
        return "thumbs_down"

    return "other"


# ── Pointing direction (Level C) ──────────────────────────────────────────────
def _get_pointing(landmarks) -> Tuple[str, Tuple[float, float]]:
    """
    Derive pointing direction and fingertip position from index finger.
    Returns (direction_str, (normalised_x, normalised_y)).
    """
    tip = landmarks.landmark[8]   # index fingertip
    mcp = landmarks.landmark[5]   # index MCP (knuckle)

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

    hands, pose = _get_mp()
    if hands is None:
        return result

    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

    # ── Level A + C: Hand gestures ────────────────────────────────────────────
    hands_result = hands.process(frame_rgb)
    if hands_result.multi_hand_landmarks:
        hand_lm = hands_result.multi_hand_landmarks[0]
        handedness = "right"
        if hands_result.multi_handedness:
            label = hands_result.multi_handedness[0].classification[0].label
            handedness = label.lower()

        gesture = _classify_hand(hand_lm)
        result.hand_gesture = gesture
        result.hand_side = handedness
        result.active_levels.append("A")

        # Level C: pointing direction
        if gesture == "point":
            direction, xy = _get_pointing(hand_lm)
            result.pointing_direction = direction
            result.pointing_xy = xy
            result.active_levels.append("C")

    # ── Level B: Head/body gestures (Pose) ────────────────────────────────────
    if pose is not None:
        pose_result = pose.process(frame_rgb)
        if pose_result.pose_landmarks:
            nose = pose_result.pose_landmarks.landmark[0]
            _nose_x_buf.append(nose.x)
            _nose_y_buf.append(nose.y)

            head_gest = _detect_head_gesture()
            if head_gest:
                result.head_gesture = head_gest
                result.active_levels.append("B")

    return result
