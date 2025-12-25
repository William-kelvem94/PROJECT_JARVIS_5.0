"""
Classe principal do assistente JARVIS
"""

import time
from typing import Optional

from .config import ConfigManager
from .logger import Logger
from ..voice.speech_engine import SpeechEngine
from ..voice.recognition_engine import RecognitionEngine
from ..commands.command_processor import CommandProcessor


class JarvisAssistant:
    """Assistente de voz JARVIS - Classe principal"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Inicializa o assistente JARVIS
        
        Args:
            config_path: Caminho para arquivo de configuração
        """
        # Inicializar configuração
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_all()
        
        # Inicializar logger
        log_level = self.config.get('system', {}).get('log_level', 'INFO')
        self.logger = Logger("JARVIS", log_level)
        
        self.logger.info("Inicializando JARVIS 5.0...")
        
        try:
            # Inicializar engines de voz
            self.speech_engine = SpeechEngine(self.config)
            self.recognition_engine = RecognitionEngine(self.config)
            
            # Inicializar processador de comandos
            self.command_processor = CommandProcessor(
                self.config, 
                self.speech_engine, 
                self.recognition_engine
            )
            
            # Estado do assistente
            self.is_running = False
            self.wake_word = self.config.get('commands', {}).get('wake_word')
            
            self.logger.info("JARVIS 5.0 inicializado com sucesso!")
            print("JARVIS 5.0 inicializado. Diga 'ajuda' para ver os comandos disponíveis.")
            
        except Exception as e:
            self.logger.critical(f"Erro crítico na inicialização: {e}")
            raise
    
    def start(self) -> None:
        """Inicia o loop principal do assistente"""
        try:
            self.is_running = True
            
            # Saudação inicial
            self._greet_user()
            
            # Loop principal
            self._main_loop()
            
        except KeyboardInterrupt:
            self.logger.info("Assistente interrompido pelo usuário")
            self.speech_engine.speak(
                "Assistente interrompido. Até a próxima!",
                emotion='aliviado'
            )
        
        except Exception as e:
            self.logger.error(f"Erro no loop principal: {e}")
            self.speech_engine.speak(
                "Ocorreu um erro inesperado. Encerrando assistente.",
                emotion='preocupado'
            )
        
        finally:
            self._cleanup()
    
    def _greet_user(self) -> None:
        """Saudação inicial do usuário"""
        greeting = ("Ah, olá! Eu sou o JARVIS 5.0, seu assistente de voz pessoal. "
                   "Estou aqui para te ajudar no que precisar. "
                   "O que você gostaria de fazer hoje?")
        
        self.speech_engine.speak(greeting, emotion='entusiasta', final_pause=1.5)
    
    def _main_loop(self) -> None:
        """Loop principal de escuta e processamento"""
        while self.is_running:
            try:
                # Se há palavra de ativação configurada, aguardar por ela
                if self.wake_word:
                    if not self._wait_for_wake_word():
                        continue
                
                # Escutar comando
                command = self.recognition_engine.listen()
                
                if command:
                    # Processar comando
                    start_time = time.time()
                    should_continue = self.command_processor.process_command(command)
                    processing_time = time.time() - start_time
                    
                    self.logger.performance_log("command_processing", processing_time)
                    
                    # Verificar se deve continuar
                    if not should_continue:
                        self.is_running = False
                        break
                
                # Pequena pausa para não sobrecarregar
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Erro no loop principal: {e}")
                self.speech_engine.speak(
                    "Ocorreu um erro inesperado. Vamos tentar novamente?",
                    emotion='preocupado'
                )
                time.sleep(1)
    
    def _wait_for_wake_word(self) -> bool:
        """
        Aguarda pela palavra de ativação
        
        Returns:
            True se palavra foi detectada, False para continuar aguardando
        """
        if not self.wake_word:
            return True
        
        self.logger.info(f"Aguardando palavra de ativação: '{self.wake_word}'")
        
        # Escutar por palavra de ativação com timeout
        return self.recognition_engine.listen_for_wake_word(self.wake_word, timeout=30.0)
    
    def stop(self) -> None:
        """Para o assistente"""
        self.logger.info("Parando assistente...")
        self.is_running = False
    
    def _cleanup(self) -> None:
        """Limpa recursos do assistente"""
        try:
            self.logger.info("Limpando recursos...")
            
            if hasattr(self, 'speech_engine'):
                self.speech_engine.cleanup()
            
            self.logger.info("JARVIS encerrado")
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza: {e}")
    
    def reload_config(self) -> bool:
        """
        Recarrega configuração
        
        Returns:
            True se sucesso, False se erro
        """
        try:
            self.config_manager.reload()
            self.config = self.config_manager.get_all()
            
            self.logger.info("Configuração recarregada")
            self.speech_engine.speak(
                "Configuração recarregada com sucesso!",
                emotion='entusiasta'
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao recarregar configuração: {e}")
            self.speech_engine.speak(
                "Erro ao recarregar configuração.",
                emotion='preocupado'
            )
            return False
    
    def get_status(self) -> dict:
        """
        Retorna status atual do assistente
        
        Returns:
            Dicionário com informações de status
        """
        return {
            'running': self.is_running,
            'wake_word': self.wake_word,
            'speech_engine': hasattr(self, 'speech_engine'),
            'recognition_engine': hasattr(self, 'recognition_engine'),
            'command_processor': hasattr(self, 'command_processor'),
            'config_loaded': bool(self.config)
        }
    
    def test_systems(self) -> dict:
        """
        Testa todos os sistemas
        
        Returns:
            Dicionário com resultados dos testes
        """
        results = {}
        
        try:
            # Testar microfone
            results['microphone'] = self.recognition_engine.test_microphone()
            
            # Testar voz
            results['speech'] = self.speech_engine.test_voice()
            
            # Testar configuração
            results['config'] = bool(self.config)
            
            # Status geral
            results['overall'] = all(results.values())
            
            self.logger.info(f"Teste de sistemas: {results}")
            
        except Exception as e:
            self.logger.error(f"Erro no teste de sistemas: {e}")
            results['error'] = str(e)
            results['overall'] = False
        
        return results
    
    def calibrate(self) -> bool:
        """
        Calibra o sistema de reconhecimento
        
        Returns:
            True se sucesso, False se erro
        """
        try:
            self.speech_engine.speak(
                "Vou calibrar o sistema. Mantenha silêncio por alguns segundos."
            )
            
            success = self.recognition_engine.calibrate()
            
            if success:
                self.speech_engine.speak(
                    "Calibração concluída com sucesso!",
                    emotion='entusiasta'
                )
            else:
                self.speech_engine.speak(
                    "Não consegui calibrar o sistema. Verifique o microfone.",
                    emotion='preocupado'
                )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro na calibração: {e}")
            return False
    
    def add_custom_command(self, keyword: str, handler) -> bool:
        """
        Adiciona comando personalizado
        
        Args:
            keyword: Palavra-chave do comando
            handler: Função que processa o comando
            
        Returns:
            True se sucesso, False se erro
        """
        try:
            self.command_processor.add_custom_command(keyword, handler)
            self.logger.info(f"Comando personalizado adicionado: {keyword}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar comando personalizado: {e}")
            return False
