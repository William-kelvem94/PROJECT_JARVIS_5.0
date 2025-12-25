"""
Processamento inteligente de fala natural para JARVIS
Otimizado para funcionar perfeitamente online e offline
"""

import re
import random
from typing import Optional, Dict, Any, List
from ..core.logger import default_logger


class SmartNaturalSpeechProcessor:
    """Processador inteligente de fala natural"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = default_logger
        self.natural_config = config.get('natural_speech', {})
        
        # Modo de operação (online/offline)
        self.online_mode = True
        
        # Configurações de naturalidade por modo
        self.online_settings = {
            'use_fillers': True,
            'use_hesitations': True,
            'use_breathing': False,  # Microsoft Edge TTS já tem respiração natural
            'use_emotions': True,
            'use_pauses': False,  # Microsoft Edge TTS já tem pausas naturais
            'intensity': 0.3  # Menos processamento, TTS já é natural
        }
        
        self.offline_settings = {
            'use_fillers': True,
            'use_hesitations': True,
            'use_breathing': True,
            'use_emotions': True,
            'use_pauses': True,
            'intensity': 0.8  # Mais processamento para compensar TTS básico
        }
    
    def set_mode(self, online: bool):
        """Define o modo de operação (online/offline)"""
        self.online_mode = online
        self.logger.info(f"Modo de processamento: {'Online' if online else 'Offline'}")
    
    def process_text(self, text: str, emotion: Optional[str] = None, engine_type: str = "online") -> str:
        """
        Processa texto para naturalidade baseado no tipo de engine
        
        Args:
            text: Texto original
            emotion: Emoção a aplicar
            engine_type: "online" (Microsoft/Google) ou "offline" (local)
        """
        if not text or not text.strip():
            return text
        
        # Definir configurações baseadas no engine
        settings = self.online_settings if engine_type == "online" else self.offline_settings
        
        # Limpar texto de entrada
        processed = self._clean_input_text(text)
        
        # Aplicar processamentos baseados no modo
        if settings['use_emotions'] and emotion:
            processed = self._add_smart_emotion(processed, emotion, settings['intensity'])
        
        if settings['use_fillers']:
            processed = self._add_smart_fillers(processed, settings['intensity'])
        
        if settings['use_hesitations']:
            processed = self._add_smart_hesitations(processed, settings['intensity'])
        
        # Apenas para modo offline (engines locais precisam de mais ajuda)
        if engine_type == "offline":
            if settings['use_breathing']:
                processed = self._add_breathing_marks(processed, settings['intensity'])
            
            if settings['use_pauses']:
                processed = self._add_pause_marks(processed, settings['intensity'])
        
        return processed.strip()
    
    def _clean_input_text(self, text: str) -> str:
        """Limpa e normaliza o texto de entrada"""
        # Remover caracteres estranhos
        text = re.sub(r'[^\w\s\.,!?;:\-\(\)\"\'àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]', '', text, flags=re.IGNORECASE)
        
        # Normalizar espaços
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remover marcadores antigos que podem estar causando problemas
        text = re.sub(r'\[pausa_[^\]]*\]', '', text)
        text = re.sub(r'\[respiração\]', '', text)
        text = re.sub(r'anderline|midia', '', text, flags=re.IGNORECASE)
        
        return text
    
    def _add_smart_emotion(self, text: str, emotion: str, intensity: float) -> str:
        """Adiciona emoção de forma inteligente"""
        if random.random() > intensity:
            return text
        
        emotion_map = {
            'entusiasta': {
                'prefix': ['', 'Ótimo! ', 'Que legal! '],
                'suffix': ['', ' Adorei!', ' Que demais!']
            },
            'preocupado': {
                'prefix': ['', 'Hmm... ', 'Eita... '],
                'suffix': ['', ' Será que está certo?', '']
            },
            'aliviado': {
                'prefix': ['', 'Ufa! ', 'Que bom! '],
                'suffix': ['', ' Que alívio!', '']
            },
            'pensativo': {
                'prefix': ['', 'Bem... ', 'Deixa eu ver... '],
                'suffix': ['', ' O que você acha?', '']
            }
        }
        
        if emotion in emotion_map:
            emotion_data = emotion_map[emotion]
            
            # Adicionar prefixo (baixa chance)
            if random.random() < 0.2:
                prefix = random.choice(emotion_data['prefix'])
                if prefix:
                    text = prefix + text
            
            # Adicionar sufixo (baixa chance)
            if random.random() < 0.15:
                suffix = random.choice(emotion_data['suffix'])
                if suffix:
                    text = text + suffix
        
        return text
    
    def _add_smart_fillers(self, text: str, intensity: float) -> str:
        """Adiciona fillers conversacionais inteligentes"""
        if random.random() > intensity * 0.5:  # Reduzir chance
            return text
        
        fillers = ['bem', 'então', 'né', 'sabe']
        
        # Adicionar filler no início (chance muito baixa)
        if random.random() < 0.1:
            filler = random.choice(fillers)
            text = f"{filler}, {text}"
        
        return text
    
    def _add_smart_hesitations(self, text: str, intensity: float) -> str:
        """Adiciona hesitações naturais"""
        if random.random() > intensity * 0.3:  # Chance ainda menor
            return text
        
        hesitations = ['hmm', 'ah', 'eh']
        
        # Adicionar hesitação (chance muito baixa)
        if random.random() < 0.08:
            hesitation = random.choice(hesitations)
            text = f"{hesitation}... {text}"
        
        return text
    
    def _add_breathing_marks(self, text: str, intensity: float) -> str:
        """Adiciona marcas de respiração para engines locais"""
        if random.random() > intensity:
            return text
        
        # Adicionar pausas de respiração naturais em frases longas
        if len(text.split()) > 15:
            words = text.split()
            mid_point = len(words) // 2
            
            # Inserir pausa natural no meio da frase
            words.insert(mid_point, '...')  # Usar reticências em vez de marcadores
            text = ' '.join(words)
        
        return text
    
    def _add_pause_marks(self, text: str, intensity: float) -> str:
        """Adiciona marcas de pausa para engines locais"""
        if random.random() > intensity:
            return text
        
        # Adicionar pausas naturais sem marcadores visíveis
        # Para engines locais, usar SSML ou pausas naturais
        text = re.sub(r',(\s+)', r', ... ', text)  # Pausa curta com reticências
        text = re.sub(r'\.(\s+)', r'. ', text)     # Pausa natural no ponto
        
        return text
    
    def break_into_phrases(self, text: str) -> List[str]:
        """Quebra texto em frases de forma inteligente"""
        if not text or len(text.strip()) == 0:
            return [text]
        
        # Quebra simples e eficiente
        phrases = re.split(r'(?<=[.!?])\s+', text.strip())
        
        # Filtrar frases vazias e muito curtas
        phrases = [p.strip() for p in phrases if p.strip() and len(p.strip()) > 2]
        
        return phrases if phrases else [text]
    
    def calculate_contextual_pause(self, current_phrase: str, previous_phrase: str, emotion: Optional[str] = None) -> float:
        """Calcula pausa contextual entre frases"""
        base_pause = 0.3
        
        # Ajustar baseado na emoção
        emotion_modifiers = {
            'entusiasta': 0.2,  # Pausas mais curtas
            'preocupado': 0.5,  # Pausas mais longas
            'pensativo': 0.6,   # Pausas ainda mais longas
            'aliviado': 0.3     # Pausas normais
        }
        
        if emotion in emotion_modifiers:
            base_pause = emotion_modifiers[emotion]
        
        # Ajustar baseado no comprimento das frases
        if len(current_phrase.split()) > 10:
            base_pause += 0.1
        
        return base_pause
    
    def process_markers(self, text: str) -> tuple:
        """Processa marcadores especiais para engines locais"""
        extra_pause = 0.0
        
        # Processar marcadores de pausa
        if '[pause_short]' in text:
            text = text.replace('[pause_short]', '')
            extra_pause += 0.2
        
        if '[pause_medium]' in text:
            text = text.replace('[pause_medium]', '')
            extra_pause += 0.4
        
        if '[breath]' in text:
            text = text.replace('[breath]', '')
            extra_pause += 0.3
        
        return text.strip(), extra_pause
