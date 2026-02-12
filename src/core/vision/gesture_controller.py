"""
Controlador de Gestos (Hands)
Utiliza MediaPipe para rastreamento de mãos e reconhecimento de gestos.
"""

import os
import logging
import threading
import time
import math
from typing import Optional, List, Dict, Tuple, Any
from collections import deque

try:
    import cv2
    CV2_AVAILABLE = True
except (ImportError, OSError) as e:
    CV2_AVAILABLE = False
    cv2 = None
    logging.warning(f"⚠️ cv2 not available in gesture_controller: {e}")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except (ImportError, OSError) as e:
    NUMPY_AVAILABLE = False
    np = None
    logging.warning(f"⚠️ numpy not available in gesture_controller: {e}")

from src.utils.config import config
from src.core.actions.action_controller import action_controller

logger = logging.getLogger(__name__)

try:
    # Silenciar logs internos do MediaPipe/GLOG/ABS
    os.environ['GLOG_minloglevel'] = '3'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    import absl.logging
    absl.logging.set_verbosity(absl.logging.ERROR)
    
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except (ImportError, OSError) as e:
    MEDIAPIPE_AVAILABLE = False
    logger.debug(f"MediaPipe não encontrado. Controle por gestos desativado.")

class GestureController:
    """Detecta gestos e comanda ações"""

    def __init__(self):
        global MEDIAPIPE_AVAILABLE
        self.is_running = False
        
        # Singularity Edition: Registro de Gestos Dinâmico
        self.gesture_registry = {
            "Open Palm": {"action": "playpause", "desc": "Play/Pause Media"},
            "Thumbs Up": {"action": "enter", "desc": "Confirmar"},
            "Fist": {"action": None, "desc": "Sem ação"},
            "Pinch": {"action": "volume", "desc": "Controle de Volume"}
        }

        self.last_gesture = "None"
        self.last_gesture_time = 0
        self.gesture_cooldown = 1.0 
        self.mp_hands = None
        self.hands = None
        self.mp_draw = None
        
        # Buffers
        from collections import deque
        self.gesture_buffer = deque(maxlen=5)
        self.pos_history = deque(maxlen=20)

        if MEDIAPIPE_AVAILABLE:
            try:
                # Tentativa 1: Import padrão (Legacy Solutions)
                if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'hands'):
                    logger.info("Usando MediaPipe Legacy Solutions.")
                    self.mp_hands = mp.solutions.hands
                    self.mp_draw = mp.solutions.drawing_utils
                    self.hands = self.mp_hands.Hands(
                        static_image_mode=False,
                        max_num_hands=1,
                        min_detection_confidence=0.7,
                        min_tracking_confidence=0.5
                    )
                
                # Tentativa 2: MediaPipe Tasks (Modern API)
                else:
                    logger.info("Legacy Solutions indisponível. Tentando MediaPipe Tasks (Modern API)...")
                    from mediapipe.tasks import python
                    from mediapipe.tasks.python import vision
                    
                    # Carregar modelo (precisa baixar o arquivo .task se não existir)
                    model_path = config.get_setting('sensory.hand_landmarker_path', 'models/vision/hand_landmarker.task')
                    
                    if not os.path.exists(model_path):
                         logger.warning(f"Modelo Task não encontrado em {model_path}. Tentando baixar/localizar...")
                         # Link para download: https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
                         # Como não podemos baixar facilmente agora, marcamos como indisponível se falhar
                    
                    base_options = python.BaseOptions(model_asset_path=model_path)
                    options = vision.HandLandmarkerOptions(
                        base_options=base_options,
                        num_hands=1,
                        min_hand_detection_confidence=0.7,
                        min_hand_presence_confidence=0.7,
                        min_tracking_confidence=0.5
                    )
                    self.landmarker = vision.HandLandmarker.create_from_options(options)
                    self.use_tasks_api = True
                    logger.info("MediaPipe Tasks (Landmarker) carregado com SUCESSO.")

            except Exception as e:
                logger.error(f"FALHA CRÍTICA ao carregar MediaPipe: {e}")
                logger.warning("O controle por gestos será DESATIVADO.")
                MEDIAPIPE_AVAILABLE = False
                self.mp_hands = None
                self.hands = None
        
        # Suavização e Tracking
        self.gesture_buffer = deque(maxlen=5)
        self.pos_history = deque(maxlen=10) # Para detectar Swipe
        self.last_pinch_dist = 0
        self.smoothing_threshold = 3

    def process_frame(self, frame) -> Tuple[Any, str]:
        """
        Processa um frame e retorna o frame desenhado + gesto detectado
        Retorna: (frame_processado, nome_gesto)
        """
        if not MEDIAPIPE_AVAILABLE or self.hands is None:
            return frame, "None"

        # Converter BGR para RGB
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        
        gesture_name = "None"

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Desenhar esqueleto
                self.mp_draw.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                # Track position for Swipe
                self.pos_history.append((hand_landmarks.landmark[9].x, hand_landmarks.landmark[9].y))
                
                # Reconhecer gesto
                raw_gesture = self._classify_gesture(hand_landmarks)
                self.gesture_buffer.append(raw_gesture)
                
                # Aplicar suavização
                gesture_name = self._get_smoothed_gesture()
                
                # AÇÕES ESPECIAIS (Contínuas ou Tracking)
                # 1. Pinch (Volume)
                if raw_gesture == "Pinch":
                    self._handle_pinch_volume(hand_landmarks)
                
                # 2. Swipe (Alt+Tab / Next)
                swipe_detected = self._detect_swipe()
                if swipe_detected:
                    self._execute_swipe_action(swipe_detected)
                    gesture_name = f"Swipe {swipe_detected}"
                
                # Ações discretas (Cooldown)
                self._execute_gesture_action(gesture_name)

        return frame, gesture_name

    def _classify_gesture(self, landmarks) -> str:
        """Classifica o gesto baseado nos pontos da mão"""
        # Extrair coordenadas Y dos dedos (Top vs Bottom)
        # Pontos: 4 (Dedão), 8 (Indicador), 12 (Médio), 16 (Anelar), 20 (Mínimo)
        
        points = landmarks.landmark
        
        # Lógica simples de dedos levantados
        fingers = []
        
        # Dedão (Lógica horizontal/vertical depende da mão, simplificando)
        # Se a ponta do dedão (4) está à esquerda/direita da base (2)
        if points[4].x < points[3].x: # Mão direita vista da camera
            fingers.append(1)
        else:
            fingers.append(0)

        # Outros 4 dedos (Se a ponta está acima da junta)
        # Lembre-se: Y cresce para baixo na imagem (0 = topo)
        for tip_id in [8, 12, 16, 20]:
            if points[tip_id].y < points[tip_id - 2].y:
                fingers.append(1)
            else:
                fingers.append(0)
        
        # Classificação básica
        total_fingers = fingers.count(1)
        
        # Detecção de PINCH (Ponta do dedão 4 e indicador 8)
        dist = math.sqrt((points[4].x - points[8].x)**2 + (points[4].y - points[8].y)**2)
        if dist < 0.05: # Threshold para pinça
            return "Pinch"
            
        if total_fingers == 5:
            return "Open Palm"
        elif total_fingers == 0:
            return "Fist"
        elif fingers[1] == 1 and total_fingers == 1:
            return "Pointing Up"
        elif fingers[0] == 1 and total_fingers == 1:
             return "Thumbs Up"
        elif fingers[1] == 1 and fingers[2] == 1 and total_fingers == 2:
            return "Victory"
        elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and total_fingers == 3:
            return "OK" # Na verdade 3 dedos levantados, mas pode ser mapeado
            
        return "Unknown"

    def _get_smoothed_gesture(self) -> str:
        """Retorna o gesto mais frequente no buffer para evitar oscilações"""
        if not self.gesture_buffer:
            return "None"
        
        counts = {}
        for g in self.gesture_buffer:
            counts[g] = counts.get(g, 0) + 1
            
        most_frequent = max(counts, key=counts.get)
        
        if counts[most_frequent] >= self.smoothing_threshold:
            return most_frequent
        
        return self.last_gesture if self.last_gesture != "Unknown" else "None"

    def _execute_gesture_action(self, gesture: str):
        """Executa ação vinculada ao gesto"""
        if gesture == "None" or gesture == "Unknown":
            return
            
        # Cooldown
        if time.time() - self.last_gesture_time < self.gesture_cooldown:
            return

        if gesture == self.last_gesture:
            # Evitar disparar muitas vezes se segurar o gesto
            # Mas permitir se passar cooldown
            pass
        
        logger.info(f"Gesto detectado e acionado: {gesture}")
        self.last_gesture = gesture
        self.last_gesture_time = time.time()
        
        # Mapeamento de Ações
        if gesture == "Open Palm":
            # Play / Pause Media
            action_controller.press_key('playpause')
            logger.info("⏯️ Gesto: Play/Pause")

    def _handle_pinch_volume(self, landmarks):
        """Controla volume baseado na distância lateral/vertical entre dedos ou movimento"""
        # Simplificação: Usar a altura da mão para aumentar/diminuir volume enquanto pinça
        p4 = landmarks.landmark[4]
        p8 = landmarks.landmark[8]
        
        # Center of pinch
        curr_y = (p4.y + p8.y) / 2
        
        if hasattr(self, '_last_pinch_y'):
            diff = self._last_pinch_y - curr_y # Y diminui p/ cima
            if abs(diff) > 0.05:
                if diff > 0:
                    action_controller.press_key('volumeup')
                else:
                    action_controller.press_key('volumedown')
                self._last_pinch_y = curr_y
        else:
            self._last_pinch_y = curr_y

    def _detect_swipe(self) -> Optional[str]:
        """Detecta movimento lateral rápido"""
        if len(self.pos_history) < 5: return None
        
        first_x = self.pos_history[0][0]
        last_x = self.pos_history[-1][0]
        
        diff = last_x - first_x
        if abs(diff) > 0.3: # Threshold de swipe
            self.pos_history.clear() # Evitar disparo duplo
            return "Right" if diff > 0 else "Left"
        return None

    def _execute_swipe_action(self, direction: str):
        """Executa ação de Swipe"""
        if direction == "Right":
            action_controller.hotkey('alt', 'tab')
            logger.info("📑 Swipe Right: Alt+Tab")
        else:
            action_controller.press_key('nexttrack')
            logger.info("⏭️ Swipe Left: Next Track")

# Instância global removida para evitar execução durante import
# gesture_controller = GestureController()
