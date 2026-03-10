"""
JARVIS Local Memory — SQLite-based, lightweight, complete.

Design goals:
- Zero external dependencies (sqlite3 is built-in Python).
- Small storage: facts are short strings (≤ 500 chars). 1000 facts ≈ 500 KB.
- Deduplication: before inserting, check for exact or near-duplicate content.
- Categories: preference | event | task | fact | code | personality | other
- Auto-cleanup: removes duplicates and entries older than MAX_DAYS if total > MAX_ENTRIES.
- Hybrid: works alongside cloud memory (mem0/Mem0), local is the fast/offline layer.
"""

import sqlite3
import os
import datetime
import re
from loguru import logger

# ── Config ──────────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "jarvis_local.db")
MAX_ENTRIES = 2000      # per user
MAX_DAYS = 365          # clean entries older than this if over limit
MAX_CONTENT_LEN = 500   # chars per memory entry
MIN_CONTENT_LEN = 8     # ignore trivial entries shorter than this
SIMILARITY_THRESHOLD = 0.6  # word overlap ratio to consider duplicate

# Texts that should NEVER be stored as memories (system prompts, instructions etc.)
_BLOCKLIST_PATTERNS = [
    r"Apresente-se brevemente",
    r"#Tarefa\b",
    r"Forneça assistência usando as ferramentas",
    r"Use o contexto do chat",
    r"SESSION_INSTRUCTION",
    r"AGENT_INSTRUCTION",
]

CATEGORIES = {
    "preference": ["gosto", "prefiro", "favorito", "odeio", "adoro", "curto", "não gosto", "música", "cor", "comida", "time"],
    "event": ["reunião", "ontem", "hoje", "amanhã", "semana", "aconteceu", "foi", "fiz", "fui"],
    "task": ["fazer", "criar", "implementar", "corrigir", "bug", "feature", "tarefa", "pendente"],
    "code": ["código", "função", "arquivo", "classe", "erro", "exception", "python", "javascript", "api"],
    "personality": ["me chamo", "meu nome", "sou", "trabalho", "projeto", "empresa"],
}


def _is_blocked(text: str) -> bool:
    for pattern in _BLOCKLIST_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def _categorize(text: str) -> str:
    text_lower = text.lower()
    for cat, keywords in CATEGORIES.items():
        if any(kw in text_lower for kw in keywords):
            return cat
    return "fact"


def _word_overlap(a: str, b: str) -> float:
    """Simple Jaccard similarity on word sets."""
    wa = set(re.findall(r'\w+', a.lower()))
    wb = set(re.findall(r'\w+', b.lower()))
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


def _truncate(text: str) -> str:
    text = text.strip()
    if len(text) > MAX_CONTENT_LEN:
        # Keep the first MAX_CONTENT_LEN chars, ending at a word boundary
        text = text[:MAX_CONTENT_LEN].rsplit(" ", 1)[0] + "…"
    return text


