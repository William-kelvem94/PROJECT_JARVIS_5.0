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
from .utils.db_manager import db_manager

# --- CONFIGURAÇÃO ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

INTERNAL_BRAIN_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "internal_brain")
VAULT_ROOT = os.getenv("JARVIS_VAULT_ROOT")
JARVIS_VAULT_DIR = os.path.join(VAULT_ROOT, "JARVIS") if VAULT_ROOT and os.path.isdir(VAULT_ROOT) else None

if not VAULT_ROOT:
    logger.warning("[UnifiedMemory] JARVIS_VAULT_ROOT não definida (ou inválida). Vault Global (Obsidian) desativado.")

class UnifiedMemory:
    """
    O Cérebro de Memória Unificado do JARVIS 5.0.
    Consolida SQLite (fatos rápidos), Cérebro Interno (Markdown local) e Obsidian (Vault Global).
    """

    def __init__(self):
        os.makedirs(INTERNAL_BRAIN_DIR, exist_ok=True)
        self._ensure_vault_dirs()

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

    async def add_memory(self, user_id: str, content: str, category: str = "fact", source: str = "conversation"):
        now = datetime.datetime.now().isoformat()

        # SQLite é rápido, mas podemos envolver em to_thread se o DB crescer muito
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

        memo_entry = f"\n- [{now}] ({category}): {content}"
        await self._write_to_both_async("Memorias/fatos_rapidos.md", memo_entry, append=True)

        logger.debug(f"[UnifiedMemory] Fato sincronizado: {content[:50]}...")
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
                # Nota: _write_to_both_async é async, então fazemos a lógica síncrona aqui
                # e chamamos a escrita via helper síncrono interno ou to_thread.
                # Para simplificar, usamos a lógica de escrita direta no thread.
                self._sync_write_helper(rel_path, header, append=False)
            self._sync_write_helper(rel_path, entry, append=True)

        await asyncio.to_thread(check_and_write)
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

        body = f\"\"\"---
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
\"\"\"
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
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT content FROM memories WHERE user_id = ? ORDER BY access_count DESC, updated_at DESC LIMIT ?",
                (user_id, limit)
            ).fetchall()
            memories = [r["content"] for r in rows]

        kb_context = await self._search_kb(query if query else "")

        context_str = ""
        if memories:
            context_str += "[MEMORIA LOCAL (FATOS RECENTES)]:\n"
            context_str += "\n".join([f"- {m}" for m in memories])

        if kb_context:
            context_str += "\n\n[CONHECIMENTO GLOBAL (OBSIDIAN)]:\n" + kb_context

        return context_str if context_str else "Nenhum contexto relevante encontrado."

    async def _search_kb(self, query: str) -> str:
        def sync_search():
            sources = [INTERNAL_BRAIN_DIR]
            if JARVIS_VAULT_DIR and os.path.isdir(JARVIS_VAULT_DIR):
                sources.append(JARVIS_VAULT_DIR)

            all_files = []
            for src in sources:
                all_files.extend(glob.glob(os.path.join(src, "**", "*.md"), recursive=True))

            unique_files = {os.path.basename(f): f for f in all_files}
            results = []
            if not query:
                latest = sorted(unique_files.values(), key=os.path.getmtime, reverse=True)[:3]
                for f in latest:
                    try:
                        c = Path(f).read_text(encoding="utf-8", errors='ignore')
                        results.append(f"[{os.path.basename(f)}]: {c[:500]}")
                    except: continue
            else:
                query_words = set(re.findall(r'\w+', query.lower()))
                matches = []
                for f_path in unique_files.values():
                    try:
                        content = Path(f_path).read_text(encoding='utf-8', errors='ignore').lower()
                        score = sum(1 for word in query_words if word in content)
                        if score > 0:
                            matches.append((score, f_path))
                    except: continue

                matches.sort(key=lambda x: x[0], reverse=True)
                for score, f_path in matches[:3]:
                    try:
                        c = Path(f_path).read_text(encoding="utf-8", errors='ignore')
                        results.append(f"[{os.path.basename(f_path)}]: {c[:700]}")
                    except: continue
            return "\n\n".join(results)

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

        return stats

memory = UnifiedMemory()
