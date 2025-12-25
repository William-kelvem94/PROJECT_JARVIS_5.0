"""
Processador de Linguagem Natural Avançado
Compreensão profunda de linguagem e contexto
"""

import re
import json
import spacy
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from ..core.logger import default_logger


class AdvancedNLPProcessor:
    """Processador avançado de linguagem natural"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = default_logger
        
        # Tentar carregar modelo spaCy português
        try:
            self.nlp = spacy.load("pt_core_news_sm")
            self.logger.info("Modelo spaCy português carregado")
        except OSError:
            try:
                # Fallback para modelo em inglês
                self.nlp = spacy.load("en_core_web_sm")
                self.logger.warning("Usando modelo spaCy em inglês (instale: python -m spacy download pt_core_news_sm)")
            except OSError:
                self.nlp = None
                self.logger.error("Nenhum modelo spaCy disponível. Usando processamento básico.")
        
        # Padrões de intenção avançados
        self.intent_patterns = {
            'system_control': {
                'patterns': [
                    r'(abr[aei]|execut[ae]|inici[ae]|rod[ae])\s+(.+)',
                    r'(fech[ae]|encerr[ae]|mat[ae]|par[ae])\s+(.+)',
                    r'(reinici[ae]|restart[ae])\s*(o\s+)?(computador|sistema|pc)',
                    r'(deslig[ae]|shutdown)\s*(o\s+)?(computador|sistema|pc)',
                    r'(hibern[ae]|suspend[ae])\s*(o\s+)?(computador|sistema|pc)'
                ],
                'entities': ['application', 'system_action']
            },
            'file_management': {
                'patterns': [
                    r'(cri[ae]|faz[ae])\s+(um\s+)?(arquivo|pasta|diretório)\s+(.+)',
                    r'(delet[ae]|remov[ae]|apag[ae])\s+(o\s+)?(arquivo|pasta)\s+(.+)',
                    r'(copi[ae]|mov[ae])\s+(o\s+)?(arquivo|pasta)\s+(.+)\s+(para|até)\s+(.+)',
                    r'(procur[ae]|encontr[ae]|ach[ae])\s+(o\s+)?(arquivo|pasta)\s+(.+)',
                    r'(list[ae]|mostr[ae])\s+(os\s+)?(arquivos|pastas)\s+(em|de|do)\s+(.+)'
                ],
                'entities': ['file_path', 'action_type', 'destination']
            },
            'web_automation': {
                'patterns': [
                    r'(abr[ae]|acess[ae]|v[aá]\s+para)\s+(o\s+)?(site|página|url)\s+(.+)',
                    r'(pesquis[ae]|procur[ae]|busqu[ae])\s+(no\s+)?(google|youtube|wikipedia)\s+(.+)',
                    r'(baix[ae]|download|faz[ae]\s+download)\s+(de\s+|do\s+)?(.+)',
                    r'(envi[ae]|mand[ae])\s+(um\s+)?(email|mensagem)\s+(para|até)\s+(.+)'
                ],
                'entities': ['url', 'search_term', 'platform', 'recipient']
            },
            'information_query': {
                'patterns': [
                    r'(que\s+horas\s+são|qual\s+é\s+a\s+hora)',
                    r'(que\s+dia\s+é\s+hoje|qual\s+é\s+a\s+data)',
                    r'(como\s+está\s+o\s+clima|previsão\s+do\s+tempo)',
                    r'(quanto\s+é|calcul[ae])\s+(.+)',
                    r'(defin[ae]|o\s+que\s+é|expliq[ae])\s+(.+)'
                ],
                'entities': ['query_type', 'calculation', 'definition_term']
            },
            'automation': {
                'patterns': [
                    r'(program[ae]|agendar?)\s+(um\s+)?(lembrete|alarme|tarefa)\s+(.+)',
                    r'(configur[ae]|defin[ae])\s+(um\s+)?(timer|cronômetro)\s+(de\s+|para\s+)?(.+)',
                    r'(ativ[ae]|desativ[ae])\s+(o\s+)?(modo\s+)?(não\s+perturb[ae]|silencioso|avião)',
                    r'(ajust[ae]|mud[ae])\s+(o\s+)?(volume|brilho|resolução)\s+(para\s+)?(.+)'
                ],
                'entities': ['schedule_time', 'timer_duration', 'setting_value']
            },
            'learning': {
                'patterns': [
                    r'(aprend[ae]|lemb?r[ae])\s+(que|de\s+que)\s+(.+)',
                    r'(esquec[ae]|delet[ae])\s+(o\s+que\s+você\s+sabe\s+sobre)\s+(.+)',
                    r'(o\s+que\s+você\s+sabe\s+sobre|me\s+fal[ae]\s+sobre)\s+(.+)',
                    r'(salv[ae]|guard[ae])\s+(esta\s+)?(informação|dados?)\s*:?\s*(.+)'
                ],
                'entities': ['knowledge_item', 'information_content']
            }
        }
        
        # Entidades nomeadas personalizadas
        self.custom_entities = {
            'applications': [
                'chrome', 'firefox', 'edge', 'notepad', 'calculator', 'paint',
                'word', 'excel', 'powerpoint', 'outlook', 'teams', 'skype',
                'spotify', 'vlc', 'photoshop', 'vscode', 'visual studio',
                'steam', 'discord', 'whatsapp', 'telegram'
            ],
            'system_locations': [
                'desktop', 'documentos', 'downloads', 'imagens', 'músicas',
                'vídeos', 'lixeira', 'área de trabalho', 'pasta do usuário'
            ],
            'time_expressions': [
                'agora', 'hoje', 'amanhã', 'ontem', 'esta semana', 'próxima semana',
                'este mês', 'próximo mês', 'em 5 minutos', 'em 1 hora', 'às 15h'
            ]
        }
        
        # Contexto da conversa
        self.conversation_context = {
            'last_intent': None,
            'last_entities': {},
            'conversation_history': [],
            'current_task': None,
            'user_preferences': {}
        }
    
    def process_text(self, text: str) -> Dict[str, Any]:
        """
        Processa texto com análise completa de NLP
        
        Args:
            text: Texto a ser processado
            
        Returns:
            Resultado completo da análise
        """
        try:
            result = {
                'original_text': text,
                'processed_text': self._preprocess_text(text),
                'intent': None,
                'entities': {},
                'confidence': 0.0,
                'context': self.conversation_context.copy(),
                'linguistic_analysis': {},
                'action_plan': []
            }
            
            # Pré-processamento
            processed_text = result['processed_text']
            
            # Análise linguística com spaCy (se disponível)
            if self.nlp:
                result['linguistic_analysis'] = self._analyze_with_spacy(processed_text)
            
            # Classificação de intenção
            intent_result = self._classify_intent(processed_text)
            result['intent'] = intent_result['intent']
            result['confidence'] = intent_result['confidence']
            
            # Extração de entidades
            result['entities'] = self._extract_entities(processed_text, result['intent'])
            
            # Análise de contexto
            result['context'] = self._analyze_context(result)
            
            # Geração de plano de ação
            result['action_plan'] = self._generate_action_plan(result)
            
            # Atualizar contexto da conversa
            self._update_conversation_context(result)
            
            self.logger.debug(f"NLP processado: {result['intent']} (confiança: {result['confidence']:.2f})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro no processamento NLP: {e}")
            return {
                'original_text': text,
                'processed_text': text,
                'intent': 'unknown',
                'entities': {},
                'confidence': 0.0,
                'context': {},
                'linguistic_analysis': {},
                'action_plan': [],
                'error': str(e)
            }
    
    def _preprocess_text(self, text: str) -> str:
        """Pré-processa o texto"""
        # Normalizar espaços
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Converter para minúsculas
        text = text.lower()
        
        # Normalizar contrações
        contractions = {
            'não': 'nao',
            'você': 'voce',
            'está': 'esta',
            'é': 'e',
            'ção': 'cao',
            'õ': 'o'
        }
        
        for original, replacement in contractions.items():
            text = text.replace(original, replacement)
        
        return text
    
    def _analyze_with_spacy(self, text: str) -> Dict[str, Any]:
        """Análise linguística com spaCy"""
        doc = self.nlp(text)
        
        return {
            'tokens': [token.text for token in doc],
            'lemmas': [token.lemma_ for token in doc],
            'pos_tags': [(token.text, token.pos_) for token in doc],
            'named_entities': [(ent.text, ent.label_) for ent in doc.ents],
            'dependencies': [(token.text, token.dep_, token.head.text) for token in doc],
            'sentences': [sent.text for sent in doc.sents]
        }
    
    def _classify_intent(self, text: str) -> Dict[str, Any]:
        """Classifica a intenção do texto"""
        best_intent = 'unknown'
        best_confidence = 0.0
        
        for intent, data in self.intent_patterns.items():
            confidence = 0.0
            matches = 0
            
            for pattern in data['patterns']:
                if re.search(pattern, text, re.IGNORECASE):
                    matches += 1
                    confidence += 0.8  # Alta confiança para match de padrão
            
            # Normalizar confiança
            if matches > 0:
                confidence = min(confidence / len(data['patterns']), 1.0)
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_intent = intent
        
        return {
            'intent': best_intent,
            'confidence': best_confidence
        }
    
    def _extract_entities(self, text: str, intent: str) -> Dict[str, Any]:
        """Extrai entidades do texto baseado na intenção"""
        entities = {}
        
        if intent in self.intent_patterns:
            patterns = self.intent_patterns[intent]['patterns']
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    
                    # Mapear grupos para entidades baseado na intenção
                    if intent == 'system_control':
                        if len(groups) >= 2:
                            entities['action'] = groups[0]
                            entities['target'] = groups[1]
                    
                    elif intent == 'file_management':
                        if len(groups) >= 4:
                            entities['action'] = groups[0]
                            entities['file_type'] = groups[2]
                            entities['file_name'] = groups[3]
                    
                    elif intent == 'web_automation':
                        if len(groups) >= 4:
                            entities['action'] = groups[0]
                            entities['platform'] = groups[2]
                            entities['query'] = groups[3]
                    
                    break
        
        # Extrair entidades customizadas
        entities.update(self._extract_custom_entities(text))
        
        return entities
    
    def _extract_custom_entities(self, text: str) -> Dict[str, List[str]]:
        """Extrai entidades customizadas"""
        entities = {}
        
        for entity_type, entity_list in self.custom_entities.items():
            found_entities = []
            
            for entity in entity_list:
                if entity.lower() in text.lower():
                    found_entities.append(entity)
            
            if found_entities:
                entities[entity_type] = found_entities
        
        return entities
    
    def _analyze_context(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa o contexto da conversa"""
        context = self.conversation_context.copy()
        
        # Analisar continuidade da conversa
        if context['last_intent'] == result['intent']:
            context['conversation_continuity'] = True
        else:
            context['conversation_continuity'] = False
        
        # Analisar referências pronominais
        pronouns = ['isso', 'aquilo', 'ele', 'ela', 'isto']
        has_pronouns = any(pronoun in result['processed_text'] for pronoun in pronouns)
        
        if has_pronouns and context['last_entities']:
            context['pronoun_resolution'] = context['last_entities']
        
        # Determinar urgência
        urgency_words = ['urgente', 'rápido', 'agora', 'imediatamente', 'já']
        context['urgency'] = any(word in result['processed_text'] for word in urgency_words)
        
        return context
    
    def _generate_action_plan(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gera plano de ação baseado na análise"""
        actions = []
        
        intent = result['intent']
        entities = result['entities']
        
        if intent == 'system_control':
            if 'action' in entities and 'target' in entities:
                actions.append({
                    'type': 'system_command',
                    'action': entities['action'],
                    'target': entities['target'],
                    'priority': 'high'
                })
        
        elif intent == 'file_management':
            actions.append({
                'type': 'file_operation',
                'operation': entities.get('action', 'unknown'),
                'file_path': entities.get('file_name', ''),
                'priority': 'medium'
            })
        
        elif intent == 'web_automation':
            actions.append({
                'type': 'web_action',
                'platform': entities.get('platform', 'browser'),
                'query': entities.get('query', ''),
                'priority': 'medium'
            })
        
        elif intent == 'information_query':
            actions.append({
                'type': 'information_retrieval',
                'query_type': 'general',
                'query': result['original_text'],
                'priority': 'low'
            })
        
        elif intent == 'automation':
            actions.append({
                'type': 'automation_task',
                'task_type': 'schedule',
                'parameters': entities,
                'priority': 'medium'
            })
        
        elif intent == 'learning':
            actions.append({
                'type': 'knowledge_management',
                'operation': 'store' if 'aprend' in result['processed_text'] else 'retrieve',
                'content': entities.get('information_content', ''),
                'priority': 'low'
            })
        
        return actions
    
    def _update_conversation_context(self, result: Dict[str, Any]):
        """Atualiza o contexto da conversa"""
        self.conversation_context['last_intent'] = result['intent']
        self.conversation_context['last_entities'] = result['entities']
        
        # Adicionar ao histórico
        self.conversation_context['conversation_history'].append({
            'timestamp': datetime.now().isoformat(),
            'text': result['original_text'],
            'intent': result['intent'],
            'confidence': result['confidence']
        })
        
        # Manter apenas últimas 10 interações
        if len(self.conversation_context['conversation_history']) > 10:
            self.conversation_context['conversation_history'] = \
                self.conversation_context['conversation_history'][-10:]
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Retorna resumo da conversa atual"""
        return {
            'total_interactions': len(self.conversation_context['conversation_history']),
            'recent_intents': [
                item['intent'] for item in 
                self.conversation_context['conversation_history'][-5:]
            ],
            'current_context': self.conversation_context['current_task'],
            'user_preferences': self.conversation_context['user_preferences']
        }
    
    def reset_context(self):
        """Reseta o contexto da conversa"""
        self.conversation_context = {
            'last_intent': None,
            'last_entities': {},
            'conversation_history': [],
            'current_task': None,
            'user_preferences': self.conversation_context.get('user_preferences', {})
        }
        self.logger.info("Contexto da conversa resetado")
