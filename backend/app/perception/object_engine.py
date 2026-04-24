import cv2
import torch
import numpy as np
from ultralytics import YOLO
from loguru import logger
from ..config import settings

class ObjectEngine:
    """
    JARVIS Spatial Awareness - Detecta objetos no ambiente físico do usuário.
    Otimizado para detecção de setup: laptops, celulares, canecas, livros, etc.
    """
    
    def __init__(self):
        self.model_path = "yolov8n.pt" # O Ultralytics baixa automaticamente se não existir
        self.model = None
        self.enabled = True
        self._initialize_model()

    def _initialize_model(self):
        try:
            # Seleciona dispositivo baseado no Perfil de Hardware (settings)
            device = settings.DEVICE_TYPE if settings.DEVICE_TYPE != "auto" else (
                "cuda" if torch.cuda.is_available() else "cpu"
            )
            
            logger.info(f"👁️ Iniciando Visão Espacial YOLOv8 em {device.upper()}...")
            self.model = YOLO(self.model_path)
            self.model.to(device)
            
            # Classes de interesse (COCO dataset)
            # 62: tv, 63: laptop, 64: mouse, 65: remote, 66: keyboard, 67: cell phone, 73: book, 41: cup
            self.target_classes = [41, 63, 64, 66, 67, 73] 
            
        except Exception as e:
            logger.error(f"Falha ao iniciar YOLOv8: {e}")
            self.enabled = False

    def analyze_frame(self, frame):
        """
        Analisa um frame e retorna os objetos detectados.
        """
        if not self.enabled or self.model is None:
            return []

        try:
            # Inferência rápida
            results = self.model.predict(
                source=frame, 
                conf=0.5, 
                verbose=False, 
                imgsz=320, # Reduzido para velocidade máxima
                classes=self.target_classes
            )
            
            detected_objects = []
            if results and len(results) > 0:
                for box in results[0].boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    label = self.model.names[cls_id]
                    detected_objects.append({
                        "label": label,
                        "confidence": conf
                    })
                    
            return detected_objects
            
        except Exception as e:
            logger.debug(f"Erro na análise de objetos: {e}")
            return []

# Singleton
object_engine = ObjectEngine()
