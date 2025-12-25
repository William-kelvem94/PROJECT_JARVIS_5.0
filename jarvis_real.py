#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - SISTEMA REAL QUE FUNCIONA
Processamento completo: Voz + Vídeo + IA + Controle do PC
"""

import os
import sys
import time
import threading
import subprocess
import cv2
import speech_recognition as sr
import pyttsx3
from pathlib import Path

# Adicionar ao path
sys.path.insert(0, str(Path(__file__).parent))

class JarvisReal:
    """JARVIS que FUNCIONA DE VERDADE"""
    
    def __init__(self):
        print("=" * 60)
        print("JARVIS 5.0 - SISTEMA REAL")
        print("PROCESSAMENTO COMPLETO FUNCIONANDO")
        print("=" * 60)
        
        # Inicializar componentes
        self.running = False
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.camera = None
        
        # Configurar TTS
        self.tts_engine.setProperty('rate', 180)
        self.tts_engine.setProperty('volume', 0.9)
        
        # Threads
        self.voice_thread = None
        self.video_thread = None
        
        # Estatísticas
        self.stats = {
            'comandos': 0,
            'frames': 0,
            'start_time': time.time()
        }
        
        print("[INIT] Componentes básicos inicializados")
    
    def inicializar_camera(self):
        """Inicializa câmera"""
        try:
            self.camera = cv2.VideoCapture(0)
            if self.camera.isOpened():
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                print("[VIDEO] Câmera inicializada: 640x480")
                return True
            else:
                print("[VIDEO] Câmera não disponível")
                return False
        except Exception as e:
            print(f"[VIDEO] Erro na câmera: {e}")
            return False
    
    def calibrar_microfone(self):
        """Calibra microfone"""
        try:
            print("[AUDIO] Calibrando microfone...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print("[AUDIO] Microfone calibrado")
            return True
        except Exception as e:
            print(f"[AUDIO] Erro no microfone: {e}")
            return False
    
    def falar(self, texto):
        """Fala texto"""
        try:
            print(f"[JARVIS] {texto}")
            self.tts_engine.say(texto)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"[TTS] Erro: {e}")
    
    def escutar(self):
        """Escuta comando"""
        try:
            with self.microphone as source:
                print("[ESCUTANDO]...")
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
            
            try:
                comando = self.recognizer.recognize_google(audio, language='pt-BR')
                print(f"[COMANDO] {comando}")
                return comando.lower()
            except sr.UnknownValueError:
                return None
            except sr.RequestError as e:
                print(f"[RECONHECIMENTO] Erro: {e}")
                return None
                
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            print(f"[AUDIO] Erro: {e}")
            return None
    
    def processar_comando(self, comando):
        """Processa comando de voz"""
        if not comando:
            return True
        
        self.stats['comandos'] += 1
        
        # Comandos de saída
        if any(word in comando for word in ['sair', 'tchau', 'encerrar', 'parar']):
            self.falar("Encerrando JARVIS. Até logo!")
            return False
        
        # Comandos de aplicação
        elif 'abrir chrome' in comando or 'abrir navegador' in comando:
            self.falar("Abrindo Chrome")
            self.executar_aplicacao('chrome')
        
        elif 'abrir calculadora' in comando:
            self.falar("Abrindo calculadora")
            self.executar_aplicacao('calc')
        
        elif 'abrir bloco de notas' in comando or 'abrir notepad' in comando:
            self.falar("Abrindo bloco de notas")
            self.executar_aplicacao('notepad')
        
        elif 'abrir explorer' in comando or 'abrir arquivos' in comando:
            self.falar("Abrindo explorador de arquivos")
            self.executar_aplicacao('explorer')
        
        # Comandos de sistema
        elif 'que horas' in comando or 'hora atual' in comando:
            hora = time.strftime("%H:%M")
            self.falar(f"São {hora}")
        
        elif 'que dia' in comando or 'data' in comando:
            data = time.strftime("%d de %B de %Y")
            self.falar(f"Hoje é {data}")
        
        elif 'screenshot' in comando or 'captura' in comando:
            self.fazer_screenshot()
        
        elif 'estatísticas' in comando or 'status' in comando:
            self.mostrar_estatisticas()
        
        # Comandos de conversação
        elif 'olá' in comando or 'oi' in comando:
            self.falar("Olá! Como posso ajudar?")
        
        elif 'como você está' in comando:
            self.falar("Estou funcionando perfeitamente! Todos os sistemas operacionais.")
        
        elif 'o que você pode fazer' in comando or 'ajuda' in comando:
            self.falar("Posso abrir programas, dar informações, fazer capturas de tela e muito mais!")
        
        else:
            self.falar("Comando não reconhecido. Diga 'ajuda' para ver o que posso fazer.")
        
        return True
    
    def executar_aplicacao(self, app):
        """Executa aplicação no Windows"""
        try:
            apps = {
                'chrome': 'chrome.exe',
                'calc': 'calc.exe',
                'notepad': 'notepad.exe',
                'explorer': 'explorer.exe'
            }
            
            if app in apps:
                subprocess.Popen(apps[app], shell=True)
                print(f"[EXEC] {apps[app]} executado")
                return True
            else:
                print(f"[EXEC] Aplicação {app} não encontrada")
                return False
                
        except Exception as e:
            print(f"[EXEC] Erro: {e}")
            return False
    
    def fazer_screenshot(self):
        """Faz screenshot"""
        try:
            if self.camera and self.camera.isOpened():
                ret, frame = self.camera.read()
                if ret:
                    filename = f"jarvis_screenshot_{int(time.time())}.jpg"
                    cv2.imwrite(filename, frame)
                    self.falar(f"Captura salva como {filename}")
                    print(f"[SCREENSHOT] {filename}")
                else:
                    self.falar("Erro ao capturar imagem")
            else:
                self.falar("Câmera não disponível")
        except Exception as e:
            print(f"[SCREENSHOT] Erro: {e}")
    
    def mostrar_estatisticas(self):
        """Mostra estatísticas"""
        uptime = int(time.time() - self.stats['start_time'])
        self.falar(f"Sistema ativo há {uptime} segundos. {self.stats['comandos']} comandos processados. {self.stats['frames']} frames de vídeo.")
    
    def thread_video(self):
        """Thread de processamento de vídeo"""
        if not self.camera:
            return
        
        print("[VIDEO] Thread de vídeo iniciada")
        
        while self.running:
            try:
                ret, frame = self.camera.read()
                if ret:
                    self.stats['frames'] += 1
                    
                    # Mostrar vídeo
                    cv2.putText(frame, f"JARVIS 5.0 - ATIVO", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, f"Comandos: {self.stats['comandos']}", (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.putText(frame, f"Frames: {self.stats['frames']}", (10, 100), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.putText(frame, "Q: Sair | S: Screenshot", (10, 450), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                    
                    cv2.imshow('JARVIS 5.0 - Sistema Real', frame)
                    
                    # Controles
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        print("[VIDEO] Saída solicitada")
                        self.running = False
                        break
                    elif key == ord('s'):
                        self.fazer_screenshot()
                
                time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                print(f"[VIDEO] Erro: {e}")
                time.sleep(1)
        
        cv2.destroyAllWindows()
        print("[VIDEO] Thread de vídeo encerrada")
    
    def thread_voz(self):
        """Thread de processamento de voz"""
        print("[AUDIO] Thread de voz iniciada")
        
        while self.running:
            try:
                comando = self.escutar()
                if comando:
                    if not self.processar_comando(comando):
                        self.running = False
                        break
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"[AUDIO] Erro na thread: {e}")
                time.sleep(1)
        
        print("[AUDIO] Thread de voz encerrada")
    
    def iniciar(self):
        """Inicia o sistema completo"""
        print("\n[INICIANDO] Sistema JARVIS Real...")
        
        # Inicializar componentes
        camera_ok = self.inicializar_camera()
        mic_ok = self.calibrar_microfone()
        
        if not mic_ok:
            print("[ERRO] Microfone não disponível")
            return False
        
        self.running = True
        
        # Iniciar threads
        if camera_ok:
            self.video_thread = threading.Thread(target=self.thread_video, daemon=True)
            self.video_thread.start()
            print("[VIDEO] Thread iniciada")
        
        self.voice_thread = threading.Thread(target=self.thread_voz, daemon=True)
        self.voice_thread.start()
        print("[AUDIO] Thread iniciada")
        
        # Saudação
        self.falar("JARVIS 5.0 sistema real ativo! Processamento de voz e vídeo funcionando!")
        
        print("\n" + "=" * 60)
        print("JARVIS 5.0 - SISTEMA REAL ATIVO!")
        print("=" * 60)
        print("\n[COMANDOS DISPONÍVEIS]")
        print("- 'Abrir Chrome/navegador'")
        print("- 'Abrir calculadora'") 
        print("- 'Abrir bloco de notas'")
        print("- 'Abrir explorer/arquivos'")
        print("- 'Que horas são?'")
        print("- 'Que dia é hoje?'")
        print("- 'Fazer screenshot'")
        print("- 'Mostrar estatísticas'")
        print("- 'Olá JARVIS'")
        print("- 'Sair/Tchau/Encerrar'")
        print("\n[CONTROLES DE VÍDEO]")
        print("- Q: Sair")
        print("- S: Screenshot")
        print("\nFale naturalmente com o JARVIS!")
        
        # Loop principal
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[INTERROMPIDO] Encerrando...")
        
        # Finalizar
        self.parar()
        return True
    
    def parar(self):
        """Para o sistema"""
        print("\n[PARANDO] Sistema JARVIS...")
        self.running = False
        
        # Aguardar threads
        if self.voice_thread and self.voice_thread.is_alive():
            self.voice_thread.join(timeout=3)
        
        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join(timeout=3)
        
        # Fechar câmera
        if self.camera:
            self.camera.release()
        
        cv2.destroyAllWindows()
        
        # Estatísticas finais
        uptime = int(time.time() - self.stats['start_time'])
        print(f"[FINAL] Sistema ativo por {uptime}s")
        print(f"[FINAL] {self.stats['comandos']} comandos processados")
        print(f"[FINAL] {self.stats['frames']} frames de vídeo")
        print("[OK] JARVIS encerrado!")


def main():
    """Função principal"""
    try:
        jarvis = JarvisReal()
        return 0 if jarvis.iniciar() else 1
    except KeyboardInterrupt:
        print("\n[INTERROMPIDO] Saindo...")
        return 0
    except Exception as e:
        print(f"[ERRO CRÍTICO] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
