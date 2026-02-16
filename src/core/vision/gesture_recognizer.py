"""
Gesture Recognition System - Reconhecimento de Gestos com MediaPipe
Permite controle hands-free do JARVIS
"""

import logging
from typing import Dict, Optional, Callable
from enum import Enum

try:
    import cv2

    CV2_AVAILABLE = True
except (ImportError, OSError) as e:
    CV2_AVAILABLE = False
    cv2 = None
    logging.warning(f"âš ï¸ cv2 not available in gesture_recognizer: {e}")

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except (ImportError, OSError) as e:
    NUMPY_AVAILABLE = False
    np = None
    logging.warning(f"âš ï¸ numpy not available in gesture_recognizer: {e}")

# Lazy import mediapipe to avoid startup issues
MEDIAPIPE_AVAILABLE = False
mp = None


def _ensure_mediapipe():
    global MEDIAPIPE_AVAILABLE, mp
    if not MEDIAPIPE_AVAILABLE and mp is None:
        try:
            import mediapipe as mp

            MEDIAPIPE_AVAILABLE = True
        except (ImportError, OSError) as e:
            MEDIAPIPE_AVAILABLE = False
            mp = None
            logger.debug(
                f"MediaPipe nÃ£o encontrado. Reconhecimento de gestos desativado: {e}"
            )


try:
    # Just check if mediapipe can be imported without actually importing it
    import importlib

    mediapipe_spec = importlib.util.find_spec("mediapipe")
    if mediapipe_spec is not None:
        MEDIAPIPE_AVAILABLE = True
    else:
        MEDIAPIPE_AVAILABLE = False
except:
    MEDIAPIPE_AVAILABLE = False


class GestureType(Enum):
    """Tipos de gestos reconhecidos"""

    NONE = "none"
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    PEACE = "peace"
    OK = "ok"
    POINTING = "pointing"
    OPEN_PALM = "open_palm"
    FIST = "fist"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"


