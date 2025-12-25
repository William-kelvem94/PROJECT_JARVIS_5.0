"""
Processador de comandos para JARVIS com IA Conversacional
"""

from typing import Dict, Callable, Optional, Any
import re

from ..core.logger import default_logger
from .system_commands import SystemCommands
from .utility_commands import UtilityCommands

# Importar IA conversacional
try:
    from ..ai.conversation_engine import ConversationEngine
    from ..ai.nlp_processor import AdvancedNLPProcessor
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class CommandProcessor:
    """Processador central de comandos do JARVIS com IA conversacional"""
    
    def __init__(self, config: Dict[str, Any], speech_engine, recognition_engine):
        self.config = config
        self.speech_engine = speech_engine
        self.recognition_engine = recognition_engine
        self.logger = default_logger
        
        # Inicializar módulos de comandos
        self.system_commands = SystemCommands(config, speech_engine)
        self.utility_commands = UtilityCommands(config, speech_engine)
        
        # Inicializar IA conversacional se disponível
        if AI_AVAILABLE:
            try:
                self.conversation_engine = ConversationEngine(config)
                self.nlp_processor = AdvancedNLPProcessor(config)
                self.ai_enabled = True
                self.logger.info("IA conversacional ativada no processador de comandos")
            except Exception as e:
                self.logger.warning(f"Erro ao inicializar IA conversacional: {e}")
                self.ai_enabled = False
        else:
            self.ai_enabled = False
            self.logger.info("IA conversacional não disponível - usando processamento básico")
        
        # Mapa de comandos (fallback)
        self.command_map = self._build_command_map()
        
        self.logger.info("Processador de comandos inicializado")
    
    def _build_command_map(self) -> Dict[str, Callable]:
        """Constrói mapa de comandos disponíveis"""
        return {
            # Comandos do sistema
            'abrir': self.system_commands.open_program,
            'executar': self.system_commands.execute_command,
            'fechar': self.system_commands.close_program,
            
            # Comandos utilitários
            'hora': self.utility_commands.tell_time,
            'data': self.utility_commands.tell_date,
            'calcular': self.utility_commands.calculate,
            'pesquisar': self.utility_commands.search_web,
            
            # Comandos de controle
            'ajuda': self._show_help,
            'sair': self._exit_assistant,
            'calibrar': self._calibrate_microphone,
            'testar': self._test_systems,
        }
    
    def process_command(self, command_text: str) -> bool:
        """
        Processa um comando de texto com IA conversacional
        
        Args:
            command_text: Texto do comando
            
        Returns:
            True se comando foi processado, False se deve sair
        """
        if not command_text or command_text.strip() == "":
            return True
        
        command_text = command_text.strip()
        
        # Verificar comandos de saída primeiro
        exit_phrases = self.config.get('commands', {}).get('exit_phrases', ['sair'])
        if any(phrase in command_text.lower() for phrase in exit_phrases):
            return self._exit_assistant(command_text)
        
        # Tratar casos especiais de reconhecimento
        if command_text == "não_entendi":
            self.speech_engine.speak(
                "Desculpe, mas não consegui entender o que você disse. Pode repetir, por favor?",
                emotion='preocupado'
            )
            return True
        
        if command_text == "erro_conexao":
            self.speech_engine.speak(
                "Ops! Parece que há um problema com a conexão. Verifique sua internet e tente novamente.",
                emotion='preocupado'
            )
            return True
        
        # Processar com IA conversacional se disponível
        if self.ai_enabled:
            return self._process_with_ai(command_text)
        else:
            return self._process_basic(command_text)
    
    def _process_with_ai(self, command_text: str) -> bool:
        """Processa comando usando IA conversacional"""
        try:
            self.logger.command_event(command_text, "processing_ai")
            
            # Análise NLP avançada
            nlp_result = self.nlp_processor.process_text(command_text)
            
            # Processamento conversacional
            conversation_result = self.conversation_engine.process_conversation(command_text, nlp_result)
            
            # Falar a resposta conversacional
            response_text = conversation_result.get('text', 'Entendi!')
            emotion = conversation_result.get('emotion', 'pensativo')
            
            self.speech_engine.speak(response_text, emotion=emotion)
            
            # Se requer ação, executar
            if conversation_result.get('requires_action', False):
                action_success = self._execute_ai_action(conversation_result, nlp_result)
                
                if not action_success:
                    # Se ação falhou, dar feedback
                    self.speech_engine.speak(
                        "Hmm, tive uma pequena dificuldade para executar isso. Pode tentar de outra forma?",
                        emotion='preocupado'
                    )
            
            self.logger.command_event(command_text, "completed_ai")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro no processamento com IA: {e}")
            # Fallback para processamento básico
            return self._process_basic(command_text)
    
    def _execute_ai_action(self, conversation_result: Dict[str, Any], nlp_result: Dict[str, Any]) -> bool:
        """Executa ação baseada no resultado da IA"""
        try:
            # Verificar tipo de ação sugerida
            suggested_action = conversation_result.get('suggested_action')
            
            if suggested_action == 'web_search':
                # Pesquisa web
                query = conversation_result.get('search_query', '')
                return self._execute_web_search(query)
            
            # Usar plano de ação do NLP
            action_plan = nlp_result.get('action_plan', [])
            
            if not action_plan:
                return False
            
            # Executar primeira ação do plano
            action = action_plan[0]
            action_type = action.get('type', 'unknown')
            
            if action_type == 'system_command':
                return self._execute_system_action(action)
            elif action_type == 'file_operation':
                return self._execute_file_action(action)
            elif action_type == 'web_action':
                return self._execute_web_action(action)
            elif action_type == 'information_retrieval':
                return self._execute_info_retrieval(action)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro ao executar ação da IA: {e}")
            return False
    
    def _execute_system_action(self, action: Dict[str, Any]) -> bool:
        """Executa ação do sistema"""
        try:
            action_name = action.get('action', '').lower()
            target = action.get('target', '')
            
            # Mapear para comandos do sistema
            if any(word in action_name for word in ['abr', 'execut', 'inici', 'rod']):
                return self.system_commands.open_program(f"abrir {target}")
            elif any(word in action_name for word in ['fech', 'encerr', 'mat', 'par']):
                return self.system_commands.close_program(f"fechar {target}")
            else:
                return self.system_commands.execute_command(f"{action_name} {target}")
                
        except Exception as e:
            self.logger.error(f"Erro na ação do sistema: {e}")
            return False
    
    def _execute_file_action(self, action: Dict[str, Any]) -> bool:
        """Executa ação de arquivo"""
        try:
            operation = action.get('operation', '')
            file_path = action.get('file_path', '')
            
            # Mapear para comandos utilitários
            command = f"{operation} {file_path}"
            return self.utility_commands.execute_command(command)
            
        except Exception as e:
            self.logger.error(f"Erro na ação de arquivo: {e}")
            return False
    
    def _execute_web_action(self, action: Dict[str, Any]) -> bool:
        """Executa ação web"""
        try:
            platform = action.get('platform', 'google')
            query = action.get('query', '')
            
            # Construir URL baseada na plataforma
            if 'google' in platform.lower():
                search_query = f"google {query}"
            elif 'youtube' in platform.lower():
                search_query = f"youtube {query}"
            else:
                search_query = query
            
            return self.utility_commands.search_web(f"pesquisar {search_query}")
            
        except Exception as e:
            self.logger.error(f"Erro na ação web: {e}")
            return False
    
    def _execute_web_search(self, query: str) -> bool:
        """Executa pesquisa web"""
        try:
            return self.utility_commands.search_web(f"pesquisar {query}")
        except Exception as e:
            self.logger.error(f"Erro na pesquisa: {e}")
            return False
    
    def _execute_info_retrieval(self, action: Dict[str, Any]) -> bool:
        """Executa recuperação de informação"""
        try:
            query = action.get('query', '').lower()
            
            # Informações que podemos responder diretamente
            if any(word in query for word in ['hora', 'horas']):
                return self.utility_commands.tell_time("que horas são")
            elif any(word in query for word in ['data', 'dia', 'hoje']):
                return self.utility_commands.tell_date("que dia é hoje")
            else:
                # Para outras informações, fazer pesquisa
                return self.utility_commands.search_web(f"pesquisar {query}")
                
        except Exception as e:
            self.logger.error(f"Erro na recuperação de informação: {e}")
            return False
    
    def _process_basic(self, command_text: str) -> bool:
        """Processamento básico (fallback)"""
        command_text_lower = command_text.lower().strip()
        
        # Processar comando normal
        try:
            self.logger.command_event(command_text, "processing")
            
            # Procurar comando correspondente
            for keyword, handler in self.command_map.items():
                if keyword in command_text_lower:
                    try:
                        result = handler(command_text)
                        self.logger.command_event(command_text, "completed")
                        return result if isinstance(result, bool) else True
                    except Exception as e:
                        self.logger.error(f"Erro ao executar comando '{keyword}': {e}")
                        self.speech_engine.speak(
                            f"Ops! Ocorreu um erro ao executar o comando. Detalhes: {str(e)}",
                            emotion='preocupado'
                        )
                        return True
            
            # Comando não reconhecido
            self._handle_unknown_command(command_text)
            return True
            
        except Exception as e:
            self.logger.error(f"Erro no processamento de comando: {e}")
            self.speech_engine.speak(
                "Ocorreu um erro inesperado. Vamos tentar novamente?",
                emotion='preocupado'
            )
            return True
    
    def _handle_unknown_command(self, command_text: str):
        """Trata comandos não reconhecidos de forma mais natural"""
        self.logger.command_event(command_text, "unknown")
        
        # Respostas mais naturais e variadas
        natural_responses = [
            "Hmm, não tenho certeza sobre isso. Pode me explicar de outra forma?",
            "Interessante! Não reconheci esse comando, mas estou sempre aprendendo. Que tal tentar 'ajuda'?",
            "Não entendi muito bem. Pode reformular ou me dizer 'ajuda' para ver o que posso fazer?",
            "Essa é nova para mim! Que tal me contar mais detalhes ou pedir 'ajuda'?",
            "Hmm... não captei isso. Pode tentar de outro jeito ou dizer 'ajuda' para ver minhas opções?"
        ]
        
        import random
        response = random.choice(natural_responses)
        
        # Sugestões baseadas em similaridade
        suggestions = self._get_command_suggestions(command_text)
        if suggestions:
            response += f" Ou talvez você quis dizer '{suggestions[0]}'?"
        
        self.speech_engine.speak(response, emotion='pensativo')
    
    def _get_command_suggestions(self, command_text: str) -> list:
        """Gera sugestões de comandos baseadas em similaridade"""
        suggestions = []
        command_lower = command_text.lower()
        
        # Palavras-chave comuns com sugestões mais naturais
        if any(word in command_lower for word in ['abrir', 'abra', 'abre', 'execute', 'rode']):
            suggestions.append('abrir Chrome')
        elif any(word in command_lower for word in ['hora', 'horas', 'tempo']):
            suggestions.append('que horas são')
        elif any(word in command_lower for word in ['data', 'dia', 'hoje']):
            suggestions.append('que dia é hoje')
        elif any(word in command_lower for word in ['calcular', 'conta', 'soma', 'matemática']):
            suggestions.append('calcular 10 mais 5')
        elif any(word in command_lower for word in ['pesquisar', 'buscar', 'procurar', 'google']):
            suggestions.append('pesquisar Python')
        elif any(word in command_lower for word in ['como', 'você', 'está']):
            suggestions.append('como você está')
        elif any(word in command_lower for word in ['piada', 'engraçado', 'humor']):
            suggestions.append('conte uma piada')
        
        return suggestions
    
    def _show_help(self, command_text: str) -> bool:
        """Mostra comandos disponíveis de forma mais natural"""
        if self.ai_enabled:
            help_text = """Oi! Posso ajudar com muitas coisas. Olha só o que sei fazer:

            🖥️ Controlar o computador: "abra o Chrome", "feche o Notepad", "execute o calculadora"
            
            ⏰ Informações úteis: "que horas são", "qual é a data de hoje"
            
            🔢 Cálculos: "calcule 25 mais 15", "quanto é 10 vezes 3"
            
            🌐 Pesquisas: "pesquise sobre Python", "procure receitas de bolo"
            
            💬 Conversação: "como você está", "conte uma piada", "me fale sobre você"
            
            🔧 Sistema: "teste o microfone", "calibre o áudio"
            
            E muito mais! Pode conversar comigo naturalmente. Sou bem esperto! 😊
            
            O que gostaria de fazer primeiro?"""
        else:
            help_text = """Claro! Deixa eu te mostrar o que sei fazer:

            Para abrir programas: "abrir navegador", "abrir calculadora"
            Para informações: "que horas são", "qual é a data"
            Para cálculos: "calcular 25 mais 15"
            Para pesquisas: "pesquisar Python"
            Para testar: "testar microfone", "calibrar"
            Para sair: "sair"
            
            O que você gostaria de tentar?"""
        
        self.speech_engine.speak(help_text, final_pause=2.0)
        return True
    
    def _exit_assistant(self, command_text: str) -> bool:
        """Encerra o assistente de forma natural"""
        farewell_messages = [
            "Até logo! Foi um prazer conversar com você. Volte sempre que precisar!",
            "Tchau! Adorei nossa conversa. Estarei aqui quando quiser falar novamente!",
            "Até mais! Espero ter sido útil. Nos vemos em breve!",
            "Bye bye! Foi ótimo ajudar você hoje. Até a próxima!",
            "Até logo! Qualquer coisa, é só me chamar. Cuide-se!"
        ]
        
        import random
        message = random.choice(farewell_messages)
        
        self.speech_engine.speak(message, emotion='aliviado')
        return False
    
    def _calibrate_microphone(self, command_text: str) -> bool:
        """Calibra o microfone"""
        self.speech_engine.speak("Vou calibrar o microfone. Mantenha silêncio por alguns segundos.")
        
        if self.recognition_engine.calibrate():
            self.speech_engine.speak("Calibração concluída com sucesso!", emotion='entusiasta')
        else:
            self.speech_engine.speak("Não consegui calibrar o microfone. Verifique se está funcionando.", emotion='preocupado')
        
        return True
    
    def _test_systems(self, command_text: str) -> bool:
        """Testa sistemas do JARVIS"""
        if 'microfone' in command_text:
            self.speech_engine.speak("Testando microfone...")
            if self.recognition_engine.test_microphone():
                self.speech_engine.speak("Microfone funcionando perfeitamente!", emotion='entusiasta')
            else:
                self.speech_engine.speak("Problema detectado no microfone.", emotion='preocupado')
        
        elif 'voz' in command_text:
            self.speech_engine.speak("Testando sistema de voz...")
            if self.speech_engine.test_voice():
                self.speech_engine.speak("Sistema de voz funcionando perfeitamente!", emotion='entusiasta')
            else:
                self.speech_engine.speak("Problema detectado no sistema de voz.", emotion='preocupado')
        
        else:
            # Teste geral
            self.speech_engine.speak("Executando teste geral dos sistemas...")
            
            mic_ok = self.recognition_engine.test_microphone()
            voice_ok = self.speech_engine.test_voice()
            
            if mic_ok and voice_ok:
                self.speech_engine.speak("Todos os sistemas funcionando perfeitamente!", emotion='entusiasta')
            else:
                issues = []
                if not mic_ok:
                    issues.append("microfone")
                if not voice_ok:
                    issues.append("voz")
                
                self.speech_engine.speak(
                    f"Problemas detectados em: {', '.join(issues)}",
                    emotion='preocupado'
                )
        
        return True
    
    def get_available_commands(self) -> list:
        """Retorna lista de comandos disponíveis"""
        return list(self.command_map.keys())
    
    def add_custom_command(self, keyword: str, handler: Callable):
        """Adiciona comando personalizado"""
        self.command_map[keyword] = handler
        self.logger.info(f"Comando personalizado adicionado: {keyword}")
    
    def remove_command(self, keyword: str) -> bool:
        """Remove comando"""
        if keyword in self.command_map:
            del self.command_map[keyword]
            self.logger.info(f"Comando removido: {keyword}")
            return True
        return False