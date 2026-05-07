import glob
import os
import re
from pathlib import Path

from loguru import logger

from .config import settings
from .unified_memory import memory

IGNORED_KB_PARTS = {
    ".git",
    ".obsidian",
    ".venv",
    ".knowledge_index",
    ".logs",
    "__pycache__",
    "node_modules",
}


def _resolve_kb_path() -> str:
    kb_path = os.getenv("JARVIS_KB_PATH") or getattr(settings, "JARVIS_KB_PATH", "")
    vault_root = os.getenv("JARVIS_VAULT_ROOT") or getattr(settings, "JARVIS_VAULT_ROOT", "")

    if kb_path and os.path.isdir(kb_path):
        return kb_path

    if vault_root:
        jarvis_dir = os.path.join(vault_root, "JARVIS")
        if os.path.isdir(jarvis_dir):
            logger.info(f"[KB] Usando segundo cerebro JARVIS/: {jarvis_dir}")
            return jarvis_dir
        if os.path.isdir(vault_root):
            logger.info(f"[KB] Usando vault inteiro como KB: {vault_root}")
            return vault_root

    fallback_seed = settings.BASE_DIR / "data" / "kb_local" / "JARVIS" / "KnowledgeBase"
    return str(fallback_seed) if fallback_seed.is_dir() else ""


def _is_ignored_md(path: str) -> bool:
    return any(part in IGNORED_KB_PARTS for part in Path(path).parts)


async def load_kb():
    """
    Carrega arquivos .md da Knowledge Base Obsidian para memoria local do JARVIS.
    O vault vivo deve vir de JARVIS_VAULT_ROOT, e JARVIS_KB_PATH aponta para
    a subarvore tecnica principal, normalmente <vault>/JARVIS.
    """
    kb_path = _resolve_kb_path()
    if not kb_path or not os.path.exists(kb_path):
        logger.warning(f"[KB] Caminho invalido ou nao configurado: {kb_path}. Pulando carga de KB externa.")
        return 0

    logger.info(f"[KB] Carregando de: {kb_path}")

    pattern = os.path.join(kb_path, "**", "*.md")
    md_files = [path for path in glob.glob(pattern, recursive=True) if not _is_ignored_md(path)]

    loaded = 0
    for file_path in md_files:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().strip()

            content = re.sub(r"^---\n[\s\S]*?\n---\n?", "", content, flags=re.MULTILINE)
            content = re.sub(r"\n\s*\n", "\n", content)
            content_cleaned = " ".join(content.split())[:10000]

            if len(content_cleaned) > 20:
                file_name = Path(file_path).stem[:50]
                source = f"kb_{file_name}"
                fact = f"[KB] {file_name}: {content_cleaned}"

                if await memory.add_memory(user_id="Chefe", content=fact, category="kb_fact", source=source):
                    loaded += 1

        except Exception as e:
            logger.debug(f"[KB] Erro em {file_path}: {e}")

    logger.success(f"[KB] {loaded} fatos sincronizados no cerebro unificado!")
    return loaded
