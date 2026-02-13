"""
ConfiguraÃ§Ãµes globais do Jarvis 5.0
Centraliza todas as configuraÃ§Ãµes, caminhos e constantes do sistema
"""

import os
import json
import platform
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import yaml

# ConfiguraÃ§Ã£o de logging gerenciada pelo LoggingConfig
from src.utils.logging_config import LoggingConfig

# SerÃ¡ inicializado no __init__ do Config para garantir paths corretos
# (Removido basicConfig estÃ¡tico que causava conflitos)

logger = logging.getLogger(__name__)

import threading

class Config:
    """Classe singleton para configuraÃ§Ãµes globais"""

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
        """Carrega configuraÃ§Ãµes do sistema"""

        # Caminhos base
        self.PROJECT_ROOT = Path(__file__).parent.parent.parent
        self.SRC_DIR = self.PROJECT_ROOT / "src"
        self.DATA_DIR = self.PROJECT_ROOT / "data"
        self.CONFIG_DIR = self.PROJECT_ROOT / "config"
        self.MODELS_DIR = self.PROJECT_ROOT / "models"
        self.DOCS_DIR = self.PROJECT_ROOT / "docs"

        # INICIALIZAR LOGGING EXTENDIDO
        try:
            LoggingConfig.setup_jarvis_logging(self.DATA_DIR)
            logger.info("âœ… Sistema de Logging Detalhado inicializado.")
        except Exception as e:
            print(f"FATAL: Erro ao iniciar logs: {e}")

        # Carregar variÃ¡veis de ambiente
        from dotenv import load_dotenv
        env_path = self.PROJECT_ROOT / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
            # logger.info(f"âœ… VariÃ¡veis de ambiente carregadas de {env_path}")
        else:
            logger.warning(f"âš ï¸ Arquivo .env nÃ£o encontrado em {env_path}")

        # DiretÃ³rios de dados
        self.CAPTURES_DIR = self.DATA_DIR / "captures"
        self.PROCESSED_DIR = self.DATA_DIR / "processed"
        self.DATABASE_FILE = self.DATA_DIR / "jarvis.db"

        # Arquivos de configuraÃ§Ã£o
        self.SETTINGS_FILE = self.CONFIG_DIR / "settings.json"
        self.OCR_CONFIG_FILE = self.CONFIG_DIR / "ocr_config.json"
        self.AI_CONFIG_FILE = self.CONFIG_DIR / "ai_config.yaml"

        # InformaÃ§Ãµes do sistema
        self.SYSTEM_INFO = {
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture()[0]
        }

        # ConfiguraÃ§Ãµes padrÃ£o
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
                "yolo_model": "models/vision/yolov8n.pt",
                "yolo_confidence": 0.25
            }
        }

        # ConfiguraÃ§Ãµes OCR especÃ­ficas
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

        # SugestÃ£o de motor baseada em hardware
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
                "name": "RelatÃ³rio",
                "patterns": ["relatÃ³rio", "relatorio", "laudo"],
                "fields": ["titulo", "data", "autor", "conteudo"]
            },
            "form": {
                "name": "FormulÃ¡rio",
                "patterns": ["formulÃ¡rio", "formulario", "cadastro"],
                "fields": ["campos", "valores"]
            }
        }

        # PadrÃµes de extraÃ§Ã£o de dados
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

        # Criar diretÃ³rios necessÃ¡rios
        self._create_directories()

        # Carregar configuraÃ§Ãµes do usuÃ¡rio
        self.user_settings = self._load_user_settings()
        
        # Carregar configuraÃ§Ãµes de IA
        self.ai_config = self._load_ai_config()

    def _find_tesseract_path(self) -> Optional[str]:
        """Encontra o caminho do Tesseract instalado com busca agressiva"""
        # 1. Verificar variÃ¡vel de ambiente customizada
        env_path = os.environ.get("TESSERACT_PATH")
        if env_path and os.path.exists(env_path):
            return env_path
            
        # 2. Verificar no prÃ³prio diretÃ³rio do projeto (Portabilidade total)
        local_path = self.PROJECT_ROOT / "tools" / "Tesseract-OCR" / "tesseract.exe"
        if local_path.exists():
            return str(local_path)

        # 3. Caminhos padrÃµes Windows/Linux
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
        """Verifica se hÃ¡ uma GPU NVIDIA disponÃ­vel (sem circular import)"""
        try:
            import subprocess
            subprocess.check_output(["nvidia-smi"], stderr=subprocess.DEVNULL)
            return True
        except:
            # Fallback para torch se jÃ¡ estiver carregado em algum lugar
            try:
                import torch
                return torch.cuda.is_available()
            except:
                return False

    def _create_directories(self):
        """Cria diretÃ³rios necessÃ¡rios se nÃ£o existirem"""
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
        """Carrega configuraÃ§Ãµes do usuÃ¡rio do arquivo JSON"""
        if self.SETTINGS_FILE.exists():
            try:
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    user_settings = json.load(f)
                logger.info("ConfiguraÃ§Ãµes do usuÃ¡rio carregadas com sucesso")
                return user_settings
            except Exception as e:
                logger.error(f"Erro ao carregar configuraÃ§Ãµes do usuÃ¡rio: {e}")
                return self.DEFAULT_SETTINGS.copy()
        else:
            # Criar arquivo de configuraÃ§Ãµes padrÃ£o
            self.save_user_settings(self.DEFAULT_SETTINGS)
            return self.DEFAULT_SETTINGS.copy()

    def save_user_settings(self, settings: Dict[str, Any]):
        """Salva configuraÃ§Ãµes do usuÃ¡rio"""
        try:
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            logger.info("ConfiguraÃ§Ãµes do usuÃ¡rio salvas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar configuraÃ§Ãµes: {e}")

    def get_setting(self, key_path: str, default=None):
        """ObtÃ©m uma configuraÃ§Ã£o especÃ­fica usando notaÃ§Ã£o de ponto"""
        keys = key_path.split('.')
        value = self.user_settings

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set_setting(self, key_path: str, value: Any):
        """Define uma configuraÃ§Ã£o especÃ­fica"""
        keys = key_path.split('.')
        config = self.user_settings

        # Navegar atÃ© o penÃºltimo nÃ­vel
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # Definir o valor
        config[keys[-1]] = value
        self.save_user_settings(self.user_settings)

    def get_ocr_config(self, engine: str) -> Dict[str, Any]:
        """ObtÃ©m configuraÃ§Ã£o especÃ­fica do OCR"""
        return self.OCR_CONFIG.get(engine, {})

    def get_document_type_config(self, doc_type: str) -> Dict[str, Any]:
        """ObtÃ©m configuraÃ§Ã£o de tipo de documento"""
        return self.SUPPORTED_DOCUMENT_TYPES.get(doc_type, {})

    def get_extraction_pattern(self, pattern_name: str) -> str:
        """ObtÃ©m padrÃ£o de extraÃ§Ã£o regex"""
        return self.EXTRACTION_PATTERNS.get(pattern_name, "")

    def get_data_categories(self) -> Dict[str, list]:
        """ObtÃ©m categorias de dados"""
        return self.DATA_CATEGORIES.copy()
    
    def _load_ai_config(self) -> Dict[str, Any]:
        """Carrega configuraÃ§Ãµes de IA do arquivo YAML"""
        if self.AI_CONFIG_FILE.exists():
            try:
                with open(self.AI_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    ai_config = yaml.safe_load(f)
                logger.info("âœ… ConfiguraÃ§Ãµes de IA carregadas de ai_config.yaml")
                return ai_config
            except Exception as e:
                logger.error(f"âŒ Erro ao carregar ai_config.yaml: {e}")
                return {}
        else:
            logger.warning(f"âš ï¸ ai_config.yaml nÃ£o encontrado em {self.AI_CONFIG_FILE}")
            return {}
    
    def get_ai_config(self, key_path: str = None, default=None):
        """
        ObtÃ©m configuraÃ§Ã£o de IA usando notaÃ§Ã£o de ponto.
        
        Exemplos:
            config.get_ai_config('ai_agent.max_react_turns')
            config.get_ai_config('brain_router.ollama_models.tier_ultra')
            config.get_ai_config()  # Retorna toda a configuraÃ§Ã£o
        """
        if key_path is None:
            return self.ai_config
        
        keys = key_path.split('.')
        value = self.ai_config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value

    def get_api_key(self, service_name: str) -> Optional[str]:
        """
        Retrieves API key for a service from environment variables.
        
        Args:
            service_name (str): 'google', 'openai', 'anthropic', etc.
            
        Returns:
            str: API Key or None if not found
        """
        from dotenv import load_dotenv
        load_dotenv()
        
        key_map = {
            'google': 'GOOGLE_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'porcupine': 'PORCUPINE_ACCESS_KEY',
            'huggingface': 'HF_TOKEN'
        }
        
        env_var = key_map.get(service_name.lower())
        if env_var:
            return os.getenv(env_var)
        return None

# InstÃ¢ncia global
config = Config()
