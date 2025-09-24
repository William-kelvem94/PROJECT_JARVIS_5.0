# Estrutura de logging para Jarvis

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("jarvis")
