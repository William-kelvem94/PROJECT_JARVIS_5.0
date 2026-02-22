import logging
from datetime import datetime
from pathlib import Path
import importlib
import sys


def test_logging_creates_timestamped_session_and_latest_copy(tmp_path):
    # Garantir que 'src' está no path (como conftest faria)
    src_path = Path(__file__).resolve().parents[2] / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    # Carregar o módulo diretamente pelo caminho para evitar problemas de import
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "logging_config",
        str(src_path / "utils" / "logging_config.py"),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    LoggingConfig = module.LoggingConfig

    data_dir = tmp_path

    # Run the logging setup
    loggers = LoggingConfig.setup_jarvis_logging(data_dir)

    # Determine date-based folder
    date_str = datetime.now().strftime("%Y-%m-%d")
    logs_root = data_dir / "logs"

    # Ensure 'last_session.txt' was created and points to an existing dir
    pointer = logs_root / "last_session.txt"
    assert pointer.exists(), "last_session.txt deve existir"
    session_path = Path(pointer.read_text(encoding="utf-8"))
    assert session_path.exists() and session_path.is_dir(), "Sessão apontada deve existir"

    # Session-specific jarvis_main.log must exist (handler may create file lazily) - trigger a log
    logger = logging.getLogger("jarvis")
    logger.info("Teste simples para criar arquivo de log de sessão")

    session_main = session_path / "jarvis_main.log"
    assert session_main.exists(), "Arquivo jarvis_main.log na sessão deve existir"

    # Latest copy in data/logs/jarvis_main.log (compatibilidade) must exist and contain the same content
    latest_main = logs_root / "jarvis_main.log"
    assert latest_main.exists(), "Cópia latest jarvis_main.log deve existir"
    assert latest_main.stat().st_size > 0, "Cópia latest não deve estar vazia"
