"""
Processador OCR para extraÃ§Ã£o de texto de imagens
Suporta mÃºltiplos engines: Tesseract, EasyOCR e integraÃ§Ã£o com APIs
"""

import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image
try:
    import pytesseract
except ImportError:
    pytesseract = None

# Lazy import heavy OCR libraries to avoid startup issues
EASYOCR_AVAILABLE = False
easyocr = None

def _ensure_easyocr():
    global EASYOCR_AVAILABLE, easyocr
    if not EASYOCR_AVAILABLE and easyocr is None:
        try:
            import easyocr
            EASYOCR_AVAILABLE = True
        except (ImportError, OSError) as e:
            EASYOCR_AVAILABLE = False
            easyocr = None
            logger.debug(f"EasyOCR nÃ£o encontrado. OCR limitado: {e}")

try:
    # Just check if easyocr can be imported without actually importing it
    import importlib
    easyocr_spec = importlib.util.find_spec("easyocr")
    if easyocr_spec is not None:
        EASYOCR_AVAILABLE = True
    else:
        EASYOCR_AVAILABLE = False
except:
    EASYOCR_AVAILABLE = False
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.utils.config import config
from src.utils.helpers import ImageHelper, TextHelper
from src.database.models import db_manager, OCRResult, Capture

logger = logging.getLogger(__name__)

