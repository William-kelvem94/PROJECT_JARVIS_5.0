"""
JARVIS Logger - Sistema de Logging Centralizado
"""

import logging
import sys
from pathlib import Path

# Configurar logging
logger = logging.getLogger("jarvis")
logger.setLevel(logging.INFO)

# Handler para console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Formato
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(formatter)

# Adicionar handler se não existir
if not logger.handlers:
    logger.addHandler(console_handler)

# Arquivo de log opcional
log_file = Path("./logs/jarvis.log")
if log_file.parent.exists():
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# Evitar duplicação de logs
logger.propagate = False