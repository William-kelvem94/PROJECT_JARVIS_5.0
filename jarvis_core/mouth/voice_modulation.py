"""
Mouth - Voice Modulation
Modulação de voz baseada em emoção
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

class VoiceModulation:
    """Modulador de voz emocional"""
    
    def __init__(self):
        self.current_emotion = "neutral"
        self.voice_profiles = {
            "neutral": {
                "rate": 1.0,
                "pitch": 1.0,
                "volume": 1.0
            },
            "excited": {
                "rate": 1.2,
                "pitch": 1.1,
                "volume": 1.2
            },
            "calm": {
                "rate": 0.9,
                "pitch": 0.95,
                "volume": 0.9
            },
            "serious": {
                "rate": 0.95,
                "pitch": 0.9,
                "volume": 1.0
            },
            "happy": {
                "rate": 1.1,
                "pitch": 1.05,
                "volume": 1.1
            }
        }
        
        logger.info("✅ Voice Modulation inicializado")
    
    def set_emotion(self, emotion: str):
        """Define emoção atual"""
        if emotion in self.voice_profiles:
            self.current_emotion = emotion
            logger.info(f"🎭 Emoção: {emotion}")
        else:
            logger.warning(f"⚠️ Emoção desconhecida: {emotion}")
    
    def get_modulation_params(self) -> dict:
        """Retorna parâmetros de modulação"""
        return self.voice_profiles.get(self.current_emotion, self.voice_profiles["neutral"])
    
    def modulate_text(self, text: str) -> str:
        """Adiciona marcadores SSML para modulação"""
        params = self.get_modulation_params()
        
        # SSML para Edge-TTS
        ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="pt-BR">
            <prosody rate="{params['rate']}" pitch="{params['pitch']}" volume="{params['volume']}">
                {text}
            </prosody>
        </speak>
        """
        
        return ssml.strip()
    
    def detect_emotion_from_text(self, text: str) -> str:
        """Detecta emoção do texto (heurística)"""
        text_lower = text.lower()
        
        # Palavras-chave emocionais
        if any(word in text_lower for word in ["urgente", "rápido", "agora", "importante"]):
            return "serious"
        elif any(word in text_lower for word in ["parabéns", "ótimo", "excelente", "incrível"]):
            return "excited"
        elif any(word in text_lower for word in ["calma", "tranquilo", "relaxe"]):
            return "calm"
        elif any(word in text_lower for word in ["feliz", "alegre", "legal"]):
            return "happy"
        else:
            return "neutral"
    
    def auto_modulate(self, text: str) -> str:
        """Auto-detecta emoção e modula"""
        emotion = self.detect_emotion_from_text(text)
        self.set_emotion(emotion)
        return self.modulate_text(text)


# Instância global
voice_modulation = VoiceModulation()
