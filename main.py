"""
JARVIS Ultimate - Assistente de IA com Vida Artificial
Sistema agnóstico ao hardware, aprendizado contínuo e controle total
"""

import os
import time
import signal
import sys
from typing import Optional
from pathlib import Path

from core.brain import Brain
from core.hearing import Hearing
from core.speech import Speech
from core.hardware import HardwareMonitor
from tools.model_manager import ModelManager
from config import config

class JarvisUltimate:
    """
    JARVIS Ultimate - A infraestrutura de vida artificial completa.

    Capacidades:
    - Aprendizado contínuo com RAG
    - Reconhecimento e síntese de voz
    - Controle total do hardware
    - Gerenciamento inteligente de modelos
    - Adaptação automática ao ambiente
    """

    def __init__(self):
        print("JARVIS Ultimate - Inicializando...")
        print(f"Usuario detectado: {config.get_user_name()}")
        print(f"Hardware: {config.get_system_info()}")

        # Componentes principais
        self.brain = Brain()
        self.hearing = Hearing()
        self.speech = Speech()
        self.hardware = HardwareMonitor()
        self.model_manager = ModelManager()

        # Estado do sistema
        self.running = False
        self.voice_mode = config.get("voice.stt_engine") != "none"

        # Estatísticas
        self.stats = {
            "start_time": time.time(),
            "interactions": 0,
            "learned_items": 0,
            "commands_executed": 0
        }

        # Configurar handlers de sinal
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handler para sinais de interrupção."""
        print("\n Sinal de interrupção recebido. Encerrando JARVIS...")
        self.stop()

    def start(self):
        """Inicia o JARVIS Ultimate."""
        if self.running:
            print("AVISO: JARVIS ja esta rodando")
            return

        self.running = True
        print(" JARVIS Ultimate iniciado!")
        print("=" * 50)

        # Saudação inicial
        self._initial_greeting()

        # Loop principal
        try:
            if self.voice_mode:
                self._voice_loop()
            else:
                self._text_loop()
        except KeyboardInterrupt:
            print("\n Encerramento solicitado pelo usuário")
        except Exception as e:
            print(f" Erro crítico: {e}")
        finally:
            self.stop()

    def stop(self):
        """Para o JARVIS Ultimate."""
        if not self.running:
            return

        self.running = False

        # Parar componentes
        if self.hearing:
            self.hearing.stop_listening()

        if self.speech:
            self.speech.stop_speaking()

        # Salvar estatísticas
        self._save_stats()

        print(" JARVIS Ultimate encerrado")
        print(f" Estatísticas finais: {self.stats}")

    def _initial_greeting(self):
        """Saudação inicial personalizada."""
        user_name = config.get_user_name()
        hardware_info = self.hardware.get_system_info()

        greeting = f"Ola {user_name}! Sou JARVIS, seu assistente de IA pessoal."

        if hardware_info["is_laptop"]:
            greeting += f" Detectei que voce esta usando seu {hardware_info['device_type'].replace('_', ' ')}."
        elif hardware_info["is_desktop"]:
            greeting += " Detectei que voce esta no seu desktop parrudo."

        greeting += " Estou pronto para ajudar com qualquer coisa!"

        print(f"JARVIS: {greeting}")

        if self.voice_mode and self.speech:
            self.speech.speak(greeting)

    def _voice_loop(self):
        """Loop principal no modo voz."""
        print(" Modo voz ativado. Diga 'Jarvis' para começar...")

        def voice_callback(text: str):
            """Callback para quando voz é detectada."""
            if not self.running:
                return

            print(f" Você disse: {text}")
            self._process_input(text, voice_response=True)

        # Iniciar escuta
        self.hearing.start_listening(callback=voice_callback)

        # Manter vivo
        while self.running:
            time.sleep(0.1)
            self._periodic_checks()

    def _text_loop(self):
        """Loop principal no modo texto."""
        print(" Modo texto ativado. Digite suas mensagens:")

        while self.running:
            try:
                user_input = input(" Você: ").strip()
                if user_input:
                    self._process_input(user_input, voice_response=False)
            except EOFError:
                break

            self._periodic_checks()

    def _process_input(self, user_input: str, voice_response: bool = False):
        """Processa entrada do usuário."""
        try:
            self.stats["interactions"] += 1

            # Verificar comandos especiais
            if self._handle_special_commands(user_input):
                return

            # Processar com o cérebro
            print("🧠 Pensando...")
            response = self.brain.think(user_input)

            # Resposta
            print(f"🤖 JARVIS: {response}")

            # Falar resposta se estiver no modo voz
            if voice_response and self.speech:
                self.speech.speak(response)

        except Exception as e:
            error_msg = f"Desculpe, ocorreu um erro: {str(e)}"
            print(f" {error_msg}")

            if voice_response and self.speech:
                self.speech.speak(error_msg)

    def _handle_special_commands(self, user_input: str) -> bool:
        """
        Trata comandos especiais que não passam pelo cérebro.

        Returns:
            True se foi um comando especial tratado
        """
        input_lower = user_input.lower()

        # Comando de status
        if input_lower in ["status", "como você está", "status do sistema"]:
            self._show_status()
            return True

        # Comando de aprendizado
        if input_lower.startswith("aprenda que") or input_lower.startswith("lembre que"):
            self._handle_learning_command(user_input)
            return True

        # Comando de voz
        if input_lower in ["calar", "ficar quieto", "parar de falar"]:
            if self.speech:
                self.speech.stop_speaking()
                print(" Ok, ficando quieto")
            return True

        # Comando de calibração
        if input_lower in ["calibrar microfone", "calibrar voz"]:
            if self.hearing:
                self.hearing.calibrate_microphone()
                print(" Microfone calibrado")
            return True

        # Comando de sair
        if input_lower in ["sair", "encerrar", "fechar", "tchau"]:
            print(" Até logo!")
            self.stop()
            return True

        return False

    def _handle_learning_command(self, user_input: str):
        """Trata comandos de aprendizado."""
        # Extrair o que aprender
        learn_text = user_input.replace("aprenda que", "").replace("lembre que", "").strip()

        if not learn_text:
            print(" O que você quer que eu aprenda?")
            return

        # Aprender
        result = self.brain.learn(learn_text, "user_teaching")

        if result.get("success"):
            print(" Aprendido!")
            self.stats["learned_items"] += 1
        else:
            print(f" Erro ao aprender: {result.get('error', 'Erro desconhecido')}")

    def _show_status(self):
        """Mostra status completo do sistema."""
        print("\n STATUS DO JARVIS ULTIMATE")
        print("=" * 40)

        # Hardware
        hw_info = self.hardware.get_system_info()
        print(f" Hardware: {hw_info['device_type']} ({hw_info['system']})")

        # CPU e memória
        if hw_info.get('cpu', {}).get('available'):
            print(f"️ CPU: {hw_info['cpu']['usage_percent']:.1f}% usado")
        if hw_info.get('memory', {}).get('available'):
            print(f"🧠 RAM: {hw_info['memory']['usage_percent']:.1f}% usado")

        # Temperatura
        if hw_info.get('temperature', {}).get('available'):
            sensors = hw_info['temperature'].get('sensors', [])
            if sensors:
                temp = sensors[0]['temperature_c']
                print(f"️ Temperatura: {temp:.1f}°C")

        # Bateria (se laptop)
        if hw_info.get('battery', {}).get('available'):
            battery = hw_info['battery']
            print(f" Bateria: {battery['percent']:.1f}% {'(carregando)' if battery['is_plugged'] else ''}")

        # Cérebro
        brain_stats = self.brain.get_stats()
        print(f"🧠 Conhecimento: {brain_stats['knowledge_items']} itens aprendidos")

        # Voz
        if self.hearing:
            hearing_status = self.hearing.get_status()
            print(f" STT: {hearing_status['engine']} ({'ativo' if hearing_status['is_listening'] else 'inativo'})")

        if self.speech:
            speech_status = self.speech.get_status()
            print(f"️ TTS: {speech_status['engine']} (volume: {speech_status['volume']}%)")

        # Modelos
        if self.model_manager:
            model_status = self.model_manager.get_status()
            print(f"🤖 Modelos: {model_status['installed_models_count']} instalados")

        # Estatísticas de uso
        uptime = time.time() - self.stats["start_time"]
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)

        print(f"⏱️ Tempo ativo: {hours}h {minutes}m")
        print(f" Interações: {self.stats['interactions']}")
        print(f" Itens aprendidos: {self.stats['learned_items']}")

        print("=" * 40)

    def _periodic_checks(self):
        """Verificações periódicas durante o loop."""
        # Verificar saúde do hardware a cada 30 segundos
        current_time = time.time()
        if not hasattr(self, '_last_health_check'):
            self._last_health_check = 0

        if current_time - self._last_health_check > 30:
            self._health_check()
            self._last_health_check = current_time

    def _health_check(self):
        """Verificação de saúde do sistema."""
        try:
            health = self.hardware.get_health_status()

            if health["overall"] == "critical":
                warning_msg = "⚠️ Sistema com problemas críticos!"
                print(warning_msg)
                if self.voice_mode and self.speech:
                    self.speech.speak(warning_msg)

            elif health["overall"] == "warning":
                print("⚠️ Atenção: sistema com avisos")

        except Exception as e:
            print(f"Erro na verificação de saúde: {e}")

    def _save_stats(self):
        """Salva estatísticas da sessão."""
        try:
            stats_file = Path("./data/session_stats.json")
            stats_file.parent.mkdir(parents=True, exist_ok=True)

            session_data = {
                "timestamp": time.time(),
                "duration_seconds": time.time() - self.stats["start_time"],
                **self.stats
            }

            with open(stats_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(session_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Erro ao salvar estatísticas: {e}")

def main():
    """Função principal."""
    try:
        # Verificar se é Docker
        if config.is_docker_environment():
            print(" Executando em ambiente Docker")

        # Inicializar JARVIS
        jarvis = JarvisUltimate()

        # Iniciar
        jarvis.start()

    except KeyboardInterrupt:
        print("\n Programa interrompido pelo usuário")
    except Exception as e:
        print(f"ERRO FATAL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()