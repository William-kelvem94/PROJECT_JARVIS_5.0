"""
Advanced Vision Pipeline - Visão Computacional Multi-Nível
Implementa pipeline de 3 níveis para análise visual progressiva
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image

try:
    import cv2
    CV2_AVAILABLE = True
except (ImportError, OSError) as e:
    CV2_AVAILABLE = False
    cv2 = None
    logging.warning(f"⚠️ cv2 not available in advanced_vision_pipeline: {e}")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except (ImportError, OSError) as e:
    NUMPY_AVAILABLE = False
    np = None
    logging.warning(f"⚠️ numpy not available in advanced_vision_pipeline: {e}")

logger = logging.getLogger(__name__)

class AdvancedVisionPipeline:
    """Pipeline de visão computacional com 3 níveis de processamento"""
    
    def __init__(self):
        self.level1_available = True  # YOLO + UI Detector (sempre disponível)
        self.level2_available = False  # EasyOCR + SAM
        self.level3_available = False  # LLaVA/Gemini
        
        self._init_level2()
        self._init_level3()
    
    def _init_level2(self):
        """Inicializa processadores de nível 2"""
        try:
            import easyocr
            self.easyocr_reader = easyocr.Reader(['pt', 'en'], gpu=False)
            self.level2_available = True
            logger.info("✅ EasyOCR inicializado (Nível 2)")
        except ImportError:
            logger.warning("⚠️ EasyOCR não disponível. Instale: pip install easyocr")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao inicializar EasyOCR: {e}")
    
    def _init_level3(self):
        """Inicializa processadores de nível 3"""
        try:
            # Verificar se Gemini está disponível
            import os
            if os.environ.get('GOOGLE_API_KEY'):
                self.level3_available = True
                logger.info("✅ Gemini Vision disponível (Nível 3)")
        except Exception as e:
            logger.warning(f"⚠️ Nível 3 não disponível: {e}")
    
    def analyze(self, image_path: str, complexity: str = "auto") -> Dict[str, Any]:
        """
        Analisa imagem usando pipeline progressivo
        
        Args:
            image_path: Caminho da imagem
            complexity: "fast", "balanced", "deep", ou "auto"
        
        Returns:
            Dicionário com resultados da análise
        """
        if not Path(image_path).exists():
            return {"error": "Imagem não encontrada"}
        
        # Determinar nível de processamento
        if complexity == "auto":
            complexity = self._auto_detect_complexity(image_path)
        
        level_map = {
            "fast": 1,
            "balanced": 2,
            "deep": 3
        }
        target_level = level_map.get(complexity, 1)
        
        results = {
            "image_path": image_path,
            "complexity": complexity,
            "level_used": 1
        }
        
        # Nível 1: Detecção rápida
        if target_level >= 1:
            results.update(self._level1_analysis(image_path))
            results["level_used"] = 1
        
        # Nível 2: Análise intermediária
        if target_level >= 2 and self.level2_available:
            results.update(self._level2_analysis(image_path))
            results["level_used"] = 2
        
        # Nível 3: Compreensão profunda
        if target_level >= 3 and self.level3_available:
            results.update(self._level3_analysis(image_path))
            results["level_used"] = 3
        
        return results
    
    def _auto_detect_complexity(self, image_path: str) -> str:
        """Detecta automaticamente a complexidade necessária"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return "fast"
            
            # Calcular métricas de complexidade
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Quantidade de texto (usando gradientes)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Complexidade visual (variância)
            variance = np.var(gray)
            
            # Decisão baseada em heurísticas
            if edge_density > 0.1 or variance > 5000:
                return "deep"  # Imagem complexa
            elif edge_density > 0.05 or variance > 2000:
                return "balanced"  # Complexidade média
            else:
                return "fast"  # Imagem simples
                
        except Exception as e:
            logger.error(f"Erro ao detectar complexidade: {e}")
            return "fast"
    
    def _level1_analysis(self, image_path: str) -> Dict[str, Any]:
        """Nível 1: Detecção rápida com YOLO + UI Detector"""
        results = {}
        
        try:
            # Usar UI Detector existente
            from src.core.ui_detector import ui_detector
            ui_elements = ui_detector.detect_ui_elements(image_path)
            results["ui_elements"] = ui_elements
            
            # OCR básico com Tesseract
            from src.core.ocr_processor import ocr_processor
            ocr_result = ocr_processor.extract_text(image_path)
            results["text_basic"] = ocr_result.get("text", "")
            
            logger.info(f"✅ Nível 1: {len(ui_elements)} elementos UI, {len(results['text_basic'])} chars")
            
        except Exception as e:
            logger.error(f"Erro no Nível 1: {e}")
            results["error_level1"] = str(e)
        
        return results
    
    def _level2_analysis(self, image_path: str) -> Dict[str, Any]:
        """Nível 2: Análise intermediária com EasyOCR"""
        results = {}
        
        try:
            # EasyOCR (melhor que Tesseract para textos complexos)
            ocr_results = self.easyocr_reader.readtext(image_path)
            
            text_advanced = []
            bboxes = []
            confidences = []
            
            for bbox, text, conf in ocr_results:
                text_advanced.append(text)
                bboxes.append(bbox)
                confidences.append(conf)
            
            results["text_advanced"] = " ".join(text_advanced)
            results["text_bboxes"] = bboxes
            results["text_confidences"] = confidences
            results["text_count"] = len(text_advanced)
            
            logger.info(f"✅ Nível 2: {len(text_advanced)} blocos de texto detectados")
            
        except Exception as e:
            logger.error(f"Erro no Nível 2: {e}")
            results["error_level2"] = str(e)
        
        return results
    
    def _level3_analysis(self, image_path: str) -> Dict[str, Any]:
        """Nível 3: Compreensão profunda com Gemini Vision"""
        results = {}
        
        try:
            from src.core.ai_agent import ai_agent
            
            # Usar Gemini Vision para análise profunda
            prompt = (
                "Analise esta imagem em detalhes. Descreva:\n"
                "1. O que você vê (objetos, pessoas, texto)\n"
                "2. O contexto (tipo de aplicação, documento, etc)\n"
                "3. Ações possíveis que o usuário pode querer fazer\n"
                "4. Qualquer informação importante ou erro visível"
            )
            
            description = ai_agent._call_gemini(prompt, image_path)
            results["deep_description"] = description
            
            logger.info(f"✅ Nível 3: Análise profunda concluída")
            
        except Exception as e:
            logger.error(f"Erro no Nível 3: {e}")
            results["error_level3"] = str(e)
        
        return results
    
    def extract_table(self, image_path: str) -> Optional[List[List[str]]]:
        """Extrai tabelas de uma imagem"""
        try:
            # Usar OpenCV para detectar estrutura de tabela
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detectar linhas horizontais e verticais
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            
            horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
            vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)
            
            # Combinar linhas
            table_structure = cv2.add(horizontal_lines, vertical_lines)
            
            # Encontrar contornos (células)
            contours, _ = cv2.findContours(table_structure, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # Ordenar células e extrair texto
            cells = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 20 and h > 20:  # Filtrar células muito pequenas
                    cells.append((x, y, w, h))
            
            # Ordenar células (esquerda para direita, cima para baixo)
            cells = sorted(cells, key=lambda c: (c[1], c[0]))
            
            # Extrair texto de cada célula com EasyOCR
            if self.level2_available:
                table_data = []
                current_row = []
                last_y = 0
                
                for x, y, w, h in cells:
                    # Nova linha se Y mudou significativamente
                    if abs(y - last_y) > 10 and current_row:
                        table_data.append(current_row)
                        current_row = []
                    
                    # Extrair região da célula
                    cell_img = img[y:y+h, x:x+w]
                    
                    # OCR na célula
                    cell_results = self.easyocr_reader.readtext(cell_img)
                    cell_text = " ".join([text for _, text, _ in cell_results])
                    
                    current_row.append(cell_text)
                    last_y = y
                
                if current_row:
                    table_data.append(current_row)
                
                logger.info(f"✅ Tabela extraída: {len(table_data)} linhas")
                return table_data
            
        except Exception as e:
            logger.error(f"Erro ao extrair tabela: {e}")
        
        return None
    
    def analyze_document(self, image_path: str) -> Dict[str, Any]:
        """Análise especializada para documentos"""
        results = {
            "document_type": "unknown",
            "text": "",
            "tables": [],
            "metadata": {}
        }
        
        try:
            # Análise completa
            analysis = self.analyze(image_path, complexity="balanced")
            results["text"] = analysis.get("text_advanced", analysis.get("text_basic", ""))
            
            # Detectar tipo de documento
            text_lower = results["text"].lower()
            if any(word in text_lower for word in ["invoice", "fatura", "nota fiscal"]):
                results["document_type"] = "invoice"
            elif any(word in text_lower for word in ["contract", "contrato"]):
                results["document_type"] = "contract"
            elif any(word in text_lower for word in ["receipt", "recibo"]):
                results["document_type"] = "receipt"
            
            # Tentar extrair tabelas
            tables = self.extract_table(image_path)
            if tables:
                results["tables"] = tables
            
            logger.info(f"✅ Documento analisado: {results['document_type']}")
            
        except Exception as e:
            logger.error(f"Erro ao analisar documento: {e}")
            results["error"] = str(e)
        
        return results


# Instância global
advanced_vision_pipeline = AdvancedVisionPipeline()