class LocalMemory:
    """Thread-safe SQLite memory store for JARVIS."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        # WAL mode: faster writes, safe concurrent reads
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
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
                CREATE INDEX IF NOT EXISTS idx_category ON memories(user_id, category);

                CREATE TABLE IF NOT EXISTS sessions (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id       TEXT NOT NULL,
                    summary       TEXT,
                    msg_count     INTEGER DEFAULT 0,
                    created_at    TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_session_user ON sessions(user_id);
            """)
        logger.info(f"[LocalMemory] DB inicializado em: {self.db_path}")

    # ── Write ───────────────────────────────────────────────────────────────

    def add_memory(self, user_id: str, content: str, source: str = "conversation") -> bool:
        """
        Insert a new memory fact. Returns True if actually inserted (not a duplicate).
        """
        content = _truncate(content)

        if len(content) < MIN_CONTENT_LEN:
            return False
        if _is_blocked(content):
            logger.debug(f"[LocalMemory] Bloqueado (instrução de sistema): {content[:60]}")
            return False

        category = _categorize(content)
        now = datetime.datetime.now().isoformat()

        # Check for duplicates
        with self._conn() as conn:
            existing = conn.execute(
                "SELECT id, content FROM memories WHERE user_id = ? ORDER BY updated_at DESC LIMIT 200",
                (user_id,)
            ).fetchall()

            for row in existing:
                if _word_overlap(content, row["content"]) >= SIMILARITY_THRESHOLD:
                    # Update timestamp so it stays "fresh" instead of inserting duplicate
                    conn.execute(
                        "UPDATE memories SET updated_at=?, access_count=access_count+1 WHERE id=?",
                        (now, row["id"])
                    )
                    logger.debug(f"[LocalMemory] Dedup: memória similar já existe (id={row['id']})")
                    return False

            conn.execute(
                "INSERT INTO memories (user_id, category, content, source, created_at, updated_at) VALUES (?,?,?,?,?,?)",
                (user_id, category, content, source, now, now)
            )
            logger.success(f"[LocalMemory] Novo fato [{category}] salvo para {user_id}: {content[:60]}")
            return True

    def add_session(self, user_id: str, messages: list[dict]) -> str:
        """
        Save conversation messages as individual memory facts (user and assistant turns).
        Also saves a compact session record. Returns summary string.
        Filters out system prompts and short/trivial messages.
        """
        saved = 0
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "").strip()
            if not content or role not in ("user", "assistant"):
                continue
            if _is_blocked(content):
                continue
            # For raw conversation turns, only save user messages as facts
            # (assistant responses are usually instructions, not facts about the user)
            if role == "user" and len(content) >= MIN_CONTENT_LEN:
                if self.add_memory(user_id, content, source="user_turn"):
                    saved += 1

        now = datetime.datetime.now().isoformat()
        summary = f"{len(messages)} mensagens processadas, {saved} fatos novos salvos."
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO sessions (user_id, summary, msg_count, created_at) VALUES (?,?,?,?)",
                (user_id, summary, len(messages), now)
            )

        self._auto_cleanup(user_id)
        logger.info(f"[LocalMemory] Sessão salva para {user_id}: {summary}")
        return summary

    def save_fact(self, user_id: str, fact: str) -> bool:
        """Explicitly save a single fact string (called by agent tool)."""
        return self.add_memory(user_id, fact, source="explicit")

    # ── Read ────────────────────────────────────────────────────────────────

    def get_all(self, user_id: str, limit: int = 100) -> list[dict]:
        """Return most recent/relevant memories."""
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT category, content, updated_at FROM memories
                   WHERE user_id = ?
                   ORDER BY access_count DESC, updated_at DESC
                   LIMIT ?""",
                (user_id, limit)
            ).fetchall()
        return [{"memory": r["content"], "category": r["category"], "updated_at": r["updated_at"]} for r in rows]

    def search(self, user_id: str, query: str, limit: int = 20) -> list[dict]:
        """Keyword search over memories."""
        words = re.findall(r'\w+', query.lower())
        if not words:
            return self.get_all(user_id, limit=limit)

        with self._conn() as conn:
            results = []
            all_rows = conn.execute(
                "SELECT category, content, updated_at FROM memories WHERE user_id = ? ORDER BY updated_at DESC",
                (user_id,)
            ).fetchall()

            scored = []
            for row in all_rows:
                score = sum(1 for w in words if w in row["content"].lower())
                if score > 0:
                    scored.append((score, row))

            scored.sort(key=lambda x: x[0], reverse=True)
            results = [
                {"memory": r["content"], "category": r["category"], "updated_at": r["updated_at"]}
                for _, r in scored[:limit]
            ]
        return results

    def get_stats(self, user_id: str) -> dict:
        with self._conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM memories WHERE user_id=?", (user_id,)).fetchone()[0]
            by_cat = conn.execute(
                "SELECT category, COUNT(*) as c FROM memories WHERE user_id=? GROUP BY category",
                (user_id,)
            ).fetchall()
            sessions = conn.execute("SELECT COUNT(*) FROM sessions WHERE user_id=?", (user_id,)).fetchone()[0]
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        return {
            "total_memories": total,
            "sessions": sessions,
            "by_category": {r["category"]: r["c"] for r in by_cat},
            "db_size_kb": round(db_size / 1024, 1)
        }

    # ── Cleanup ─────────────────────────────────────────────────────────────

    def _auto_cleanup(self, user_id: str):
        """Remove oldest entries if above MAX_ENTRIES. Keeps storage small."""
        with self._conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM memories WHERE user_id=?", (user_id,)).fetchone()[0]
            if total > MAX_ENTRIES:
                cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=MAX_DAYS)).isoformat()
                deleted = conn.execute(
                    """DELETE FROM memories WHERE user_id=? AND updated_at < ?
                       AND id NOT IN (
                           SELECT id FROM memories WHERE user_id=? ORDER BY access_count DESC, updated_at DESC LIMIT ?
                       )""",
                    (user_id, cutoff_date, user_id, MAX_ENTRIES)
                ).rowcount
                if deleted:
                    conn.execute("VACUUM")
                    logger.info(f"[LocalMemory] Cleanup: {deleted} entradas antigas removidas para {user_id}.")

    def clear_user(self, user_id: str):
        """Remove all memories for a user (use with care)."""
        with self._conn() as conn:
            conn.execute("DELETE FROM memories WHERE user_id=?", (user_id,))
            conn.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
        logger.warning(f"[LocalMemory] Memória local de '{user_id}' apagada.")


# Singleton
local_memory = LocalMemory()
