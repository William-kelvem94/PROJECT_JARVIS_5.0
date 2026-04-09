# Migrated to centralized config/settings.py for chain loading (.env + env/.env) and NEXT_PUBLIC_ compat
from pathlib import Path
import sys

root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config.settings import settings
