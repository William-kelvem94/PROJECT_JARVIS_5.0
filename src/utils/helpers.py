"""
FunÃ§Ãµes auxiliares e utilitÃ¡rios para o Jarvis 5.0
ContÃ©m funÃ§Ãµes comuns usadas em todo o sistema
"""

import os
import re
import hashlib
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from PIL import Image

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except (ImportError, OSError) as e:
    NUMPY_AVAILABLE = False
    # Fallback for type hints
    class MockNumpy:
        ndarray = type('ndarray', (), {})
    np = MockNumpy()
    logging.warning(f"âš ï¸ numpy not available in helpers: {e}")

try:
    import cv2
    CV2_AVAILABLE = True
except (ImportError, OSError) as e:
    CV2_AVAILABLE = False
    cv2 = None
    logging.warning(f"âš ï¸ cv2 not available in helpers: {e}")

from src.utils.config import config

logger = logging.getLogger(__name__)

class FileHelper:
    """UtilitÃ¡rios para manipulaÃ§Ã£o de arquivos"""

    @staticmethod
    def get_file_hash(file_path: Union[str, Path]) -> str:
        """Calcula hash SHA256 de um arquivo"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Erro ao calcular hash do arquivo {file_path}: {e}")
            return ""

    @staticmethod
    def get_file_size_mb(file_path: Union[str, Path]) -> float:
        """Retorna tamanho do arquivo em MB"""
        try:
            return os.path.getsize(file_path) / (1024 * 1024)
        except Exception:
            return 0.0

    @staticmethod
    def ensure_directory(path: Union[str, Path]):
        """Garante que um diretÃ³rio existe"""
        Path(path).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_unique_filename(directory: Union[str, Path], filename: str, extension: str = "") -> str:
        """Gera nome de arquivo Ãºnico"""
        base_name = Path(filename).stem
        if extension and not extension.startswith('.'):
            extension = f".{extension}"

        counter = 1
        unique_name = f"{base_name}{extension}"

        while (Path(directory) / unique_name).exists():
            unique_name = f"{base_name}_{counter}{extension}"
            counter += 1

        return unique_name

    @staticmethod
    def cleanup_old_files(directory: Union[str, Path], max_age_days: int = 30):
        """Remove arquivos antigos de um diretÃ³rio"""
        try:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=max_age_days)
            directory = Path(directory)

            for file_path in directory.glob("*"):
                if file_path.is_file():
                    file_age = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_age < cutoff_date:
                        file_path.unlink()
                        logger.info(f"Arquivo antigo removido: {file_path}")
        except Exception as e:
            logger.error(f"Erro ao limpar arquivos antigos: {e}")

class ImageHelper:
    """UtilitÃ¡rios para processamento de imagens"""

    @staticmethod
    def preprocess_image(image: Image.Image) -> Image.Image:
        """PrÃ©-processa imagem para melhorar OCR"""
        try:
            # Converter para escala de cinza
            if image.mode != 'L':
                image = image.convert('L')

            # Aumentar contraste
            image = ImageHelper._enhance_contrast(image)

            # Redimensionar se necessÃ¡rio
            image = ImageHelper._resize_for_ocr(image)

            return image
        except Exception as e:
            logger.error(f"Erro no prÃ©-processamento da imagem: {e}")
            return image

    @staticmethod
    def _enhance_contrast(image: Image.Image) -> Image.Image:
        """Melhora o contraste da imagem"""
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(2.0)

    @staticmethod
    def _resize_for_ocr(image: Image.Image, max_width: int = 2000) -> Image.Image:
        """Redimensiona imagem mantendo proporÃ§Ã£o para OCR"""
        width, height = image.size
        if width > max_width:
            ratio = max_width / width
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return image

    @staticmethod
    def image_to_cv2(image: Image.Image) -> np.ndarray:
        """Converte PIL Image para OpenCV array"""
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    @staticmethod
    def cv2_to_image(cv2_image: np.ndarray) -> Image.Image:
        """Converte OpenCV array para PIL Image"""
        return Image.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))

    @staticmethod
    def detect_text_regions(image: Image.Image) -> List[Tuple[int, int, int, int]]:
        """Detecta regiÃµes de texto na imagem"""
        try:
            cv_image = ImageHelper.image_to_cv2(image)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

            # Aplicar threshold
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Encontrar contornos
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                # Filtrar regiÃµes muito pequenas (provavelmente ruÃ­do)
                if w > 20 and h > 10:
                    text_regions.append((x, y, x + w, y + h))

            return text_regions
        except Exception as e:
            logger.error(f"Erro na detecÃ§Ã£o de regiÃµes de texto: {e}")
            return []

class TextHelper:
    """UtilitÃ¡rios para processamento de texto"""

    @staticmethod
    def clean_ocr_text(text: str) -> str:
        """Limpa texto extraÃ­do do OCR"""
        if not text:
            return ""

        # Remover mÃºltiplos espaÃ§os
        text = re.sub(r'\s+', ' ', text)

        # Remover caracteres especiais indesejados
        text = re.sub(r'[^\w\s.,;:!?()[\]{}@#$%&*+-=<>|/\\\'"Ã¢Ã Ã¡ÃªÃ¨Ã©Ã®Ã¬Ã­Ã´Ã²Ã³Ã»Ã¹ÃºÃ§Ã±Ã‚Ã€ÃÃŠÃˆÃ‰ÃŽÃŒÃÃ”Ã’Ã“Ã›Ã™ÃšÃ‡Ã‘]', '', text)

        # Corrigir quebras de linha inconsistentes
        text = re.sub(r'\n\s*\n', '\n\n', text)

        return text.strip()

    @staticmethod
    def extract_patterns(text: str, patterns: Dict[str, str]) -> Dict[str, List[str]]:
        """Extrai padrÃµes regex do texto"""
        results = {}

        for pattern_name, pattern in patterns.items():
            try:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    results[pattern_name] = list(set(matches))  # Remover duplicatas
            except re.error as e:
                logger.error(f"Erro no padrÃ£o regex {pattern_name}: {e}")

        return results

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normaliza texto para processamento"""
        if not text:
            return ""

        # Converter para minÃºsculas
        text = text.lower()

        # Remover acentos
        text = TextHelper._remove_accents(text)

        # Remover pontuaÃ§Ã£o desnecessÃ¡ria
        text = re.sub(r'[^\w\s]', ' ', text)

        return text.strip()

    @staticmethod
    def _remove_accents(text: str) -> str:
        """Remove acentos do texto"""
        accents = {
            'Ã¡': 'a', 'Ã ': 'a', 'Ã¢': 'a', 'Ã£': 'a', 'Ã¤': 'a',
            'Ã©': 'e', 'Ã¨': 'e', 'Ãª': 'e', 'Ã«': 'e',
            'Ã­': 'i', 'Ã¬': 'i', 'Ã®': 'i', 'Ã¯': 'i',
            'Ã³': 'o', 'Ã²': 'o', 'Ã´': 'o', 'Ãµ': 'o', 'Ã¶': 'o',
            'Ãº': 'u', 'Ã¹': 'u', 'Ã»': 'u', 'Ã¼': 'u',
            'Ã§': 'c', 'Ã±': 'n'
        }

        for accented, normal in accents.items():
            text = text.replace(accented, normal)
            text = text.replace(accented.upper(), normal.upper())

        return text

    @staticmethod
    def calculate_text_similarity(text1: str, text2: str) -> float:
        """Calcula similaridade entre dois textos usando Jaccard"""
        if not text1 or not text2:
            return 0.0

        # Tokenizar
        tokens1 = set(TextHelper.normalize_text(text1).split())
        tokens2 = set(TextHelper.normalize_text(text2).split())

        # Calcular similaridade Jaccard
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))

        return intersection / union if union > 0 else 0.0

