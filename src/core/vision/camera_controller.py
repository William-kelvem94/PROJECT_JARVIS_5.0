"""
Controlador de Câmera (Eyes)
Responsável por detecção de presença e reconhecimento facial
"""

import threading
import time
import logging
import shutil
from typing import Optional, List, Dict, Any, Callable
from pathlib import Path
from datetime import datetime
import numpy as np

# Safe CV2 Import
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None

from src.utils.config import config
from src.core.vision.gesture_controller import gesture_controller
from src.core.intelligence.emotion_detector import emotion_detector
from src.core.management.hardware_manager import hardware_manager

logger = logging.getLogger(__name__)

# MANDATORY: face_recognition is REQUIRED
try:
    import face_recognition
    FACE_REC_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ face-recognition not available. FaceID features disabled. {e}")
    FACE_REC_AVAILABLE = False
    face_recognition = None

class CameraController:
    """Controla a webcam e processa visão computacional"""

    def __init__(self):
        self.camera_index = config.get_setting('sensory.camera_index', 0)
        self.is_monitoring = False
        self.monitor_thread = None
        self.last_seen_user = None
        self.last_seen_time = 0
        self.known_face_encodings = []
        self.known_face_names = []
        self.face_detection_model = config.get_setting('sensory.camera_index', 'hog')
        
        # Estado emocional
        self.current_emotion = "neutral"
        self.emotion_history = []
        
        # FASE 1: FPS Adaptativo para economia de CPU
        self.active_fps = 30  # FPS quando há movimento/usuário
        self.idle_fps = 5     # FPS quando cenário estático
        self.motion_threshold = 5000  # Threshold de pixels diferentes para detectar movimento
        self.previous_frame = None
        
        # Otimização: Usar GPU se disponível
        try:
            if hardware_manager.get_device() == "cuda":
                 if self.face_detection_model == 'hog':
                     logger.info("GPU detectada. Ajustando FaceID para modo CNN para maior precisão.")
                     self.face_detection_model = 'cnn'
            else:
                if self.face_detection_model == 'cnn':
                    logger.warning("Modelo CNN solicitado mas rodando em CPU. Isso será LENTO. Recomendo HOG para CPU.")
                    self.face_detection_model = 'hog'
        except Exception as e:
            logger.warning(f"Erro ao verificar hardware para câmera: {e}")
        
        # Callback para enviar vídeo para GUI (se necessário)
        self.on_frame_ready: Optional[Callable[[Any], None]] = None
        
        # Carregar faces conhecidas em background se FaceRec disponível
        if FACE_REC_AVAILABLE:
            threading.Thread(target=self._load_known_faces, daemon=True, name="CamFaceSync").start()

    def _load_known_faces(self):
        """Carrega faces da pasta de dados para reconhecimento"""
        if not FACE_REC_AVAILABLE or face_recognition is None:
            return
            
        # Usar caminho absoluto centralizado
        faces_dir = config.DATA_DIR / 'faces'
        faces_dir.mkdir(parents=True, exist_ok=True)

        quarantine_dir = faces_dir / "quarantine"
        
        # Aceitar jpg, jpeg, png
        count = 0
        for file_path in list(faces_dir.glob("*.jpg")) + list(faces_dir.glob("*.png")) + list(faces_dir.glob("*.jpeg")):
            try:
                # O nome do arquivo é o nome da pessoa (remove sufixo de ângulo)
                raw_name = file_path.stem
                name = raw_name.split('_')[0]
                
                image = face_recognition.load_image_file(str(file_path))
                encodings = face_recognition.face_encodings(image)
                
                if encodings:
                    self.known_face_encodings.append(encodings[0])
                    self.known_face_names.append(name)
                    count += 1
                    logger.info(f"   👤 FaceID: Carregada biometria de '{raw_name}'")
                else:
                    # TRATAMENTO: Mover para quarentena se não houver face
                    logger.error(f"   ❌ FaceID: Rosto não identificado em '{file_path.name}'. Isolando em quarentena.")
                    quarantine_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(file_path), str(quarantine_dir / file_path.name))
            except Exception as e:
                logger.error(f"   ❌ FaceID: Erro ao tratar {file_path.name}: {e}")
                
        if count > 0:
            logger.info(f"✅ Camera: {count} perfis biométricos sincronizados.")

    def start_monitoring(self):
        """Inicia monitoramento em background"""
        if self.is_monitoring: return
        if not CV2_AVAILABLE:
            logger.error("OpenCV not available. Cannot start monitoring.")
            return

        # SAFE START: Load faces only when monitoring starts
        if not self.known_face_encodings and FACE_REC_AVAILABLE:
             threading.Thread(target=self._load_known_faces, daemon=True, name="CamFaceSync").start()

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True, name="SentinelCameraThread")
        self.monitor_thread.start()
        logger.info("Monitoramento de visão iniciado.")

    def stop_monitoring(self):
        """Para monitoramento"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

    def _monitor_loop(self):
        """Loop principal de visão com FPS adaptativo"""
        if not CV2_AVAILABLE: return

        # 🔒 PERMISSÃO CHECK: Verificar acesso à câmera
        try:
            import platform
            if platform.system() == "Windows":
                test_capture = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
                if test_capture and test_capture.isOpened():
                    test_capture.release()
                    logger.info("✅ Permissões de câmera verificadas")
                else:
                    logger.error("❌ Sem permissão para acessar a câmera.")
                    self.is_monitoring = False
                    return
        except Exception:
            pass

        time.sleep(2) # Safe delay
        
        video_capture = None
        try:
            logger.info("📹 Opening camera...")
            
            for attempt in range(3):
                try:
                    # Use hardware lock to prevent conflicts with heavy loads
                    with hardware_manager.neural_lock:
                        video_capture = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
                    if video_capture and video_capture.isOpened():
                        break
                except Exception as e:
                    logger.warning(f"Tentativa {attempt+1} de abrir câmera falhou: {e}")
                    time.sleep(1)
            
            if not video_capture or not video_capture.isOpened():
                logger.error(f"Não foi possível abrir a câmera {self.camera_index}.")
                return
                
            logger.info("✅ Camera opened successfully")

            process_this_frame = True
            is_active_mode = True

            while self.is_monitoring:
                ret, frame = video_capture.read()
                if not ret or frame is None or frame.size == 0:
                    time.sleep(1)
                    continue

                if len(frame.shape) != 3 or frame.shape[2] != 3:
                    time.sleep(1)
                    continue

                self._current_frame_cache = frame.copy()

                # Detecção de Movimento
                motion_detected = False
                try:
                    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)
                    
                    if self.previous_frame is not None:
                        frame_delta = cv2.absdiff(self.previous_frame, gray_frame)
                        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
                        non_zero_count = cv2.countNonZero(thresh)
                        
                        if non_zero_count > self.motion_threshold:
                            motion_detected = True
                            self.last_seen_time = time.time()
                    
                    self.previous_frame = gray_frame
                except Exception:
                    motion_detected = True

                idle_time = time.time() - self.last_seen_time if self.last_seen_time > 0 else 0
                should_be_active = motion_detected or idle_time < 10
                
                if should_be_active and not is_active_mode:
                    is_active_mode = True
                elif not should_be_active and is_active_mode:
                    is_active_mode = False

                # Face Recognition
                if is_active_mode and FACE_REC_AVAILABLE and getattr(self, '_faceid_failures', 0) < 5:
                    if process_this_frame:
                        try:
                            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                            rgb_small_frame = small_frame[:, :, ::-1]
                            r_frame = np.ascontiguousarray(rgb_small_frame)
                            
                            face_locations = face_recognition.face_locations(r_frame, model="hog")

                            if face_locations:
                                face_encodings = face_recognition.face_encodings(r_frame, face_locations)
                                for face_encoding in face_encodings:
                                    match = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
                                    name = "Desconhecido"
                                    if True in match:
                                        name = self.known_face_names[match.index(True)]

                                    if name != self.last_seen_user or (time.time() - self.last_seen_time > 60):
                                        logger.info(f"Usuário identificado: {name}")
                                        self.last_seen_user = name

                                        # Sync Identity
                                        try:
                                            from src.core.management.context_manager import context_manager
                                            from src.core.management.user_manager import user_manager
                                            if name != "Desconhecido":
                                                context_manager.switch_user(name)
                                                user_manager.record_presence(name)
                                        except ImportError: pass

                                    self.last_seen_time = time.time()
                                self._faceid_failures = 0
                        except Exception as e:
                            logger.debug(f"Erro FaceID: {e}")
                            self._faceid_failures = getattr(self, '_faceid_failures', 0) + 1
            
                # Emoção (Opcional - wrap in try/except)
                if is_active_mode and emotion_detector:
                    try:
                        emotion_data = emotion_detector.detect_emotion_from_frame(frame)
                        self.current_emotion = emotion_data['emotion']
                    except: pass

                process_this_frame = not process_this_frame
            
                # Gestos
                if is_active_mode:
                    try:
                        from src.core.vision.gesture_controller import get_gesture_controller
                        gesture_ctrl = get_gesture_controller()
                        if gesture_ctrl:
                            processed_frame, gesture = gesture_ctrl.process_frame(frame)
                            if self.on_frame_ready:
                                try:
                                    rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                                    self.on_frame_ready(rgb_frame)
                                except: pass
                    except: pass

                sleep_time = (1.0 / self.active_fps) if is_active_mode else (1.0 / self.idle_fps)
                time.sleep(sleep_time)

        except Exception as e:
            logger.error(f"Erro no loop de monitoramento: {e}")
        finally:
            if video_capture:
                video_capture.release()

    def register_new_face(self, name: str) -> bool:
        if not FACE_REC_AVAILABLE:
            logger.error("Face recognition not available.")
            return False
        if not CV2_AVAILABLE:
            return False

        try:
            video_capture = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            if not video_capture.isOpened(): return False

            faces_dir = config.DATA_DIR / 'faces'
            faces_dir.mkdir(parents=True, exist_ok=True)
            
            # Simple single shot for safety
            ret, frame = video_capture.read()
            if ret:
                save_path = faces_dir / f"{name}_front.jpg"
                cv2.imwrite(str(save_path), frame)
                self._load_known_faces()
                video_capture.release()
                return True
            
            video_capture.release()
            return False
        except Exception:
            return False

    def capture_context(self) -> Dict[str, Any]:
        """Captura um snapshot leve de contexto"""
        return {
            "timestamp": datetime.now().isoformat(),
            "last_user": self.last_seen_user,
            "current_emotion": self.current_emotion,
            "face_detected": (time.time() - self.last_seen_time < 5)
        }

    def save_snapshot(self, path: Path):
        try:
             if hasattr(self, '_current_frame_cache') and self._current_frame_cache is not None:
                 cv2.imwrite(str(path), self._current_frame_cache)
                 return True
             return False
        except Exception:
            return False

# ============================================================================
# SINGLETON INSTANCE (Lazy Load)
# ============================================================================
_camera_controller = None

def get_camera_controller():
    global _camera_controller
    if _camera_controller is None:
        _camera_controller = CameraController()
    return _camera_controller

# Global instance (Caution: Accessing this variable instantiates the controller if not lazy loaded elsewhere)
# To be safe, we don't instantiate it at module level if we want pure lazy loading,
# but existing code expects 'camera_controller' to be an instance.
# We will leave it as an instance but ensure __init__ is safe.
camera_controller = get_camera_controller()
