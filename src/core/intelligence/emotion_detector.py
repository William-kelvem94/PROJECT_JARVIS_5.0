"""
Detector de EmoÃ§Ãµes (Neural Emotional Intelligence)
Analisa expressÃµes faciais (via FER) e tons de voz para ajustar a persona do Jarvis.
"""

import logging
from typing import Dict, Any, Optional

try:
    import cv2
    CV2_AVAILABLE = True
except (ImportError, OSError) as e:
    CV2_AVAILABLE = False
    cv2 = None
    logging.warning(f"âš ï¸ cv2 not available in emotion_detector: {e}")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except (ImportError, OSError) as e:
    NUMPY_AVAILABLE = False
    np = None
    logging.warning(f"âš ï¸ numpy not available in emotion_detector: {e}")

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
                # mtcnn=True para maior precisÃ£o, False para performance (CPU)
                self.emotion_model = FER(mtcnn=False) 
                logger.info("Detector de emoÃ§Ãµes (FER) carregado.")
            except Exception as e:
                logger.error(f"Erro ao carregar detector FER: {e}")
        
        self.last_emotion = "neutral"
        self.last_score = 0.0

    def detect_emotion_from_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Detecta emoÃ§Ãµes na imagem atual"""
        if not FER_AVAILABLE or self.emotion_model is None:
            return {"emotion": "neutral", "score": 1.0}

        try:
            results = self.emotion_model.detect_emotions(frame)
            if not results:
                return {"emotion": self.last_emotion, "score": self.last_score}

            emotions = results[0]['emotions']
            dominant_emotion = max(emotions, key=emotions.get)
            score = emotions[dominant_emotion]

            self.last_emotion = dominant_emotion
            self.last_score = score
            
            return {"emotion": dominant_emotion, "score": score}
        except Exception as e:
            logger.error(f"Erro na detecÃ§Ã£o de emoÃ§Ã£o visual: {e}")
            return {"emotion": "neutral", "score": 0.0}

    def analyze_voice_tone(self, audio_path: str) -> Dict[str, Any]:
        """
        Analisa o tom de voz usando o processador avanÃ§ado
        """
        try:
            from src.core.audio.advanced_speech_processor import advanced_speech_processor
            voice_data = advanced_speech_processor.analyze_speech_emotion(audio_path)
            return voice_data
        except Exception as e:
            logger.error(f"Erro ao analisar tom de voz: {e}")
            return {"emotion": "neutral", "confidence": 0.0}

    def get_consolidated_emotion(self, visual_data: Dict, audio_data: Dict) -> Dict[str, Any]:
        """
        FusÃ£o Multimodal (Cross-Modal Fusion): Face (60%) + Voz (40%)
        """
        v_emo = visual_data.get("emotion", "neutral")
        v_score = visual_data.get("score", 0.0)
        
        a_emo = audio_data.get("emotion", "neutral")
        a_score = audio_data.get("confidence", 0.0)
        
        # Pesos da FusÃ£o
        fused_score = (v_score * 0.6) + (a_score * 0.4)
        
        # LÃ³gica de dominÃ¢ncia
        if v_emo == a_emo:
            final_emotion = v_emo
        elif v_score > a_score + 0.2:
            final_emotion = v_emo
        else:
            final_emotion = a_emo
            
        return {
            "emotion": final_emotion,
            "confidence": fused_score,
            "is_multimodal": True
        }

    def get_personality_modifier(self, emotion: str) -> Dict[str, str]:
        """Retorna parÃ¢metros para ajustar o System Prompt do AIAgent"""
        modifiers = {
            "happy": {
                "prefix": "Fico feliz em vÃª-lo de bom humor, Senhor. ",
                "style": "leve e sarcÃ¡stico",
                "energy": "alta"
            },
            "sad": {
                "prefix": "Lamento se as coisas nÃ£o estÃ£o fÃ¡ceis hoje, Senhor. Conte comigo. ",
                "style": "acolhedor e eficiente",
                "energy": "baixa"
            },
            "angry": {
                "prefix": "Percebo sua frustraÃ§Ã£o, Senhor. Vou resolver isso o mais rÃ¡pido possÃ­vel. ",
                "style": "direto e sem rodeios",
                "energy": "mÃ¡xima"
            },
            "fear": {
                "prefix": "Fique tranquilo, Senhor. Estou monitorando tudo. ",
                "style": "calmo e protetor",
                "energy": "estÃ¡vel"
            },
            "surprise": {
                "prefix": "Impressionante, nÃ£o Ã©? ",
                "style": "entusiasta",
                "energy": "vibrante"
            },
            "neutral": {
                "prefix": "",
                "style": "clÃ¡ssico Jarvis",
                "energy": "padrÃ£o"
            }
        }
        return modifiers.get(emotion, modifiers["neutral"])

# InstÃ¢ncia global
emotion_detector = EmotionDetector()
