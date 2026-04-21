import os
import glob
import re
from pathlib import Path
from loguru import logger
from .config import settings
from .unified_memory import memory

async def load_kb():
    """
    Carrega arquivos .md da Knowledge Base Obsidian para memória local do JARVIS.
    Sincroniza fatos da KB com o UnifiedMemory (SQLite).
    """
    kb_path = getattr(settings, 'jarvis_kb_path', '').strip()
    vault_root = os.getenv("JARVIS_VAULT_ROOT", getattr(settings, 'jarvis_vault_root', '')).strip()

    if not kb_path and vault_root:
        # Tenta o segundo cérebro consolidado (nova estrutura)
        fallback_jarvis = os.path.join(vault_root, "JARVIS")
        if os.path.isdir(fallback_jarvis):
            kb_path = fallback_jarvis
            logger.info(f"[KB] Usando segundo cérebro JARVIS/: {kb_path}")

    if not kb_path or not os.path.exists(kb_path):
        logger.warning(f"[KB] Caminho inválido ou não configurado: {kb_path}. Pulando carga de KB externa.")
        return 0

    logger.info(f"[KB] Carregando de: {kb_path}")

    pattern = os.path.join(kb_path, "**", "*.md")
    md_files = glob.glob(pattern, recursive=True)

    loaded = 0
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().strip()

            content = re.sub(r'^---\n[\s\S]*?\n---\n?', '', content, flags=re.MULTILINE)
            content = re.sub(r'\n\s*\n', '\n', content) 

            # RAG Local: Ingerindo conteúdo como fatos técnicos
            content_cleaned = ' '.join(content.split())[:10000] 

            if len(content_cleaned) > 20: 
                file_name = Path(file_path).stem[:50]
                source = f"kb_{file_name}"
                
                fact = f"[KB] {file_name}: {content_cleaned}"
                # Salva como fato no SQLite unificado
                if await memory.add_memory(user_id="Chefe", content=fact, category="kb_fact", source=source):
                    loaded += 1

        except Exception as e:
            logger.debug(f"[KB] Erro em {file_path}: {e}")

    logger.success(f"[KB] {loaded} fatos sincronizados no cérebro unificado!")
    return loaded
