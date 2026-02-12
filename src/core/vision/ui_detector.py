"""
Módulo de Detecção de Elementos de Interface (UI Detector)
Usa o YOLOv8 para identificar ícones, botões e outros componentes visuais.
"""

import os
import logging
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False

from src.utils.config import config

logger = logging.getLogger(__name__)

class UIDetector:
    """Classe para detecção de objetos de interface usando YOLOv8"""

    def __init__(self, model_path: Optional[str] = None):
        self.enabled = config.get_setting('vision.yolo_enabled', True)
        self.model = None
        
        if self.enabled and ULTRALYTICS_AVAILABLE:
            try:
                # Se não houver modelo customizado, usa o YOLOv8n (nano) na pasta models
                path = model_path or config.get_setting('vision.yolo_model', 'models/vision/yolov8n.pt')
                # Garantir caminho absoluto para estabilidade
                if not os.path.isabs(path):
                    path = str(Path(__file__).parent.parent.parent.parent / path)
                
                self.model = YOLO(path)
                logger.info(f"Modelo YOLO carregado: {path}")
            except Exception as e:
                logger.error(f"Erro ao carregar modelo YOLO: {e}")
                self.enabled = False
        else:
            if not ULTRALYTICS_AVAILABLE:
                logger.warning("Ultralytics não instalado. YOLO UI Detector desativado.")
            self.enabled = False

    def detect_elements(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Detecta elementos de UI na imagem
        Returns: Lista de dicionários com {label, confidence, x, y, w, h}
        """
        if not self.enabled or self.model is None:
            return []

        try:
            results = self.model(image_path, verbose=False)
            detections = []

            for r in results:
                boxes = r.boxes
                for box in boxes:
                    # Coordenadas (xywh)
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    w = x2 - x1
                    h = y2 - y1
                    
                    label_id = int(box.cls[0])
                    label = self.model.names[label_id]
                    confidence = float(box.conf[0])

                    if confidence >= config.get_setting('vision.yolo_confidence', 0.25):
                        detections.append({
                            'label': label,
                            'confidence': confidence,
                            'x': int(x1),
                            'y': int(y1),
                            'width': int(w),
                            'height': int(h),
                            'center': (int(x1 + w/2), int(y1 + h/2))
                        })

            logger.info(f"YOLO detectou {len(detections)} elementos em {image_path}")
            return detections

        except Exception as e:
            logger.error(f"Erro na detecção YOLO: {e}")
            return []

    def get_summary(self, detections: List[Dict[str, Any]]) -> str:
        """Gera uma descrição textual do que foi visto"""
        if not detections:
            return "Nenhum elemento visual identificado além de texto."
            
        summary_parts = []
        labels = [d['label'] for d in detections]
        unique_labels = set(labels)
        
        for label in unique_labels:
            count = labels.count(label)
            summary_parts.append(f"{count} {label}(s)")
            
        return "Elementos visuais identificados: " + ", ".join(summary_parts)

# Instância global removida para evitar execução durante import
# ui_detector = UIDetector()
