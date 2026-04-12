"""
JARVIS Face Engine — Adaptive facial recognition.

Level C — Presence detection via MediaPipe (lightweight, ~10 MB)
           Detects if someone is in frame + face count + basic landmarks.

Level B — Emotion estimation via MediaPipe FaceMesh landmarks (always available)
           Rule-based: mouth openness, eye openness, brow position → emotion.
           Optional upgrade: DeepFace (blocked on Python 3.14 due to TensorFlow).

Level A — Identity recognition via face_recognition/dlib (heavy, ~200 MB)
           Recognises WHO is in frame by comparing to enrolled photos.

Install:
  pip install mediapipe opencv-python      → Level C + B (landmark emotion)
  pip install face_recognition             → + Level A (needs cmake + dlib)
    Windows pre-built: pip install dlib‑<version>-cp3xx-win_amd64.whl first

All levels stack — available ones run, missing ones are silently skipped.
"""

import os
import time
from dataclasses import dataclass, field
from typing import Optional, List

from loguru import logger

# ── Data directories ─────────────────────────────────────────────────────────
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
FACES_DIR = os.path.join(_BASE_DIR, "data", "faces")
MODELS_DIR = os.path.join(_BASE_DIR, "data", "models")


# ── Result dataclass ───────────────────────────────────────────────────────────
@dataclass
class FaceResult:
    present: bool = False
    count: int = 0
    emotion: str = "neutral"
    emotion_score: float = 0.0
    identity: Optional[str] = None
    identity_confidence: float = 0.0
    active_levels: List[str] = field(default_factory=list)


# ── Capability detection ───────────────────────────────────────────────────────
HAS_CV2 = False
HAS_MEDIAPIPE = False
HAS_DEEPFACE = False
HAS_FACE_RECOGNITION = False

try:
    import cv2  # type: ignore
    import numpy as np
    HAS_CV2 = True
except ImportError:
    pass

try:
    import mediapipe as mp  # type: ignore  # noqa: F401
    if HAS_CV2:
        HAS_MEDIAPIPE = True
        logger.info("[FaceEngine] ✅ Level C+B (MediaPipe presence + landmark emotion) available")
    else:
        logger.warning("[FaceEngine] Level C skipped — opencv-python not installed")
except ImportError:
    logger.warning("[FaceEngine] Level C unavailable — install: pip install mediapipe opencv-python")

try:
    from deepface import DeepFace  # type: ignore  # noqa: F401
    HAS_DEEPFACE = True
    logger.info("[FaceEngine] ✅ Level B+ (DeepFace DNN emotion) also available — will use for higher accuracy")
except ImportError:
    logger.info("[FaceEngine] DeepFace not available (needs TensorFlow ≤3.12) — using landmark-based emotion (Level B)")

try:
    import face_recognition as _fr  # type: ignore  # noqa: F401
    HAS_FACE_RECOGNITION = True
    logger.info("[FaceEngine] ✅ Level A (face_recognition identity) available")
except ImportError:
    logger.warning("[FaceEngine] Level A unavailable — install: pip install face_recognition (needs dlib/cmake)")


# ── Lazy MediaPipe initialisation (Tasks API — mediapipe ≥ 0.10.30) ─────────
_mp_landmarker = None
_mp_init_failed = False  # flag: once failed, stop retrying every frame


def _get_mp_models():
    """Return a FaceLandmarker (tasks API) or None if unavailable."""
    global _mp_landmarker, _mp_init_failed
    if _mp_landmarker is not None:
        return _mp_landmarker
    if _mp_init_failed:
        return None
    if not HAS_MEDIAPIPE:
        return None
    model_path = os.path.join(MODELS_DIR, "face_landmarker.task")
    if not os.path.exists(model_path):
        logger.warning(f"[FaceEngine] face_landmarker.task not found — run setup.py to download")
        _mp_init_failed = True
        return None
    try:
        from mediapipe.tasks import python as _mp_tasks
        from mediapipe.tasks.python import vision as _mp_vision
        
        # MediaPipe no Windows via pip frequentemente não tem suporte a GPU habilitado nos build flags.
        # Forçamos CPU para garantir que funcione sem erros.
        delegate = _mp_tasks.BaseOptions.Delegate.CPU
        
        base_opts = _mp_tasks.BaseOptions(
            model_asset_path=model_path,
            delegate=delegate
        )
        opts = _mp_vision.FaceLandmarkerOptions(
            base_options=base_opts,
            num_faces=4,
            min_face_detection_confidence=0.5,
            min_tracking_confidence=0.4,
        )
        _mp_landmarker = _mp_vision.FaceLandmarker.create_from_options(opts)
        logger.success(f"[FaceEngine] FaceLandmarker ready (Delegate: {delegate.name})")
    except Exception as e:
        logger.error(f"[FaceEngine] MediaPipe init failed: {e}")
        _mp_init_failed = True  # don't retry on every frame
    return _mp_landmarker


