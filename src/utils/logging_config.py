"""
Sistema de Logging Configurável com Rotação Automática
Previne crescimento infinito de logs e mantém histórico gerenciável
"""

import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Optional
import sys

class LoggingConfig:
    """Configurador central de logging para JARVIS"""
    
    # Configurações padrão
    DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10MB por arquivo
    DEFAULT_BACKUP_COUNT = 5  # 5 arquivos de backup = 50MB total
    DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
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
        Configura um logger com rotação automática de arquivos
        
        Args:
            logger_name: Nome do logger
            log_file: Path completo do arquivo de log
            level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_bytes: Tamanho máximo do arquivo antes de rotacionar (bytes)
            backup_count: Número de backups a manter
            console_output: Se deve também logar no console
            format_string: Formato customizado (opcional)
        
        Returns:
            logging.Logger: Logger configurado
        """
        # Criar diretório se não existir
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Obter ou criar logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        
        # Limpar handlers existentes para evitar duplicação
        logger.handlers.clear()
        
        # Formato de mensagem
        formatter = logging.Formatter(
            format_string or LoggingConfig.DEFAULT_FORMAT,
            datefmt=LoggingConfig.DEFAULT_DATE_FORMAT
        )
        
        # Handler de arquivo com rotação
        file_handler = RotatingFileHandler(
            filename=str(log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Handler de console (opcional)
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.WARNING)  # Console só para warnings+
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
        Configura um logger com rotação baseada em tempo (diária, semanal, etc)
        
        Args:
            logger_name: Nome do logger
            log_file: Path completo do arquivo de log
            level: Nível de logging
            when: Quando rotacionar ('S','M','H','D','midnight','W0'-'W6')
            interval: Intervalo de tempo
            backup_count: Número de backups a manter
            console_output: Se deve também logar no console
        
        Returns:
            logging.Logger: Logger configurado
        """
        # Criar diretório se não existir
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
        
        # Handler de arquivo com rotação por tempo
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
    def setup_jarvis_logging(data_dir: Path) -> dict:
        """
        Configura todo o sistema de logging do JARVIS
        
        Args:
            data_dir: Diretório base de dados (onde ficam os logs)
        
        Returns:
            dict: Dicionário com todos os loggers configurados
        """
        logs_dir = data_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        loggers = {}
        
        # Logger principal do sistema (rotação por tamanho)
        loggers['main'] = LoggingConfig.setup_rotating_logger(
            logger_name='jarvis',
            log_file=logs_dir / 'jarvis_singularity.log',
            level=logging.INFO,
            max_bytes=10 * 1024 * 1024,  # 10MB
            backup_count=5,
            console_output=True
        )
        
        # Logger de visão (rotação menor pois pode gerar muito log)
        loggers['vision'] = LoggingConfig.setup_rotating_logger(
            logger_name='core.vision',
            log_file=logs_dir / 'vision.log',
            level=logging.INFO,
            max_bytes=5 * 1024 * 1024,  # 5MB
            backup_count=3,
            console_output=False
        )
        
        # Logger de áudio
        loggers['audio'] = LoggingConfig.setup_rotating_logger(
            logger_name='core.audio',
            log_file=logs_dir / 'audio.log',
            level=logging.INFO,
            max_bytes=5 * 1024 * 1024,  # 5MB
            backup_count=3,
            console_output=False
        )
        
        # Logger de IA/Intelligence
        loggers['intelligence'] = LoggingConfig.setup_rotating_logger(
            logger_name='core.intelligence',
            log_file=logs_dir / 'intelligence.log',
            level=logging.DEBUG,  # DEBUG para análise detalhada
            max_bytes=10 * 1024 * 1024,  # 10MB
            backup_count=5,
            console_output=False
        )
        
        # Logger de erros apenas (rotação diária)
        loggers['errors'] = LoggingConfig.setup_timed_rotating_logger(
            logger_name='jarvis.errors',
            log_file=logs_dir / 'errors.log',
            level=logging.ERROR,
            when='midnight',
            backup_count=30,  # Manter 30 dias de erros
            console_output=True
        )
        
        return loggers


def get_or_create_logger(name: str, log_file: Optional[Path] = None) -> logging.Logger:
    """
    Função helper para obter/criar logger rapidamente
    
    Args:
        name: Nome do logger
        log_file: Path do arquivo (opcional, usa nome padrão se não fornecido)
    
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
        max_bytes=1024,  # 1KB para teste rápido
        backup_count=3
    )
    
    # Gerar logs de teste
    for i in range(100):
        test_logger.info(f"Mensagem de teste {i}: " + "x" * 100)
    
    print("✅ Teste de rotação de logs concluído. Verifique test_logs/")
