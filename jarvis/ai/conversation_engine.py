"""
Motor de Conversação Natural
Sistema de diálogo inteligente e natural para o JARVIS
"""

import re
import json
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import requests
from ..core.logger import default_logger


class ConversationEngine:
    """Motor de conversação natural e inteligente"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = default_logger
        
        # Personalidade do JARVIS
        self.personality = {
            'name': 'JARVIS',
            'traits': ['inteligente', 'prestativo', 'educado', 'eficiente', 'amigável'],
            'humor_level': 0.3,  # 0-1, quanto humor usar
            'formality_level': 0.4,  # 0-1, quão formal ser
            'enthusiasm_level': 0.6  # 0-1, quão entusiasmado ser
        }
        
        # Base de conhecimento conversacional
        self.knowledge_base = {
            'greetings': {
                'patterns': [
                    r'(oi|olá|hey|e aí|opa|salve)',
                    r'(bom dia|boa tarde|boa noite)',
                    r'(como vai|tudo bem|como está)'
                ],
                'responses': [
                    "Olá! Como posso ajudá-lo hoje?",
                    "Oi! É um prazer falar com você. Em que posso ser útil?",
                    "Olá! Estou aqui e pronto para ajudar. O que precisa?",
                    "Oi! Como está? Em que posso auxiliá-lo?",
                    "Olá! Que bom ter você aqui. Como posso ajudar?"
                ]
            },
            'capabilities': {
                'patterns': [
                    r'(o que você|que você|você consegue|pode fazer|suas funções)',
                    r'(me ajuda|ajudar|fazer por mim|capacidades)',
                    r'(quais são|lista|comandos disponíveis)'
                ],
                'responses': [
                    "Posso fazer muitas coisas! Controlo seu computador, abro programas, gerencio arquivos, pesquiso na internet, respondo perguntas, e muito mais. Que tal me dizer o que precisa?",
                    "Sou seu assistente pessoal! Posso executar aplicações, controlar o sistema, organizar arquivos, fazer pesquisas, calcular, e conversar sobre diversos assuntos. O que gostaria de fazer?",
                    "Tenho várias habilidades: automação do Windows, controle de aplicações, gerenciamento de arquivos, pesquisas web, cálculos, e conversação natural. Como posso ajudá-lo especificamente?",
                    "Estou aqui para tornar sua vida mais fácil! Posso abrir programas, organizar arquivos, controlar o sistema, pesquisar informações, e muito mais. Qual tarefa posso realizar para você?"
                ]
            },
            'personal_questions': {
                'patterns': [
                    r'(quem é você|seu nome|como se chama)',
                    r'(você é|o que é|tipo de)',
                    r'(de onde vem|criado|desenvolvido)'
                ],
                'responses': [
                    "Sou o JARVIS, seu assistente de voz inteligente! Fui criado para ser seu companheiro digital e ajudá-lo com diversas tarefas.",
                    "Me chamo JARVIS - Just A Rather Very Intelligent System. Sou um assistente de IA desenvolvido para tornar sua experiência com o computador mais natural e eficiente.",
                    "Sou o JARVIS, um assistente virtual inteligente. Minha missão é ajudá-lo de forma natural e eficiente em suas tarefas diárias.",
                    "Eu sou o JARVIS! Pense em mim como seu assistente pessoal digital, sempre pronto para ajudar com o que precisar."
                ]
            },
            'time_questions': {
                'patterns': [
                    r'(que horas|hora atual|horário)',
                    r'(que dia|data de hoje|hoje é)',
                    r'(ano|mês|semana)'
                ],
                'responses': self._generate_time_responses
            },
            'weather': {
                'patterns': [
                    r'(clima|tempo|temperatura|chuva|sol)',
                    r'(previsão|meteorologia|weather)'
                ],
                'responses': [
                    "Infelizmente não tenho acesso direto a informações meteorológicas no momento. Posso abrir um site de previsão do tempo para você, se quiser!",
                    "Para informações sobre o clima, posso abrir o site do tempo.com ou climatempo.com.br. Gostaria que eu fizesse isso?",
                    "Não tenho dados meteorológicos atuais, mas posso pesquisar a previsão do tempo na internet para você. Qual cidade te interessa?"
                ]
            },
            'compliments': {
                'patterns': [
                    r'(obrigado|obrigada|valeu|thanks)',
                    r'(muito bom|excelente|perfeito|ótimo)',
                    r'(parabéns|legal|incrível|fantástico)'
                ],
                'responses': [
                    "Fico feliz em ajudar! É para isso que estou aqui.",
                    "Por nada! Sempre que precisar, estarei disponível.",
                    "Que bom que foi útil! Conte comigo sempre que necessário.",
                    "Obrigado pelo elogio! Adoro quando posso ser útil.",
                    "É um prazer ajudar! Estou sempre aqui quando precisar."
                ]
            },
            'jokes_humor': {
                'patterns': [
                    r'(piada|humor|engraçado|rir)',
                    r'(conte uma|me faz rir|algo divertido)'
                ],
                'responses': [
                    "Por que os programadores preferem o modo escuro? Porque a luz atrai bugs! 😄",
                    "Qual é o cúmulo da velocidade? É apertar Ctrl+Z antes de Ctrl+C! 😂",
                    "Por que o computador foi ao médico? Porque estava com vírus! 🤖",
                    "O que o Java falou para o C++? Você é muito complicado, eu sou mais simples! ☕",
                    "Por que o Wi-Fi e o Bluetooth terminaram? Porque não conseguiam se conectar emocionalmente! 📶"
                ]
            },
            'feelings': {
                'patterns': [
                    r'(como você está|tudo bem com você|se sente)',
                    r'(feliz|triste|cansado|animado)'
                ],
                'responses': [
                    "Estou ótimo, obrigado por perguntar! Sempre energizado e pronto para ajudar. E você, como está?",
                    "Me sinto muito bem! Adoro quando posso ser útil. Como está seu dia?",
                    "Estou excelente! Cada interação me deixa mais animado para ajudar. E você?",
                    "Muito bem, obrigado! Sempre feliz quando posso conversar e ajudar. Como você está se sentindo?"
                ]
            },
            'small_talk': {
                'patterns': [
                    r'(conversar|bater papo|falar sobre)',
                    r'(interessante|legal|curioso)',
                    r'(você gosta|prefere|acha)'
                ],
                'responses': [
                    "Adoro conversar! Sobre o que gostaria de falar? Posso discutir tecnologia, curiosidades, ou qualquer assunto que interesse você.",
                    "Que bom que quer conversar! Sou curioso sobre muitos assuntos. Tem algum tópico específico em mente?",
                    "Conversas são ótimas! Posso falar sobre ciência, tecnologia, curiosidades do mundo, ou o que você quiser. Do que gostaria de falar?",
                    "Sempre disponível para uma boa conversa! Que tal me contar algo interessante sobre seu dia ou algum assunto que te fascina?"
                ]
            },
            'unknown_friendly': [
                "Hmm, não tenho certeza sobre isso, mas posso tentar ajudar de outra forma. Pode me explicar melhor o que precisa?",
                "Interessante pergunta! Não tenho essa informação específica, mas posso pesquisar na internet para você, se quiser.",
                "Não sei exatamente sobre isso, mas estou sempre aprendendo! Posso tentar encontrar a resposta ou ajudar com algo relacionado?",
                "Essa é nova para mim! Que tal reformular a pergunta ou me dizer como posso ajudar de outra maneira?",
                "Não tenho certeza, mas adoro aprender coisas novas! Pode me dar mais detalhes sobre o que está procurando?"
            ]
        }
        
        # Contexto da conversa
        self.conversation_context = {
            'user_name': None,
            'conversation_mood': 'neutral',
            'topics_discussed': [],
            'last_question_type': None,
            'user_preferences': {},
            'conversation_flow': []
        }
        
        # Memória de curto prazo
        self.short_term_memory = []
        
        self.logger.info("Conversation Engine inicializado com personalidade natural")
    
    def process_conversation(self, user_input: str, nlp_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa entrada conversacional e gera resposta natural
        
        Args:
            user_input: Texto do usuário
            nlp_result: Resultado do processamento NLP
            
        Returns:
            Resposta conversacional completa
        """
        try:
            # Adicionar à memória de curto prazo
            self._add_to_memory(user_input, 'user')
            
            # Detectar tipo de conversa
            conversation_type = self._detect_conversation_type(user_input)
            
            # Gerar resposta baseada no tipo
            if conversation_type == 'greeting':
                response = self._handle_greeting(user_input)
            elif conversation_type == 'question':
                response = self._handle_question(user_input, nlp_result)
            elif conversation_type == 'command':
                response = self._handle_command_conversation(user_input, nlp_result)
            elif conversation_type == 'small_talk':
                response = self._handle_small_talk(user_input)
            elif conversation_type == 'personal':
                response = self._handle_personal_question(user_input)
            else:
                response = self._handle_unknown_input(user_input)
            
            # Adicionar personalidade à resposta
            response = self._add_personality(response, conversation_type)
            
            # Atualizar contexto
            self._update_conversation_context(user_input, response, conversation_type)
            
            # Adicionar resposta à memória
            self._add_to_memory(response['text'], 'assistant')
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erro no processamento conversacional: {e}")
            return {
                'text': "Desculpe, tive um pequeno problema para processar isso. Pode tentar novamente?",
                'emotion': 'preocupado',
                'confidence': 0.5,
                'type': 'error',
                'requires_action': False
            }
    
    def _detect_conversation_type(self, text: str) -> str:
        """Detecta o tipo de conversa"""
        text_lower = text.lower()
        
        # Verificar padrões específicos
        for category, data in self.knowledge_base.items():
            if isinstance(data, dict) and 'patterns' in data:
                for pattern in data['patterns']:
                    if re.search(pattern, text_lower):
                        if category == 'greetings':
                            return 'greeting'
                        elif category in ['capabilities', 'time_questions', 'weather']:
                            return 'question'
                        elif category == 'personal_questions':
                            return 'personal'
                        elif category in ['small_talk', 'jokes_humor', 'feelings']:
                            return 'small_talk'
        
        # Verificar se é comando (baseado no NLP)
        command_indicators = ['abr', 'fech', 'execut', 'cri', 'delet', 'pesquis', 'calcul']
        if any(indicator in text_lower for indicator in command_indicators):
            return 'command'
        
        # Verificar se é pergunta
        question_indicators = ['?', 'como', 'quando', 'onde', 'por que', 'o que', 'qual']
        if any(indicator in text_lower for indicator in question_indicators):
            return 'question'
        
        return 'unknown'
    
    def _handle_greeting(self, text: str) -> Dict[str, Any]:
        """Lida com cumprimentos"""
        responses = self.knowledge_base['greetings']['responses']
        
        # Personalizar baseado no horário
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 12:
            time_responses = [
                "Bom dia! Como posso ajudá-lo hoje?",
                "Olá! Que bom começar o dia conversando com você. Em que posso ser útil?"
            ]
        elif 12 <= current_hour < 18:
            time_responses = [
                "Boa tarde! Como está seu dia? Em que posso ajudar?",
                "Olá! Espero que esteja tendo uma tarde produtiva. Como posso auxiliá-lo?"
            ]
        elif 18 <= current_hour < 22:
            time_responses = [
                "Boa noite! Como foi seu dia? Em que posso ajudar?",
                "Olá! Que bom falar com você nesta noite. Como posso ser útil?"
            ]
        else:
            time_responses = [
                "Olá! Trabalhando até tarde? Como posso ajudá-lo?",
                "Oi! Ainda acordado? Em que posso ser útil nesta madrugada?"
            ]
        
        # Combinar respostas gerais com específicas do horário
        all_responses = responses + time_responses
        response_text = random.choice(all_responses)
        
        return {
            'text': response_text,
            'emotion': 'entusiasta',
            'confidence': 0.9,
            'type': 'greeting',
            'requires_action': False
        }
    
    def _handle_question(self, text: str, nlp_result: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com perguntas"""
        text_lower = text.lower()
        
        # Verificar tipos específicos de pergunta
        for category, data in self.knowledge_base.items():
            if isinstance(data, dict) and 'patterns' in data:
                for pattern in data['patterns']:
                    if re.search(pattern, text_lower):
                        if callable(data['responses']):
                            response_text = data['responses']()
                        else:
                            response_text = random.choice(data['responses'])
                        
                        return {
                            'text': response_text,
                            'emotion': 'pensativo',
                            'confidence': 0.8,
                            'type': 'question_answer',
                            'requires_action': False
                        }
        
        # Pergunta não reconhecida - tentar ser útil
        helpful_responses = [
            "Essa é uma pergunta interessante! Infelizmente não tenho essa informação específica, mas posso pesquisar na internet para você. Gostaria?",
            "Hmm, não sei exatamente sobre isso. Que tal eu fazer uma pesquisa online para encontrar a resposta?",
            "Não tenho certeza sobre essa pergunta específica. Posso tentar encontrar a informação na web, se quiser!",
            "Interessante pergunta! Não tenho essa resposta na ponta da língua, mas posso pesquisar para você. Quer que eu faça isso?"
        ]
        
        return {
            'text': random.choice(helpful_responses),
            'emotion': 'pensativo',
            'confidence': 0.6,
            'type': 'question_unknown',
            'requires_action': True,
            'suggested_action': 'web_search',
            'search_query': text
        }
    
    def _handle_command_conversation(self, text: str, nlp_result: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com comandos de forma conversacional"""
        intent = nlp_result.get('intent', 'unknown')
        confidence = nlp_result.get('confidence', 0.0)
        
        # Respostas conversacionais para comandos
        command_responses = {
            'system_control': [
                "Claro! Vou executar isso para você.",
                "Perfeito! Já estou cuidando disso.",
                "Entendido! Executando agora.",
                "Pode deixar comigo! Fazendo isso agora."
            ],
            'file_management': [
                "Certo! Vou organizar isso para você.",
                "Entendi! Cuidando dos arquivos agora.",
                "Perfeito! Já estou trabalhando nisso.",
                "Pode contar comigo! Organizando os arquivos."
            ],
            'web_automation': [
                "Ótima ideia! Vou abrir isso para você.",
                "Claro! Navegando para lá agora.",
                "Perfeito! Já estou acessando.",
                "Entendido! Abrindo o site agora."
            ]
        }
        
        if intent in command_responses:
            response_text = random.choice(command_responses[intent])
            emotion = 'entusiasta'
        else:
            response_text = "Entendi o que você quer! Vou tentar executar isso para você."
            emotion = 'pensativo'
        
        return {
            'text': response_text,
            'emotion': emotion,
            'confidence': confidence,
            'type': 'command_acknowledgment',
            'requires_action': True,
            'nlp_result': nlp_result
        }
    
    def _handle_small_talk(self, text: str) -> Dict[str, Any]:
        """Lida com conversa casual"""
        text_lower = text.lower()
        
        # Verificar padrões específicos
        for category in ['compliments', 'jokes_humor', 'feelings', 'small_talk']:
            if category in self.knowledge_base:
                data = self.knowledge_base[category]
                if isinstance(data, dict) and 'patterns' in data:
                    for pattern in data['patterns']:
                        if re.search(pattern, text_lower):
                            response_text = random.choice(data['responses'])
                            
                            return {
                                'text': response_text,
                                'emotion': 'entusiasta' if category == 'jokes_humor' else 'aliviado',
                                'confidence': 0.8,
                                'type': 'small_talk',
                                'requires_action': False
                            }
        
        # Conversa casual genérica
        casual_responses = [
            "Que interessante! Conte-me mais sobre isso.",
            "Legal! Adoro quando podemos conversar assim.",
            "Hmm, que bacana! O que mais você gostaria de compartilhar?",
            "Interessante ponto de vista! Como você chegou a essa conclusão?",
            "Que legal! Sempre gosto de aprender algo novo."
        ]
        
        return {
            'text': random.choice(casual_responses),
            'emotion': 'entusiasta',
            'confidence': 0.7,
            'type': 'casual_conversation',
            'requires_action': False
        }
    
    def _handle_personal_question(self, text: str) -> Dict[str, Any]:
        """Lida com perguntas pessoais sobre o JARVIS"""
        responses = self.knowledge_base['personal_questions']['responses']
        response_text = random.choice(responses)
        
        return {
            'text': response_text,
            'emotion': 'entusiasta',
            'confidence': 0.9,
            'type': 'personal_info',
            'requires_action': False
        }
    
    def _handle_unknown_input(self, text: str) -> Dict[str, Any]:
        """Lida com entrada não reconhecida de forma amigável"""
        responses = self.knowledge_base['unknown_friendly']
        response_text = random.choice(responses)
        
        return {
            'text': response_text,
            'emotion': 'pensativo',
            'confidence': 0.4,
            'type': 'clarification_needed',
            'requires_action': False
        }
    
    def _generate_time_responses(self) -> str:
        """Gera respostas sobre horário/data"""
        now = datetime.now()
        
        time_responses = [
            f"Agora são {now.strftime('%H:%M')} do dia {now.strftime('%d/%m/%Y')}.",
            f"São {now.strftime('%H:%M')} de {now.strftime('%A, %d de %B de %Y')}.",
            f"O horário atual é {now.strftime('%H:%M')} e hoje é {now.strftime('%d/%m/%Y')}."
        ]
        
        return random.choice(time_responses)
    
    def _add_personality(self, response: Dict[str, Any], conversation_type: str) -> Dict[str, Any]:
        """Adiciona traços de personalidade à resposta"""
        
        # Adicionar humor ocasionalmente
        if (self.personality['humor_level'] > 0.5 and 
            random.random() < 0.2 and 
            conversation_type not in ['command', 'error']):
            
            humor_additions = [
                " 😊", " 🤖", " 😄", " 👍", " ✨"
            ]
            response['text'] += random.choice(humor_additions)
        
        # Ajustar formalidade
        if self.personality['formality_level'] < 0.3:
            # Mais casual
            response['text'] = response['text'].replace('Gostaria', 'Quer')
            response['text'] = response['text'].replace('Poderia', 'Pode')
        
        # Ajustar entusiasmo
        if (self.personality['enthusiasm_level'] > 0.7 and 
            response['emotion'] == 'entusiasta'):
            
            enthusiasm_additions = [
                " Que legal!", " Adorei!", " Perfeito!", " Excelente!"
            ]
            if random.random() < 0.3:
                response['text'] += random.choice(enthusiasm_additions)
        
        return response
    
    def _update_conversation_context(self, user_input: str, response: Dict[str, Any], conv_type: str):
        """Atualiza contexto da conversa"""
        self.conversation_context['last_question_type'] = conv_type
        self.conversation_context['conversation_flow'].append({
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'response_type': conv_type,
            'response_emotion': response['emotion']
        })
        
        # Manter apenas últimas 20 interações
        if len(self.conversation_context['conversation_flow']) > 20:
            self.conversation_context['conversation_flow'] = \
                self.conversation_context['conversation_flow'][-20:]
    
    def _add_to_memory(self, text: str, speaker: str):
        """Adiciona à memória de curto prazo"""
        self.short_term_memory.append({
            'timestamp': datetime.now().isoformat(),
            'speaker': speaker,
            'text': text
        })
        
        # Manter apenas últimas 10 mensagens
        if len(self.short_term_memory) > 10:
            self.short_term_memory = self.short_term_memory[-10:]
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Retorna resumo da conversa"""
        return {
            'total_interactions': len(self.conversation_context['conversation_flow']),
            'conversation_mood': self.conversation_context['conversation_mood'],
            'topics_discussed': self.conversation_context['topics_discussed'],
            'user_name': self.conversation_context['user_name'],
            'recent_memory': self.short_term_memory[-5:] if self.short_term_memory else []
        }
    
    def set_user_name(self, name: str):
        """Define nome do usuário"""
        self.conversation_context['user_name'] = name
        self.logger.info(f"Nome do usuário definido: {name}")
    
    def reset_conversation(self):
        """Reseta contexto da conversa"""
        self.conversation_context = {
            'user_name': self.conversation_context.get('user_name'),  # Manter nome
            'conversation_mood': 'neutral',
            'topics_discussed': [],
            'last_question_type': None,
            'user_preferences': self.conversation_context.get('user_preferences', {}),  # Manter preferências
            'conversation_flow': []
        }
        self.short_term_memory = []
        self.logger.info("Contexto da conversa resetado")
