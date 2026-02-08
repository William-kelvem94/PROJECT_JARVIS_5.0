"""
Controlador de Câmera (Eyes)
Responsável por detecção de presença e reconhecimento facial
"""

try:
    import cv2
    CV2_AVAILABLE = True
except (ImportError, OSError) as e:
    CV2_AVAILABLE = False
    cv2 = None
    import logging
    logging.warning(f"⚠️ cv2 not available in camera_controller: {e}")

import threading
import time
import logging
from typing import Optional, List, Dict
from pathlib import Path
from datetime import datetime
from src.utils.config import config
from src.core.vision.gesture_controller import gesture_controller
from src.core.intelligence.emotion_detector import emotion_detector
from src.core.management.hardware_manager import hardware_manager

logger = logging.getLogger(__name__)

try:
    import face_recognition
    FACE_REC_AVAILABLE = True
except ImportError:
    FACE_REC_AVAILABLE = False
    logger.warning("Biblioteca face_recognition não encontrada. Funcionalidades de FaceID desativadas.")

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
        self.face_detection_model = config.get_setting('sensory.face_detection_model', 'hog')
        
        # Estado emocional
        self.current_emotion = "neutral"
        self.emotion_history = []
        
        # Otimização: Usar GPU se disponível
        if hardware_manager.get_device() == "cuda":
             if self.face_detection_model == 'hog':
                 logger.info("GPU detectada. Ajustando FaceID para modo CNN para maior precisão.")
                 self.face_detection_model = 'cnn'
        else:
            if self.face_detection_model == 'cnn':
                logger.warning("Modelo CNN solicitado mas rodando em CPU. Isso será LENTO. Recomendo HOG para CPU.")
                self.face_detection_model = 'hog'
        
        # Fallback mechanism: Load Haar Cascade
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        except Exception as e:
            logger.warning(f"Erro ao carregar Haar Cascade: {e}")
            self.face_cascade = None
        
        # Callback para enviar vídeo para GUI (se necessário)
        self.on_frame_ready: Optional[Callable[[Any], None]] = None
        
        # Carregar faces conhecidas
        self._load_known_faces()

    def _load_known_faces(self):
        """Carrega faces da pasta de dados para reconhecimento"""
        if not FACE_REC_AVAILABLE: return

        faces_dir = Path(config.get_setting('app.data_dir', 'data')) / 'faces'
        faces_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Carregando faces de {faces_dir}...")
        
        for file_path in faces_dir.glob("*.[jp][pn]g"):
            try:
                # O nome do arquivo é o nome da pessoa
                name = file_path.stem
                image = face_recognition.load_image_file(str(file_path))
                encodings = face_recognition.face_encodings(image)
                
                if encodings:
                    self.known_face_encodings.append(encodings[0])
                    self.known_face_names.append(name)
                    logger.info(f"Face carregada: {name}")
            except Exception as e:
                logger.error(f"Erro ao carregar face {file_path}: {e}")

    def start_monitoring(self):
        """Inicia monitoramento em background"""
        if self.is_monitoring: return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Monitoramento de visão iniciado.")

    def stop_monitoring(self):
        """Para monitoramento"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

        # 🆕 MEDIAPIPE FACE DETECTION (Stable Fallback)
        self.mp_face_detection = None
        self.face_detector = None
        if MEDIAPIPE_AVAILABLE:
            try:
                import mediapipe as mp
                self.mp_face_detection = mp.solutions.face_detection
                self.face_detector = self.mp_face_detection.FaceDetection(
                    model_selection=0, # 0 for short range (2m), 1 for long range (5m)
                    min_detection_confidence=0.5
                )
                logger.info("✅ MediaPipe Face Detection inicializado (Estável)")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao inicializar MediaPipe Face: {e}")

    def _monitor_loop(self):
        """Loop principal de visão"""
        video_capture = cv2.VideoCapture(self.camera_index)
        
        if not video_capture.isOpened():
            logger.error(f"Não foi possível abrir a câmera {self.camera_index}")
            return

        process_this_frame = True

        while self.is_monitoring:
            ret, frame = video_capture.read()
            if not ret:
                time.sleep(1)
                continue

            # Prioridade 1: MediaPipe (Estabilidade)
            human_detected = False
            if self.face_detector:
                results_mp = self.face_detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                if results_mp.detections:
                    human_detected = True
                    for detection in results_mp.detections:
                        # Desenhar detecção MediaPipe
                        bbox = detection.location_data.relative_bounding_box
                        h, w, c = frame.shape
                        x, y, bw, bh = int(bbox.xmin * w), int(bbox.ymin * h), int(bbox.width * w), int(bbox.height * h)
                        cv2.rectangle(frame, (x, y), (x + bw, y + bh), (0, 255, 0), 2)
                        cv2.putText(frame, "HUMAN", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # Prioridade 2: Face Recognition (Identidade) - Apenas se não houver falhas consecutivas
            if FACE_REC_AVAILABLE and getattr(self, '_faceid_failures', 0) < 5:
                if process_this_frame:
                    try:
                        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                        rgb_small_frame = small_frame[:, :, ::-1]
                        
                        # Buscar faces com HOG
                        face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
                        
                        if face_locations:
                            try:
                                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                                for face_encoding in face_encodings:
                                    match = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
                                    name = "Desconhecido"
                                    if True in match:
                                        name = self.known_face_names[match.index(True)]
                                    
                                    # Log e atualização
                                    if name != self.last_seen_user or (time.time() - self.last_seen_time > 60):
                                        logger.info(f"Usuário identificado: {name}")
                                        self.last_seen_user = name
                                    self.last_seen_time = time.time()
                                self._faceid_failures = 0
                            except Exception:
                                self._faceid_failures = getattr(self, '_faceid_failures', 0) + 1
                    except Exception as e:
                        logger.debug(f"Erro FaceID: {e}")
            
            # Fallback se identificação falhar mas human_detected for true
            if human_detected and (not self.last_seen_user or time.time() - self.last_seen_time > 60):
                if not self.last_seen_user or self.last_seen_user == "Desconhecido":
                    self.last_seen_user = "Human"
                    self.last_seen_time = time.time()
                    logger.info("Presença humana detectada (Estável via MediaPipe)")

            # Emoção e Gestos
            if human_detected:
                try:
                    emotion_data = emotion_detector.detect_emotion_from_frame(frame)
                    self.current_emotion = emotion_data['emotion']
                except: pass

            process_this_frame = not process_this_frame
            
            # Processamento de Gestos (Todo frame ou intercalado)
            try:
                # Safe check for gesture controller
                if gesture_controller:
                    # Retorna frame desenhado se MediaPipe ativo
                    processed_frame, gesture = gesture_controller.process_frame(frame)
                    
                    if self.on_frame_ready:
                        # Enviar para UI (converter BGR para RGB para tkinter)
                        try:
                            rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                            self.on_frame_ready(rgb_frame)
                        except Exception:
                            pass

                    if gesture != "None":
                        logger.debug(f"Gesto: {gesture}")
            except Exception as e:
                # Silently ignore gesture errors to prevent log flooding
                pass

            process_this_frame = not process_this_frame
            time.sleep(0.03) # Mais fluido

        video_capture.release()

    def register_new_face(self, name: str) -> bool:
        """Tira uma foto agora e aprende como sendo 'name'"""
        if not FACE_REC_AVAILABLE: return False
        
        try:
            video_capture = cv2.VideoCapture(self.camera_index)
            ret, frame = video_capture.read()
            video_capture.release()
            
            if not ret: return False

            # Salvar imagem
            faces_dir = Path(config.get_setting('app.data_dir', 'data')) / 'faces'
            faces_dir.mkdir(parents=True, exist_ok=True)
            
            save_path = faces_dir / f"{name}.jpg"
            cv2.imwrite(str(save_path), frame)
            
            # Recarregar faces
            self._load_known_faces()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao registrar nova face: {e}")
            return False

    def _is_cnn_supported(self) -> bool:
        """Verifica se dlib foi compilado com suporte a CUDA para CNN"""
        try:
            import dlib
            return dlib.DLIB_USE_CUDA
        except Exception:
            return False

# Instância global
camera_controller = CameraController()
