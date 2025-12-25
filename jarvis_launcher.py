#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Launcher Principal
Sistema integrado completo com processamento de voz, vídeo, IA e automação
"""

import sys
import os
import time
import cv2
import threading
from pathlib import Path

# Adicionar diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from jarvis.core.integrated_system import IntegratedSystem
from jarvis.video.video_processor import VideoProcessor
from jarvis.ai.training_manager import TrainingManager


class JarvisLauncher:
    """Launcher principal do JARVIS 5.0"""
    
    def __init__(self):
        self.integrated_system = None
        self.video_processor = None
        self.training_manager = None
        self.display_thread = None
        self.running = False
        
    def initialize(self):
        """Inicializa todos os sistemas"""
        print("=" * 60)
        print("JARVIS 5.0 - SISTEMA INTEGRADO COMPLETO")
        print("Processamento de Voz + Video + IA + Automacao")
        print("=" * 60)
        
        try:
            # 1. Sistema Integrado Principal
            print("\n[INICIANDO] Sistema Integrado Principal...")
            self.integrated_system = IntegratedSystem()
            
            if not self.integrated_system.initialize_all_systems():
                print("[ERRO] Falha na inicializacao do sistema principal")
                return False
            
            print("[OK] Sistema principal inicializado!")
            
            # 2. Processador de Vídeo
            print("\n[INICIANDO] Processador de Video...")
            try:
                config = self.integrated_system.config
                self.video_processor = VideoProcessor(config)
                
                if self.video_processor.start_processing():
                    print("[OK] Processador de video ativo!")
                else:
                    print("[AVISO] Video nao disponivel - continuando sem video")
                    
            except Exception as e:
                print(f"[AVISO] Video limitado: {e}")
                self.video_processor = None
            
            # 3. Gerenciador de Treinamento
            print("\n[INICIANDO] Gerenciador de Treinamento de IA...")
            try:
                config = self.integrated_system.config
                self.training_manager = TrainingManager(config)
                print("[OK] Gerenciador de treinamento ativo!")
                
            except Exception as e:
                print(f"[AVISO] Treinamento limitado: {e}")
                self.training_manager = None
            
            # 4. Exibir capacidades
            self._display_capabilities()
            
            return True
            
        except Exception as e:
            print(f"[ERRO CRITICO] {e}")
            return False
    
    def _display_capabilities(self):
        """Exibe todas as capacidades do sistema"""
        print("\n[SISTEMA] Capacidades Ativas:")
        print("- Reconhecimento de voz neural")
        print("- Sintese de voz natural (Microsoft Edge TTS)")
        print("- IA conversacional com aprendizado continuo")
        print("- Processamento de linguagem natural")
        print("- Tomada de decisoes inteligente")
        print("- Controle e automacao do Windows")
        
        if self.video_processor:
            print("- Processamento de video HD em tempo real")
            print("- Deteccao facial e reconhecimento de gestos")
            print("- Analise de movimento")
            print("- Interface visual interativa")
        
        if self.training_manager:
            print("- Treinamento automatico de modelos de IA")
            print("- Aprendizado baseado em feedback")
            print("- Memoria de preferencias do usuario")
            print("- Otimizacao continua de performance")
    
    def start_display_thread(self):
        """Inicia thread de exibição de vídeo"""
        if not self.video_processor:
            return
            
        def display_loop():
            print("\n[VIDEO] Interface visual ativa")
            print("[INFO] Pressione 'Q' para sair, 'S' para screenshot, 'R' para reset")
            
            while self.running:
                try:
                    # Processar frame
                    result = self.video_processor.process_frame()
                    
                    if result:
                        # Registrar dados para treinamento
                        if self.training_manager and result.get('faces'):
                            self.training_manager.record_user_preference(
                                'video', 'faces_detected', len(result['faces'])
                            )
                    
                    # Obter frame para exibição
                    display_frame = self.video_processor.get_display_frame()
                    
                    if display_frame is not None:
                        cv2.imshow('JARVIS 5.0 - Sistema Integrado', display_frame)
                        
                        # Controles
                        key = cv2.waitKey(1) & 0xFF
                        if key == ord('q'):
                            print("[VIDEO] Saida solicitada via interface")
                            self.running = False
                            break
                        elif key == ord('s'):
                            filename = self.video_processor.save_screenshot()
                            print(f"[CAPTURA] Screenshot salvo: {filename}")
                        elif key == ord('r'):
                            self.video_processor.reset_stats()
                            print("[RESET] Estatisticas de video reiniciadas")
                    
                    time.sleep(0.03)  # ~30 FPS
                    
                except Exception as e:
                    print(f"[ERRO VIDEO] {e}")
                    time.sleep(1)
            
            cv2.destroyAllWindows()
            print("[VIDEO] Interface visual encerrada")
        
        self.display_thread = threading.Thread(target=display_loop, daemon=True)
        self.display_thread.start()
    
    def start(self):
        """Inicia o sistema completo"""
        if not self.initialize():
            return False
        
        self.running = True
        
        # Iniciar interface de vídeo
        self.start_display_thread()
        
        print("\n" + "=" * 60)
        print("JARVIS 5.0 - SISTEMA COMPLETO ATIVO!")
        print("=" * 60)
        print("\n[CONTROLES]")
        print("- Fale naturalmente com o JARVIS")
        
        if self.video_processor:
            print("- Interface de video com overlay inteligente")
            print("- Controles: Q=Sair, S=Screenshot, R=Reset")
        
        print("- Comandos de voz: 'sair', 'tchau', 'encerrar' para finalizar")
        print("- Ctrl+C para parada de emergencia")
        
        # Saudação inicial integrada
        welcome_msg = "JARVIS 5.0 sistema completo ativo! Processamento de voz, video e IA funcionando perfeitamente."
        
        # Registrar interação para treinamento
        if self.training_manager:
            self.training_manager.record_voice_interaction(
                "sistema_iniciado", welcome_msg, True
            )
        
        # Iniciar sistema integrado (loop principal)
        try:
            self.integrated_system.start_integrated_system()
            
        except KeyboardInterrupt:
            print("\n[INTERROMPIDO] Sistema encerrado pelo usuario")
        
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """Para todos os sistemas"""
        print("\n[ENCERRANDO] Parando sistema completo...")
        self.running = False
        
        # Parar sistema integrado
        if self.integrated_system:
            self.integrated_system.stop_integrated_system()
        
        # Parar processador de vídeo
        if self.video_processor:
            self.video_processor.stop()
        
        # Salvar dados de treinamento
        if self.training_manager:
            self.training_manager.save_training_data()
            
            # Exibir resumo de treinamento
            summary = self.training_manager.get_training_summary()
            print(f"\n[TREINAMENTO] Resumo Final:")
            print(f"- Total de interacoes: {summary['total_interactions']}")
            print(f"- Comandos de voz: {summary['voice_commands']}")
            print(f"- Conversacoes: {summary['conversations']}")
            print(f"- Preferencias: {summary['user_preferences']}")
            print(f"- Feedback: {summary['feedback_entries']}")
        
        # Aguardar thread de vídeo
        if self.display_thread and self.display_thread.is_alive():
            self.display_thread.join(timeout=3)
        
        print("[OK] JARVIS 5.0 sistema completo encerrado!")


def main():
    """Função principal"""
    try:
        launcher = JarvisLauncher()
        success = launcher.start()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n[INTERROMPIDO] Encerrando JARVIS...")
        return 0
    
    except Exception as e:
        print(f"[ERRO CRITICO] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
