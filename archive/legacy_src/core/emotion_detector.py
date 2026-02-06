"""
Detector de Emoções (Neural Emotional Intelligence)
Analisa expressões faciais (via FER) e tons de voz para ajustar a persona do Jarvis.
"""

import logging
import cv2
import numpy as np
from typing import Dict, Any, Optional

try:
    from fer import FER
    FER_AVAILABLE = True
except ImportError:
    FER_AVAILABLE = False

logger = logging.getLogger(__name__)

class EmotionDetector:
    """Class to detect human emotions via vision and voice"""

    def __init__(self):
        self.emotion_model = None
        if FER_AVAILABLE:
            try:
                # mtcnn=True para maior precisão, False para performance (CPU)
                self.emotion_model = FER(mtcnn=False) 
                logger.info("Detector de emoções (FER) carregado.")
            except Exception as e:
                logger.error(f"Erro ao carregar detector FER: {e}")
        
        self.last_emotion = "neutral"
        self.last_score = 0.0

    def detect_emotion_from_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Detecta emoções na imagem atual"""
        if not FER_AVAILABLE or self.emotion_model is None:
            return {"emotion": "neutral", "score": 1.0}

        try:
            # Detectar emoções
            results = self.emotion_model.detect_emotions(frame)
            
            if not results:
                return {"emotion": self.last_emotion, "score": self.last_score}

            # Pegar a emoção dominante da primeira face detectada
            emotions = results[0]['emotions']
            dominant_emotion = max(emotions, key=emotions.get)
            score = emotions[dominant_emotion]

            self.last_emotion = dominant_emotion
            self.last_score = score

            return {"emotion": dominant_emotion, "score": score}
        except Exception as e:
            logger.error(f"Erro na detecção de emoção visual: {e}")
            return {"emotion": "neutral", "score": 0.0}

    def analyze_voice_tone(self, audio_data: np.ndarray) -> str:
        """
        Analisa o tom de voz (Simples: intensidade e pitch)
        (Será expandido com librosa se necessário)
        """
        # Por enquanto, mantemos neutral até integrar librosa no fluxo de áudio real
        return "neutral"

    def get_personality_modifier(self, emotion: str) -> Dict[str, str]:
        """Retorna parâmetros para ajustar o System Prompt do AIAgent"""
        modifiers = {
            "happy": {
                "prefix": "Fico feliz em vê-lo de bom humor, Senhor. ",
                "style": "leve e sarcástico",
                "energy": "alta"
            },
            "sad": {
                "prefix": "Lamento se as coisas não estão fáceis hoje, Senhor. Conte comigo. ",
                "style": "acolhedor e eficiente",
                "energy": "baixa"
            },
            "angry": {
                "prefix": "Percebo sua frustração, Senhor. Vou resolver isso o mais rápido possível. ",
                "style": "direto e sem rodeios",
                "energy": "máxima"
            },
            "fear": {
                "prefix": "Fique tranquilo, Senhor. Estou monitorando tudo. ",
                "style": "calmo e protetor",
                "energy": "estável"
            },
            "surprise": {
                "prefix": "Impressionante, não é? ",
                "style": "entusiasta",
                "energy": "vibrante"
            },
            "neutral": {
                "prefix": "",
                "style": "clássico Jarvis",
                "energy": "padrão"
            }
        }
        return modifiers.get(emotion, modifiers["neutral"])

# Instância global
emotion_detector = EmotionDetector()
