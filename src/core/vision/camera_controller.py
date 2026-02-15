"""
Controlador de CÃ¢mera (Eyes)
ResponsÃ¡vel por detecÃ§Ã£o de presenÃ§a e reconhecimento facial
"""

import cv2
CV2_AVAILABLE = True

import threading
import time
import logging
import shutil
from typing import Optional, List, Dict, Any, Callable
from pathlib import Path
from datetime import datetime
import numpy as np
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
    logger.critical(f"❌ face-recognition REQUIRED but not available! Install: pip install face-recognition")
    logger.critical(f"Import error: {e}")
    FACE_REC_AVAILABLE = False
    face_recognition = None

class CameraController:
    """Controla a webcam e processa visÃ£o computacional"""

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
        
        # ðŸ†• FASE 1: FPS Adaptativo para economia de CPU
        self.active_fps = 30  # FPS quando hÃ¡ movimento/usuÃ¡rio
        self.idle_fps = 5     # FPS quando cenÃ¡rio estÃ¡tico
        self.motion_threshold = 5000  # Threshold de pixels diferentes para detectar movimento
        self.previous_frame = None
        
        # OtimizaÃ§Ã£o: Usar GPU se disponÃ­vel
        if hardware_manager.get_device() == "cuda":
             if self.face_detection_model == 'hog':
                 logger.info("GPU detectada. Ajustando FaceID para modo CNN para maior precisÃ£o.")
                 self.face_detection_model = 'cnn'
        else:
            if self.face_detection_model == 'cnn':
                logger.warning("Modelo CNN solicitado mas rodando em CPU. Isso serÃ¡ LENTO. Recomendo HOG para CPU.")
                self.face_detection_model = 'hog'
        
        # ðŸ†• MEDIAPIPE FACE DETECTION: DISABLED FOR STABILITY
        self.mp_face_detection = None
        self.face_detector = None
        # try:
        #     import mediapipe as mp
        #     self.mp_face_detection = mp.solutions.face_detection
        #     self.face_detector = self.mp_face_detection.FaceDetection(
        #         model_selection=0,
        #         min_detection_confidence=0.5
        #     )
        #     logger.info("âœ… MediaPipe Face Detection inicializado (EstÃ¡vel)")
        # except Exception as e:
        #     logger.warning(f"âš ï¸ Erro ao inicializar MediaPipe Face: {e}")
        
        # Callback para enviar vÃ­deo para GUI (se necessÃ¡rio)
        self.on_frame_ready: Optional[Callable[[Any], None]] = None
        
        # Carregar faces conhecidas em background
        threading.Thread(target=self._load_known_faces, daemon=True, name="CamFaceSync").start()

    def _load_known_faces(self):
        """Carrega faces da pasta de dados para reconhecimento"""
        if not FACE_REC_AVAILABLE or face_recognition is None:
            logger.warning("⚠️ Face recognition not available for loading known faces")
            return
            
        # Usar caminho absoluto centralizado
        faces_dir = config.DATA_DIR / 'faces'
        faces_dir.mkdir(parents=True, exist_ok=True)

        quarantine_dir = faces_dir / "quarantine"
        
        
        # Aceitar jpg, jpeg, png
        count = 0
        for file_path in list(faces_dir.glob("*.jpg")) + list(faces_dir.glob("*.png")) + list(faces_dir.glob("*.jpeg")):
            try:
                # O nome do arquivo Ã© o nome da pessoa (remove sufixo de Ã¢ngulo)
                raw_name = file_path.stem
                name = raw_name.split('_')[0]
                
                image = face_recognition.load_image_file(str(file_path))
                encodings = face_recognition.face_encodings(image)
                
                if encodings:
                    self.known_face_encodings.append(encodings[0])
                    self.known_face_names.append(name)
                    count += 1
                    logger.info(f"   ðŸ‘¤ FaceID: Carregada biometria de '{raw_name}'")
                else:
                    # TRATAMENTO: Mover para quarentena se nÃ£o houver face
                    logger.error(f"   âŒ FaceID: Rosto nÃ£o identificado em '{file_path.name}'. Isolando em quarentena.")
                    quarantine_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(file_path), str(quarantine_dir / file_path.name))
            except Exception as e:
                logger.error(f"   âŒ FaceID: Erro ao tratar {file_path.name}: {e}")
                
        if count == 0:
            logger.warning("   ðŸ”¶ Camera: Nenhum perfil facial ativo.")
        else:
            logger.info(f"âœ… Camera: {count} perfis biomÃ©tricos sincronizados.")

    def start_monitoring(self):
        """Inicia monitoramento em background"""
        if self.is_monitoring: return
        
        # ðŸ†• SAFE START: Load faces only when monitoring starts
        if not self.known_face_encodings:
             threading.Thread(target=self._load_known_faces, daemon=True, name="CamFaceSync").start()

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True, name="SentinelCameraThread")
        self.monitor_thread.start()
        logger.info("Monitoramento de visÃ£o iniciado.")

    def stop_monitoring(self):
        """Para monitoramento"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

    def _monitor_loop(self):
        """Loop principal de visÃ£o com FPS adaptativo"""        # 🔒 PERMISSÃO CHECK: Verificar acesso à câmera antes de tentar abrir
        try:
            import platform
            if platform.system() == "Windows":
                # No Windows, tentar uma abertura rápida para verificar permissões
                test_capture = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
                if test_capture and test_capture.isOpened():
                    test_capture.release()
                    logger.info("✅ Permissões de câmera verificadas")
                else:
                    logger.error("❌ Sem permissão para acessar a câmera. Verifique as configurações de privacidade.")
                    self.is_monitoring = False
                    return
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível verificar permissões da câmera: {e}")
                # ðŸ†• SAFE DELAY: Garantir que a GUI e outros sistemas estejam prontos
        time.sleep(2)
        
        video_capture = None
        try:
            # ðŸ†• DIRECTSHOW: Force DSHOW backend to avoid MSMF conflicts with PyQt6
            # ðŸ†• GLOBAL NEURAL LOCK: Prevent conflicts with model loading
            logger.info("ðŸ“¹ Opening camera with DirectShow backend...")
            
            # Tentar abrir a cÃ¢mera com retry
            for attempt in range(3):
                try:
                    with hardware_manager.neural_lock:
                        video_capture = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
                    if video_capture and video_capture.isOpened():
                        break
                except Exception as e:
                    logger.warning(f"Tentativa {attempt+1} de abrir cÃ¢mera falhou: {e}")
                    time.sleep(1)
            
            if not video_capture or not video_capture.isOpened():
                logger.error(f"NÃ£o foi possÃ­vel abrir a cÃ¢mera {self.camera_index} apÃ³s mÃºltiplas tentativas.")
                return
                
            logger.info("âœ… Camera opened successfully (FPS Adaptativo Ativo)")

            process_this_frame = True
            is_active_mode = True  # ComeÃ§a em modo ativo

            while self.is_monitoring:
                ret, frame = video_capture.read()
                if not ret or frame is None or frame.size == 0:
                    logger.warning("⚠️ Frame inválido ou corrompido da câmera, pulando...")
                    time.sleep(1)
                    continue

                # 🛡️ DATA VALIDATION: Verificar integridade do frame
                if len(frame.shape) != 3 or frame.shape[2] != 3:
                    logger.warning("⚠️ Frame com formato inválido, pulando...")
                    time.sleep(1)
                    continue

                self._current_frame_cache = frame.copy()

                # ðŸ†• FASE 1: DetecÃ§Ã£o de Movimento para FPS Adaptativo
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
                    logger.debug(f"Erro na detecÃ§Ã£o de movimento: {e}")
                    motion_detected = True  # Fallback: assume movimento

                # Determinar modo (Ativo vs Idle)
                idle_time = time.time() - self.last_seen_time if self.last_seen_time > 0 else 0
                should_be_active = motion_detected or idle_time < 10  # 10s de grace period
                
                # TransiÃ§Ã£o de modo com log
                if should_be_active and not is_active_mode:
                    logger.info("âš¡ Camera: Modo ATIVO (movimento detectado)")
                    is_active_mode = True
                elif not should_be_active and is_active_mode:
                    logger.info("ðŸ’¤ Camera: Modo IDLE (cenÃ¡rio estÃ¡tico)")
                    is_active_mode = False

                # Processar Face Recognition APENAS em modo ativo
                if is_active_mode and getattr(self, '_faceid_failures', 0) < 5:
                    if process_this_frame:
                        try:
                            if not FACE_REC_AVAILABLE or face_recognition is None:
                                pass  # Skip face recognition if not available
                            else:
                                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                                rgb_small_frame = small_frame[:, :, ::-1]
                                
                                 # Garantir que o frame seja contíguo e no formato correto para o dlib
                                r_frame = np.ascontiguousarray(rgb_small_frame)
                                
                                # Buscar faces com HOG
                                face_locations = face_recognition.face_locations(r_frame, model="hog")
                            
                                if face_locations:
                                    try:
                                        face_encodings = face_recognition.face_encodings(r_frame, face_locations)
                                        for face_encoding in face_encodings:
                                            match = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
                                            name = "Desconhecido"
                                            if True in match:
                                                name = self.known_face_names[match.index(True)]
                                            
                                            # Log e atualização
                                            if name != self.last_seen_user or (time.time() - self.last_seen_time > 60):
                                                logger.info(f"Usuário identificado: {name}")
                                                self.last_seen_user = name
                                                
                                                # 🔄 SYNC IDENTITY: Alternar Workspace e Role se for um usuário autorizado
                                                from src.core.management.context_manager import context_manager
                                                from src.core.management.user_manager import user_manager
                                                if name != "Desconhecido":
                                                    context_manager.switch_user(name)
                                                    user_manager.record_presence(name)

                                            self.last_seen_time = time.time()
                                        self._faceid_failures = 0
                                    except Exception as e:
                                        logger.debug(f"Erro no processamento de faces: {e}")
                                        self._faceid_failures = getattr(self, '_faceid_failures', 0) + 1
                        except Exception as e:
                            logger.debug(f"Erro FaceID: {e}")
                            self._faceid_failures = getattr(self, '_faceid_failures', 0) + 1
            
                # EmoÃ§Ã£o (apenas em modo ativo)
                if is_active_mode:
                    try:
                        emotion_data = emotion_detector.detect_emotion_from_frame(frame)
                        self.current_emotion = emotion_data['emotion']
                    except: pass


                    # ðŸ†• BRILHO ADAPTATIVO (Stark Context) - DESATIVADO POR SOLICITAÃ‡ÃƒO
                    # O Jarvis mantÃ©m o poder de controlar (via DeviceManager), mas nÃ£o faz isso sozinho.
                    # if getattr(self, '_brightness_counter', 0) % 100 == 0: # Check a cada ~3s
                    #     self._check_ambient_light(frame)
                    # self._brightness_counter = getattr(self, '_brightness_counter', 0) + 1

                process_this_frame = not process_this_frame
            
                # Processamento de Gestos (apenas em modo ativo)
                if is_active_mode:
                    try:
                        # Lazy load gesture controller
                        from src.core.vision.gesture_controller import get_gesture_controller
                        gesture_ctrl = get_gesture_controller()
                        
                        if gesture_ctrl:
                            # Retorna frame desenhado se MediaPipe ativo
                            processed_frame, gesture = gesture_ctrl.process_frame(frame)
                            
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

                # ðŸ†• FASE 1: FPS Adaptativo
                sleep_time = (1.0 / self.active_fps) if is_active_mode else (1.0 / self.idle_fps)
                time.sleep(sleep_time)

        except Exception as e:
            logger.error(f"âŒ Erro no loop de monitoramento: {e}")
        finally:
            if video_capture:
                video_capture.release()
                logger.info("ðŸ“¹ Camera released")

    def register_new_face(self, name: str) -> bool:
        """Tira fotos de mÃºltiplos Ã¢ngulos para mapear o usuÃ¡rio de forma inteligente"""
        try:
            if not FACE_REC_AVAILABLE or face_recognition is None:
                logger.error("❌ Face recognition not available for user registration!")
                return False
                
            from src.core.audio.voice_controller import voice_controller
            # ðŸ†• DIRECTSHOW
            video_capture = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            
            if not video_capture.isOpened():
                logger.error("NÃ£o foi possÃ­vel abrir a cÃ¢mera para cadastro.")
                return False

            logger.info(f"ðŸŽ­ Iniciando mapeamento facial dinÃ¢mico para: {name}")
            voice_controller.speak(f"Iniciando mapeamento facial para {name}. Por favor, fique de frente para a cÃ¢mera.")
            
            faces_dir = config.DATA_DIR / 'faces'
            faces_dir.mkdir(parents=True, exist_ok=True)
            
            angles = [
                {"msg": "Olhe diretamente para a cÃ¢mera.", "suffix": "front"},
                {"msg": "Agora, vire levemente a cabeÃ§a para a direita.", "suffix": "right"},
                {"msg": "Perfeito. Agora para a esquerda.", "suffix": "left"},
                {"msg": "Incline a cabeÃ§a um pouco para cima.", "suffix": "up"},
                {"msg": "E finalmente, um pouco para baixo.", "suffix": "down"}
            ]
            
            captured_count = 0
            for angle in angles:
                voice_controller.speak(angle["msg"])
                
                # Aguardar detecÃ§Ã£o de face antes de capturar
                face_found = False
                attempts = 0
                while not face_found and attempts < 30: # Max 30 frames (~3-5s)
                    ret, frame = video_capture.read()
                    if not ret: break
                    
                    # DetecÃ§Ã£o rÃ¡pida para confirmar presenÃ§a
                    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                    rgb_small = small_frame[:, :, ::-1]
                    locations = face_recognition.face_locations(rgb_small, model="hog")
                    
                    if locations:
                        face_found = True
                        save_path = faces_dir / f"{name}_{angle['suffix']}.jpg"
                        cv2.imwrite(str(save_path), frame)
                        logger.info(f"ðŸ“¸ Capturado Ã¢ngulo: {angle['suffix']}")
                        captured_count += 1
                        time.sleep(1) # Pausa para o usuÃ¡rio mudar a posiÃ§Ã£o
                    
                    attempts += 1
                    time.sleep(0.1)
                
                if not face_found:
                    voice_controller.speak("NÃ£o consegui detectar seu rosto. Vamos tentar o prÃ³ximo Ã¢ngulo.")

            video_capture.release()
            
            if captured_count > 0:
                voice_controller.speak(f"Mapeamento concluÃ­do com sucesso. JÃ¡ te reconheÃ§o agora, {name}.")
                # Hot-reload no controlador de cÃ¢mera
                self._load_known_faces()
                
                # Sincronizar com o Vision System (Singleton) se disponÃ­vel
                try:
                    from src.core.vision.vision_system import get_vision_system
                    vs = get_vision_system()
                    vs._load_known_faces()
                except: pass
                
                return True
            else:
                voice_controller.speak("Falha ao capturar biometria. Certifique-se de que hÃ¡ iluminaÃ§Ã£o suficiente.")
                return False
            
        except Exception as e:
            logger.error(f"Erro ao registrar nova face: {e}")
            return False

    def _check_ambient_light(self, frame):
        """Ajusta o brilho do Windows baseado na luz detectada pela cÃ¢mera"""
        try:
            from src.core.management.device_manager import device_manager
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            avg_brightness = cv2.mean(gray)[0]
            
            # Mapeamento 0-255 -> 0-100%
            target_brightness = int((avg_brightness / 255.0) * 100)
            target_brightness = max(10, min(100, target_brightness))
            
            current_br = getattr(self, '_last_brightness', -1)
            # SÃ³ muda se a diferenÃ§a for > 15% para evitar flickering
            if abs(target_brightness - current_br) > 15:
                device_manager.set_brightness(target_brightness)
                self._last_brightness = target_brightness
                logger.info(f"ðŸ’¡ Brilho adaptativo: Ambiente {avg_brightness:.1f} -> Tela {target_brightness}%")
        except Exception as e:
            logger.debug(f"Falha no brilho adaptativo: {e}")

    def _is_cnn_supported(self) -> bool:
        """Verifica se dlib foi compilado com suporte a CUDA para CNN"""
        try:
            import dlib
            return dlib.DLIB_USE_CUDA
        except Exception:
            return False

    # 🛡️ MÉTODOS DE SEGURANÇA (SENTINEL PROTOCOL)
    
    def detect_unauthorized_access(self) -> bool:
        """Retorna True se houver alguém não autorizado (Desconhecido) diante da câmera"""
        return self.last_seen_user == "Desconhecido" and (time.time() - self.last_seen_time < 5)

    def is_master_present(self) -> bool:
        """Retorna True se o Master (William) estiver diante da câmera"""
        # William é o master default, buscamos por ele no registro
        return self.last_seen_user == "William" and (time.time() - self.last_seen_time < 5)

    def is_master_alone(self) -> bool:
        """Verifica se William é a única pessoa visível"""
        # Simplificação: se o master está presente e o último visto foi ele, consideramos seguro.
        # Numa versão avançada, contaríamos faces no frame atual.
        return self.is_master_present()

    def capture_context(self) -> Dict[str, Any]:
        """Captura um snapshot leve de contexto para a observação adaptativa da IA"""
        context = {
            "timestamp": datetime.now().isoformat(),
            "last_user": self.last_seen_user,
            "current_emotion": self.current_emotion,
            "face_detected": (time.time() - self.last_seen_time < 5)
        }
        
        # Opcional: Snapshot se o sistema não estiver sobrecarregado
        from src.core.management.hardware_manager import hardware_manager
        if not hardware_manager.is_throttled:
            snapshot_path = config.PROJECT_ROOT / "data" / "status" / "cam_context.jpg"
            snapshot_path.parent.mkdir(parents=True, exist_ok=True)
            if self.save_snapshot(snapshot_path):
                context["image_path"] = str(snapshot_path)
                
        return context

    def save_snapshot(self, path: Path):
        """Salva o frame atual em um arquivo (Snap de Evidência)"""
        try:
             # Usar o último frame processado (precisaríamos expor o frame do loop ou abrir a câmera rapidamente)
             # Para evitar conflitos de travamento de hardware, tentamos capturar o frame atual se monitoramento estiver ativo
             if hasattr(self, '_current_frame_cache') and self._current_frame_cache is not None:
                 cv2.imwrite(str(path), self._current_frame_cache)
                 return True
             
             # Fallback: Abrir câmera rapidinho se não estiver monitorando
             cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
             ret, frame = cap.read()
             if ret:
                 cv2.imwrite(str(path), frame)
             cap.release()
             return ret
        except Exception as e:
            logger.error(f"Erro ao salvar snapshot: {e}")
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

# Global instance
camera_controller = get_camera_controller()
