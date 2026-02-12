# ============================================================================
# JARVIS SINGULARITY - Vision Enhancer (Phase 4: Vision Enhancement)
# ============================================================================
# Detecção avançada de UI com YOLO + OCR
# Permite JARVIS "ver" e entender elementos na tela
# ============================================================================

import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import cv2

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# IMPORTS CONDICIONAIS
# -------------------------------------------------------------------------
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logger.warning("⚠️ Ultralytics YOLO não disponível - detecção avançada desabilitada")

try:
    import easyocr
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger.warning("⚠️ EasyOCR não disponível - OCR desabilitado")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("⚠️ PIL não disponível")


# ============================================================================
# VISION ENHANCER
# ============================================================================
class VisionEnhancer:
    """
    Visão computacional avançada para JARVIS.
    
    CAPACIDADES:
    - Detecção de UI elements com YOLO
    - OCR para extrair texto
    - Identificação de botões, inputs, menus
    - Coordenadas precisas para cliques
    """
    
    def __init__(self, model_size: str = "n"):
        """
        Inicializa o Vision Enhancer.
        
        Args:
            model_size: Tamanho do modelo YOLO (n=nano, s=small, m=medium)
        """
        logger.info("👁️ Inicializando Vision Enhancer...")
        
        self.yolo_model = None
        self.ocr_reader = None
        self.model_size = model_size
        
        # Inicializar YOLO
        if YOLO_AVAILABLE:
            try:
                # Usar modelo pré-treinado YOLO no diretório correto
                model_path = f"models/vision/yolov8{model_size}.pt"
                self.yolo_model = YOLO(model_path)
                logger.info(f"✅ YOLO {model_size} carregado de {model_path}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar YOLO: {e}")
        
        # Inicializar OCR
        if OCR_AVAILABLE:
            try:
                # Suporte para português e inglês
                self.ocr_reader = easyocr.Reader(['pt', 'en'], gpu=False)
                logger.info("✅ EasyOCR carregado (PT/EN)")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar OCR: {e}")
        
        logger.info("✅ Vision Enhancer online")
    
    def analyze_screen(
        self,
        image_path: str,
        detect_ui: bool = True,
        extract_text: bool = True
    ) -> Dict[str, Any]:
        """
        Análise completa da tela.
        
        Args:
            image_path: Path da screenshot
            detect_ui: Se True, detecta elementos UI
            extract_text: Se True, extrai texto com OCR
        
        Returns:
            Dict com ui_elements, text_regions, summary
        """
        result = {
            "ui_elements": [],
            "text_regions": [],
            "summary": "",
            "clickable_areas": []
        }
        
        try:
            # Carregar imagem
            if not Path(image_path).exists():
                logger.error(f"❌ Imagem não encontrada: {image_path}")
                return result
            
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"❌ Erro ao carregar imagem: {image_path}")
                return result
            
            # 1. Detecção de UI com YOLO
            if detect_ui and self.yolo_model:
                ui_elements = self._detect_ui_elements(image)
                result["ui_elements"] = ui_elements
                result["clickable_areas"] = self._extract_clickable_areas(ui_elements)
            
            # 2. OCR para texto
            if extract_text and self.ocr_reader:
                text_regions = self._extract_text(image)
                result["text_regions"] = text_regions
            
            # 3. Gerar resumo
            result["summary"] = self._generate_summary(result)
            
            logger.info(f"👁️ Análise completa: {len(result['ui_elements'])} elementos UI, "
                       f"{len(result['text_regions'])} regiões de texto")
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Erro na análise: {e}")
            return result
    
    def _detect_ui_elements(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detecta elementos UI com YOLO"""
        elements = []
        
        try:
            # Executar detecção
            results = self.yolo_model(image, verbose=False)
            
            # Processar resultados
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Extrair informações
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    
                    # Nome da classe
                    class_name = result.names[cls]
                    
                    elements.append({
                        "type": class_name,
                        "bbox": {
                            "x1": int(x1),
                            "y1": int(y1),
                            "x2": int(x2),
                            "y2": int(y2)
                        },
                        "center": {
                            "x": int((x1 + x2) / 2),
                            "y": int((y1 + y2) / 2)
                        },
                        "confidence": conf,
                        "area": int((x2 - x1) * (y2 - y1))
                    })
            
            logger.info(f"🔍 Detectados {len(elements)} elementos UI")
        
        except Exception as e:
            logger.error(f"❌ Erro na detecção UI: {e}")
        
        return elements
    
    def _extract_text(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Extrai texto com OCR"""
        text_regions = []
        
        try:
            # Executar OCR
            results = self.ocr_reader.readtext(image)
            
            for bbox, text, conf in results:
                # Calcular bounding box
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                
                x1, y1 = int(min(x_coords)), int(min(y_coords))
                x2, y2 = int(max(x_coords)), int(max(y_coords))
                
                text_regions.append({
                    "text": text,
                    "bbox": {
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2
                    },
                    "center": {
                        "x": int((x1 + x2) / 2),
                        "y": int((y1 + y2) / 2)
                    },
                    "confidence": conf
                })
            
            logger.info(f"📝 Extraídas {len(text_regions)} regiões de texto")
        
        except Exception as e:
            logger.error(f"❌ Erro no OCR: {e}")
        
        return text_regions
    
    def _extract_clickable_areas(self, ui_elements: List[Dict]) -> List[Dict[str, Any]]:
        """Extrai áreas clicáveis dos elementos UI"""
        clickable = []
        
        # Classes consideradas clicáveis
        clickable_classes = ["button", "link", "icon", "menu", "checkbox", "radio"]
        
        for elem in ui_elements:
            if any(c in elem["type"].lower() for c in clickable_classes):
                clickable.append({
                    "type": elem["type"],
                    "center": elem["center"],
                    "bbox": elem["bbox"]
                })
        
        return clickable
    
    def _generate_summary(self, analysis: Dict[str, Any]) -> str:
        """Gera resumo da análise visual"""
        parts = []
        
        # UI Elements
        if analysis["ui_elements"]:
            ui_count = len(analysis["ui_elements"])
            parts.append(f"{ui_count} elementos UI detectados")
            
            # Contar por tipo
            types = {}
            for elem in analysis["ui_elements"]:
                t = elem["type"]
                types[t] = types.get(t, 0) + 1
            
            top_types = sorted(types.items(), key=lambda x: x[1], reverse=True)[:3]
            types_str = ", ".join([f"{count} {t}" for t, count in top_types])
            parts.append(f"Principais: {types_str}")
        
        # Text
        if analysis["text_regions"]:
            text_count = len(analysis["text_regions"])
            parts.append(f"{text_count} regiões de texto")
            
            # Texto mais longo
            longest = max(analysis["text_regions"], key=lambda x: len(x["text"]))
            if len(longest["text"]) > 50:
                parts.append(f"Texto principal: '{longest['text'][:50]}...'")
        
        # Clickable
        if analysis["clickable_areas"]:
            click_count = len(analysis["clickable_areas"])
            parts.append(f"{click_count} áreas clicáveis")
        
        return " | ".join(parts) if parts else "Nenhum elemento detectado"
    
    def find_element_by_text(
        self,
        image_path: str,
        target_text: str,
        fuzzy: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Encontra elemento por texto.
        
        Args:
            image_path: Path da screenshot
            target_text: Texto a buscar
            fuzzy: Se True, busca parcial
        
        Returns:
            Dict com coordenadas ou None
        """
        analysis = self.analyze_screen(image_path, detect_ui=False, extract_text=True)
        
        target_lower = target_text.lower()
        
        for region in analysis["text_regions"]:
            text_lower = region["text"].lower()
            
            # Match exato ou fuzzy
            if fuzzy:
                if target_lower in text_lower or text_lower in target_lower:
                    return region
            else:
                if text_lower == target_lower:
                    return region
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do Vision Enhancer"""
        return {
            "yolo_available": bool(self.yolo_model),
            "ocr_available": bool(self.ocr_reader),
            "model_size": self.model_size
        }


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================
vision_enhancer = VisionEnhancer(model_size="n")  # Nano para performance