class OCRProcessor:
    """Classe principal para processamento OCR"""

    def __init__(self):
        self.tesseract_available = False
        self.easyocr_available = False
        self.easyocr_reader = None

        # ConfiguraÃ§Ãµes
        self.ocr_engine = config.get_setting('ocr.engine', 'tesseract')
        self.languages = config.get_setting('ocr.languages', ['por', 'eng'])
        self.confidence_threshold = config.get_setting('ocr.confidence_threshold', 60)
        self.preprocessing = config.get_setting('ocr.preprocessing', True)
        self.timeout = config.get_setting('processing.timeout', 30)

        # Inicializar engines
        self._initialize_engines()

        logger.info("Processador OCR inicializado")

    def _initialize_engines(self):
        """Inicializa engines OCR disponÃ­veis"""
        try:
            # Inicializar Tesseract
            tesseract_config = config.get_ocr_config('tesseract')
            tesseract_path = tesseract_config.get('path')

            if tesseract_path and Path(tesseract_path).exists():
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                self.tesseract_available = True
                logger.info("Tesseract OCR inicializado")
            else:
                # Tentar caminho padrÃ£o
                try:
                    pytesseract.get_tesseract_version()
                    self.tesseract_available = True
                    logger.info("Tesseract OCR encontrado no PATH")
                except Exception:
                    logger.warning("Tesseract nÃ£o encontrado")

            # Marcar EasyOCR como disponÃ­vel mas nÃ£o inicializar ainda (lazy)
            if EASYOCR_AVAILABLE:
                self.easyocr_available = True
                logger.info("EasyOCR disponÃ­vel (lazy loading)")
            else:
                logger.warning("EasyOCR nÃ£o encontrado")

        except Exception as e:
            logger.error(f"Erro na inicializaÃ§Ã£o dos engines OCR: {e}")

    def _ensure_easyocr_reader(self):
        """Initialize EasyOCR reader only when needed (lazy)"""
        if self.easyocr_reader is None and self.easyocr_available:
            try:
                _ensure_easyocr()
                if EASYOCR_AVAILABLE and easyocr:
                    easyocr_config = config.get_ocr_config('easyocr')
                    self.easyocr_reader = easyocr.Reader(
                        lang_list=self.languages,
                        gpu=easyocr_config.get('gpu', False),
                        model_storage_directory=easyocr_config.get('model_storage_directory'),
                        user_network_directory=easyocr_config.get('user_network_directory'),
                        detect_network=easyocr_config.get('detect_network', 'craft'),
                        recog_network=easyocr_config.get('recog_network', 'crnn'),
                        download_enabled=easyocr_config.get('download_enabled', True)
                    )
                    logger.info("EasyOCR reader initialized on demand")
                else:
                    self.easyocr_available = False
            except Exception as e:
                logger.error(f"Erro ao inicializar EasyOCR reader: {e}")
                self.easyocr_available = False

    def process_image(self, image_path: str, capture_id: Optional[int] = None,
                     engine: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Processa imagem com OCR

        Args:
            image_path: Caminho da imagem
            capture_id: ID da captura no banco (opcional)
            engine: Engine OCR a usar (opcional)

        Returns:
            DicionÃ¡rio com resultados ou None se erro
        """
        try:
            start_time = time.time()

            # Carregar imagem
            image = Image.open(image_path)

            # PrÃ©-processar se necessÃ¡rio
            if self.preprocessing:
                image = ImageHelper.preprocess_image(image)

            # Selecionar engine
            selected_engine = engine or self.ocr_engine

            # Processar com engine selecionada
            if selected_engine == 'tesseract' and self.tesseract_available:
                result = self._process_with_tesseract(image)
            elif selected_engine == 'easyocr' and self.easyocr_available:
                result = self._process_with_easyocr(image)
            elif selected_engine == 'hybrid' and self.tesseract_available and self.easyocr_available:
                result = self._process_hybrid(image)
            else:
                logger.error(f"Engine OCR '{selected_engine}' nÃ£o disponÃ­vel")
                return None

            processing_time = time.time() - start_time

            # Adicionar metadados
            result.update({
                'processing_time': processing_time,
                'engine_used': selected_engine,
                'image_path': image_path,
                'image_size': f"{image.width}x{image.height}",
                'timestamp': time.time()
            })

            # Salvar no banco se capture_id fornecido
            if capture_id:
                self._save_ocr_result(capture_id, result)

            logger.info(f"OCR processado com sucesso: {image_path} ({processing_time:.2f}s)")
            return result

        except Exception as e:
            logger.error(f"Erro no processamento OCR de {image_path}: {e}")
            return None

    def _process_with_tesseract(self, image: Image.Image) -> Dict[str, Any]:
        """Processa imagem usando Tesseract"""
        try:
            # ConfiguraÃ§Ã£o Tesseract
            tesseract_config = config.get_ocr_config('tesseract')
            custom_config = tesseract_config.get('config', '--oem 3 --psm 6')

            # Executar OCR
            ocr_data = pytesseract.image_to_data(
                image,
                lang='+'.join(self.languages),
                config=custom_config,
                output_type=pytesseract.Output.DICT,
                timeout=self.timeout
            )

            # Extrair texto completo
            raw_text = pytesseract.image_to_string(
                image,
                lang='+'.join(self.languages),
                config=custom_config,
                timeout=self.timeout
            )

            # Calcular confianÃ§a mÃ©dia
            confidences = [int(conf) for conf in ocr_data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            # Extrair regiÃµes de texto
            text_regions = []
            for i, conf in enumerate(ocr_data['conf']):
                if conf != '-1' and int(conf) >= self.confidence_threshold:
                    text_regions.append({
                        'text': ocr_data['text'][i],
                        'x': ocr_data['left'][i],
                        'y': ocr_data['top'][i],
                        'width': ocr_data['width'][i],
                        'height': ocr_data['height'][i],
                        'confidence': int(conf)
                    })

            # Limpar texto
            cleaned_text = TextHelper.clean_ocr_text(raw_text)

            return {
                'raw_text': raw_text,
                'cleaned_text': cleaned_text,
                'confidence_score': avg_confidence,
                'text_regions': text_regions,
                'language': '+'.join(self.languages),
                'engine': 'tesseract'
            }

        except Exception as e:
            logger.error(f"Erro no processamento com Tesseract: {e}")
            return {
                'raw_text': '',
                'cleaned_text': '',
                'confidence_score': 0,
                'text_regions': [],
                'language': '+'.join(self.languages),
                'engine': 'tesseract',
                'error': str(e)
            }

    def _process_with_easyocr(self, image: Image.Image) -> Dict[str, Any]:
        """Processa imagem usando EasyOCR"""
        try:
            # Ensure EasyOCR reader is initialized
            self._ensure_easyocr_reader()
            
            if self.easyocr_reader is None:
                return {
                    'text': '',
                    'confidence': 0,
                    'language': '+'.join(self.languages),
                    'engine': 'easyocr',
                    'error': 'EasyOCR reader not available'
                }
            
            # Converter para array numpy
            cv_image = ImageHelper.image_to_cv2(image)

            # Executar OCR
            results = self.easyocr_reader.readtext(cv_image)

            # Processar resultados
            raw_text = ' '.join([result[1] for result in results])
            text_regions = []

            total_confidence = 0
            for result in results:
                bbox, text, confidence = result
                confidence_percent = confidence * 100

                if confidence_percent >= self.confidence_threshold:
                    text_regions.append({
                        'text': text,
                        'x': int(bbox[0][0]),
                        'y': int(bbox[0][1]),
                        'width': int(bbox[2][0] - bbox[0][0]),
                        'height': int(bbox[2][1] - bbox[0][1]),
                        'confidence': confidence_percent
                    })

                    total_confidence += confidence_percent

            avg_confidence = total_confidence / len(results) if results else 0

            # Limpar texto
            cleaned_text = TextHelper.clean_ocr_text(raw_text)

            return {
                'raw_text': raw_text,
                'cleaned_text': cleaned_text,
                'confidence_score': avg_confidence,
                'text_regions': text_regions,
                'language': '+'.join(self.languages),
                'engine': 'easyocr'
            }

        except Exception as e:
            logger.error(f"Erro no processamento com EasyOCR: {e}")
            return {
                'raw_text': '',
                'cleaned_text': '',
                'confidence_score': 0,
                'text_regions': [],
                'language': '+'.join(self.languages),
                'engine': 'easyocr',
                'error': str(e)
            }

    def _process_hybrid(self, image: Image.Image) -> Dict[str, Any]:
        """Processa imagem usando abordagem hÃ­brida"""
        try:
            # Processar com ambos os engines
            tesseract_result = self._process_with_tesseract(image)
            easyocr_result = self._process_with_easyocr(image)

            # Combinar resultados
            # Usar o texto com maior confianÃ§a mÃ©dia
            if tesseract_result['confidence_score'] >= easyocr_result['confidence_score']:
                primary_result = tesseract_result
                secondary_result = easyocr_result
            else:
                primary_result = easyocr_result
                secondary_result = tesseract_result

            # Melhorar texto combinando regiÃµes
            combined_regions = primary_result['text_regions'] + secondary_result['text_regions']
            combined_regions.sort(key=lambda x: (x['y'], x['x']))  # Ordenar por posiÃ§Ã£o

            # Remover duplicatas prÃ³ximas
            filtered_regions = []
            for region in combined_regions:
                # Verificar se regiÃ£o similar jÃ¡ existe
                duplicate = False
                for existing in filtered_regions:
                    if (abs(region['x'] - existing['x']) < 20 and
                        abs(region['y'] - existing['y']) < 20 and
                        abs(region['confidence'] - existing['confidence']) < 10):
                        duplicate = True
                        break

                if not duplicate:
                    filtered_regions.append(region)

            return {
                'raw_text': primary_result['raw_text'],
                'cleaned_text': primary_result['cleaned_text'],
                'confidence_score': primary_result['confidence_score'],
                'text_regions': filtered_regions,
                'language': primary_result['language'],
                'engine': 'hybrid',
                'engines_used': ['tesseract', 'easyocr'],
                'tesseract_confidence': tesseract_result['confidence_score'],
                'easyocr_confidence': easyocr_result['confidence_score']
            }

        except Exception as e:
            logger.error(f"Erro no processamento hÃ­brido: {e}")
            return {
                'raw_text': '',
                'cleaned_text': '',
                'confidence_score': 0,
                'text_regions': [],
                'language': '+'.join(self.languages),
                'engine': 'hybrid',
                'error': str(e)
            }

    def _save_ocr_result(self, capture_id: int, ocr_result: Dict[str, Any]):
        """Salva resultado OCR no banco de dados"""
        try:
            ocr_record = OCRResult(
                capture_id=capture_id,
                ocr_engine=ocr_result['engine'],
                language=ocr_result['language'],
                raw_text=ocr_result['raw_text'],
                cleaned_text=ocr_result.get('cleaned_text', ''),
                confidence_score=ocr_result.get('confidence_score', 0),
                processing_time=ocr_result.get('processing_time', 0),
                text_regions=ocr_result.get('text_regions', [])
            )

            db_manager.execute_in_session(lambda session: session.add(ocr_record))

        except Exception as e:
            logger.error(f"Erro ao salvar resultado OCR: {e}")

    def process_batch(self, image_paths: List[str], max_workers: int = 4) -> Dict[str, Any]:
        """
        Processa lote de imagens em paralelo

        Args:
            image_paths: Lista de caminhos de imagens
            max_workers: NÃºmero mÃ¡ximo de threads

        Returns:
            DicionÃ¡rio com resultados por imagem
        """
        results = {}
        start_time = time.time()

        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submeter tarefas
                future_to_path = {
                    executor.submit(self.process_image, path): path
                    for path in image_paths
                }

                # Coletar resultados
                for future in as_completed(future_to_path):
                    path = future_to_path[future]
                    try:
                        result = future.result()
                        results[path] = result
                    except Exception as e:
                        logger.error(f"Erro no processamento de {path}: {e}")
                        results[path] = None

        except Exception as e:
            logger.error(f"Erro no processamento em lote: {e}")

        total_time = time.time() - start_time
        logger.info(f"Lote processado: {len(results)} imagens em {total_time:.2f}s")

        return results

    def get_available_engines(self) -> List[str]:
        """Retorna lista de engines OCR disponÃ­veis"""
        engines = []
        if self.tesseract_available:
            engines.append('tesseract')
        if self.easyocr_available:
            engines.append('easyocr')
        if self.tesseract_available and self.easyocr_available:
            engines.append('hybrid')
        return engines

    def test_engines(self) -> Dict[str, bool]:
        """Testa disponibilidade dos engines OCR"""
        results = {}

        # Testar Tesseract
        if self.tesseract_available:
            try:
                # Criar imagem de teste simples
                test_image = Image.new('RGB', (100, 50), color='white')
                result = self._process_with_tesseract(test_image)
                results['tesseract'] = 'error' not in result
            except Exception:
                results['tesseract'] = False
        else:
            results['tesseract'] = False

        # Testar EasyOCR
        if self.easyocr_available:
            try:
                self._ensure_easyocr_reader()
                if self.easyocr_reader is None:
                    results['easyocr'] = False
                else:
                    test_image = Image.new('RGB', (100, 50), color='white')
                    cv_image = ImageHelper.image_to_cv2(test_image)
                    test_results = self.easyocr_reader.readtext(cv_image)
                    results['easyocr'] = True
            except Exception:
                results['easyocr'] = False
        else:
            results['easyocr'] = False

        # Testar hÃ­brido
        results['hybrid'] = results.get('tesseract', False) and results.get('easyocr', False)

        return results

    def get_engine_info(self) -> Dict[str, Any]:
        """Retorna informaÃ§Ãµes sobre os engines disponÃ­veis"""
        return {
            'available_engines': self.get_available_engines(),
            'default_engine': self.ocr_engine,
            'languages': self.languages,
            'confidence_threshold': self.confidence_threshold,
            'preprocessing_enabled': self.preprocessing,
            'timeout_seconds': self.timeout,
            'engine_status': self.test_engines()
        }

# InstÃ¢ncia global removida para evitar execuÃ§Ã£o durante import
# ocr_processor = OCRProcessor()
