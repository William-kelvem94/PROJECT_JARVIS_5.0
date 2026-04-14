import os
import sqlite3
import datetime
import re
import glob
from pathlib import Path
from loguru import logger
from .config import settings

# --- CONFIGURAÇÃO ---
# --- CONFIGURAÇÃO ---
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "jarvis_local.db")
INTERNAL_BRAIN_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "internal_brain")
VAULT_ROOT = os.getenv("JARVIS_VAULT_ROOT", r"C:\Users\willi\Documents\GitHub\Will-obsidian") # Fallback para o path que você me passou
JARVIS_VAULT_DIR = os.path.join(VAULT_ROOT, "JARVIS") if VAULT_ROOT and os.path.isdir(VAULT_ROOT) else None

class UnifiedMemory:
    """
    O Cérebro de Memória Unificado do JARVIS 5.0.
    Consolida SQLite (fatos rápidos), Cérebro Interno (Markdown local) e Obsidian (Vault Global).
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        os.makedirs(INTERNAL_BRAIN_DIR, exist_ok=True)
        self._init_db()
        self._ensure_vault_dirs()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self):
        with self._conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS memories (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id     TEXT    NOT NULL,
                    category    TEXT    NOT NULL DEFAULT 'fact',
                    content     TEXT    NOT NULL,
                    source      TEXT    DEFAULT 'conversation',
                    created_at  TEXT    NOT NULL,
                    updated_at  TEXT    NOT NULL,
                    access_count INTEGER DEFAULT 0
                );
                CREATE INDEX IF NOT EXISTS idx_user ON memories(user_id);
                
                CREATE TABLE IF NOT EXISTS sessions (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id       TEXT NOT NULL,
                    summary       TEXT,
                    msg_count     INTEGER DEFAULT 0,
                    created_at    TEXT NOT NULL
                );
            """)
        logger.info(f"[UnifiedMemory] Banco SQLite e Cérebro Interno operacional.")

    def _ensure_vault_dirs(self):
        subs = ["Memorias/Episodicas", "Memorias/Diario", "Aprendizado", "Contexto-Atual"]
        # Garante estrutura no Cérebro Interno (Projeto)
        for sub in subs:
            os.makedirs(os.path.join(INTERNAL_BRAIN_DIR, sub), exist_ok=True)
        
        # Garante estrutura no Vault Global (Obsidian)
        if os.path.isdir(JARVIS_VAULT_DIR):
            for sub in subs:
                os.makedirs(os.path.join(JARVIS_VAULT_DIR, sub), exist_ok=True)

    # --- ESCRITA SINCRONIZADA ---

    async def add_memory(self, user_id: str, content: str, category: str = "fact", source: str = "conversation"):
        """Salva fato no SQLite e cria entrada em Markdown tanto no Interno quanto no Global."""
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

        # Espelhamento em Markdown (Memo)
        memo_entry = f"\n- [{now}] ({category}): {content}"
        self._write_to_both("Memorias/fatos_rapidos.md", memo_entry, append=True)
        
        logger.debug(f"[UnifiedMemory] Fato sincronizado: {content[:50]}...")
        return True

    def _write_to_both(self, rel_path: str, content: str, append: bool = False):
        """Helper para escrever no cérebro interno e no global simultaneamente."""
        paths = [os.path.join(INTERNAL_BRAIN_DIR, rel_path)]
        if os.path.isdir(JARVIS_VAULT_DIR):
            paths.append(os.path.join(JARVIS_VAULT_DIR, rel_path))
            
        for p in paths:
            try:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                mode = 'a' if append else 'w'
                with open(p, mode, encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                logger.error(f"Erro na sincronização de memória em {p}: {e}")

    async def save_session(self, user_id: str, messages: list, summary: str):
        """Salva resumo da sessão no SQLite e nos Diários (Interno + Global)."""
        now = datetime.datetime.now().isoformat()
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO sessions (user_id, summary, msg_count, created_at) VALUES (?,?,?,?)",
                (user_id, summary, len(messages), now)
            )

        # Diário Sincronizado
        entry = f"\n### Sessão {datetime.datetime.now().strftime('%H:%M')}\n- {summary}\n"
        self._write_to_both(f"Memorias/Diario/{date_str}.md", entry, append=True)
        logger.info(f"[UnifiedMemory] Sessão {date_str} sincronizada nos dois cérebros.")

    # --- LEITURA ---

    async def get_context(self, user_id: str, query: str = None, limit: int = 15) -> str:
        """Busca o contexto unificado."""
        memories = []
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT content FROM memories WHERE user_id = ? ORDER BY access_count DESC, updated_at DESC LIMIT ?",
                (user_id, limit)
            ).fetchall()
            memories = [r["content"] for r in rows]

        # Busca na KB (Markdown) - Prioriza a Global, mas olha a Interna também
        kb_context = await self._search_kb(query if query else "")
        
        context_str = ""
        if memories:
            context_str += "[MEMORIA LOCAL (FATOS RECENTES)]:\n"
            context_str += "\n".join([f"- {m}" for m in memories])
            
        if kb_context:
            context_str += "\n\n[CONHECIMENTO GLOBAL (OBSIDIAN)]:\n" + kb_context
            
        return context_str if context_str else "Nenhum contexto relevante encontrado."

    async def _search_kb(self, query: str) -> str:
        """Busca em ambos os vaults de markdown."""
        sources = [INTERNAL_BRAIN_DIR]
        if os.path.isdir(JARVIS_VAULT_DIR):
            sources.append(JARVIS_VAULT_DIR)
            
        all_files = []
        for src in sources:
            all_files.extend(glob.glob(os.path.join(src, "**/*.md"), recursive=True))
        
        # Deduplicação por nome de arquivo (já que são espelhos)
        unique_files = {os.path.basename(f): f for f in all_files}.values()
        
        # Busca simples
        files = []
        if query:
            words = query.lower().split()
            for f in list(unique_files)[:40]:
                try:
                    t = Path(f).read_text(encoding='utf-8').lower()
                    if any(w in t for w in words): files.append(f)
                except: continue
            files = files[:3]
        else:
            files = sorted(unique_files, key=os.path.getmtime, reverse=True)[:3]
            
        results = []
        for f in files:
            try:
                c = Path(f).read_text(encoding="utf-8")
                clean = re.sub(r'#+\s+', '', c)[:500]
                results.append(f"[{os.path.basename(f)}]: {clean}")
            except: continue
        return "\n".join(results)

# Singleton
memory = UnifiedMemory()