class DataHelper:
    """UtilitÃ¡rios para manipulaÃ§Ã£o de dados"""

    @staticmethod
    def validate_cpf(cpf: str) -> bool:
        """Valida CPF brasileiro"""
        cpf = re.sub(r'[^\d]', '', cpf)

        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False

        def calculate_digit(cpf_slice: str, multiplier: int) -> int:
            total = sum(int(digit) * weight for digit, weight in zip(cpf_slice, range(multiplier, 1, -1)))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder

        first_digit = calculate_digit(cpf[:9], 10)
        second_digit = calculate_digit(cpf[:10], 11)

        return cpf[-2:] == f"{first_digit}{second_digit}"

    @staticmethod
    def validate_cnpj(cnpj: str) -> bool:
        """Valida CNPJ brasileiro"""
        cnpj = re.sub(r'[^\d]', '', cnpj)

        if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
            return False

        def calculate_digit(cnpj_slice: str, weights: List[int]) -> int:
            total = sum(int(digit) * weight for digit, weight in zip(cnpj_slice, weights))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder

        weights_first = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        weights_second = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

        first_digit = calculate_digit(cnpj[:12], weights_first)
        second_digit = calculate_digit(cnpj[:13], weights_second)

        return cnpj[-2:] == f"{first_digit}{second_digit}"

    @staticmethod
    def format_money(value: Union[str, float, int]) -> str:
        """Formata valor monetÃ¡rio brasileiro"""
        try:
            if isinstance(value, str):
                # Remover sÃ­mbolos e converter
                value = float(re.sub(r'[^\d.,]', '', value).replace(',', '.'))

            return f"R$ {value:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
        except (ValueError, TypeError):
            return str(value)

    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime.datetime]:
        """Parseia data em vÃ¡rios formatos"""
        date_formats = [
            '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%Y/%m/%d',
            '%d/%m/%y', '%d-%m-%y', '%m/%d/%Y', '%m-%d-%Y'
        ]

        for fmt in date_formats:
            try:
                return datetime.datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue

        return None