# ── Landmark-based emotion estimation (Level B, no DeepFace) ──────────────────
# MediaPipe FaceMesh 468-landmark indices
_LEFT_EYE_TOP    = [159, 160, 161]
_LEFT_EYE_BOT    = [145, 144, 163]
_LEFT_EYE_L      = 33
_LEFT_EYE_R      = 133
_RIGHT_EYE_TOP   = [386, 387, 388]
_RIGHT_EYE_BOT   = [374, 373, 380]
_RIGHT_EYE_L     = 362
_RIGHT_EYE_R     = 263
_MOUTH_TOP       = [13, 312, 311, 310]
_MOUTH_BOT       = [14, 82, 87, 88]
_MOUTH_L         = 61
_MOUTH_R         = 291
_LEFT_BROW_TOP   = [70, 63, 105, 66, 107]
_LEFT_BROW_BOT   = [159, 158, 157, 173]
_LEFT_EYE_CENTER  = 159
_RIGHT_BROW_TOP  = [300, 293, 334, 296, 336]
_RIGHT_BROW_BOT  = [386, 385, 384, 398]
_RIGHT_EYE_CENTER = 386


def _avg_y(lm, indices):
    return sum(lm[i].y for i in indices) / len(indices)


def _dist(lm, a, b):
    dx = lm[a].x - lm[b].x
    dy = lm[a].y - lm[b].y
    return (dx * dx + dy * dy) ** 0.5


def _estimate_emotion_from_landmarks(landmarks) -> tuple[str, float]:
    """
    Rule-based emotion estimation from FaceMesh 468 landmarks.
    Returns (emotion_label, confidence 0..1).
    """
    # In Tasks API, face_landmarks[0] is already a list[NormalizedLandmark]
    lm = landmarks

    # Eye Aspect Ratio (EAR) — mean of left and right
    def ear(top_idx, bot_idx, l_idx, r_idx):
        vert = _dist(lm, top_idx[0], bot_idx[0])
        horiz = _dist(lm, l_idx, r_idx)
        return vert / (horiz + 1e-6)

    left_ear  = ear([_LEFT_EYE_TOP[0]],  [_LEFT_EYE_BOT[0]],  _LEFT_EYE_L,  _LEFT_EYE_R)
    right_ear = ear([_RIGHT_EYE_TOP[0]], [_RIGHT_EYE_BOT[0]], _RIGHT_EYE_L, _RIGHT_EYE_R)
    mean_ear = (left_ear + right_ear) / 2.0

    # Mouth Aspect Ratio (MAR)
    mouth_vert  = _dist(lm, _MOUTH_TOP[0], _MOUTH_BOT[0])
    mouth_horiz = _dist(lm, _MOUTH_L, _MOUTH_R)
    mar = mouth_vert / (mouth_horiz + 1e-6)

    # Brow raise: compare brow top to eye center (positive = raised)
    left_brow_raise  = _avg_y(lm, _LEFT_BROW_BOT)  - lm[_LEFT_EYE_CENTER].y
    right_brow_raise = _avg_y(lm, _RIGHT_BROW_BOT) - lm[_RIGHT_EYE_CENTER].y
    brow_raise = (left_brow_raise + right_brow_raise) / 2.0  # negative = raised (y grows down)

    # Mouth corners (higher Y = frown, lower Y = smile)
    left_corner  = lm[_MOUTH_L].y
    right_corner = lm[_MOUTH_R].y
    mouth_center_y = lm[_MOUTH_TOP[0]].y
    corner_lift = mouth_center_y - (left_corner + right_corner) / 2.0

    # ── Decision rules ─────────
    # Surprised: wide eyes + open mouth + raised brows
    if mean_ear > 0.35 and mar > 0.45 and brow_raise < -0.015:
        return ("surprise", min(1.0, (mar * 1.6 + mean_ear) / 2.0))

    # Happy: corners lifted + moderate mouth open
    if corner_lift < -0.005 and mar > 0.05:
        confidence = min(1.0, abs(corner_lift) * 60 + mar * 0.5)
        return ("happy", round(confidence, 2))

    # Sad: corners dropped + eyes not wide
    if corner_lift > 0.008 and mean_ear < 0.30:
        return ("sad", round(min(1.0, corner_lift * 50), 2))

    # Angry: brows lowered (positive brow_raise) + narrow eyes
    if brow_raise > 0.010 and mean_ear < 0.27:
        return ("angry", round(min(1.0, brow_raise * 40), 2))

    # Fear: wide eyes + raised brows + slightly open mouth
    if mean_ear > 0.32 and brow_raise < -0.012 and mar > 0.20:
        return ("fear", round(min(1.0, mean_ear * 2.2), 2))

    # Disgust: one brow lowered asymmetrically
    brow_asymm = abs(left_brow_raise - right_brow_raise)
    if brow_asymm > 0.008 and brow_raise > 0:
        return ("disgust", round(min(1.0, brow_asymm * 60), 2))

    return ("neutral", 0.80)


# ── Enrolled faces for Level A ─────────────────────────────────────────────────
_enrolled: dict = {}
_enrolled_loaded = False


