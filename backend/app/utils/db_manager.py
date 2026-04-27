import os
import sqlite3
from loguru import logger
from threading import Lock

class DBManager:
    _instance = None
    _lock = Lock()

    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "jarvis_local.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = DBManager()
        return cls._instance

    def get_connection(self) -> sqlite3.Connection:
        """
        Retorna uma conexão configurada com WAL para melhor concorrência.
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def _get_conn(self) -> sqlite3.Connection:
        return self.get_connection()

    def save_telemetry(self, cpu_usage: float, ram_usage: float) -> None:
        status = "warning" if ram_usage > 85 else "success"
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO telemetry (cpu_usage, ram_usage, status, timestamp) VALUES (?, ?, ?, ?)",
                (cpu_usage, ram_usage, status, __import__('datetime').datetime.now().isoformat()),
            )
            conn.commit()

    def _init_db(self):
        """
        Inicializa as tabelas se não existirem.
        """
        with self.get_connection() as conn:
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

                CREATE TABLE IF NOT EXISTS telemetry (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpu_usage   REAL,
                    ram_usage   REAL,
                    status      TEXT,
                    timestamp   TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_telemetry_time ON telemetry(timestamp);
            """)
        logger.info("[DBManager] Banco de dados inicializado.")

db_manager = DBManager.get_instance()
