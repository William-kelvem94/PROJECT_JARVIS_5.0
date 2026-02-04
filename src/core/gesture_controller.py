"""
Controlador de Gestos (Hands)
Utiliza MediaPipe para rastreamento de mãos e reconhecimento de gestos.
"""

import cv2
import logging
import threading
import time
import math
from typing import Optional, List, Dict, Tuple, Any
from collections import deque
import numpy as np
from src.utils.config import config
from src.core.action_controller import action_controller

logger = logging.getLogger(__name__)

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    logger.warning("MediaPipe não encontrado. Controle por gestos desativado.")

class GestureController:
    """Detecta gestos e comanda ações"""

    def __init__(self):
        global MEDIAPIPE_AVAILABLE
        self.is_running = False
        self.last_gesture = "None"
        self.last_gesture_time = 0
        self.gesture_cooldown = 1.0 # Segundos entre ações

        if MEDIAPIPE_AVAILABLE:
            try:
                self.mp_hands = mp.solutions.hands
                self.hands = self.mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=1,
                    min_detection_confidence=0.7,
                    min_tracking_confidence=0.5
                )
                self.mp_draw = mp.solutions.drawing_utils
            except AttributeError as e:
                logger.error(f"Erro ao inicializar MediaPipe (Atributo não encontrado): {e}")
                MEDIAPIPE_AVAILABLE = False
                self.mp_hands = None
                self.hands = None
            except Exception as e:
                logger.error(f"Erro desconhecido no MediaPipe: {e}")
                MEDIAPIPE_AVAILABLE = False
        
        # Suavização de gestos
        self.gesture_buffer = deque(maxlen=5)
        self.smoothing_threshold = 3

    def process_frame(self, frame) -> Tuple[Any, str]:
        """
        Processa um frame e retorna o frame desenhado + gesto detectado
        Retorna: (frame_processado, nome_gesto)
        """
        if not MEDIAPIPE_AVAILABLE:
            return frame, "MediaPipe Missing"

        # Converter BGR para RGB
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        
        gesture_name = "None"

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Desenhar esqueleto
                self.mp_draw.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                # Reconhecer gesto
                raw_gesture = self._classify_gesture(hand_landmarks)
                self.gesture_buffer.append(raw_gesture)
                
                # Aplicar suavização (votação majoritária)
                gesture_name = self._get_smoothed_gesture()
                
                # Executar ação
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
        if gesture == "Thumbs Up":
            # Confirmar / Enter
            action_controller.press_key('enter')
        elif gesture == "Open Palm":
            # Parar / Pause Media
            action_controller.press_key('playpause') 
        elif gesture == "Fist":
            # Scroll Down (Exemplo)
            # action_controller.scroll(-10) # Implementar scroll depois
            pass

# Instância global
gesture_controller = GestureController()
