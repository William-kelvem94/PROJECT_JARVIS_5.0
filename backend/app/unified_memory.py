import os
import sqlite3
import datetime
import re
import glob
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger
from dotenv import load_dotenv
try:
    import chromadb
except Exception:
    chromadb = None
try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

from .utils.db_manager import db_manager

# --- CONFIGURAÇÃO ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

INTERNAL_BRAIN_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "internal_brain")
CHROMA_DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chroma_db")
VAULT_ROOT = os.getenv("JARVIS_VAULT_ROOT")
JARVIS_VAULT_DIR = os.path.join(VAULT_ROOT, "JARVIS") if VAULT_ROOT and os.path.isdir(VAULT_ROOT) else None

if not VAULT_ROOT:
    logger.warning("[UnifiedMemory] JARVIS_VAULT_ROOT não definida (ou inválida). Vault Global (Obsidian) desativado.")

class UnifiedMemory:
    """
    O Cérebro de Memória Unificado do JARVIS 5.0 com Semantic RAG.
    Consolida SQLite (fatos), Markdown (estrutura) e ChromaDB (Busca Semântica).
    """

    def __init__(self):
        os.makedirs(INTERNAL_BRAIN_DIR, exist_ok=True)
        os.makedirs(CHROMA_DB_DIR, exist_ok=True)
        self._ensure_vault_dirs()

        # Initialize Embedding Model
        self.model = None
        self.chroma_client = None
        self.collection = None
        if chromadb is not None and SentenceTransformer is not None:
            logger.info("[UnifiedMemory] Carregando modelo de embeddings...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
            self.collection = self.chroma_client.get_or_create_collection(name="jarvis_memories")
            logger.info("[UnifiedMemory] Sistema de Memória Semântica inicializado.")
        else:
            logger.warning("[UnifiedMemory] ChromaDB/SentenceTransformer indisponíveis. Busca semântica desativada.")

    def _conn(self) -> sqlite3.Connection:
        return db_manager.get_connection()

    def _ensure_vault_dirs(self):
        subs = [
            "Memorias/Episodicas",
            "Memorias/Diario",
            "Aprendizado",
            "Decisoes",
            "Contexto-Atual",
            "Sobre-Will"
        ]
        for sub in subs:
            os.makedirs(os.path.join(INTERNAL_BRAIN_DIR, sub), exist_ok=True)

        if JARVIS_VAULT_DIR and os.path.isdir(JARVIS_VAULT_DIR):
            for sub in subs:
                os.makedirs(os.path.join(JARVIS_VAULT_DIR, sub), exist_ok=True)

    def _slugify(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_]+', '-', text)
        return text[:60]

    async def _write_to_both_async(self, rel_path: str, content: str, append: bool = False):
        """Executa a escrita de arquivos em threads separadas para não bloquear o event loop."""
        def sync_write():
            paths = [os.path.join(INTERNAL_BRAIN_DIR, rel_path)]
            if JARVIS_VAULT_DIR and os.path.isdir(JARVIS_VAULT_DIR):
                paths.append(os.path.join(JARVIS_VAULT_DIR, rel_path))

            for p in paths:
                try:
                    os.makedirs(os.path.dirname(p), exist_ok=True)
                    mode = 'a' if append else 'w'
                    with open(p, mode, encoding='utf-8') as f:
                        f.write(content)
                except Exception as e:
                    logger.error(f"Erro na sincronização de memória em {p}: {e}")

        await asyncio.to_thread(sync_write)

    async def _index_semantic_memory(self, content: str, metadata: Dict[str, Any]):
        """Vetoriza e armazena a memória no ChromaDB."""
        if self.model is None or self.collection is None:
            return
        def sync_index():
            try:
                embedding = self.model.encode(content).tolist()
                # Generate a unique ID based on content hash or timestamp
                mem_id = f"{metadata.get('user_id', 'default')}_{datetime.datetime.now().timestamp()}"
                self.collection.add(
                    embeddings=[embedding],
                    documents=[content],
                    metadatas=[metadata],
                    ids=[mem_id]
                )
            except Exception as e:
                logger.error(f"Erro ao indexar memória semântica: {e}")

        await asyncio.to_thread(sync_index)

    async def add_memory(self, user_id: str, content: str, category: str = "fact", source: str = "conversation"):
        now = datetime.datetime.now().isoformat()

        with self._conn() as conn:
            existing = conn.execute(
                "SELECT id FROM memories WHERE user_id = ? AND content = ?", (user_id, content)
            ).fetchone()

            if existing:
                conn.execute("UPDATE memories SET updated_at=?, access_count=access_count+1 WHERE id=?", (now, existing["id"]))
                return False

            conn.execute(
                "INSERT INTO memories (user_id, category, content, source, created_at, updated_at) VALUES (?,?,?,?,?,?)",
                (user_id, category, content, source, now, now)
            )

        # Semantic Indexing Hook
        await self._index_semantic_memory(content, {"user_id": user_id, "category": category, "source": source})

        memo_entry = f"\n- [{now}] ({category}): {content}"
        await self._write_to_both_async("Memorias/fatos_rapidos.md", memo_entry, append=True)

        logger.debug(f"[UnifiedMemory] Fato sincronizado e vetorizado: {content[:50]}...")
        return True

    async def save_session(self, user_id: str, messages: list, summary: str):
        now = datetime.datetime.now().isoformat()
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        hora_str = datetime.datetime.now().strftime("%H:%M")

        with self._conn() as conn:
            conn.execute(
                "INSERT INTO sessions (user_id, summary, msg_count, created_at) VALUES (?,?,?,?)",
                (user_id, summary, len(messages), now)
            )

        # Vectorize the session summary
        await self._index_semantic_memory(f"Session Summary: {summary}", {"user_id": user_id, "category": "session_summary"})

        entry = f"\n### Sessão — {hora_str}\n- **Resumo:** {summary}\n"
        await self._write_to_both_async(f"Memorias/Diario/{date_str}.md", entry, append=True)
        logger.info(f"[UnifiedMemory] Sessão {date_str} sincronizada nos dois cérebros.")

    async def save_episodic(self, title: str, content: str, project: str = "", importance: str = "MEDIA", keywords: List[str] = []) -> str:
        now_dt = datetime.datetime.now()
        date = now_dt.strftime("%Y-%m-%d")
        hora = now_dt.strftime("%H:%M")
        slug = self._slugify(title)
        filename = f"{date}-{slug}.md"
        rel_path = os.path.join("Memorias", "Episodicas", filename)

        tags_str = ", ".join(["jarvis", "memoria", "episodica"] + keywords)

        body = f"""---
title: "{title}"
date: "{date}"
hora: "{hora}"
tags: [{tags_str}]
importancia: "{importance}"
projeto: "{project}"
---

# {title}

## 📝 Conteúdo
{content}

---
*Salvo via UnifiedMemory em: {date} {hora}*
"""
        await self._write_to_both_async(rel_path, body, append=False)

        # Vectorize episodic memory
        await self._index_semantic_memory(f"{title}: {content}", {"category": "episodic", "project": project, "importance": importance})

        return rel_path

    async def append_diary(self, summary: str, facts_saved: int = 0) -> str:
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        hora_str = now.strftime("%H:%M")
        rel_path = f"Memorias/Diario/{date_str}.md"

        entry = f"\n### Sessão — {hora_str}\n- **Resumo:** {summary}\n- **Fatos novos:** {facts_saved}\n"
        await self._write_to_both_async(rel_path, entry, append=True)
        return rel_path

    async def save_learning(self, fact: str, category: str = "tecnico") -> bool:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        rel_path = "Aprendizado/INDEX.md"
        entry = f"| {date} | {category} | {fact[:120]} |\n"

        def check_and_write():
            path_local = os.path.join(INTERNAL_BRAIN_DIR, rel_path)
            if not os.path.exists(path_local):
                header = "# 🎓 Índice de Aprendizado\n\n| Data | Categoria | Fato |\n|---|---|---|\n"
                self._sync_write_helper(rel_path, header, append=False)
            self._sync_write_helper(rel_path, entry, append=True)

        await asyncio.to_thread(check_and_write)
        # Vectorize learning fact
        await self._index_semantic_memory(fact, {"category": "learning", "learning_category": category})
        return True

    def _sync_write_helper(self, rel_path: str, content: str, append: bool = False):
        """Versão síncrona para uso interno em threads."""
        paths = [os.path.join(INTERNAL_BRAIN_DIR, rel_path)]
        if JARVIS_VAULT_DIR and os.path.isdir(JARVIS_VAULT_DIR):
            paths.append(os.path.join(JARVIS_VAULT_DIR, rel_path))
        for p in paths:
            try:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                mode = 'a' if append else 'w'
                with open(p, mode, encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                logger.error(f"Erro na sincronização de memória em {p}: {e}")

    async def update_current_state(self, project: str, done: str, next_action: str, notes: str = ""):
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        hora = datetime.datetime.now().strftime("%H:%M")
        rel_path = "Contexto-Atual/Estado.md"

        body = f"""---
title: "Estado Atual — Jarvis"
updated: {date} {hora}
---

# 🚀 Estado Atual

- **Data:** {date} às {hora}
- **Projeto em foco:** {project}
- **O que foi feito:** {done}
- **Próxima ação:** {next_action}

## 📝 Notas
{notes}
"""
        await self._write_to_both_async(rel_path, body, append=False)
        return rel_path

    async def get_all(self, user_id: str = "Chefe") -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT content as memory, updated_at FROM memories WHERE user_id = ? ORDER BY updated_at DESC",
                (user_id,)
            ).fetchall()
            return [dict(r) for r in rows]

    async def get_context(self, user_id: str, query: str = None, limit: int = 15) -> str:
        # 1. Get recent facts from SQLite
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT content FROM memories WHERE user_id = ? ORDER BY access_count DESC, updated_at DESC LIMIT ?",
                (user_id, limit)
            ).fetchall()
            memories = [r["content"] for r in rows]

        # 2. Semantic Search in ChromaDB
        semantic_context = await self._search_semantic(query, user_id)

        context_str = ""
        if memories:
            context_str += "[MEMORIA LOCAL (FATOS RECENTES)]:\n"
            context_str += "\n".join([f"- {m}" for m in memories])

        if semantic_context:
            context_str += "\n\n[CONHECIMENTO SEMÂNTICO (VETORIZADO)]:\n" + semantic_context

        return context_str if context_str else "Nenhum contexto relevante encontrado."

    async def _search_semantic(self, query: str, user_id: str) -> str:
        if not query or self.model is None or self.collection is None:
            return ""

        def sync_search():
            try:
                query_embedding = self.model.encode(query).tolist()
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=5,
                    where={"user_id": user_id} if user_id != "Chefe" else None
                )

                documents = results.get("documents", [[]])[0]
                if not documents:
                    return ""

                return "\n".join([f"- {doc}" for doc in documents])
            except Exception as e:
                logger.error(f"Erro na busca semântica: {e}")
                return ""

        return await asyncio.to_thread(sync_search)

    def is_vault_available(self) -> bool:
        return JARVIS_VAULT_DIR is not None and os.path.isdir(JARVIS_VAULT_DIR)

    def get_stats(self) -> dict:
        stats = {
            "available": self.is_vault_available(),
            "internal_brain_path": INTERNAL_BRAIN_DIR,
            "vault_path": JARVIS_VAULT_DIR
        }
        subs = ["Memorias/Episodicas", "Memorias/Diario", "Aprendizado"]
        for sub in subs:
            path = os.path.join(INTERNAL_BRAIN_DIR, sub)
            files = glob.glob(os.path.join(path, "*.md"))
            stats[sub.split("/")[-1].lower()] = len(files)

        with self._conn() as conn:
            row = conn.execute("SELECT COUNT(*) as count FROM memories").fetchone()
            stats["sqlite_facts"] = row["count"]

        # Add ChromaDB stats
        try:
            stats["semantic_memories"] = self.collection.count()
        except:
            stats["semantic_memories"] = 0

        return stats

memory = UnifiedMemory()