def _ensure_enrolled():
    global _enrolled, _enrolled_loaded
    if _enrolled_loaded or not HAS_FACE_RECOGNITION:
        return
    _enrolled_loaded = True
    if not os.path.isdir(FACES_DIR):
        return
    import face_recognition as fr  # type: ignore
    for name in os.listdir(FACES_DIR):
        subdir = os.path.join(FACES_DIR, name)
        if not os.path.isdir(subdir):
            continue
        encodings = []
        for fn in os.listdir(subdir):
            if not fn.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            try:
                img = fr.load_image_file(os.path.join(subdir, fn))
                found = fr.face_encodings(img)
                if found:
                    encodings.append(found[0])
            except Exception as ex:
                logger.debug(f"[FaceEngine] Skipped {fn}: {ex}")
        if encodings:
            _enrolled[name] = encodings
            logger.info(f"[FaceEngine] Enrolled '{name}': {len(encodings)} sample(s)")


# ── Throttle state ─────────────────────────────────────────────────────────────
_emotion_ts: float = 0.0
_identity_ts: float = 0.0
_EMOTION_RATE = 2.0    # Level B: at most 0.5 FPS
_IDENTITY_RATE = 3.0   # Level A: at most 0.33 FPS


# ── Public API ─────────────────────────────────────────────────────────────────
def analyze_frame(frame_bgr) -> FaceResult:
    """
    Analyse one BGR camera frame.
    Call from a single background thread only — not thread-safe across threads.
    """
    global _emotion_ts, _identity_ts

    result = FaceResult()
    if frame_bgr is None:
        return result

    now = time.monotonic()

    # ── Level C: Presence (MediaPipe Tasks API) ──────────────────────────────
    landmarker = _get_mp_models()
    if landmarker is None:
        return result

    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
    lm_result = landmarker.detect(mp_image)

    if not lm_result.face_landmarks:
        return result  # No face found — skip B and A

    result.present = True
    result.count = len(lm_result.face_landmarks)
    result.active_levels.append("C")

    # ── Level B: Emotion ──────────────────────────────────────────────────────
    # Try DeepFace (DNN accuracy) first; fall back to FaceLandmarker landmark rules.
    if (now - _emotion_ts) >= _EMOTION_RATE:
        try:
            if HAS_DEEPFACE:
                from deepface import DeepFace  # type: ignore
                analysis = DeepFace.analyze(
                    frame_bgr,
                    actions=["emotion"],
                    enforce_detection=False,
                    silent=True,
                )
                if isinstance(analysis, list):
                    analysis = analysis[0]
                dominant = analysis.get("dominant_emotion", "neutral")
                score_raw = float(analysis.get("emotion", {}).get(dominant, 0.0))
                result.emotion = dominant
                result.emotion_score = round(score_raw / 100.0, 2) if score_raw > 1.0 else round(score_raw, 2)
                result.active_levels.append("B")
            else:
                # Landmark-based emotion (face_landmarks[0] is list[NormalizedLandmark])
                emotion, score = _estimate_emotion_from_landmarks(lm_result.face_landmarks[0])
                result.emotion = emotion
                result.emotion_score = score
                result.active_levels.append("B")
            _emotion_ts = now
        except Exception as ex:
            logger.debug(f"[FaceEngine] Emotion analysis skipped: {ex}")

    # ── Level A: Identity (face_recognition) ──────────────────────────────────
    _ensure_enrolled()
    if HAS_FACE_RECOGNITION and _enrolled and (now - _identity_ts) >= _IDENTITY_RATE:
        try:
            import face_recognition as fr  # type: ignore
            encodings = fr.face_encodings(frame_rgb)
            if encodings:
                best_name: Optional[str] = None
                best_dist: float = 0.6  # threshold — lower = stricter
                for enc in encodings:
                    for name, refs in _enrolled.items():
                        dists = fr.face_distance(refs, enc)
                        min_d = float(np.min(dists))
                        if min_d < best_dist:
                            best_dist, best_name = min_d, name
                if best_name:
                    result.identity = best_name
                    result.identity_confidence = round(1.0 - best_dist, 2)
                    result.active_levels.append("A")
            _identity_ts = now
        except Exception as ex:
            logger.debug(f"[FaceEngine] Identity analysis skipped: {ex}")

    return result


def enroll_face(name: str, frame_bgr) -> str:
    """
    Enrol a face photo for identity recognition (Level A).
    Returns a status string.
    """
    if not HAS_FACE_RECOGNITION:
        return "Level A (face_recognition) not installed — enrolment not possible."
    if not HAS_CV2:
        return "opencv-python not installed."
    try:
        out_dir = os.path.join(FACES_DIR, name)
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"{int(time.time())}.jpg")
        cv2.imwrite(path, frame_bgr)
        # Force reload
        global _enrolled_loaded
        _enrolled_loaded = False
        _ensure_enrolled()
        logger.success(f"[FaceEngine] ✅ Enrolled face for '{name}' → {path}")
        return f"Face enrolled for '{name}'. Total samples: {len(_enrolled.get(name, []))}"
    except Exception as e:
        logger.error(f"[FaceEngine] Enrol failed: {e}")
        return f"Error enrolling face: {e}"