class SystemHelper:
    """UtilitÃ¡rios do sistema"""

    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """ObtÃ©m informaÃ§Ãµes do sistema"""
        import platform
        import psutil

        try:
            return {
                "os": platform.system(),
                "os_version": platform.version(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "disk_total": psutil.disk_usage('/').total / (1024**3),  # GB
                "disk_free": psutil.disk_usage('/').free / (1024**3),  # GB
                "gpu": SystemHelper.get_gpu_info()
            }
        except Exception as e:
            logger.error(f"Erro ao obter informaÃ§Ãµes do sistema: {e}")
            return {}

    @staticmethod
    def get_gpu_info() -> Dict[str, Any]:
        """Detecta disponibilidade de GPU (NVIDIA/CUDA)"""
        info = {"available": False, "name": "None", "driver": "None"}
        
        # Tentar via torch se disponÃ­vel (mais confiÃ¡vel para IA)
        try:
            import torch
            if torch.cuda.is_available():
                info["available"] = True
                info["name"] = torch.cuda.get_device_name(0)
                info["driver"] = "CUDA (torch)"
                return info
        except ImportError:
            pass

        # Tentar via linha de comando (nvidia-smi)
        try:
            import subprocess
            output = subprocess.check_output(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], 
                                          stderr=subprocess.DEVNULL, universal_newlines=True)
            if output:
                info["available"] = True
                info["name"] = output.strip()
                info["driver"] = "NVIDIA-SMI"
                return info
        except (Exception, FileNotFoundError):
            pass

        return info

    @staticmethod
    def is_admin() -> bool:
        """Verifica se o programa estÃ¡ rodando como administrador"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    @staticmethod
    def create_shortcut(target_path: str, shortcut_path: str, description: str = ""):
        """Cria atalho no Windows"""
        try:
            import winshell
            from win32com.client import Dispatch

            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = target_path
            shortcut.WorkingDirectory = str(Path(target_path).parent)
            shortcut.Description = description
            shortcut.save()
        except Exception as e:
            logger.error(f"Erro ao criar atalho: {e}")

# InstÃ¢ncias globais para conveniÃªncia
file_helper = FileHelper()
image_helper = ImageHelper()
text_helper = TextHelper()
data_helper = DataHelper()
system_helper = SystemHelper()
