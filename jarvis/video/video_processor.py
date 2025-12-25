#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Processador de Vídeo Integrado
Processamento de vídeo em tempo real com detecção facial e reconhecimento de gestos
"""

import cv2
import numpy as np
import time
from typing import Optional, Dict, List, Any
from pathlib import Path

from ..core.logger import Logger


class VideoProcessor:
    """Processador de vídeo integrado para o JARVIS"""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa o processador de vídeo"""
        self.config = config
        self.logger = Logger("VIDEO_PROCESSOR", "INFO")
        
        # Configurações de vídeo
        self.video_config = config.get('video', {})
        self.width = self.video_config.get('width', 1280)
        self.height = self.video_config.get('height', 720)
        self.fps = self.video_config.get('fps', 30)
        
        # Componentes de visão
        self.camera = None
        self.face_cascade = None
        self.eye_cascade = None
        
        # Estado do processamento
        self.running = False
        self.current_frame = None
        self.prev_frame = None
        
        # Estatísticas
        self.stats = {
            'frames_processed': 0,
            'faces_detected': 0,
            'gestures_detected': 0,
            'motion_events': 0,
            'start_time': time.time()
        }
        
        # Inicializar componentes
        self._initialize_camera()
        self._initialize_classifiers()
    
    def _initialize_camera(self):
        """Inicializa a câmera"""
        try:
            self.camera = cv2.VideoCapture(0)
            
            if self.camera.isOpened():
                # Configurar câmera
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self.camera.set(cv2.CAP_PROP_FPS, self.fps)
                
                self.logger.info(f"Câmera inicializada: {self.width}x{self.height}@{self.fps}fps")
            else:
                self.logger.warning("Câmera não disponível")
                self.camera = None
                
        except Exception as e:
            self.logger.error(f"Erro ao inicializar câmera: {e}")
            self.camera = None
    
    def _initialize_classifiers(self):
        """Inicializa classificadores de detecção"""
        try:
            cascade_path = cv2.data.haarcascades
            
            # Classificador de faces
            face_cascade_file = cascade_path + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(face_cascade_file)
            
            # Classificador de olhos
            eye_cascade_file = cascade_path + 'haarcascade_eye.xml'
            self.eye_cascade = cv2.CascadeClassifier(eye_cascade_file)
            
            if not self.face_cascade.empty() and not self.eye_cascade.empty():
                self.logger.info("Classificadores de detecção carregados")
            else:
                self.logger.warning("Erro ao carregar classificadores")
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar classificadores: {e}")
    
    def start_processing(self):
        """Inicia o processamento de vídeo"""
        if not self.camera:
            self.logger.warning("Câmera não disponível para processamento")
            return False
        
        self.running = True
        self.logger.info("Processamento de vídeo iniciado")
        return True
    
    def process_frame(self) -> Optional[Dict[str, Any]]:
        """Processa um frame de vídeo e retorna resultados"""
        if not self.running or not self.camera:
            return None
        
        try:
            ret, frame = self.camera.read()
            if not ret:
                time.sleep(0.01)  # Pequena pausa se não conseguir ler frame
                return None
            
            # Redimensionar frame para otimizar processamento
            if frame.shape[1] > 640:
                scale_factor = 640 / frame.shape[1]
                new_width = 640
                new_height = int(frame.shape[0] * scale_factor)
                frame = cv2.resize(frame, (new_width, new_height))
            
            self.current_frame = frame
            self.stats['frames_processed'] += 1
            
            # Processar detecções apenas a cada 3 frames para otimizar
            results = None
            if self.stats['frames_processed'] % 3 == 0:
                results = self._analyze_frame(frame)
            else:
                # Frame básico sem análise pesada
                results = {
                    'timestamp': time.time(),
                    'faces': [],
                    'eyes': 0,
                    'motion': 0,
                    'gestures': [],
                    'skip_analysis': True
                }
            
            # Atualizar frame anterior apenas quando necessário
            if self.stats['frames_processed'] % 2 == 0:
                self.prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro no processamento de frame: {e}")
            time.sleep(0.1)  # Pausa maior em caso de erro
            return None
    
    def _analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analisa um frame e extrai informações (otimizado)"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            results = {
                'timestamp': time.time(),
                'faces': [],
                'eyes': 0,
                'motion': 0,
                'gestures': []
            }
            
            # Detecção facial otimizada
            if self.face_cascade and not self.face_cascade.empty():
                # Parâmetros otimizados para melhor performance
                faces = self.face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.2,  # Aumentado para menos detecções
                    minNeighbors=3,   # Reduzido para melhor performance
                    minSize=(60, 60), # Aumentado o tamanho mínimo
                    maxSize=(300, 300)  # Limitado o tamanho máximo
                )
                
                # Limitar número de faces processadas
                for i, (x, y, w, h) in enumerate(faces[:3]):  # Máximo 3 faces
                    face_info = {
                        'x': int(x), 'y': int(y),
                        'width': int(w), 'height': int(h),
                        'center': (int(x + w/2), int(y + h/2))
                    }
                    results['faces'].append(face_info)
                    
                    # Detectar olhos apenas na primeira face para otimizar
                    if i == 0 and self.eye_cascade and not self.eye_cascade.empty():
                        roi_gray = gray[y:y+h, x:x+w]
                        eyes = self.eye_cascade.detectMultiScale(
                            roi_gray, scaleFactor=1.1, minNeighbors=3
                        )
                        results['eyes'] = len(eyes)
                
                if len(faces) > 0:
                    self.stats['faces_detected'] += len(faces)
            
            # Detecção de movimento otimizada
            if self.prev_frame is not None:
                motion = self._detect_motion(gray)
                results['motion'] = motion
                
                if motion > 2000:  # Threshold aumentado
                    self.stats['motion_events'] += 1
            
            # Detecção de gestos apenas se houver movimento significativo
            if results['motion'] > 1500:
                gestures = self._detect_gestures_optimized(frame)
                results['gestures'] = gestures
                if gestures:
                    self.stats['gestures_detected'] += len(gestures)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro na análise de frame: {e}")
            return {
                'timestamp': time.time(),
                'faces': [],
                'eyes': 0,
                'motion': 0,
                'gestures': [],
                'error': str(e)
            }
    
    def _detect_motion(self, current_gray: np.ndarray) -> int:
        """Detecta movimento entre frames"""
        if self.prev_frame is None:
            return 0
        
        try:
            diff = cv2.absdiff(self.prev_frame, current_gray)
            thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
            motion_pixels = cv2.countNonZero(thresh)
            return motion_pixels
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de movimento: {e}")
            return 0
    
    def _detect_gestures_optimized(self, frame: np.ndarray) -> List[str]:
        """Detecta gestos básicos (versão otimizada)"""
        gestures = []
        
        try:
            # Reduzir resolução para análise de gestos
            h, w = frame.shape[:2]
            small_frame = cv2.resize(frame, (w//2, h//2))
            
            # Análise básica otimizada
            gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            thresh = cv2.threshold(blurred, 80, 255, cv2.THRESH_BINARY)[1]
            
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Processar apenas os 3 maiores contornos
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:3]
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 500 < area < 5000:  # Área ajustada para frame menor
                    # Análise simplificada da forma
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter * perimeter)
                        
                        # Classificação baseada na circularidade
                        if circularity > 0.7:
                            gestures.append('closed_fist')
                        elif circularity > 0.4:
                            gestures.append('open_palm')
                        else:
                            gestures.append('pointing')
                        
                        # Limitar a 2 gestos para performance
                        if len(gestures) >= 2:
                            break
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de gestos: {e}")
        
        return gestures
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """Retorna o frame atual"""
        return self.current_frame.copy() if self.current_frame is not None else None
    
    def get_display_frame(self) -> Optional[np.ndarray]:
        """Retorna frame com overlay para exibição"""
        if self.current_frame is None:
            return None
        
        display_frame = self.current_frame.copy()
        
        # Adicionar overlay com informações
        self._draw_overlay(display_frame)
        
        return display_frame
    
    def _draw_overlay(self, frame: np.ndarray):
        """Desenha overlay com informações no frame"""
        h, w = frame.shape[:2]
        
        # Fundo para informações
        cv2.rectangle(frame, (10, 10), (400, 120), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (400, 120), (0, 255, 0), 2)
        
        # Informações do sistema
        uptime = time.time() - self.stats['start_time']
        info_lines = [
            "JARVIS 5.0 - PROCESSAMENTO DE VIDEO",
            f"Uptime: {int(uptime//3600):02d}:{int((uptime%3600)//60):02d}:{int(uptime%60):02d}",
            f"Frames: {self.stats['frames_processed']}",
            f"Faces: {self.stats['faces_detected']}",
            f"Gestos: {self.stats['gestures_detected']}",
            f"Movimento: {self.stats['motion_events']} eventos"
        ]
        
        for i, line in enumerate(info_lines):
            color = (0, 255, 255) if i == 0 else (255, 255, 255)
            font_scale = 0.6 if i == 0 else 0.5
            cv2.putText(frame, line, (15, 25 + i*15), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, 1)
        
        # Status no canto inferior
        cv2.putText(frame, "Q: Sair | S: Screenshot | R: Reset", 
                   (10, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    def save_screenshot(self, filename: Optional[str] = None) -> str:
        """Salva screenshot do frame atual"""
        if self.current_frame is None:
            raise ValueError("Nenhum frame disponível para screenshot")
        
        if filename is None:
            timestamp = int(time.time())
            filename = f"jarvis_screenshot_{timestamp}.jpg"
        
        cv2.imwrite(filename, self.current_frame)
        self.logger.info(f"Screenshot salvo: {filename}")
        return filename
    
    def reset_stats(self):
        """Reinicia estatísticas"""
        self.stats = {
            'frames_processed': 0,
            'faces_detected': 0,
            'gestures_detected': 0,
            'motion_events': 0,
            'start_time': time.time()
        }
        self.logger.info("Estatísticas de vídeo reiniciadas")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do processamento"""
        uptime = time.time() - self.stats['start_time']
        stats = self.stats.copy()
        stats['uptime'] = uptime
        stats['fps_avg'] = stats['frames_processed'] / uptime if uptime > 0 else 0
        return stats
    
    def stop(self):
        """Para o processamento de vídeo"""
        self.running = False
        
        if self.camera:
            self.camera.release()
        
        cv2.destroyAllWindows()
        
        # Estatísticas finais
        uptime = time.time() - self.stats['start_time']
        self.logger.info(f"Processamento finalizado após {uptime:.1f}s")
        self.logger.info(f"Frames processados: {self.stats['frames_processed']}")
        self.logger.info(f"FPS médio: {self.stats['frames_processed']/uptime:.1f}")
        
        self.logger.info("Processador de vídeo finalizado")
