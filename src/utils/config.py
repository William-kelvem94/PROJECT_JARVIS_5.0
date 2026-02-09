"""
Configurações globais do Jarvis 5.0
Centraliza todas as configurações, caminhos e constantes do sistema
"""

import os
import json
import platform
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('data', 'logs', 'jarvis.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

import threading

class Config:
    """Classe singleton para configurações globais"""

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self._load_config()
                    self._initialized = True

    def _load_config(self):
        """Carrega configurações do sistema"""

        # Caminhos base
        self.PROJECT_ROOT = Path(__file__).parent.parent.parent
        self.SRC_DIR = self.PROJECT_ROOT / "src"
        self.DATA_DIR = self.PROJECT_ROOT / "data"
        self.CONFIG_DIR = self.PROJECT_ROOT / "config"
        self.MODELS_DIR = self.PROJECT_ROOT / "models"
        self.DOCS_DIR = self.PROJECT_ROOT / "docs"

        # Diretórios de dados
        self.CAPTURES_DIR = self.DATA_DIR / "captures"
        self.PROCESSED_DIR = self.DATA_DIR / "processed"
        self.DATABASE_FILE = self.DATA_DIR / "jarvis.db"

        # Arquivos de configuração
        self.SETTINGS_FILE = self.CONFIG_DIR / "settings.json"
        self.OCR_CONFIG_FILE = self.CONFIG_DIR / "ocr_config.json"

        # Informações do sistema
        self.SYSTEM_INFO = {
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture()[0]
        }

        # Configurações padrão
        self.DEFAULT_SETTINGS = {
            "app": {
                "name": "Jarvis 5.0",
                "version": "5.0.0",
                "language": "pt-BR",
                "theme": "dark"
            },
            "capture": {
                "default_format": "PNG",
                "quality": 95,
                "hotkey": "ctrl+shift+s",
                "auto_save": True,
                "capture_delay": 0.5
            },
            "ocr": {
                "engine": "tesseract",  # tesseract, easyocr, or hybrid
                "languages": ["por", "eng"],
                "confidence_threshold": 60,
                "preprocessing": True,
                "post_correction": True
            },
            "processing": {
                "max_workers": 4,
                "batch_size": 10,
                "timeout": 30,
                "retry_attempts": 3
            },
            "storage": {
                "auto_organize": True,
                "compression": True,
                "encryption": False,
                "retention_days": 365
            },
            "analysis": {
                "enable_ai": True,
                "categorization": True,
                "entity_extraction": True,
                "sentiment_analysis": False
            },
            "interface": {
                "minimize_to_tray": True,
                "show_notifications": True,
                "auto_start": False,
                "check_updates": True
            },
            "vision": {
                "yolo_enabled": True,
                "yolo_model": "yolov8n.pt",
                "yolo_confidence": 0.25
            }
        }

        # Configurações OCR específicas
        self.OCR_CONFIG = {
            "tesseract": {
                "path": self._find_tesseract_path(),
                "config": "--oem 3 --psm 6",
                "timeout": 30
            },
            "easyocr": {
                "gpu": self._has_gpu(),
                "model_storage_directory": str(self.MODELS_DIR),
                "user_network_directory": str(self.MODELS_DIR),
                "detect_network": "craft",
                "recog_network": "crnn",
                "download_enabled": True,
                "detector": True,
                "recognizer": True
            }
        }

        # Sugestão de motor baseada em hardware
        if self._has_gpu():
            self.DEFAULT_SETTINGS["ocr"]["engine"] = "easyocr"
        else:
            self.DEFAULT_SETTINGS["ocr"]["engine"] = "tesseract"

        # Tipos de documento suportados
        self.SUPPORTED_DOCUMENT_TYPES = {
            "receipt": {
                "name": "Nota Fiscal",
                "patterns": ["nota fiscal", "cupom fiscal", "recibo"],
                "fields": ["numero", "data", "valor", "emitente", "destinatario"]
            },
            "invoice": {
                "name": "Fatura",
                "patterns": ["fatura", "conta", "boleto"],
                "fields": ["numero", "vencimento", "valor", "pagador", "beneficiario"]
            },
            "contract": {
                "name": "Contrato",
                "patterns": ["contrato", "acordo", "termo"],
                "fields": ["numero", "partes", "data", "objeto", "valor"]
            },
            "report": {
                "name": "Relatório",
                "patterns": ["relatório", "relatorio", "laudo"],
                "fields": ["titulo", "data", "autor", "conteudo"]
            },
            "form": {
                "name": "Formulário",
                "patterns": ["formulário", "formulario", "cadastro"],
                "fields": ["campos", "valores"]
            }
        }

        # Padrões de extração de dados
        self.EXTRACTION_PATTERNS = {
            "cpf": r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b",
            "cnpj": r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b",
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}\b",
            "cep": r"\b\d{5}-?\d{3}\b",
            "money": r"R?\$\s*\d{1,3}(?:\.\d{3})*,\d{2}",
            "date": r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
            "url": r"https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?"
        }

        # Categorias de dados
        self.DATA_CATEGORIES = {
            "personal": ["nome", "cpf", "telefone", "email", "endereco"],
            "financial": ["valor", "conta", "agencia", "banco", "pix"],
            "business": ["cnpj", "empresa", "contrato", "projeto"],
            "documents": ["numero", "data", "validade", "codigo"]
        }

        # Criar diretórios necessários
        self._create_directories()

        # Carregar configurações do usuário
        self.user_settings = self._load_user_settings()

    def _find_tesseract_path(self) -> Optional[str]:
        """Encontra o caminho do Tesseract instalado com busca agressiva"""
        # 1. Verificar variável de ambiente customizada
        env_path = os.environ.get("TESSERACT_PATH")
        if env_path and os.path.exists(env_path):
            return env_path
            
        # 2. Verificar no próprio diretório do projeto (Portabilidade total)
        local_path = self.PROJECT_ROOT / "tools" / "Tesseract-OCR" / "tesseract.exe"
        if local_path.exists():
            return str(local_path)

        # 3. Caminhos padrões Windows/Linux
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"D:\Program Files\Tesseract-OCR\tesseract.exe",
            "/usr/bin/tesseract",
            "/usr/local/bin/tesseract"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        # 4. Tentar encontrar via PATH do sistema
        import shutil
        tesseract_path = shutil.which("tesseract")
        if tesseract_path:
            return tesseract_path

        return None

    def _has_gpu(self) -> bool:
        """Verifica se há uma GPU NVIDIA disponível (sem circular import)"""
        try:
            import subprocess
            subprocess.check_output(["nvidia-smi"], stderr=subprocess.DEVNULL)
            return True
        except:
            # Fallback para torch se já estiver carregado em algum lugar
            try:
                import torch
                return torch.cuda.is_available()
            except:
                return False

    def _create_directories(self):
        """Cria diretórios necessários se não existirem"""
        directories = [
            self.CAPTURES_DIR,
            self.PROCESSED_DIR,
            self.CONFIG_DIR,
            self.MODELS_DIR,
            self.DATA_DIR / "temp",
            self.DATA_DIR / "exports"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _load_user_settings(self) -> Dict[str, Any]:
        """Carrega configurações do usuário do arquivo JSON"""
        if self.SETTINGS_FILE.exists():
            try:
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    user_settings = json.load(f)
                logger.info("Configurações do usuário carregadas com sucesso")
                return user_settings
            except Exception as e:
                logger.error(f"Erro ao carregar configurações do usuário: {e}")
                return self.DEFAULT_SETTINGS.copy()
        else:
            # Criar arquivo de configurações padrão
            self.save_user_settings(self.DEFAULT_SETTINGS)
            return self.DEFAULT_SETTINGS.copy()

    def save_user_settings(self, settings: Dict[str, Any]):
        """Salva configurações do usuário"""
        try:
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            logger.info("Configurações do usuário salvas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")

    def get_setting(self, key_path: str, default=None):
        """Obtém uma configuração específica usando notação de ponto"""
        keys = key_path.split('.')
        value = self.user_settings

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set_setting(self, key_path: str, value: Any):
        """Define uma configuração específica"""
        keys = key_path.split('.')
        config = self.user_settings

        # Navegar até o penúltimo nível
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # Definir o valor
        config[keys[-1]] = value
        self.save_user_settings(self.user_settings)

    def get_ocr_config(self, engine: str) -> Dict[str, Any]:
        """Obtém configuração específica do OCR"""
        return self.OCR_CONFIG.get(engine, {})

    def get_document_type_config(self, doc_type: str) -> Dict[str, Any]:
        """Obtém configuração de tipo de documento"""
        return self.SUPPORTED_DOCUMENT_TYPES.get(doc_type, {})

    def get_extraction_pattern(self, pattern_name: str) -> str:
        """Obtém padrão de extração regex"""
        return self.EXTRACTION_PATTERNS.get(pattern_name, "")

    def get_data_categories(self) -> Dict[str, list]:
        """Obtém categorias de dados"""
        return self.DATA_CATEGORIES.copy()

# Instância global
config = Config()
