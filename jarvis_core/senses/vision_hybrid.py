"""
Senses - Vision Hybrid
Sistema de visão com 3 níveis de profundidade
"""

import logging
from typing import Optional, Dict, Tuple
from pathlib import Path
import time

logger = logging.getLogger(__name__)

class VisionLevel:
    """Níveis de análise de visão"""
    FAST = 1      # < 100ms - Frame diff + OCR básico
    MEDIUM = 2    # 500ms-2s - EasyOCR + UI tree
    DEEP = 3      # 2-5s - Gemini Vision

class VisionSystem:
    """Sistema de visão híbrido"""
    
    def __init__(self):
        self.cv2 = None
        self.easyocr_reader = None
        self.gemini_client = None
        
        # Lazy loading
        try:
            import cv2
            self.cv2 = cv2
            logger.info("✅ OpenCV disponível")
        except ImportError:
            logger.warning("⚠️ OpenCV não instalado")
        
        logger.info("✅ Vision System inicializado")
    
    def analyze(self, image_path: str, level: str = "auto") -> Dict:
        """Analisa imagem com nível apropriado"""
        start_time = time.time()
        
        # Auto-selecionar nível
        if level == "auto":
            level = self._auto_select_level(image_path)
        
        result = {}
        
        if level == "fast" or level == VisionLevel.FAST:
            result = self._analyze_level_1(image_path)
        elif level == "medium" or level == VisionLevel.MEDIUM:
            result = self._analyze_level_2(image_path)
        elif level == "deep" or level == VisionLevel.DEEP:
            result = self._analyze_level_3(image_path)
        
        latency = time.time() - start_time
        result["latency_ms"] = int(latency * 1000)
        result["level"] = level
        
        logger.info(f"✅ Análise completa: {level} ({result['latency_ms']}ms)")
        
        return result
    
    def _auto_select_level(self, image_path: str) -> str:
        """Seleciona nível baseado em heurísticas"""
        # Por enquanto, sempre usar nível médio
        return "medium"
    
    def _analyze_level_1(self, image_path: str) -> Dict:
        """Nível 1: Rápido (Frame diff + OCR básico)"""
        if not self.cv2:
            return {"error": "OpenCV não disponível"}
        
        try:
            # Carregar imagem
            img = self.cv2.imread(image_path)
            
            if img is None:
                return {"error": "Imagem não encontrada"}
            
            # Informações básicas
            height, width = img.shape[:2]
            
            # OCR básico com Tesseract (se disponível)
            text = ""
            try:
                import pytesseract
                text = pytesseract.image_to_string(img)
            except:
                pass
            
            return {
                "width": width,
                "height": height,
                "text": text,
                "method": "opencv_tesseract"
            }
        except Exception as e:
            logger.error(f"❌ Erro nível 1: {e}")
            return {"error": str(e)}
    
    def _analyze_level_2(self, image_path: str) -> Dict:
        """Nível 2: Médio (EasyOCR + análise estrutural)"""
        try:
            # Lazy load EasyOCR
            if not self.easyocr_reader:
                import easyocr
                self.easyocr_reader = easyocr.Reader(['pt', 'en'])
                logger.info("📥 EasyOCR carregado")
            
            # OCR
            results = self.easyocr_reader.readtext(image_path)
            
            # Extrair texto
            text_blocks = []
            for (bbox, text, confidence) in results:
                text_blocks.append({
                    "text": text,
                    "confidence": float(confidence),
                    "bbox": bbox
                })
            
            full_text = " ".join([block["text"] for block in text_blocks])
            
            return {
                "text": full_text,
                "text_blocks": text_blocks,
                "num_blocks": len(text_blocks),
                "method": "easyocr"
            }
        except ImportError:
            logger.warning("⚠️ EasyOCR não instalado. Fallback para nível 1.")
            return self._analyze_level_1(image_path)
        except Exception as e:
            logger.error(f"❌ Erro nível 2: {e}")
            return {"error": str(e)}
    
    def _analyze_level_3(self, image_path: str) -> Dict:
        """Nível 3: Profundo (Gemini Vision)"""
        try:
            import google.generativeai as genai
            from PIL import Image
            
            # Configurar Gemini (precisa de API key)
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                logger.warning("⚠️ GEMINI_API_KEY não configurada")
                return self._analyze_level_2(image_path)
            
            genai.configure(api_key=api_key)
            
            # Carregar imagem
            img = Image.open(image_path)
            
            # Analisar
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content([
                "Descreva esta imagem em detalhes. Identifique textos, objetos, pessoas e ações.",
                img
            ])
            
            return {
                "description": response.text,
                "method": "gemini_vision"
            }
        except ImportError:
            logger.warning("⚠️ Gemini não disponível. Fallback para nível 2.")
            return self._analyze_level_2(image_path)
        except Exception as e:
            logger.error(f"❌ Erro nível 3: {e}")
            return {"error": str(e)}


import os

# Instância global
vision_system = VisionSystem()
