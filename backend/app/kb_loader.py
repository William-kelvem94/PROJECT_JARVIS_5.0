import os
import glob
import re
from pathlib import Path
from loguru import logger
from .config import settings
from .local_memory import local_memory

async def load_kb():
    """
    Carrega arquivos .md da Knowledge Base Obsidian para memória local do JARVIS.
    """
    kb_path = getattr(settings, 'jarvis_kb_path', '').strip()
    vault_root = getattr(settings, 'jarvis_vault_root', '').strip()

    if not kb_path and vault_root:
        # Tenta o segundo cérebro consolidado (nova estrutura)
        fallback_jarvis = os.path.join(vault_root, "JARVIS")
        fallback_old_kb = os.path.join(vault_root, "Projetos", "Privados", "PROJECT_JARVIS_5.0-KnowledgeBase")
        if os.path.isdir(fallback_jarvis):
            kb_path = fallback_jarvis
            logger.info(f"[KB] Usando segundo cérebro JARVIS/: {kb_path}")
        elif os.path.isdir(fallback_old_kb):
            kb_path = fallback_old_kb
            logger.info(f"[KB] Usando fallback KB antiga: {kb_path}")

    if not kb_path or not os.path.exists(kb_path):
        logger.warning(f"[KB] Caminho inválido: {kb_path}. Pulando.")
        return 0

    logger.info(f"[KB] Carregando de: {kb_path}")

    pattern = os.path.join(kb_path, "**", "*.md")
    md_files = glob.glob(pattern, recursive=True)

    loaded = 0
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            # Remove frontmatter mas mantem títulos (importantes para contexto)
            content = re.sub(r'^---\n[\s\S]*?\n---\n?', '', content, flags=re.MULTILINE)
            # content = re.sub(r'^#{1,6} .*', '', content, flags=re.MULTILINE | re.I) # REMOVIDO: Títulos são úteis
            content = re.sub(r'\n\s*\n', '\n', content)  # Limpa linhas vazias excessivas

            # Aumentado de 450 para 10000 para dar contexto real à IA (RAG de verdade)
            content_cleaned = ' '.join(content.split())[:10000] 

            if len(content_cleaned) > 20: 
                file_name = Path(file_path).stem[:50]
                tag = "jarvis_kb"
                if "Memorias" in file_path: tag = "jarvis_memory"
                
                fact = f"[KB/{file_name}]: {content_cleaned}"
                if local_memory.save_fact(tag, fact):
                    loaded += 1

        except Exception as e:
            logger.debug(f"[KB] Erro em {file_path}: {e}")

    logger.success(f"[KB] {loaded} fatos carregados!")
    return loaded
