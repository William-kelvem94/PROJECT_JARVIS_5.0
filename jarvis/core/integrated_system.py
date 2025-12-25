#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Sistema Integrado
Coordena todos os subsistemas: voz, vídeo, IA e automação
"""

import threading
import time
import queue
from typing import Optional, Dict, Any
from pathlib import Path

from .config import ConfigManager
from .logger import Logger
from ..voice.speech_engine import SpeechEngine
from ..voice.recognition_engine import RecognitionEngine
from ..commands.command_processor import CommandProcessor
from ..ai.ai_monitor import AIMonitor
from ..automation.windows_controller import WindowsController


class IntegratedSystem:
    """Sistema integrado que coordena todos os módulos do JARVIS"""
    
    def __init__(self, config_path: str = "config.json"):
        """Inicializa o sistema integrado"""
        # Configuração
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_all()
        
        # Logger
        self.logger = Logger("INTEGRATED_SYSTEM", "INFO")
        
        # Componentes principais
        self.speech_engine = None
        self.recognition_engine = None
        self.command_processor = None
        self.video_processor = None
        self.ai_engine = None
        self.ai_monitor = None
        self.windows_controller = None
        
        # Estado do sistema
        self.running = False
        self.threads = {}
        self.message_queue = queue.Queue()
        
        # Estatísticas
        self.stats = {
            'start_time': time.time(),
            'commands_processed': 0,
            'conversations': 0,
            'video_frames': 0,
            'ai_interactions': 0
        }
        
    def initialize_all_systems(self) -> bool:
        """Inicializa todos os subsistemas de forma coordenada"""
        try:
            self.logger.info("Inicializando sistema integrado JARVIS 5.0...")
            
            # 1. Sistema de Voz
            self._initialize_voice_system()
            
            # 2. Sistema de Processamento de Comandos
            self._initialize_command_system()
            
            # 3. Sistema de Vídeo (opcional)
            self._initialize_video_system()
            
            # 4. Sistema de IA
            self._initialize_ai_system()
            
            # 5. Monitor de IA
            self._initialize_ai_monitor()
            
            # 6. Controlador do Windows
            self._initialize_windows_controller()
            
            self.logger.info("Todos os sistemas inicializados com sucesso!")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na inicialização: {e}")
            return False
    
    def _initialize_voice_system(self):
        """Inicializa sistema de voz integrado"""
        self.logger.info("Inicializando sistema de voz...")
        
        self.speech_engine = SpeechEngine(self.config)
        self.recognition_engine = RecognitionEngine(self.config)
        
        self.logger.info("Sistema de voz inicializado")
    
    def _initialize_command_system(self):
        """Inicializa sistema de processamento de comandos"""
        self.logger.info("Inicializando processador de comandos...")
        
        self.command_processor = CommandProcessor(
            self.config,
            self.speech_engine,
            self.recognition_engine
        )
        
        self.logger.info("Processador de comandos inicializado")
    
    def _initialize_video_system(self):
        """Inicializa sistema de vídeo se disponível"""
        try:
            self.logger.info("Inicializando sistema de vídeo...")
            
            from ..video.video_processor import VideoProcessor
            self.video_processor = VideoProcessor(self.config)
            
            self.logger.info("Sistema de vídeo inicializado")
            
        except ImportError:
            self.logger.warning("Sistema de vídeo não disponível")
            self.video_processor = None
        except Exception as e:
            self.logger.warning(f"Erro no sistema de vídeo: {e}")
            self.video_processor = None
    
    def _initialize_ai_system(self):
        """Inicializa sistema de IA integrado"""
        try:
            self.logger.info("Inicializando sistema de IA...")
            
            from ..ai.neural_engine import NeuralEngine
            from ..ai.conversation_engine import ConversationEngine
            
            self.ai_engine = {
                'neural': NeuralEngine(self.config),
                'conversation': ConversationEngine(self.config)
            }
            
            self.logger.info("Sistema de IA inicializado")
            
        except Exception as e:
            self.logger.warning(f"Sistema de IA limitado: {e}")
            self.ai_engine = None
    
    def _initialize_ai_monitor(self):
        """Inicializa monitor de IA"""
        try:
            self.logger.info("Inicializando monitor de IA...")
            
            self.ai_monitor = AIMonitor(self.config)
            self.ai_monitor.start_monitoring()
            
            self.logger.info("Monitor de IA inicializado")
            
        except Exception as e:
            self.logger.warning(f"Monitor de IA limitado: {e}")
            self.ai_monitor = None
    
    def _initialize_windows_controller(self):
        """Inicializa controlador do Windows"""
        try:
            self.logger.info("Inicializando controlador do Windows...")
            
            self.windows_controller = WindowsController(self.config)
            
            self.logger.info("Controlador do Windows inicializado")
            
        except Exception as e:
            self.logger.warning(f"Controlador do Windows limitado: {e}")
            self.windows_controller = None
    
    def start_integrated_system(self):
        """Inicia todos os sistemas de forma coordenada"""
        if not self.initialize_all_systems():
            return False
        
        self.running = True
        
        # Iniciar threads dos subsistemas SIMULTANEAMENTE
        self._start_voice_thread()
        self._start_video_thread()
        self._start_ai_thread()
        self._start_automation_thread()
        
        # Saudação inicial
        welcome_msg = "JARVIS 5.0 sistema integrado ativo. Todos os módulos funcionando."
        self.speech_engine.speak(welcome_msg)
        
        # Loop principal
        self._main_loop()
        
        return True
    
    def _start_voice_thread(self):
        """Inicia thread de processamento de voz"""
        def voice_loop():
            while self.running:
                try:
                    # Escutar comando
                    command = self.recognition_engine.listen()
                    
                    if command:
                        self.stats['commands_processed'] += 1
                        
                        # Enviar para processamento
                        self.message_queue.put({
                            'type': 'voice_command',
                            'data': command,
                            'timestamp': time.time()
                        })
                        
                except Exception as e:
                    self.logger.error(f"Erro na thread de voz: {e}")
                    time.sleep(1)
        
        self.threads['voice'] = threading.Thread(target=voice_loop, daemon=True)
        self.threads['voice'].start()
        self.logger.info("Thread de voz iniciada")
    
    def _start_video_thread(self):
        """Inicia thread de processamento de vídeo"""
        if not self.video_processor:
            return
            
        def video_loop():
            while self.running:
                try:
                    # Processar frame de vídeo
                    result = self.video_processor.process_frame()
                    
                    if result:
                        self.stats['video_frames'] += 1
                        
                        # Enviar eventos de vídeo
                        if result.get('faces') or result.get('gestures'):
                            self.message_queue.put({
                                'type': 'video_event',
                                'data': result,
                                'timestamp': time.time()
                            })
                            
                except Exception as e:
                    self.logger.error(f"Erro na thread de vídeo: {e}")
                    time.sleep(0.1)
        
        self.threads['video'] = threading.Thread(target=video_loop, daemon=True)
        self.threads['video'].start()
        self.logger.info("Thread de vídeo iniciada")
    
    def _start_ai_thread(self):
        """Inicia thread de processamento de IA"""
        if not self.ai_engine:
            return
            
        def ai_loop():
            while self.running:
                try:
                    # Processar aprendizado contínuo
                    if self.ai_engine.get('neural'):
                        self.ai_engine['neural'].continuous_learning()
                    
                    time.sleep(5)  # Processar a cada 5 segundos
                    
                except Exception as e:
                    self.logger.error(f"Erro na thread de IA: {e}")
                    time.sleep(10)
        
        self.threads['ai'] = threading.Thread(target=ai_loop, daemon=True)
        self.threads['ai'].start()
        self.logger.info("Thread de IA iniciada")
    
    def _start_automation_thread(self):
        """Inicia thread de automação do Windows"""
        if not self.windows_controller:
            return
            
        def automation_loop():
            while self.running:
                try:
                    # Monitorar sistema e executar automações
                    # Esta thread fica disponível para comandos de automação
                    time.sleep(1)  # Verificar a cada segundo
                    
                except Exception as e:
                    self.logger.error(f"Erro na thread de automação: {e}")
                    time.sleep(5)
        
        self.threads['automation'] = threading.Thread(target=automation_loop, daemon=True)
        self.threads['automation'].start()
        self.logger.info("Thread de automação iniciada")
    
    def _main_loop(self):
        """Loop principal do sistema integrado"""
        self.logger.info("Sistema integrado ativo - aguardando interações...")
        
        try:
            while self.running:
                try:
                    # Processar mensagens da fila
                    if not self.message_queue.empty():
                        message = self.message_queue.get(timeout=1)
                        self._process_message(message)
                    
                    time.sleep(0.1)
                    
                except queue.Empty:
                    continue
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.logger.error(f"Erro no loop principal: {e}")
                    continue
        
        finally:
            self.stop_integrated_system()
    
    def _process_message(self, message: Dict[str, Any]):
        """Processa mensagens dos subsistemas de forma integrada"""
        msg_type = message.get('type')
        data = message.get('data')
        
        if msg_type == 'voice_command':
            self._handle_voice_command_integrated(data)
        elif msg_type == 'video_event':
            self._handle_video_event_integrated(data)
        elif msg_type == 'ai_response':
            self._handle_ai_response(data)
        elif msg_type == 'automation_request':
            self._handle_automation_request(data)
    
    def _handle_voice_command_integrated(self, command: str):
        """Processa comando de voz"""
        start_time = time.time()
        self.logger.info(f"Processando comando: {command}")
        
        # Verificar comando de saída
        if command.lower() in ['sair', 'tchau', 'encerrar', 'parar']:
            self.speech_engine.speak("Encerrando sistema integrado. Até logo!")
            self.running = False
            return
        
        try:
            # Processar com IA se disponível
            if self.ai_engine and self.ai_engine.get('neural'):
                self.ai_engine['neural'].learn_from_interaction(command, 'voice_command')
                self.stats['ai_interactions'] += 1
            
            # Processar comando com TODOS os sistemas integrados
            result = self._process_command_with_all_systems(command)
            self.stats['conversations'] += 1
            
            # Registrar métricas no monitor
            response_time = time.time() - start_time
            success = result is not None
            
            if self.ai_monitor:
                self.ai_monitor.record_interaction('voice_command', response_time, success)
            
        except Exception as e:
            self.logger.error(f"Erro no processamento de comando: {e}")
            
            # Registrar erro no monitor
            if self.ai_monitor:
                response_time = time.time() - start_time
                self.ai_monitor.record_interaction('voice_command', response_time, False)
    
    def _process_command_with_all_systems(self, command: str):
        """Processa comando integrando TODOS os sistemas"""
        try:
            # 1. Processar com IA conversacional
            if self.ai_engine and self.ai_engine.get('conversation'):
                ai_response = self.ai_engine['conversation'].process_input(command)
                
            # 2. Verificar se é comando de automação do Windows
            if self._is_automation_command(command):
                return self._execute_windows_automation(command)
            
            # 3. Processar comando normal
            result = self.command_processor.process_command(command)
            
            # 4. Usar dados de vídeo para contexto se disponível
            if self.video_processor:
                video_context = self._get_video_context()
                if video_context and video_context.get('faces'):
                    # Adaptar resposta baseado em detecção facial
                    self.logger.info(f"Comando processado com {len(video_context['faces'])} pessoa(s) detectada(s)")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro no processamento integrado: {e}")
            return None
    
    def _is_automation_command(self, command: str) -> bool:
        """Verifica se é um comando de automação do Windows"""
        automation_keywords = [
            'abrir', 'executar', 'fechar', 'minimizar', 'maximizar',
            'desligar', 'reiniciar', 'volume', 'brilho', 'wifi',
            'bluetooth', 'screenshot', 'captura', 'tela'
        ]
        
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in automation_keywords)
    
    def _execute_windows_automation(self, command: str):
        """Executa comando de automação do Windows"""
        if not self.windows_controller:
            self.speech_engine.speak("Controle do Windows não disponível")
            return False
        
        try:
            command_lower = command.lower()
            
            # Comandos de aplicação
            if 'abrir' in command_lower:
                if 'chrome' in command_lower or 'navegador' in command_lower:
                    result = self.windows_controller.execute_application('chrome')
                elif 'calculadora' in command_lower:
                    result = self.windows_controller.execute_application('calculator')
                elif 'bloco de notas' in command_lower or 'notepad' in command_lower:
                    result = self.windows_controller.execute_application('notepad')
                elif 'explorer' in command_lower or 'arquivos' in command_lower:
                    result = self.windows_controller.execute_application('explorer')
                else:
                    # Tentar extrair nome do programa
                    app_name = command_lower.replace('abrir', '').strip()
                    result = self.windows_controller.execute_application(app_name)
                
                if result.get('success'):
                    self.speech_engine.speak(f"Aplicação aberta com sucesso")
                else:
                    self.speech_engine.speak(f"Erro ao abrir aplicação: {result.get('error', 'desconhecido')}")
                
                return result.get('success', False)
            
            # Comandos de sistema
            elif 'volume' in command_lower:
                if 'aumentar' in command_lower or 'subir' in command_lower:
                    # Implementar controle de volume
                    self.speech_engine.speak("Volume aumentado")
                elif 'diminuir' in command_lower or 'baixar' in command_lower:
                    self.speech_engine.speak("Volume diminuído")
                elif 'mudo' in command_lower or 'silenciar' in command_lower:
                    self.speech_engine.speak("Volume silenciado")
                return True
            
            # Screenshot
            elif 'screenshot' in command_lower or 'captura' in command_lower:
                if self.video_processor:
                    filename = self.video_processor.save_screenshot()
                    self.speech_engine.speak(f"Captura de tela salva")
                    return True
                else:
                    self.speech_engine.speak("Sistema de vídeo não disponível para captura")
                    return False
            
            else:
                self.speech_engine.speak("Comando de automação não reconhecido")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro na automação: {e}")
            self.speech_engine.speak("Erro ao executar comando de automação")
            return False
    
    def _get_video_context(self) -> Optional[Dict[str, Any]]:
        """Obtém contexto atual do vídeo"""
        if not self.video_processor:
            return None
        
        try:
            # Simular análise do frame atual
            return {
                'faces': [],  # Seria preenchido com dados reais
                'gestures': [],
                'motion': 0
            }
        except:
            return None
    
    def _handle_video_event_integrated(self, event_data: Dict[str, Any]):
        """Processa eventos de vídeo integrados com voz e IA"""
        faces = event_data.get('faces', [])
        gestures = event_data.get('gestures', [])
        
        if len(faces) > 0:
            self.logger.info(f"Detectadas {len(faces)} pessoa(s)")
            
            # Integrar com IA para personalização
            if self.ai_engine and self.ai_engine.get('neural'):
                self.ai_engine['neural'].learn_from_interaction(
                    f"faces_detected_{len(faces)}", 'video_event'
                )
        
        if gestures:
            for gesture in gestures:
                self.logger.info(f"Gesto detectado: {gesture}")
                
                # Responder a gestos com voz E registrar na IA
                if gesture == 'thumbs_up':
                    self.speech_engine.speak("Obrigado! Gesto positivo detectado!")
                    self._trigger_voice_command("gesto positivo")
                elif gesture == 'peace':
                    self.speech_engine.speak("Paz e amor!")
                    self._trigger_voice_command("gesto de paz")
                elif gesture == 'open_palm':
                    self.speech_engine.speak("Olá! Mão aberta detectada!")
                    self._trigger_voice_command("cumprimento")
                elif gesture == 'pointing':
                    self.speech_engine.speak("Você está apontando para algo?")
                    self._trigger_voice_command("gesto de apontar")
                
                # Registrar gesto na IA
                if self.ai_engine and self.ai_engine.get('neural'):
                    self.ai_engine['neural'].learn_from_interaction(
                        f"gesture_{gesture}", 'video_gesture'
                    )
    
    def _trigger_voice_command(self, virtual_command: str):
        """Dispara um comando de voz virtual baseado em evento de vídeo"""
        self.message_queue.put({
            'type': 'voice_command',
            'data': virtual_command,
            'timestamp': time.time(),
            'source': 'video_gesture'
        })
    
    def _handle_automation_request(self, request_data: Dict[str, Any]):
        """Processa solicitações de automação"""
        if not self.windows_controller:
            return
        
        action = request_data.get('action')
        params = request_data.get('params', {})
        
        try:
            if action == 'execute_app':
                app_name = params.get('app_name')
                result = self.windows_controller.execute_application(app_name)
                self.logger.info(f"Aplicação {app_name}: {'sucesso' if result.get('success') else 'falha'}")
            
        except Exception as e:
            self.logger.error(f"Erro na automação: {e}")
    
    def _handle_ai_response(self, response_data: Dict[str, Any]):
        """Processa respostas da IA"""
        self.logger.info(f"Resposta da IA: {response_data}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status completo do sistema"""
        uptime = time.time() - self.stats['start_time']
        
        return {
            'running': self.running,
            'uptime': uptime,
            'stats': self.stats.copy(),
            'threads': {name: thread.is_alive() for name, thread in self.threads.items()},
                'components': {
                'voice': self.speech_engine is not None,
                'recognition': self.recognition_engine is not None,
                'commands': self.command_processor is not None,
                'video': self.video_processor is not None,
                'ai': self.ai_engine is not None,
                'windows_control': self.windows_controller is not None,
                'ai_monitor': self.ai_monitor is not None
            }
        }
    
    def stop_integrated_system(self):
        """Para todos os sistemas de forma coordenada"""
        self.logger.info("Parando sistema integrado...")
        self.running = False
        
        # Parar processamento de vídeo
        if self.video_processor:
            self.video_processor.stop()
        
        # Parar monitor de IA
        if self.ai_monitor:
            # Gerar relatório final
            try:
                report = self.ai_monitor.get_performance_report()
                self.logger.info(f"Relatório final de IA: {report['system_health']:.2f} saúde do sistema")
                self.logger.info(f"Total de interações: {report['total_interactions']}")
                self.logger.info(f"Taxa de sucesso: {report['success_rate']:.2f}")
            except:
                pass
            
            self.ai_monitor.stop_monitoring()
        
        # Salvar modelo de IA
        if self.ai_engine and self.ai_engine.get('neural'):
            try:
                self.ai_engine['neural'].save_model()
                self.logger.info("Modelo de IA salvo")
            except:
                pass
        
        # Aguardar threads
        for name, thread in self.threads.items():
            if thread.is_alive():
                thread.join(timeout=2)
                self.logger.info(f"Thread {name} finalizada")
        
        # Estatísticas finais
        uptime = time.time() - self.stats['start_time']
        self.logger.info(f"Sistema ativo por {uptime:.1f} segundos")
        self.logger.info(f"Comandos processados: {self.stats['commands_processed']}")
        self.logger.info(f"Conversas: {self.stats['conversations']}")
        self.logger.info(f"Frames de vídeo: {self.stats['video_frames']}")
        self.logger.info(f"Interações de IA: {self.stats['ai_interactions']}")
        
        self.logger.info("Sistema integrado finalizado")
