"""
Processador de fala natural para JARVIS
"""

import re
import random
import time
from typing import List, Tuple, Optional, Dict, Any

from ..core.logger import default_logger


class NaturalSpeechProcessor:
    """Processador que torna a fala extremamente natural"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = default_logger
        self.natural_config = config.get('natural_speech', {})
    
    def process_text(self, text: str, emotion: Optional[str] = None) -> str:
        """
        Processa texto para naturalidade extrema
        
        Args:
            text: Texto original
            emotion: Emoção a aplicar
            
        Returns:
            Texto processado para naturalidade
        """
        if not text or not text.strip():
            return text
        
        # #region agent log
        with open(r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor\debug.log', 'a', encoding='utf-8') as f:
            import json, time
            f.write(json.dumps({"sessionId":"debug-session","runId":"voice-debug","hypothesisId":"B","location":"natural_speech.py:process_text:entry","message":"Iniciando processamento de texto natural","data":{"original_text":text,"emotion":emotion,"natural_config":self.natural_config},"timestamp":int(time.time()*1000)}) + '\n')
        # #endregion
        
        processed = text.lower()
        
        # Aplicar processamentos se habilitados na config
        if self.natural_config.get('emotion_detection', True) and emotion:
            processed = self._add_emotion_to_text(processed, emotion)
            # #region agent log
            with open(r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor\debug.log', 'a', encoding='utf-8') as f:
                import json, time
                f.write(json.dumps({"sessionId":"debug-session","runId":"voice-debug","hypothesisId":"B,C","location":"natural_speech.py:process_text:emotion_added","message":"Emoção adicionada ao texto","data":{"emotion":emotion,"text_after_emotion":processed},"timestamp":int(time.time()*1000)}) + '\n')
            # #endregion
        
        if self.natural_config.get('use_fillers', True):
            before_fillers = processed
            processed = self._add_conversational_fillers(processed)
            # #region agent log
            with open(r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor\debug.log', 'a', encoding='utf-8') as f:
                import json, time
                f.write(json.dumps({"sessionId":"debug-session","runId":"voice-debug","hypothesisId":"B,C","location":"natural_speech.py:process_text:fillers_added","message":"Fillers conversacionais adicionados","data":{"before":before_fillers,"after":processed},"timestamp":int(time.time()*1000)}) + '\n')
            # #endregion
        
        if self.natural_config.get('use_hesitations', True):
            before_hesitations = processed
            processed = self._add_human_hesitations(processed)
            # #region agent log
            with open(r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor\debug.log', 'a', encoding='utf-8') as f:
                import json, time
                f.write(json.dumps({"sessionId":"debug-session","runId":"voice-debug","hypothesisId":"B,C","location":"natural_speech.py:process_text:hesitations_added","message":"Hesitações humanas adicionadas","data":{"before":before_hesitations,"after":processed},"timestamp":int(time.time()*1000)}) + '\n')
            # #endregion
        
        if self.natural_config.get('use_breathing', True):
            before_breathing = processed
            processed = self._add_simulated_breathing(processed)
            # #region agent log
            with open(r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor\debug.log', 'a', encoding='utf-8') as f:
                import json, time
                f.write(json.dumps({"sessionId":"debug-session","runId":"voice-debug","hypothesisId":"B,C","location":"natural_speech.py:process_text:breathing_added","message":"Respiração simulada adicionada","data":{"before":before_breathing,"after":processed},"timestamp":int(time.time()*1000)}) + '\n')
            # #endregion
        
        if self.natural_config.get('conversation_flow', True):
            before_flow = processed
            processed = self._add_conversational_markers(processed)
            # #region agent log
            with open(r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor\debug.log', 'a', encoding='utf-8') as f:
                import json, time
                f.write(json.dumps({"sessionId":"debug-session","runId":"voice-debug","hypothesisId":"B,C","location":"natural_speech.py:process_text:flow_added","message":"Marcadores conversacionais adicionados","data":{"before":before_flow,"after":processed},"timestamp":int(time.time()*1000)}) + '\n')
            # #endregion
        
        # #region agent log
        with open(r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor\debug.log', 'a', encoding='utf-8') as f:
            import json, time
            f.write(json.dumps({"sessionId":"debug-session","runId":"voice-debug","hypothesisId":"B,C","location":"natural_speech.py:process_text:final","message":"Processamento final concluído","data":{"original_text":text,"final_processed":processed,"length_change":len(processed)-len(text)},"timestamp":int(time.time()*1000)}) + '\n')
        # #endregion
        
        return processed
    
    def _add_emotion_to_text(self, text: str, emotion: str) -> str:
        """Adiciona elementos emocionais ao texto"""
        emotion_map = {
            'entusiasta': {
                'prefix': ['Uau! ', 'Que legal! ', 'Ótimo! '],
                'suffix': [' Que demais!', ' Incrível, né?', ' Adorei!']
            },
            'preocupado': {
                'prefix': ['Ah... ', 'Hmm... ', 'Eita... '],
                'suffix': [' Será que está tudo bem?', ' Espero que dê certo.', '']
            },
            'aliviado': {
                'prefix': ['Ufa! ', 'Ainda bem! ', 'Que bom! '],
                'suffix': [' Que alívio!', ' Graças a Deus!', '']
            },
            'pensativo': {
                'prefix': ['Hmm... ', 'Deixa eu ver... ', 'Bem... '],
                'suffix': ['', ' O que você acha?', ' Faz sentido?']
            }
        }
        
        if emotion in emotion_map:
            emotion_data = emotion_map[emotion]
            
            # Adicionar prefixo (30% de chance)
            if random.random() < 0.3:
                prefix = random.choice(emotion_data['prefix'])
                text = prefix + text
            
            # Adicionar sufixo (20% de chance)
            if random.random() < 0.2:
                suffix = random.choice(emotion_data['suffix'])
                text = text + suffix
        
        return text
    
    def _add_conversational_fillers(self, text: str) -> str:
        """Adiciona fillers conversacionais naturais"""
        fillers = {
            'inicio': ['então, ', 'olha, ', 'tipo, ', 'sabe, ', 'ah, ', 'bom, ', 'bem, '],
            'meio': [' né?', ' tá?', ' então', ' tipo', ' sabe', ' né mesmo'],
            'conectivos': [' então quer dizer', ' tipo assim', ' sabe como é', ' entende']
        }
        
        # Filler no início (40% de chance)
        if random.random() < 0.4 and not any(text.startswith(f) for f in fillers['inicio']):
            text = random.choice(fillers['inicio']) + text
        
        # Filler no meio para frases longas (25% de chance)
        if len(text.split()) > 10 and random.random() < 0.25:
            words = text.split()
            position = len(words) // 2
            filler = random.choice(fillers['meio'])
            words.insert(position, filler)
            text = ' '.join(words)
        
        # Filler no final para perguntas (60% de chance)
        if '?' in text and random.random() < 0.6:
            text = text.rstrip('?') + ' ' + random.choice(fillers['meio']) + '?'
        
        return text
    
    def _add_human_hesitations(self, text: str) -> str:
        """Adiciona hesitações que simulam pensamento humano"""
        hesitations = ['eh...', 'hmm...', 'tipo...', 'ah...', 'então...', 'bem...']
        
        # Palavras que podem gerar hesitação
        trigger_words = ['erro', 'problema', 'importante', 'atenção', 'cuidado', 'difícil']
        
        for word in trigger_words:
            if word in text and random.random() < 0.2:
                pos = text.find(word)
                if pos > 0:
                    hesitation = random.choice(hesitations)
                    text = text[:pos] + hesitation + ' ' + text[pos:]
                    break
        
        return text
    
    def _add_simulated_breathing(self, text: str) -> str:
        """Adiciona marcadores de respiração simulada"""
        # Para frases muito longas, adicionar respiração
        if len(text.split()) > 15:
            words = text.split()
            breath_pos = len(words) // 2
            words.insert(breath_pos, '[resp]')
            text = ' '.join(words)
        
        return text
    
    def _add_conversational_markers(self, text: str) -> str:
        """Adiciona marcadores que controlam o fluxo conversacional"""
        # Para engines online (Microsoft/Google), não adicionar marcadores visíveis
        # Eles já têm naturalidade própria e interpretam pontuação corretamente
        
        # Apenas normalizar espaçamento para melhor interpretação
        import re
        text = re.sub(r'([.!?])\s+', r'\1 ', text)  # Normalizar espaços após pontuação
        text = re.sub(r',\s+', r', ', text)         # Normalizar espaços após vírgula
        text = re.sub(r'\s+', ' ', text)            # Remover espaços extras
        
        return text.strip()
    
    def break_into_phrases(self, text: str) -> List[str]:
        """Quebra texto em frases de forma ultra-inteligente"""
        if not text or len(text.strip()) == 0:
            return [text]
        
        # Normalizar espaços
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Quebra básica por pontuação
        phrases = self._basic_punctuation_break(text)
        
        # Quebra avançada para frases muito longas
        final_phrases = []
        for phrase in phrases:
            if len(phrase.split()) > 25:
                sub_phrases = self._advanced_conversational_break(phrase)
                final_phrases.extend(sub_phrases)
            else:
                final_phrases.append(phrase)
        
        # Filtrar frases vazias
        return [p for p in final_phrases if p.strip()]
    
    def _basic_punctuation_break(self, text: str) -> List[str]:
        """Quebra básica por pontuação"""
        # Marcadores principais
        markers = [
            r'(?<=[.!?])\s+(?=[A-ZÀ-Ú])',  # Após pontuação + maiúscula
            r'(?<=!)\s+',  # Após exclamação
            r'(?<=\?)\s+',  # Após interrogação
        ]
        
        phrases = [text]
        for marker in markers:
            new_phrases = []
            for phrase in phrases:
                parts = re.split(marker, phrase)
                new_phrases.extend([p.strip() for p in parts if p.strip()])
            phrases = new_phrases
        
        return phrases
    
    def _advanced_conversational_break(self, phrase: str) -> List[str]:
        """Quebra avançada baseada em contexto conversacional"""
        # Marcadores conversacionais prioritários
        conversational_markers = [
            ' e então ', ' mas sabe ', ' tipo assim ', ' quer dizer ',
            ' na verdade ', ' por exemplo ', ' ou seja ', ' em outras palavras ',
            ' acontece que ', ' o problema é ', ' a questão é ', ' o fato é '
        ]
        
        for marker in conversational_markers:
            if marker in phrase.lower():
                parts = phrase.split(marker)
                if len(parts) == 2 and len(parts[0].split()) >= 5 and len(parts[1].split()) >= 3:
                    return [
                        parts[0] + marker.rstrip(),
                        marker.lstrip() + parts[1]
                    ]
        
        # Conectivos lógicos
        logical_connectors = [' e ', ' mas ', ' porém ', ' pois ', ' porque ', ' então ']
        for connector in logical_connectors:
            if connector in phrase.lower():
                parts = phrase.split(connector)
                if len(parts) == 2 and len(parts[0].split()) > 8 and len(parts[1].split()) > 4:
                    return [
                        parts[0] + connector.rstrip(),
                        connector.lstrip() + parts[1]
                    ]
        
        # Quebra por tamanho se necessário
        words = phrase.split()
        if len(words) > 30:
            mid = len(words) // 2
            # Procurar quebra natural próxima ao meio
            for i in range(mid - 3, mid + 3):
                if i > 0 and i < len(words):
                    word = words[i].lower()
                    if word in ['que', 'e', 'mas', 'porém', 'pois', 'porque', 'então']:
                        return [' '.join(words[:i+1]), ' '.join(words[i+1:])]
            
            # Quebra simples no meio
            return [' '.join(words[:mid]), ' '.join(words[mid:])]
        
        return [phrase]
    
    def process_markers(self, phrase: str) -> Tuple[str, float]:
        """Processa marcadores especiais e retorna frase limpa + pausa extra"""
        extra_pause = 0
        
        # Processar marcadores de pausa
        marker_pauses = {
            '[pausa_curta]': 0.3,
            '[pausa_media]': 0.6,
            '[pausa_longa]': 1.0,
            '[pausa_mudanca]': 0.8,
            '[resp]': 0.4
        }
        
        for marker, pause in marker_pauses.items():
            if marker in phrase:
                extra_pause = max(extra_pause, pause)
                phrase = phrase.replace(marker, '')
        
        # Limpar espaços extras
        phrase = ' '.join(phrase.split())
        
        return phrase, extra_pause
    
    def calculate_contextual_pause(self, current_phrase: str, previous_phrase: str, 
                                 emotion: Optional[str] = None) -> float:
        """Calcula pausa contextual entre frases"""
        base_pause = 0.3
        
        # Ajustes emocionais
        if emotion == 'preocupado':
            base_pause += 0.2
        elif emotion == 'entusiasta':
            base_pause -= 0.1
        
        # Ajustes baseados no conteúdo
        current_lower = current_phrase.lower()
        previous_lower = previous_phrase.lower()
        
        # Pausas após hesitações
        if any(hesit in previous_lower for hesit in ['hmm', 'eh', 'tipo', 'ah']):
            base_pause += 0.3
        
        # Pausas antes de informações importantes
        if any(word in current_lower for word in ['erro', 'problema', 'atenção', 'importante']):
            base_pause += 0.4
        
        # Pausas após pontuação forte
        if previous_phrase.endswith(('!', '?', '...')):
            base_pause += 0.5
        elif previous_phrase.endswith('.'):
            base_pause += 0.3
        
        return max(0.1, min(1.2, base_pause))
    
    def calculate_contextual_speed(self, phrase: str, base_speed: int, 
                                 emotion: Optional[str] = None) -> int:
        """Calcula velocidade contextual da frase"""
        speed = float(base_speed)
        words = len(phrase.split())
        phrase_lower = phrase.lower()
        
        # Ajustes emocionais
        if emotion == 'entusiasta':
            speed *= 1.1
        elif emotion == 'preocupado':
            speed *= 0.85
        elif emotion == 'pensativo':
            speed *= 0.9
        
        # Ajustes por tamanho
        if words > 20:
            speed *= 0.8
        elif words < 4:
            speed *= 1.25
        
        # Ajustes por conteúdo
        if any(word in phrase_lower for word in ['erro', 'problema', 'desculpe', 'ops']):
            speed *= 0.75
        elif any(word in phrase_lower for word in ['pronto', 'feito', 'sucesso', 'ótimo']):
            speed *= 1.15
        elif any(word in phrase_lower for word in ['hmm', 'eh', 'tipo', 'ah']):
            speed *= 0.9
        
        # Ajustes por pontuação
        if '?' in phrase:
            speed *= 0.95
        elif '!' in phrase:
            speed *= 1.05
        
        return int(max(80, min(300, speed)))
    
    def calculate_contextual_pitch(self, phrase: str, base_pitch: int, 
                                 emotion: Optional[str] = None) -> int:
        """Calcula pitch contextual da frase"""
        pitch = base_pitch
        phrase_lower = phrase.lower()
        
        # Ajustes emocionais
        if emotion == 'entusiasta':
            pitch += 8
        elif emotion == 'preocupado':
            pitch -= 5
        elif emotion == 'aliviado':
            pitch += 3
        
        # Ajustes por conteúdo
        if any(word in phrase_lower for word in ['erro', 'ops', 'desculpe', 'problema']):
            pitch -= 12
        elif any(word in phrase_lower for word in ['pronto', 'feito', 'sucesso', 'ótimo']):
            pitch += 6
        elif any(word in phrase_lower for word in ['hmm', 'eh', 'tipo', 'ah']):
            pitch -= 3
        
        # Variação silábica
        syllable_variation = self._calculate_syllable_variation(phrase)
        pitch += syllable_variation
        
        return max(20, min(100, pitch))
    
    def calculate_contextual_volume(self, phrase: str, base_volume: float, 
                                  emotion: Optional[str] = None) -> float:
        """Calcula volume contextual da frase"""
        volume = base_volume
        phrase_lower = phrase.lower()
        
        # Ajustes emocionais
        if emotion == 'entusiasta':
            volume += 0.1
        elif emotion == 'preocupado':
            volume -= 0.05
        
        # Ajustes por conteúdo
        if any(word in phrase_lower for word in ['erro', 'problema']):
            volume -= 0.1
        elif any(word in phrase_lower for word in ['pronto', 'sucesso']):
            volume += 0.05
        
        return max(0.1, min(1.0, volume))
    
    def _calculate_syllable_variation(self, phrase: str) -> int:
        """Calcula variação de pitch baseada em sílabas"""
        words = phrase.split()
        if len(words) < 2:
            return 0
        
        # Contagem aproximada de sílabas
        total_syllables = sum(self._count_syllables(word) for word in words)
        
        variation = 0
        
        # Última palavra tende a ter pitch mais baixo
        if len(words) > 1:
            variation -= 2
        
        # Frases com muitas sílabas têm variação maior
        if total_syllables > 15:
            variation += 1
        
        # Perguntas têm pitch mais alto no final
        if '?' in phrase:
            variation += 3
        
        # Hesitações têm pitch mais baixo
        if any(hesit in phrase.lower() for hesit in ['hmm', 'eh', 'tipo']):
            variation -= 3
        
        return variation
    
    def _count_syllables(self, word: str) -> int:
        """Conta sílabas aproximadamente para português"""
        word = word.lower()
        vowels = 'aeiouáéíóúâêôãõ'
        syllables = 0
        
        i = 0
        while i < len(word):
            if word[i] in vowels:
                syllables += 1
                # Pular vogais consecutivas (ditongos)
                while i + 1 < len(word) and word[i + 1] in vowels:
                    i += 1
            i += 1
        
        return max(1, syllables)
