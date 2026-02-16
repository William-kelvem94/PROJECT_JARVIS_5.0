"""
Configurações globais do Jarvis 5.0
Centraliza todas as configurações, caminhos e constantes do sistema
"""

import os
import json
import platform
import threading
from pathlib import Path
from typing import Dict, Any, Optional

# Safe Imports
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    yaml = None
    YAML_AVAILABLE = False

try:
    from pydantic import BaseModel, ValidationError, Field

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

    # Dummy classes for Safe Mode
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    class ValidationError(Exception):
        pass

    class Field:
        pass


try:
    import jsonschema
except ImportError:
    jsonschema = None

# Configuração de logging centralizada
from src.utils.logging_config import LoggingConfig
from src.utils.jarvis_logger import get_component_logger

logger = get_component_logger("config")

# Schemas de validação (Conditional)
if PYDANTIC_AVAILABLE:

    class AIConfigSchema(BaseModel):
        """Schema para ai_config.yaml"""

        model_name: Optional[str] = None
        max_tokens: Optional[int] = None
        temperature: Optional[float] = None
        cache_enabled: bool = True
        long_term_memory_enabled: bool = True

        class Config:
            extra = "allow"

    class SettingsSchema(BaseModel):
        """Schema para settings.json"""

        app: Dict[str, Any]
        capture: Dict[str, Any]
        ocr: Dict[str, Any]
        processing: Dict[str, Any]
        storage: Dict[str, Any]
        analysis: Dict[str, Any]
        interface: Dict[str, Any]

        class Config:
            extra = "allow"

