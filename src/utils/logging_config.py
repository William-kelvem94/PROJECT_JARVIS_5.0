"""
Sistema de Logging ConfigurÃ¡vel com RotaÃ§Ã£o AutomÃ¡tica
Previne crescimento infinito de logs e mantÃ©m histÃ³rico gerenciÃ¡vel
"""

import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Optional
import sys

# Import the unified JARVIS logger
from .jarvis_logger import jarvis_logger, setup_jarvis_logging

class LoggingConfig:
    """Configurador central de logging para JARVIS"""
    
    # ConfiguraÃ§Ãµes padrÃ£o
    DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10MB por arquivo
    DEFAULT_BACKUP_COUNT = 5  # 5 arquivos de backup = 50MB total
    DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'    
    @staticmethod
    def setup_jarvis_logging(data_dir: Path):
        """
        Setup complete JARVIS logging system with unified logger
        
        Args:
            data_dir: Base data directory
        """
        log_dir = data_dir / "logs"
        
        # Setup unified JARVIS logging
        unified_logger = setup_jarvis_logging(log_dir)
        
        # Setup additional specialized loggers
        LoggingConfig._setup_specialized_loggers(log_dir)
        
        return unified_logger
    
    @staticmethod
    def _setup_specialized_loggers(log_dir: Path):
        """Setup specialized loggers for specific purposes"""
        
        # Critical errors logger (always log to separate file)
        _critical_logger = LoggingConfig.setup_rotating_logger(
            logger_name="jarvis.critical",
            log_file=log_dir / "errors_critical.log",
            level=logging.ERROR,
            max_bytes=20*1024*1024,  # 20MB
            backup_count=10,
            console_output=False  # Critical errors always go to file
        )
        
        # Performance metrics logger
        _perf_logger = LoggingConfig.setup_rotating_logger(
            logger_name="jarvis.performance",
            log_file=log_dir / "performance.log",
            level=logging.INFO,
            max_bytes=50*1024*1024,  # 50MB
            backup_count=3,
            console_output=False
        )
        
        # Session logger (rotates daily)
        _session_logger = LoggingConfig.setup_timed_rotating_logger(
            logger_name="jarvis.session",
            log_file=log_dir / "jarvis_session.log",
            level=logging.DEBUG,
            when='midnight',
            backup_count=30,  # Keep 30 days
            console_output=True
        )    
    @staticmethod
    def setup_rotating_logger(
        logger_name: str,
        log_file: Path,
        level: int = logging.INFO,
        max_bytes: int = DEFAULT_MAX_BYTES,
        backup_count: int = DEFAULT_BACKUP_COUNT,
        console_output: bool = True,
        format_string: Optional[str] = None
    ) -> logging.Logger:
        """
        Configura um logger com rotaÃ§Ã£o automÃ¡tica de arquivos
        
        Args:
            logger_name: Nome do logger
            log_file: Path completo do arquivo de log
            level: NÃ­vel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_bytes: Tamanho mÃ¡ximo do arquivo antes de rotacionar (bytes)
            backup_count: NÃºmero de backups a manter
            console_output: Se deve tambÃ©m logar no console
            format_string: Formato customizado (opcional)
        
        Returns:
            logging.Logger: Logger configurado
        """
        # Criar diretÃ³rio se nÃ£o existir
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Obter ou criar logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        
        # Limpar handlers existentes para evitar duplicaÃ§Ã£o
        logger.handlers.clear()
        
        # Formato de mensagem
        formatter = logging.Formatter(
            format_string or LoggingConfig.DEFAULT_FORMAT,
            datefmt=LoggingConfig.DEFAULT_DATE_FORMAT
        )
        
        # Handler de arquivo com rotaÃ§Ã£o
        file_handler = RotatingFileHandler(
            filename=str(log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8',
            delay=True  # Thread-safe: abre arquivo apenas quando necessÃ¡rio
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Handler de console (opcional)
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.WARNING)  # Console sÃ³ para warnings+
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    @staticmethod
    def setup_timed_rotating_logger(
        logger_name: str,
        log_file: Path,
        level: int = logging.INFO,
        when: str = 'midnight',
        interval: int = 1,
        backup_count: int = 7,
        console_output: bool = True
    ) -> logging.Logger:
        """
        Configura um logger com rotaÃ§Ã£o baseada em tempo (diÃ¡ria, semanal, etc)
        
        Args:
            logger_name: Nome do logger
            log_file: Path completo do arquivo de log
            level: NÃ­vel de logging
            when: Quando rotacionar ('S','M','H','D','midnight','W0'-'W6')
            interval: Intervalo de tempo
            backup_count: NÃºmero de backups a manter
            console_output: Se deve tambÃ©m logar no console
        
        Returns:
            logging.Logger: Logger configurado
        """
        # Criar diretÃ³rio se nÃ£o existir
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Obter ou criar logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        logger.handlers.clear()
        
        # Formato de mensagem
        formatter = logging.Formatter(
            LoggingConfig.DEFAULT_FORMAT,
            datefmt=LoggingConfig.DEFAULT_DATE_FORMAT
        )
        
        # Handler de arquivo com rotaÃ§Ã£o por tempo
        file_handler = TimedRotatingFileHandler(
            filename=str(log_file),
            when=when,
            interval=interval,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Handler de console (opcional)
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.WARNING)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    @staticmethod
    def setup_jarvis_session_logging(data_dir: Path) -> dict:
        """
        Configura todo o sistema de logging do JARVIS 5.0 (session-level)
        Organiza logs em pastas por data (YYYY-MM-DD) para fÃ¡cil auditoria.
        """
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Criar diretÃ³rio da sessÃ£o (ex: data/logs/2026-02-10/)
        session_dir = data_dir / "logs" / date_str
        session_dir.mkdir(parents=True, exist_ok=True)
        
        loggers = {}
        
        # 1. Logger PRINCIPAL (Info+)
        loggers['main'] = LoggingConfig.setup_rotating_logger(
            logger_name='jarvis',  # Root logger capture
            log_file=session_dir / 'jarvis_main.log',
            level=logging.INFO,
            max_bytes=10 * 1024 * 1024,
            backup_count=10,
            console_output=True
        )
        
        # 2. Logger DETALHADO (Debug total - Arquivo gigante, mas Ãºtil)
        # Capture root logger 'jarvis' debugs too
        debug_handler = RotatingFileHandler(
            filename=str(session_dir / 'jarvis_detailed_debug.log'),
            maxBytes=20 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(logging.Formatter(LoggingConfig.DEFAULT_FORMAT))
        logging.getLogger().addHandler(debug_handler) # Attach to root
        
        # 3. Componentes EspecÃ­ficos (Separados para clareza)
        
        # Vision (OCR, YOLO)
        loggers['vision'] = LoggingConfig.setup_rotating_logger(
            logger_name='src.core.vision', # Mapeia imports src.core.vision...
            log_file=session_dir / 'component_vision.log',
            level=logging.DEBUG, 
            console_output=False
        )
        
        # Audio (STT, TTS)
        loggers['audio'] = LoggingConfig.setup_rotating_logger(
            logger_name='src.core.audio',
            log_file=session_dir / 'component_audio.log',
            level=logging.DEBUG,
            console_output=False
        )
        
        # Intelligence (AI, Brain, Memory)
        loggers['intelligence'] = LoggingConfig.setup_rotating_logger(
            logger_name='src.core.intelligence',
            log_file=session_dir / 'component_intelligence.log',
            level=logging.DEBUG, # Fundamental para debug de pensamento
            console_output=False
        )
        
        # 4. Logger de ERROS CRÃTICOS (Agregado global)
        error_handler = RotatingFileHandler(
            filename=str(session_dir / 'errors_critical.log'),
            maxBytes=5 * 1024 * 1024,
            backupCount=10,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(LoggingConfig.DEFAULT_FORMAT))
        logging.getLogger().addHandler(error_handler)
        
        # 5. Filtrar avisos inofensivos de terÃ§eitos
        logging.getLogger('easyocr').setLevel(logging.ERROR)
        logging.getLogger('easyocr.easyocr').setLevel(logging.ERROR)
        
        return loggers


def get_or_create_logger(name: str, log_file: Optional[Path] = None) -> logging.Logger:
    """
    FunÃ§Ã£o helper para obter/criar logger rapidamente
    
    Args:
        name: Nome do logger
        log_file: Path do arquivo (opcional, usa nome padrÃ£o se nÃ£o fornecido)
    
    Returns:
        logging.Logger: Logger configurado
    """
    if log_file is None:
        from pathlib import Path
        log_file = Path(__file__).parent.parent.parent / "data" / "logs" / f"{name}.log"
    
    return LoggingConfig.setup_rotating_logger(
        logger_name=name,
        log_file=log_file,
        level=logging.INFO
    )


# Exemplo de uso direto
if __name__ == "__main__":
    # Teste do sistema de logging
    from pathlib import Path
    
    test_logger = LoggingConfig.setup_rotating_logger(
        logger_name="test",
        log_file=Path("test_logs/test.log"),
        max_bytes=1024,  # 1KB para teste rÃ¡pido
        backup_count=3
    )
    
    # Gerar logs de teste
    for i in range(100):
        test_logger.info(f"Mensagem de teste {i}: " + "x" * 100)
    
    print("âœ… Teste de rotaÃ§Ã£o de logs concluÃ­do. Verifique test_logs/")