class GestureRecognizer:
    """Sistema de reconhecimento de gestos"""

    def __init__(self):
        self.mediapipe_available = False
        self.hands = None
        self.mp_hands = None
        self.mp_drawing = None

        self.gesture_callbacks: Dict[GestureType, Callable] = {}
        self.last_gesture = GestureType.NONE
        self.gesture_history = []

        self._init_mediapipe()

    def _init_mediapipe(self):
        """Inicializa MediaPipe Hands"""
        try:
            _ensure_mediapipe()
            if not MEDIAPIPE_AVAILABLE or mp is None:
                logger.warning("MediaPipe failed to load")
                return

            self.mp_hands = mp.solutions.hands
            self.mp_drawing = mp.solutions.drawing_utils

            # Configurar detector de mÃ£os
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5,
            )

            self.mediapipe_available = True
            logger.info("âœ… MediaPipe Hands inicializado")

        except ImportError:
            logger.warning(
                "âš ï¸ MediaPipe nÃ£o disponÃ­vel. Instale: pip install mediapipe"
            )
        except Exception as e:
            logger.warning(f"âš ï¸ Erro ao inicializar MediaPipe: {e}")

    def detect_gesture(self, frame) -> Optional[GestureType]:
        """
        Detecta gesto em um frame

        Args:
            frame: Frame de vÃ­deo (BGR)

        Returns:
            Tipo de gesto detectado ou None
        """
        if not self.mediapipe_available:
            return None

        try:
            # Converter BGR para RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Processar frame
            results = self.hands.process(rgb_frame)

            if not results.multi_hand_landmarks:
                return GestureType.NONE

            # Analisar primeira mÃ£o detectada
            hand_landmarks = results.multi_hand_landmarks[0]

            # Classificar gesto baseado em landmarks
            gesture = self._classify_gesture(hand_landmarks)

            # Atualizar histÃ³rico
            if gesture != self.last_gesture:
                self.gesture_history.append(gesture)
                if len(self.gesture_history) > 10:
                    self.gesture_history.pop(0)

                # Executar callback se registrado
                if gesture in self.gesture_callbacks:
                    self.gesture_callbacks[gesture]()

                self.last_gesture = gesture

            return gesture

        except Exception as e:
            logger.error(f"Erro ao detectar gesto: {e}")
            return None

    def _classify_gesture(self, landmarks) -> GestureType:
        """Classifica gesto baseado em landmarks da mÃ£o"""
        # Extrair coordenadas dos dedos
        thumb_tip = landmarks.landmark[4]
        index_tip = landmarks.landmark[8]
        middle_tip = landmarks.landmark[12]
        ring_tip = landmarks.landmark[16]
        pinky_tip = landmarks.landmark[20]

        wrist = landmarks.landmark[0]

        # Calcular se dedos estÃ£o estendidos
        fingers_up = []

        # Polegar (comparaÃ§Ã£o horizontal)
        if thumb_tip.x < landmarks.landmark[3].x:
            fingers_up.append(1)
        else:
            fingers_up.append(0)

        # Outros dedos (comparaÃ§Ã£o vertical)
        for tip_id in [8, 12, 16, 20]:
            if landmarks.landmark[tip_id].y < landmarks.landmark[tip_id - 2].y:
                fingers_up.append(1)
            else:
                fingers_up.append(0)

        # Classificar gestos
        total_fingers = sum(fingers_up)

        # Polegar para cima
        if fingers_up == [1, 0, 0, 0, 0]:
            return GestureType.THUMBS_UP

        # Polegar para baixo
        if fingers_up == [0, 0, 0, 0, 0] and thumb_tip.y > wrist.y:
            return GestureType.THUMBS_DOWN

        # Paz (V)
        if fingers_up == [0, 1, 1, 0, 0]:
            return GestureType.PEACE

        # OK (polegar + indicador)
        if fingers_up == [1, 1, 0, 0, 0]:
            return GestureType.OK

        # Apontar
        if fingers_up == [0, 1, 0, 0, 0]:
            return GestureType.POINTING

        # Palma aberta
        if total_fingers == 5:
            return GestureType.OPEN_PALM

        # Punho fechado
        if total_fingers == 0:
            return GestureType.FIST

        return GestureType.NONE

    def register_gesture_callback(self, gesture: GestureType, callback: Callable):
        """Registra callback para um gesto"""
        self.gesture_callbacks[gesture] = callback
        logger.info(f"âœ… Callback registrado para gesto: {gesture.value}")

    def draw_landmarks(self, frame: np.ndarray, landmarks) -> np.ndarray:
        """Desenha landmarks da mÃ£o no frame"""
        if not self.mediapipe_available:
            return frame

        try:
            self.mp_drawing.draw_landmarks(
                frame, landmarks, self.mp_hands.HAND_CONNECTIONS
            )
        except Exception as e:
            logger.error(f"Erro ao desenhar landmarks: {e}")

        return frame

    def get_gesture_name(self, gesture: GestureType) -> str:
        """Retorna nome amigÃ¡vel do gesto"""
        names = {
            GestureType.THUMBS_UP: "ðŸ‘ Polegar para cima",
            GestureType.THUMBS_DOWN: "ðŸ‘Ž Polegar para baixo",
            GestureType.PEACE: "âœŒï¸ Paz",
            GestureType.OK: "ðŸ‘Œ OK",
            GestureType.POINTING: "ðŸ‘‰ Apontando",
            GestureType.OPEN_PALM: "ðŸ–ï¸ Palma aberta",
            GestureType.FIST: "âœŠ Punho fechado",
            GestureType.NONE: "Nenhum",
        }
        return names.get(gesture, gesture.value)


# InstÃ¢ncia global removida para evitar execuÃ§Ã£o durante import
# gesture_recognizer = GestureRecognizer()


# Exemplo de uso
if __name__ == "__main__":
    # Registrar callbacks
    def on_thumbs_up():
        print("ðŸ‘ Gesto: Polegar para cima!")

    def on_peace():
        print("âœŒï¸ Gesto: Paz!")

    gesture_recognizer.register_gesture_callback(GestureType.THUMBS_UP, on_thumbs_up)
    gesture_recognizer.register_gesture_callback(GestureType.PEACE, on_peace)

    # Capturar da webcam
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Detectar gesto
        gesture = gesture_recognizer.detect_gesture(frame)

        # Mostrar gesto detectado
        if gesture and gesture != GestureType.NONE:
            gesture_name = gesture_recognizer.get_gesture_name(gesture)
            cv2.putText(
                frame,
                gesture_name,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

        cv2.imshow("Gesture Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
