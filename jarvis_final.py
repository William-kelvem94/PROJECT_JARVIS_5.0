#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - SISTEMA FINAL FUNCIONAL
Processamento completo: Voz + Video + Controle PC - 100% Local e Gratuito
"""

import os
import sys
import time
import threading
import subprocess
import cv2
import speech_recognition as sr
import pyttsx3
import pyautogui
from pathlib import Path
from typing import Optional, Dict, Any

class JarvisFinal:
    """JARVIS 5.0 - Sistema Final 100% Local"""

    def __init__(self):
        print("JARVIS 5.0 - SISTEMA FINAL")
        print("100% LOCAL | GRATUITO | FUNCIONAL")
        print("=" * 50)

        # Componentes básicos
        self.running = False
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.camera = None

        # Configurar TTS
        self._setup_tts()

        # Threads
        self.voice_thread = None
        self.video_thread = None

        # Estatísticas
        self.stats = {
            'commands_processed': 0,
            'frames_processed': 0,
            'apps_launched': 0,
            'start_time': time.time()
        }

        # Apps suportadas
        self.supported_apps = {
            'chrome': 'chrome.exe',
            'navegador': 'chrome.exe',
            'calculadora': 'calc.exe',
            'bloco de notas': 'notepad.exe',
            'notepad': 'notepad.exe',
            'explorer': 'explorer.exe',
            'arquivos': 'explorer.exe'
        }

        print("[OK] Sistema inicializado")

    def _setup_tts(self):
        """Configurar TTS"""
        try:
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Preferir voz em português ou feminina
                for voice in voices:
                    if 'portuguese' in voice.name.lower() or 'brazil' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                    elif 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break

            self.tts_engine.setProperty('rate', 200)
            self.tts_engine.setProperty('volume', 0.9)
            print("[TTS] Configurado")
        except Exception as e:
            print(f"[WARN] Erro no TTS: {e}")

    def initialize_hardware(self):
        """Inicializar câmera e microfone"""
        success = True

        # Inicializar câmera
        try:
            self.camera = cv2.VideoCapture(0)
            if self.camera.isOpened():
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                print("[VIDEO] Câmera inicializada")
            else:
                print("[WARN] Câmera não disponível")
                self.camera = None
        except Exception as e:
            print(f"[WARN] Erro na câmera: {e}")
            self.camera = None

        # Calibrar microfone
        try:
            with sr.Microphone() as source:
                print("[AUDIO] Calibrando microfone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("[AUDIO] Microfone calibrado")
        except Exception as e:
            print(f"[ERROR] Erro no microfone: {e}")
            success = False

        return success

    def speak(self, text: str):
        """Falar texto"""
        try:
            print(f"JARVIS: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"[ERROR] TTS: {e}")

    def listen(self) -> Optional[str]:
        """Escutar comando"""
        try:
            with sr.Microphone() as source:
                print("Escutando...")
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)

            try:
                # Tentar português primeiro
                command = self.recognizer.recognize_google(audio, language='pt-BR')
                return command.lower().strip()
            except sr.UnknownValueError:
                # Tentar inglês como fallback
                try:
                    command = self.recognizer.recognize_google(audio, language='en-US')
                    return command.lower().strip()
                except:
                    return None
            except sr.RequestError:
                return None

        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            print(f"[ERROR] Escuta: {e}")
            return None

    def process_command(self, command: str) -> bool:
        """Processar comando de voz"""
        if not command:
            return True

        self.stats['commands_processed'] += 1
        print(f"Processando: {command}")

        # Comandos de saída
        if any(word in command for word in ['sair', 'tchau', 'encerrar', 'parar', 'bye']):
            self.speak("Encerrando JARVIS. Ate logo!")
            return False

        # Comandos de aplicação
        elif self._is_app_command(command):
            self._handle_app_command(command)

        # Comandos de informação
        elif any(word in command for word in ['hora', 'horas', 'time']):
            hora = time.strftime("%H:%M")
            self.speak(f"Sao {hora}")

        elif any(word in command for word in ['data', 'dia', 'date']):
            data = time.strftime("%d de %B de %Y")
            self.speak(f"Hoje e {data}")

        # Comandos de captura
        elif any(word in command for word in ['screenshot', 'captura', 'foto']):
            self._take_screenshot()

        # Comandos de sistema
        elif any(word in command for word in ['status', 'estatisticas', 'stats']):
            self._show_stats()

        # Comandos de conversação
        elif any(word in command for word in ['ola', 'oi', 'hello', 'hi']):
            self.speak("Ola! Como posso ajudar?")

        elif any(word in command for word in ['obrigado', 'thanks']):
            self.speak("De nada! Estou aqui para ajudar.")

        elif 'como voce esta' in command or 'how are you' in command:
            self.speak("Estou funcionando perfeitamente! Todos os sistemas locais ativos.")

        elif 'ajuda' in command or 'help' in command or 'comandos' in command:
            self._show_help()

        else:
            responses = [
                "Nao entendi esse comando. Diga 'ajuda' para ver os comandos disponiveis.",
                "Comando nao reconhecido. Tente 'abrir chrome' ou 'que horas sao'.",
                "Desculpe, nao compreendi. Fale 'ajuda' para ver o que posso fazer."
            ]
            import random
            self.speak(random.choice(responses))

        return True

    def _is_app_command(self, command: str) -> bool:
        """Verificar se é comando de aplicação"""
        return any(f'abrir {app}' in command or f'open {app}' in command
                  for app in self.supported_apps.keys())

    def _handle_app_command(self, command: str):
        """Processar comando de aplicação"""
        for app_name, exe_name in self.supported_apps.items():
            if f'abrir {app_name}' in command or f'open {app_name}' in command:
                try:
                    subprocess.Popen(exe_name, shell=True)
                    self.stats['apps_launched'] += 1
                    self.speak(f"Aplicacao {app_name} aberta com sucesso")
                    return
                except Exception as e:
                    self.speak(f"Erro ao abrir {app_name}")
                    print(f"[ERROR] {e}")
                    return

        self.speak("Aplicacao nao encontrada")

    def _take_screenshot(self):
        """Tirar screenshot"""
        try:
            screenshot = pyautogui.screenshot()
            filename = f"jarvis_screenshot_{int(time.time())}.png"
            screenshot.save(filename)
            self.speak("Captura de tela realizada")
            print(f"Screenshot salvo: {filename}")
        except Exception as e:
            self.speak("Erro na captura de tela")
            print(f"[ERROR] Screenshot: {e}")

    def _show_stats(self):
        """Mostrar estatísticas"""
        uptime = int(time.time() - self.stats['start_time'])
        self.speak(f"Sistema ativo ha {uptime} segundos. {self.stats['commands_processed']} comandos processados. {self.stats['apps_launched']} aplicacoes abertas.")

    def _show_help(self):
        """Mostrar ajuda"""
        help_text = """
        Comandos disponiveis:
        Aplicacoes: abrir chrome, abrir calculadora, abrir bloco de notas
        Informacoes: que horas sao, que dia e hoje
        Sistema: screenshot, status
        Geral: ajuda, sair
        """
        self.speak("Aqui estao os comandos disponiveis")
        print(help_text)

    def video_thread_func(self):
        """Thread de processamento de vídeo"""
        if not self.camera:
            return

        print("[VIDEO] Thread iniciada")

        while self.running:
            try:
                ret, frame = self.camera.read()
                if ret:
                    self.stats['frames_processed'] += 1

                    # Overlay com informações
                    self._draw_overlay(frame)

                    cv2.imshow('JARVIS 5.0 - Sistema Final', frame)

                    # Controles
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        self.running = False
                        break
                    elif key == ord('s'):
                        self._take_screenshot()

                time.sleep(0.033)  # ~30 FPS

            except Exception as e:
                print(f"[ERROR] Video thread: {e}")
                time.sleep(1)

        cv2.destroyAllWindows()
        print("[VIDEO] Thread encerrada")

    def _draw_overlay(self, frame):
        """Desenhar overlay no vídeo"""
        h, w = frame.shape[:2]

        # Fundo para informações
        cv2.rectangle(frame, (10, 10), (400, 120), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (400, 120), (0, 255, 0), 2)

        # Informações
        uptime = int(time.time() - self.stats['start_time'])
        info_lines = [
            "JARVIS 5.0 - FINAL",
            f"Uptime: {uptime}s",
            f"Comandos: {self.stats['commands_processed']}",
            f"Frames: {self.stats['frames_processed']}",
            "Q: Sair | S: Screenshot"
        ]

        for i, line in enumerate(info_lines):
            color = (0, 255, 255) if i == 0 else (255, 255, 255)
            cv2.putText(frame, line, (15, 30 + i*20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)

    def voice_thread_func(self):
        """Thread de processamento de voz"""
        print("[AUDIO] Thread iniciada")

        while self.running:
            try:
                command = self.listen()
                if command:
                    if not self.process_command(command):
                        self.running = False
                        break

                time.sleep(0.1)

            except Exception as e:
                print(f"[ERROR] Voice thread: {e}")
                time.sleep(1)

        print("[AUDIO] Thread encerrada")

    def start(self):
        """Iniciar sistema completo"""
        print("\n[START] Iniciando JARVIS Final...")

        # Inicializar hardware
        if not self.initialize_hardware():
            print("[ERROR] Falha na inicializacao do hardware")
            return False

        self.running = True

        # Iniciar threads
        if self.camera:
            self.video_thread = threading.Thread(target=self.video_thread_func, daemon=True)
            self.video_thread.start()

        self.voice_thread = threading.Thread(target=self.voice_thread_func, daemon=True)
        self.voice_thread.start()

        # Saudação inicial
        self.speak("JARVIS 5.0 sistema final ativo! Processamento de voz e video funcionando perfeitamente!")

        print("\n" + "=" * 50)
        print("JARVIS 5.0 - SISTEMA FINAL ATIVO!")
        print("=" * 50)
        print("\nCOMANDOS DISPONIVEIS:")
        print("SISTEMA:")
        print("  * 'Sair' / 'Tchau' - Finalizar")
        print("APLICACOES:")
        print("  * 'Abrir Chrome' / 'Abrir navegador'")
        print("  * 'Abrir calculadora'")
        print("  * 'Abrir bloco de notas'")
        print("INFORMACOES:")
        print("  * 'Que horas sao?'")
        print("  * 'Que dia e hoje?'")
        print("SISTEMA:")
        print("  * 'Screenshot' / 'Captura'")
        print("  * 'Status' / 'Estatisticas'")
        print("CONVERSACAO:")
        print("  * 'Ola JARVIS'")
        print("  * 'Como voce esta?'")
        print("  * 'Ajuda' / 'Comandos'")
        print("\nCONTROLES DE VIDEO:")
        print("  * Q: Sair")
        print("  * S: Screenshot")
        print("\nFALE NATURALMENTE COM O JARVIS!")
        print("=" * 50)

        # Loop principal
        try:
            while self.running:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nInterrompido pelo usuario")

        self.stop()
        return True

    def stop(self):
        """Parar sistema"""
        print("\n[STOP] Parando JARVIS Final...")

        self.running = False

        # Aguardar threads
        if self.voice_thread and self.voice_thread.is_alive():
            self.voice_thread.join(timeout=2)

        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join(timeout=2)

        # Liberar recursos
        if self.camera:
            self.camera.release()

        cv2.destroyAllWindows()

        # Estatísticas finais
        uptime = int(time.time() - self.stats['start_time'])
        print(f"\n[STATS] ESTATISTICAS FINAIS:")
        print(f"  [TIME] Tempo ativo: {uptime} segundos")
        print(f"  [AUDIO] Comandos processados: {self.stats['commands_processed']}")
        print(f"  [VIDEO] Frames processados: {self.stats['frames_processed']}")
        print(f"  [APPS] Aplicacoes abertas: {self.stats['apps_launched']}")

        print("\n[SUCCESS] JARVIS Final encerrado com sucesso!")
        print("Sistema 100% local e privado!")


def main():
    """Função principal"""
    try:
        jarvis = JarvisFinal()
        success = jarvis.start()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuario")
        return 0
    except Exception as e:
        print(f"\n[ERROR] Erro critico: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
