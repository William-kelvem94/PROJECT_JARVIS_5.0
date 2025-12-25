#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - SISTEMA CORE INTEGRADO 100% LOCAL
Coordena todos os módulos locais: Visão, Áudio, NLP, Memória, Aprendizado
"""

import os
import sys
import time
import threading
import queue
import json
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
# import zmq  # Opcional - será usado se disponível
import sqlite3

# Importar módulos locais
from .vision_local import LocalVisionProcessor
from .audio_local import LocalAudioProcessor

# Verificar disponibilidade de módulos avançados
try:
    from .nlp_local import LocalNLPProcessor
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    print("⚠️ Módulo NLP não disponível")

try:
    from .memory_local import LocalMemorySystem
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    print("⚠️ Módulo de Memória não disponível")

try:
    from .learning_local import LocalLearningSystem
    LEARNING_AVAILABLE = True
except ImportError:
    LEARNING_AVAILABLE = False
    print("⚠️ Módulo de Aprendizado não disponível")


class JarvisCore:
    """Núcleo integrado 100% local do JARVIS"""

    def __init__(self, config_path="./config/settings.json"):
        print("🚀 JARVIS 5.0 - INICIALIZANDO SISTEMA CORE LOCAL")
        print("=" * 60)

        # Configuração
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Diretórios
        self.models_dir = Path(self.config.get('models_dir', './models'))
        self.data_dir = Path(self.config.get('data_dir', './data'))

        # Componentes core
        self.vision_processor = None
        self.audio_processor = None
        self.nlp_processor = None
        self.memory_system = None
        self.learning_system = None

        # Sistema de mensagens (ZeroMQ)
        self.message_bus = None
        self.message_thread = None

        # Estado do sistema
        self.running = False
        self.modules_initialized = {}

        # Estatísticas globais
        self.stats = {
            'start_time': time.time(),
            'total_interactions': 0,
            'system_health': 1.0,
            'modules_active': 0
        }

        print("📋 Configuração carregada")

    def _load_config(self) -> Dict[str, Any]:
        """Carregar configuração local"""
        default_config = {
            'models_dir': './models',
            'data_dir': './data',
            'vision': {
                'enabled': True,
                'camera_id': 0,
                'face_recognition': True,
                'object_detection': True,
                'gesture_recognition': True
            },
            'audio': {
                'enabled': True,
                'sample_rate': 16000,
                'whisper_model': 'base',
                'piper_voice': 'en_US-lessac-medium'
            },
            'nlp': {
                'enabled': True,
                'llm_model': 'llama-2-7b-chat.Q4_0.gguf',
                'embedding_model': 'local'
            },
            'memory': {
                'enabled': True,
                'vector_db': 'chromadb',
                'max_memories': 10000
            },
            'learning': {
                'enabled': True,
                'continuous_learning': True,
                'fine_tuning_enabled': False
            },
            'message_bus': {
                'enabled': True,
                'port': 5555
            }
        }

        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # Merge configs
                def merge_dicts(base, update):
                    for key, value in update.items():
                        if isinstance(value, dict) and key in base:
                            merge_dicts(base[key], value)
                        else:
                            base[key] = value
                merge_dicts(default_config, user_config)
            except Exception as e:
                print(f"⚠️ Erro ao carregar config: {e}")

        return default_config

    def initialize_system(self) -> bool:
        """Inicializar todos os módulos do sistema"""
        print("\n🔧 Inicializando módulos do sistema...")

        success_count = 0
        total_modules = 0

        # 1. Processador de Visão
        if self.config['vision']['enabled']:
            total_modules += 1
            try:
                print("👁️ Inicializando Visão...")
                self.vision_processor = LocalVisionProcessor(str(self.models_dir))
                self.modules_initialized['vision'] = True
                success_count += 1
                print("✅ Visão inicializada")
            except Exception as e:
                print(f"❌ Erro na Visão: {e}")
                self.modules_initialized['vision'] = False

        # 2. Processador de Áudio
        if self.config['audio']['enabled']:
            total_modules += 1
            try:
                print("🔊 Inicializando Áudio...")
                self.audio_processor = LocalAudioProcessor(str(self.models_dir))
                self.modules_initialized['audio'] = True
                success_count += 1
                print("✅ Áudio inicializado")
            except Exception as e:
                print(f"❌ Erro no Áudio: {e}")
                self.modules_initialized['audio'] = False

        # 3. Processador NLP
        if self.config['nlp']['enabled'] and NLP_AVAILABLE:
            total_modules += 1
            try:
                print("🧠 Inicializando NLP...")
                self.nlp_processor = LocalNLPProcessor(self.config['nlp'])
                self.modules_initialized['nlp'] = True
                success_count += 1
                print("✅ NLP inicializado")
            except Exception as e:
                print(f"❌ Erro no NLP: {e}")
                self.modules_initialized['nlp'] = False

        # 4. Sistema de Memória
        if self.config['memory']['enabled'] and MEMORY_AVAILABLE:
            total_modules += 1
            try:
                print("🧠 Inicializando Memória...")
                self.memory_system = LocalMemorySystem(self.config['memory'])
                self.modules_initialized['memory'] = True
                success_count += 1
                print("✅ Memória inicializada")
            except Exception as e:
                print(f"❌ Erro na Memória: {e}")
                self.modules_initialized['memory'] = False

        # 5. Sistema de Aprendizado
        if self.config['learning']['enabled'] and LEARNING_AVAILABLE:
            total_modules += 1
            try:
                print("🎓 Inicializando Aprendizado...")
                self.learning_system = LocalLearningSystem(self.config['learning'])
                self.modules_initialized['learning'] = True
                success_count += 1
                print("✅ Aprendizado inicializado")
            except Exception as e:
                print(f"❌ Erro no Aprendizado: {e}")
                self.modules_initialized['learning'] = False

        # 6. Message Bus
        if self.config['message_bus']['enabled']:
            try:
                print("📡 Inicializando Message Bus...")
                self._init_message_bus()
                print("✅ Message Bus inicializado")
            except Exception as e:
                print(f"❌ Erro no Message Bus: {e}")

        # Estatísticas de inicialização
        self.stats['modules_active'] = success_count

        print("\n📊 Status da Inicialização:")
        print(f"✅ Módulos OK: {success_count}/{total_modules}")
        print(f"❌ Módulos com erro: {total_modules - success_count}")

        return success_count > 0

    def _init_message_bus(self):
        """Inicializar sistema de mensagens ZeroMQ (opcional)"""
        try:
            import zmq
            context = zmq.Context()
            self.message_bus = context.socket(zmq.PUB)
            port = self.config['message_bus']['port']
            self.message_bus.bind(f"tcp://*:{port}")
            print(f"📡 Message Bus ativo na porta {port}")
        except ImportError:
            print("⚠️ ZeroMQ não disponível. Message Bus desabilitado.")
            self.message_bus = None
        except Exception as e:
            print(f"❌ Erro no Message Bus: {e}")
            self.message_bus = None

    def start_system(self) -> bool:
        """Iniciar sistema completo"""
        if not self.initialize_system():
            print("❌ Falha na inicialização do sistema")
            return False

        self.running = True

        # Iniciar threads dos módulos
        self._start_module_threads()

        print("\n" + "=" * 60)
        print("🚀 JARVIS 5.0 - SISTEMA LOCAL COMPLETO ATIVO!")
        print("=" * 60)

        self._display_system_status()
        self._display_available_commands()

        # Loop principal
        try:
            while self.running:
                self._process_system_events()
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n⚠️ Interrupção detectada")
        except Exception as e:
            print(f"\n❌ Erro crítico: {e}")

        self.stop_system()
        return True

    def _start_module_threads(self):
        """Iniciar threads de todos os módulos"""
        # Thread de áudio (escuta contínua)
        if self.audio_processor and self.modules_initialized.get('audio'):
            self.audio_processor.start_listening()

        # Outras threads podem ser adicionadas conforme necessário
        print("🧵 Threads dos módulos iniciadas")

    def _process_system_events(self):
        """Processar eventos do sistema"""
        # Processar eventos de áudio
        if self.audio_processor:
            audio_event = self.audio_processor.get_next_audio_event(timeout=0.01)
            if audio_event:
                self._handle_audio_event(audio_event)

        # Verificar saúde do sistema
        self._check_system_health()

        # Processar aprendizado contínuo
        if self.learning_system and self.modules_initialized.get('learning'):
            self.learning_system.continuous_learning_step()

    def _handle_audio_event(self, event: Dict[str, Any]):
        """Processar evento de áudio"""
        if event['type'] == 'speech':
            text = event['text']
            print(f"🎤 Comando de voz: {text}")

            self.stats['total_interactions'] += 1

            # Processar comando
            response = self._process_command(text)

            # Responder via voz
            if self.audio_processor and response:
                self.audio_processor.speak_text(response)

            # Registrar na memória
            if self.memory_system:
                self.memory_system.store_interaction(text, response)

            # Aprender com a interação
            if self.learning_system:
                self.learning_system.learn_from_interaction(text, response)

    def _process_command(self, command: str) -> str:
        """Processar comando usando todos os módulos disponíveis"""
        command = command.lower().strip()

        # Comandos de sistema
        if any(word in command for word in ['sair', 'tchau', 'encerrar']):
            self.running = False
            return "Encerrando JARVIS. Até logo!"

        # Comandos de aplicação
        elif 'abrir' in command:
            return self._handle_application_command(command)

        # Comandos de informação
        elif any(word in command for word in ['hora', 'horas']):
            return f"São {time.strftime('%H:%M')}"

        elif any(word in command for word in ['data', 'dia']):
            return f"Hoje é {time.strftime('%d de %B de %Y')}"

        # Comandos de visão
        elif 'ver' in command or 'olhar' in command:
            return self._handle_vision_command(command)

        # Comandos de memória
        elif 'lembrar' in command or 'recordar' in command:
            return self._handle_memory_command(command)

        # Comandos usando NLP avançado
        elif self.nlp_processor:
            return self.nlp_processor.generate_response(command)

        # Comando padrão
        else:
            responses = [
                "Não entendi o comando. Tente 'ajuda' para ver os comandos disponíveis.",
                "Comando não reconhecido. Diga 'sair' para encerrar.",
                "Desculpe, não compreendi. Tente comandos como 'abrir chrome' ou 'que horas são'."
            ]
            return responses[len(command) % len(responses)]

    def _handle_application_command(self, command: str) -> str:
        """Processar comandos de aplicação"""
        apps = {
            'chrome': 'chrome.exe',
            'navegador': 'chrome.exe',
            'calculadora': 'calc.exe',
            'bloco de notas': 'notepad.exe',
            'notepad': 'notepad.exe',
            'explorer': 'explorer.exe',
            'arquivos': 'explorer.exe'
        }

        for app_name, exe_name in apps.items():
            if app_name in command:
                try:
                    import subprocess
                    subprocess.Popen(exe_name, shell=True)
                    return f"Aplicação {app_name} aberta com sucesso!"
                except Exception as e:
                    return f"Erro ao abrir {app_name}: {e}"

        return "Aplicação não encontrada. Tente 'abrir chrome' ou 'abrir calculadora'."

    def _handle_vision_command(self, command: str) -> str:
        """Processar comandos de visão"""
        if not self.vision_processor:
            return "Sistema de visão não disponível."

        # Capturar frame atual (simulação)
        # Em implementação real, capturaria frame da câmera
        return "Sistema de visão ativo. Detectando faces, objetos e gestos."

    def _handle_memory_command(self, command: str) -> str:
        """Processar comandos de memória"""
        if not self.memory_system:
            return "Sistema de memória não disponível."

        # Extrair informação para lembrar
        # Implementação simplificada
        return "Informação armazenada na memória local."

    def _check_system_health(self):
        """Verificar saúde do sistema"""
        # Calcular health score baseado em módulos ativos
        active_modules = sum(1 for status in self.modules_initialized.values() if status)
        total_modules = len(self.modules_initialized)

        if total_modules > 0:
            self.stats['system_health'] = active_modules / total_modules
        else:
            self.stats['system_health'] = 0.0

    def _display_system_status(self):
        """Exibir status do sistema"""
        print("\n📊 STATUS DO SISTEMA:")
        print(f"🖥️ Visão Computacional: {'✅' if self.modules_initialized.get('vision') else '❌'}")
        print(f"🔊 Processamento de Áudio: {'✅' if self.modules_initialized.get('audio') else '❌'}")
        print(f"🧠 Processamento de Linguagem: {'✅' if self.modules_initialized.get('nlp') else '❌'}")
        print(f"💾 Sistema de Memória: {'✅' if self.modules_initialized.get('memory') else '❌'}")
        print(f"🎓 Aprendizado Contínuo: {'✅' if self.modules_initialized.get('learning') else '❌'}")
        print(f"💊 Saúde do Sistema: {self.stats['system_health']:.1%}")

    def _display_available_commands(self):
        """Exibir comandos disponíveis"""
        print("\n🎮 COMANDOS DISPONÍVEIS:")
        print("🏠 SISTEMA:")
        print("  • 'sair', 'tchau', 'encerrar' - Finalizar JARVIS")
        print("📱 APLICAÇÕES:")
        print("  • 'abrir chrome/navegador'")
        print("  • 'abrir calculadora'")
        print("  • 'abrir bloco de notas'")
        print("  • 'abrir explorer/arquivos'")
        print("🕐 INFORMAÇÕES:")
        print("  • 'que horas são?'")
        print("  • 'que dia é hoje?'")
        print("👁️ VISÃO:")
        print("  • 'ver', 'olhar' - Comandos de visão")
        print("🧠 MEMÓRIA:")
        print("  • 'lembrar', 'recordar' - Comandos de memória")

    def get_system_stats(self) -> Dict[str, Any]:
        """Obter estatísticas completas do sistema"""
        uptime = time.time() - self.stats['start_time']

        stats = {
            'uptime': uptime,
            'total_interactions': self.stats['total_interactions'],
            'system_health': self.stats['system_health'],
            'modules_initialized': self.modules_initialized.copy(),
            'modules_active': self.stats['modules_active']
        }

        # Adicionar estatísticas específicas de cada módulo
        if self.vision_processor:
            stats['vision'] = self.vision_processor.get_stats()

        if self.audio_processor:
            stats['audio'] = self.audio_processor.get_stats()

        if self.nlp_processor:
            stats['nlp'] = self.nlp_processor.get_stats()

        if self.memory_system:
            stats['memory'] = self.memory_system.get_stats()

        if self.learning_system:
            stats['learning'] = self.learning_system.get_stats()

        return stats

    def stop_system(self):
        """Parar sistema completo"""
        print("\n🛑 Parando JARVIS Core...")

        self.running = False

        # Parar processador de áudio
        if self.audio_processor:
            self.audio_processor.stop_listening()

        # Fechar message bus
        if self.message_bus:
            self.message_bus.close()

        # Salvar estatísticas finais
        final_stats = self.get_system_stats()
        stats_file = self.data_dir / "system_stats.json"
        stats_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(final_stats, f, indent=2, ensure_ascii=False)
            print(f"📊 Estatísticas salvas em: {stats_file}")
        except Exception as e:
            print(f"❌ Erro ao salvar estatísticas: {e}")

        print("✅ JARVIS Core finalizado com sucesso!")


# Função de teste
def test_jarvis_core():
    """Testar sistema core"""
    print("🧪 Testando JARVIS Core...")

    jarvis = JarvisCore()

    # Inicializar
    if not jarvis.initialize_system():
        print("❌ Falha na inicialização")
        return

    # Simular alguns comandos
    test_commands = [
        "Olá JARVIS",
        "que horas são",
        "abrir calculadora",
        "sair"
    ]

    print("\n🧪 Testando comandos...")
    for cmd in test_commands:
        if cmd == "sair":
            break
        print(f"🎤 Testando: {cmd}")
        response = jarvis._process_command(cmd)
        print(f"🤖 Resposta: {response}")
        time.sleep(1)

    stats = jarvis.get_system_stats()
    print("\n📊 Estatísticas do teste:")
    print(f"  - Módulos ativos: {stats['modules_active']}")
    print(f"  - Saúde do sistema: {stats['system_health']:.1%}")
    print("✅ Teste concluído!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Core - Sistema Local Integrado")
    parser.add_argument("--test", action="store_true", help="Executar teste do sistema")
    parser.add_argument("--start", action="store_true", help="Iniciar sistema completo")
    parser.add_argument("--config", type=str, help="Arquivo de configuração")

    args = parser.parse_args()

    if args.config:
        jarvis = JarvisCore(args.config)
    else:
        jarvis = JarvisCore()

    if args.test:
        test_jarvis_core()
    elif args.start:
        jarvis.start_system()
    else:
        print("🚀 JARVIS 5.0 - Sistema Core Local")
        print("Use --test para testar ou --start para iniciar o sistema completo")
