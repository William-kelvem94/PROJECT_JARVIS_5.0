"""
Controlador de Câmera (Eyes)
Responsável por detecção de presença e reconhecimento facial
"""

import cv2
CV2_AVAILABLE = True

import threading
import time
import logging
import shutil
from typing import Optional, List, Dict
from pathlib import Path
from datetime import datetime
from src.utils.config import config
from src.core.vision.gesture_controller import gesture_controller
from src.core.intelligence.emotion_detector import emotion_detector
from src.core.management.hardware_manager import hardware_manager

logger = logging.getLogger(__name__)

# Face recognition is now mandatory
import face_recognition
FACE_REC_AVAILABLE = True

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
        
        # 🆕 FASE 1: FPS Adaptativo para economia de CPU
        self.active_fps = 30  # FPS quando há movimento/usuário
        self.idle_fps = 5     # FPS quando cenário estático
        self.motion_threshold = 5000  # Threshold de pixels diferentes para detectar movimento
        self.previous_frame = None
        
        # Otimização: Usar GPU se disponível
        if hardware_manager.get_device() == "cuda":
             if self.face_detection_model == 'hog':
                 logger.info("GPU detectada. Ajustando FaceID para modo CNN para maior precisão.")
                 self.face_detection_model = 'cnn'
        else:
            if self.face_detection_model == 'cnn':
                logger.warning("Modelo CNN solicitado mas rodando em CPU. Isso será LENTO. Recomendo HOG para CPU.")
                self.face_detection_model = 'hog'
        
        # 🆕 MEDIAPIPE FACE DETECTION: DISABLED FOR STABILITY
        self.mp_face_detection = None
        self.face_detector = None
        # try:
        #     import mediapipe as mp
        #     self.mp_face_detection = mp.solutions.face_detection
        #     self.face_detector = self.mp_face_detection.FaceDetection(
        #         model_selection=0,
        #         min_detection_confidence=0.5
        #     )
        #     logger.info("✅ MediaPipe Face Detection inicializado (Estável)")
        # except Exception as e:
        #     logger.warning(f"⚠️ Erro ao inicializar MediaPipe Face: {e}")
        
        # Callback para enviar vídeo para GUI (se necessário)
        self.on_frame_ready: Optional[Callable[[Any], None]] = None
        
        # Carregar faces conhecidas em background
        threading.Thread(target=self._load_known_faces, daemon=True, name="CamFaceSync").start()

    def _load_known_faces(self):
        """Carrega faces da pasta de dados para reconhecimento"""
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
                
        if count == 0:
            logger.warning("   🔶 Camera: Nenhum perfil facial ativo.")
        else:
            logger.info(f"✅ Camera: {count} perfis biométricos sincronizados.")

    def start_monitoring(self):
        """Inicia monitoramento em background"""
        if self.is_monitoring: return
        
        # 🆕 SAFE START: Load faces only when monitoring starts
        if not self.known_face_encodings:
             threading.Thread(target=self._load_known_faces, daemon=True, name="CamFaceSync").start()

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Monitoramento de visão iniciado.")

    def stop_monitoring(self):
        """Para monitoramento"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

    def _monitor_loop(self):
        """Loop principal de visão com FPS adaptativo"""
        # 🆕 SAFE DELAY: Garantir que a GUI e outros sistemas estejam prontos
        time.sleep(2)
        
        video_capture = None
        try:
            # 🆕 DIRECTSHOW: Force DSHOW backend to avoid MSMF conflicts with PyQt6
            # 🆕 GLOBAL NEURAL LOCK: Prevent conflicts with model loading
            logger.info("📹 Opening camera with DirectShow backend...")
            
            # Tentar abrir a câmera com retry
            for attempt in range(3):
                try:
                    with hardware_manager.neural_lock:
                        video_capture = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
                    if video_capture and video_capture.isOpened():
                        break
                except Exception as e:
                    logger.warning(f"Tentativa {attempt+1} de abrir câmera falhou: {e}")
                    time.sleep(1)
            
            if not video_capture or not video_capture.isOpened():
                logger.error(f"Não foi possível abrir a câmera {self.camera_index} após múltiplas tentativas.")
                return
                
            logger.info("✅ Camera opened successfully (FPS Adaptativo Ativo)")

            process_this_frame = True
            is_active_mode = True  # Começa em modo ativo

            while self.is_monitoring:
                ret, frame = video_capture.read()
                if not ret:
                    time.sleep(1)
                    continue

                # 🆕 FASE 1: Detecção de Movimento para FPS Adaptativo
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
                except Exception as e:
                    logger.debug(f"Erro na detecção de movimento: {e}")
                    motion_detected = True  # Fallback: assume movimento

                # Determinar modo (Ativo vs Idle)
                idle_time = time.time() - self.last_seen_time if self.last_seen_time > 0 else 0
                should_be_active = motion_detected or idle_time < 10  # 10s de grace period
                
                # Transição de modo com log
                if should_be_active and not is_active_mode:
                    logger.info("⚡ Camera: Modo ATIVO (movimento detectado)")
                    is_active_mode = True
                elif not should_be_active and is_active_mode:
                    logger.info("💤 Camera: Modo IDLE (cenário estático)")
                    is_active_mode = False

                # Processar Face Recognition APENAS em modo ativo
                if is_active_mode and getattr(self, '_faceid_failures', 0) < 5:
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
            
                # Emoção (apenas em modo ativo)
                if is_active_mode:
                    try:
                        emotion_data = emotion_detector.detect_emotion_from_frame(frame)
                        self.current_emotion = emotion_data['emotion']
                    except: pass


                    # 🆕 BRILHO ADAPTATIVO (Stark Context) - DESATIVADO POR SOLICITAÇÃO
                    # O Jarvis mantém o poder de controlar (via DeviceManager), mas não faz isso sozinho.
                    # if getattr(self, '_brightness_counter', 0) % 100 == 0: # Check a cada ~3s
                    #     self._check_ambient_light(frame)
                    # self._brightness_counter = getattr(self, '_brightness_counter', 0) + 1

                process_this_frame = not process_this_frame
            
                # Processamento de Gestos (apenas em modo ativo)
                if is_active_mode:
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

                # 🆕 FASE 1: FPS Adaptativo
                sleep_time = (1.0 / self.active_fps) if is_active_mode else (1.0 / self.idle_fps)
                time.sleep(sleep_time)

        except Exception as e:
            logger.error(f"❌ Erro no loop de monitoramento: {e}")
        finally:
            if video_capture:
                video_capture.release()
                logger.info("📹 Camera released")

    def register_new_face(self, name: str) -> bool:
        """Tira fotos de múltiplos ângulos para mapear o usuário de forma inteligente"""
        try:
            from src.core.audio.voice_controller import voice_controller
            # 🆕 DIRECTSHOW
            video_capture = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            
            if not video_capture.isOpened():
                logger.error("Não foi possível abrir a câmera para cadastro.")
                return False

            logger.info(f"🎭 Iniciando mapeamento facial dinâmico para: {name}")
            voice_controller.speak(f"Iniciando mapeamento facial para {name}. Por favor, fique de frente para a câmera.")
            
            faces_dir = config.DATA_DIR / 'faces'
            faces_dir.mkdir(parents=True, exist_ok=True)
            
            angles = [
                {"msg": "Olhe diretamente para a câmera.", "suffix": "front"},
                {"msg": "Agora, vire levemente a cabeça para a direita.", "suffix": "right"},
                {"msg": "Perfeito. Agora para a esquerda.", "suffix": "left"},
                {"msg": "Incline a cabeça um pouco para cima.", "suffix": "up"},
                {"msg": "E finalmente, um pouco para baixo.", "suffix": "down"}
            ]
            
            captured_count = 0
            for angle in angles:
                voice_controller.speak(angle["msg"])
                
                # Aguardar detecção de face antes de capturar
                face_found = False
                attempts = 0
                while not face_found and attempts < 30: # Max 30 frames (~3-5s)
                    ret, frame = video_capture.read()
                    if not ret: break
                    
                    # Detecção rápida para confirmar presença
                    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                    rgb_small = small_frame[:, :, ::-1]
                    locations = face_recognition.face_locations(rgb_small, model="hog")
                    
                    if locations:
                        face_found = True
                        save_path = faces_dir / f"{name}_{angle['suffix']}.jpg"
                        cv2.imwrite(str(save_path), frame)
                        logger.info(f"📸 Capturado ângulo: {angle['suffix']}")
                        captured_count += 1
                        time.sleep(1) # Pausa para o usuário mudar a posição
                    
                    attempts += 1
                    time.sleep(0.1)
                
                if not face_found:
                    voice_controller.speak("Não consegui detectar seu rosto. Vamos tentar o próximo ângulo.")

            video_capture.release()
            
            if captured_count > 0:
                voice_controller.speak(f"Mapeamento concluído com sucesso. Já te reconheço agora, {name}.")
                # Hot-reload no controlador de câmera
                self._load_known_faces()
                
                # Sincronizar com o Vision System (Singleton) se disponível
                try:
                    from src.core.vision.vision_system import get_vision_system
                    vs = get_vision_system()
                    vs._load_known_faces()
                except: pass
                
                return True
            else:
                voice_controller.speak("Falha ao capturar biometria. Certifique-se de que há iluminação suficiente.")
                return False
            
        except Exception as e:
            logger.error(f"Erro ao registrar nova face: {e}")
            return False

    def _check_ambient_light(self, frame):
        """Ajusta o brilho do Windows baseado na luz detectada pela câmera"""
        try:
            from src.core.management.device_manager import device_manager
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            avg_brightness = cv2.mean(gray)[0]
            
            # Mapeamento 0-255 -> 0-100%
            target_brightness = int((avg_brightness / 255.0) * 100)
            target_brightness = max(10, min(100, target_brightness))
            
            current_br = getattr(self, '_last_brightness', -1)
            # Só muda se a diferença for > 15% para evitar flickering
            if abs(target_brightness - current_br) > 15:
                device_manager.set_brightness(target_brightness)
                self._last_brightness = target_brightness
                logger.info(f"💡 Brilho adaptativo: Ambiente {avg_brightness:.1f} -> Tela {target_brightness}%")
        except Exception as e:
            logger.debug(f"Falha no brilho adaptativo: {e}")

    def _is_cnn_supported(self) -> bool:
        """Verifica se dlib foi compilado com suporte a CUDA para CNN"""
        try:
            import dlib
            return dlib.DLIB_USE_CUDA
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

# Global instance removida para evitar execução durante import
# camera_controller = get_camera_controller()