else:

    class AIConfigSchema(BaseModel):
        pass

    class SettingsSchema(BaseModel):
        pass


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

        # INICIALIZAR LOGGING EXTENDIDO
        try:
            LoggingConfig.setup_jarvis_logging(self.DATA_DIR)
            logger.info("✅ Sistema de Logging Unificado JARVIS inicializado.")
        except Exception as e:
            print(f"FATAL: Erro ao iniciar logs: {e}")

        # Carregar variáveis de ambiente
        try:
            from dotenv import load_dotenv

            env_path = self.PROJECT_ROOT / ".env"
            if env_path.exists():
                load_dotenv(dotenv_path=env_path, override=True)
            else:
                logger.warning(f"⚠️ Arquivo .env não encontrado em {env_path}")
        except ImportError:
            logger.warning(
                "python-dotenv não instalado. Variáveis de ambiente não carregadas do .env"
            )

        # Core Data Subdirectories
        self.LOGS_DIR = self.DATA_DIR / "logs"
        self.CACHE_DIR = self.DATA_DIR / "cache"
        self.DB_DIR = self.DATA_DIR / "database"
        self.MEMORY_DIR = self.DATA_DIR / "memory"
        self.VISION_DIR = self.DATA_DIR / "vision"
        self.AUDIO_DIR = self.DATA_DIR / "audio"
        self.SYSTEM_DIR = self.DATA_DIR / "system"
        self.LEARNING_DIR = self.DATA_DIR / "learning"
        self.SECURITY_DIR = self.DATA_DIR / "security"
        self.BACKUPS_DIR = self.DATA_DIR / "backups"
        self.WORKFLOWS_DIR = self.DATA_DIR / "workflows"
        self.USERS_DIR = self.DATA_DIR / "users"
        self.TESTS_DIR = self.DATA_DIR / "tests"

        # Specific Paths
        self.CAPTURES_DIR = self.VISION_DIR / "captures"
        self.PROCESSED_DIR = self.VISION_DIR / "processed"
        self.DATABASE_FILE = self.DB_DIR / "jarvis.db"
        self.FEEDBACK_FILE = self.DB_DIR / "feedback.db"
        self.HEALTH_REPORT_FILE = self.SYSTEM_DIR / "system_health.json"

        # Temp & Exports
        self.TEMP_DIR = self.DATA_DIR / "temp"
        self.EXPORTS_DIR = self.DATA_DIR / "exports"

        # Arquivos de configuração (SISTEMA)
        self.SETTINGS_FILE = self.CONFIG_DIR / "settings.json"
        self.OCR_CONFIG_FILE = self.CONFIG_DIR / "ocr_config.json"
        self.AI_CONFIG_FILE = self.CONFIG_DIR / "ai_config.yaml"

        # Informações do sistema
        self.SYSTEM_INFO = {
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture()[0],
        }

        # Caminhos de USUÁRIO (Camada de Sobreposição)
        if self.SYSTEM_INFO["os"] == "Windows":
            self.USER_CONFIG_DIR = (
                Path(os.environ.get("APPDATA", "~")).expanduser() / "Jarvis"
            )
        else:
            self.USER_CONFIG_DIR = Path("~/.config/jarvis").expanduser()

        self.USER_SETTINGS_FILE = self.USER_CONFIG_DIR / "settings.json"
        self.USER_AI_CONFIG_FILE = self.USER_CONFIG_DIR / "ai_config.yaml"
        self.USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # Configurações padrão
        self.DEFAULT_SETTINGS = {
            "app": {
                "name": "Jarvis 5.0",
                "version": "5.0.0",
                "language": "pt-BR",
                "theme": "dark",
            },
            "capture": {
                "default_format": "PNG",
                "quality": 95,
                "hotkey": "ctrl+shift+s",
                "auto_save": True,
                "capture_delay": 0.5,
            },
            "ocr": {
                "engine": "tesseract",  # tesseract, easyocr, or hybrid
                "languages": ["por", "eng"],
                "confidence_threshold": 60,
                "preprocessing": True,
                "post_correction": True,
            },
            "processing": {
                "max_workers": 4,
                "batch_size": 10,
                "timeout": 30,
                "retry_attempts": 3,
            },
            "storage": {
                "auto_organize": True,
                "compression": True,
                "encryption": False,
                "retention_days": 365,
            },
            "analysis": {
                "enable_ai": True,
                "categorization": True,
                "entity_extraction": True,
                "sentiment_analysis": False,
            },
            "interface": {
                "minimize_to_tray": True,
                "show_notifications": True,
                "auto_start": False,
                "check_updates": True,
            },
            "portability": {"target_user_email": os.getenv("JARVIS_USER_EMAIL", "")},
            "vision": {
                "yolo_enabled": True,
                "yolo_model": "models/vision/yolov8n.pt",
                "yolo_confidence": 0.25,
            },
        }

        # Configurações OCR específicas
        self.OCR_CONFIG = {
            "tesseract": {
                "path": self._find_tesseract_path(),
                "config": "--oem 3 --psm 6",
                "timeout": 30,
            },
            "easyocr": {
                "gpu": self._has_gpu(),
                "model_storage_directory": str(self.MODELS_DIR),
                "user_network_directory": str(self.MODELS_DIR),
                "detect_network": "craft",
                "recog_network": "crnn",
                "download_enabled": True,
                "detector": True,
                "recognizer": True,
            },
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
                "fields": ["numero", "data", "valor", "emitente", "destinatario"],
            },
            "invoice": {
                "name": "Fatura",
                "patterns": ["fatura", "conta", "boleto"],
                "fields": ["numero", "vencimento", "valor", "pagador", "beneficiario"],
            },
            "contract": {
                "name": "Contrato",
                "patterns": ["contrato", "acordo", "termo"],
                "fields": ["numero", "partes", "data", "objeto", "valor"],
            },
            "report": {
                "name": "Relatório",
                "patterns": ["relatório", "relatorio", "laudo"],
                "fields": ["titulo", "data", "autor", "conteudo"],
            },
            "form": {
                "name": "Formulário",
                "patterns": ["formulário", "formulario", "cadastro"],
                "fields": ["campos", "valores"],
            },
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
            "url": r"https?://(?:[-\w.])+(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?",
        }

        # Categorias de dados
        self.DATA_CATEGORIES = {
            "personal": ["nome", "cpf", "telefone", "email", "endereco"],
            "financial": ["valor", "conta", "agencia", "banco", "pix"],
            "business": ["cnpj", "empresa", "contrato", "projeto"],
            "documents": ["numero", "data", "validade", "codigo"],
        }

        # Criar diretórios necessários
        self._create_directories()

        # Carregar configurações do usuário
        self.user_settings = self._load_user_settings()

        # Carregar configurações de IA
        self.ai_config = self._load_ai_config()

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
            "/usr/local/bin/tesseract",
            "/opt/homebrew/bin/tesseract",  # MacOS
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

            if platform.system() == "Windows":
                # Avoid popping up console window
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.check_output(
                    ["nvidia-smi"], stderr=subprocess.DEVNULL, startupinfo=startupinfo
                )
            else:
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
            self.LOGS_DIR,
            self.CACHE_DIR,
            self.DB_DIR,
            self.MEMORY_DIR,
            self.SYSTEM_DIR,
            self.LEARNING_DIR,
            self.SECURITY_DIR,
            self.BACKUPS_DIR,
            self.WORKFLOWS_DIR,
            self.USERS_DIR,
            self.TESTS_DIR,
            self.TEMP_DIR,
            self.EXPORTS_DIR,
        ]

        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.warning(f"Could not create directory {directory}: {e}")

    def _load_user_settings(self) -> Dict[str, Any]:
        """Carrega configurações do sistema e sobrepõe com as do usuário (Camadas)"""
        settings = self.DEFAULT_SETTINGS.copy()

        # 1. Carregar do Sistema (Project Root / config)
        if self.SETTINGS_FILE.exists():
            try:
                with open(self.SETTINGS_FILE, "r", encoding="utf-8") as f:
                    system_settings = json.load(f)
                    self._deep_update(settings, system_settings)
            except Exception as e:
                logger.error(f"Erro ao carregar settings do sistema: {e}")

        # 2. Carregar do Usuário (AppData ou ~/.config)
        if self.USER_SETTINGS_FILE.exists():
            try:
                with open(self.USER_SETTINGS_FILE, "r", encoding="utf-8") as f:
                    user_settings = json.load(f)
                    self._deep_update(settings, user_settings)
                    logger.info(
                        f"✅ Configurações do usuário carregadas de {self.USER_SETTINGS_FILE}"
                    )
            except Exception as e:
                logger.error(f"Erro ao carregar settings do usuário: {e}")

        return settings

    def _deep_update(self, base_dict: Dict, update_with: Dict):
        """Atualiza dicionário aninhado recursivamente"""
        for k, v in update_with.items():
            if (
                isinstance(v, dict)
                and k in base_dict
                and isinstance(base_dict[k], dict)
            ):
                self._deep_update(base_dict[k], v)
            else:
                base_dict[k] = v

    def save_user_settings(self, settings: Dict[str, Any]):
        """Salva configurações do usuário com backup automático"""
        try:
            # Criar backup se arquivo existir
            if self.SETTINGS_FILE.exists():
                backup_file = self.SETTINGS_FILE.with_suffix(".json.backup")
                import shutil

                shutil.copy2(self.SETTINGS_FILE, backup_file)
                logger.debug(f"Backup criado: {backup_file}")

            with open(self.SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            logger.info("Configurações do usuário salvas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")

    def get_setting(self, key_path: str, default=None):
        """Obtém uma configuração específica usando notação de ponto"""
        keys = key_path.split(".")
        value = self.user_settings

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set_setting(self, key_path: str, value: Any):
        """Define uma configuração específica"""
        keys = key_path.split(".")
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

    def _load_ai_config(self) -> Dict[str, Any]:
        """Carrega configurações de IA do arquivo YAML"""
        if not YAML_AVAILABLE:
            logger.warning("YAML not available. Using default AI config.")
            return self._get_default_ai_config()

        if self.AI_CONFIG_FILE.exists():
            try:
                with open(self.AI_CONFIG_FILE, "r", encoding="utf-8") as f:
                    ai_config = yaml.safe_load(f)

                # Validar configuração
                if PYDANTIC_AVAILABLE:
                    try:
                        validated_config = AIConfigSchema(**ai_config)
                        logger.info("✅ Configurações de IA validadas com sucesso")
                    except ValidationError as e:
                        logger.error(f"❌ Configuração de IA inválida: {e}")
                        # Usar valores padrão para campos inválidos
                        ai_config = self._get_default_ai_config()

                logger.info("✅ Configurações de IA carregadas de ai_config.yaml")
                return ai_config
            except Exception as e:
                logger.error(f"❌ Erro ao carregar ai_config.yaml: {e}")
                return self._get_default_ai_config()
        else:
            logger.warning(f"⚠️ ai_config.yaml não encontrado em {self.AI_CONFIG_FILE}")
            return self._get_default_ai_config()

    def _get_default_ai_config(self) -> Dict[str, Any]:
        """Retorna configurações padrão de IA"""
        return {
            "model_name": "microsoft/DialoGPT-medium",
            "max_tokens": 1000,
            "temperature": 0.7,
            "cache_enabled": True,
            "long_term_memory_enabled": True,
        }

    def get_ai_config(self, key_path: str = None, default=None):
        """
        Obtém configuração de IA usando notação de ponto.
        """
        if key_path is None:
            return self.ai_config

        keys = key_path.split(".")
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
        """
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass

        key_map = {
            "google": "GOOGLE_API_KEY",
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "porcupine": "PORCUPINE_ACCESS_KEY",
            "huggingface": "HF_TOKEN",
        }

        env_var = key_map.get(service_name.lower())
        if env_var:
            return os.getenv(env_var)
        return None


# Instância global
config = Config()
