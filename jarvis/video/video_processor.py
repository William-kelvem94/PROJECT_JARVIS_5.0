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
                return None
            
            self.current_frame = frame
            self.stats['frames_processed'] += 1
            
            # Processar detecções
            results = self._analyze_frame(frame)
            
            # Atualizar frame anterior
            self.prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro no processamento de frame: {e}")
            return None
    
    def _analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analisa um frame e extrai informações"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        results = {
            'timestamp': time.time(),
            'faces': [],
            'eyes': 0,
            'motion': 0,
            'gestures': []
        }
        
        # Detecção facial
        if self.face_cascade and not self.face_cascade.empty():
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50)
            )
            
            for (x, y, w, h) in faces:
                face_info = {
                    'x': int(x), 'y': int(y),
                    'width': int(w), 'height': int(h),
                    'center': (int(x + w/2), int(y + h/2))
                }
                results['faces'].append(face_info)
                
                # Detectar olhos na região facial
                roi_gray = gray[y:y+h, x:x+w]
                if self.eye_cascade and not self.eye_cascade.empty():
                    eyes = self.eye_cascade.detectMultiScale(roi_gray)
                    results['eyes'] += len(eyes)
            
            if len(faces) > 0:
                self.stats['faces_detected'] += len(faces)
        
        # Detecção de movimento
        if self.prev_frame is not None:
            motion = self._detect_motion(gray)
            results['motion'] = motion
            
            if motion > 1000:  # Threshold para movimento significativo
                self.stats['motion_events'] += 1
        
        # Detecção de gestos (simplificada)
        gestures = self._detect_gestures(frame)
        results['gestures'] = gestures
        if gestures:
            self.stats['gestures_detected'] += len(gestures)
        
        return results
    
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
    
    def _detect_gestures(self, frame: np.ndarray) -> List[str]:
        """Detecta gestos básicos (implementação simplificada)"""
        gestures = []
        
        # Esta é uma implementação básica
        # Em uma versão completa, usaríamos MediaPipe ou similar
        try:
            # Análise básica de contornos para gestos
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
            
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 1000 < area < 10000:  # Área típica de uma mão
                    # Análise básica da forma
                    hull = cv2.convexHull(contour)
                    hull_area = cv2.contourArea(hull)
                    
                    if hull_area > 0:
                        solidity = area / hull_area
                        
                        # Classificação básica baseada na solidez
                        if solidity > 0.9:
                            gestures.append('closed_fist')
                        elif solidity > 0.7:
                            gestures.append('open_palm')
                        else:
                            gestures.append('pointing')
            
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
