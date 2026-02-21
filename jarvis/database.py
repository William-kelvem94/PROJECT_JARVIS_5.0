# -*- coding: utf-8 -*-
import sqlite3
import json
import time
from pathlib import Path
from typing import List, Dict, Any

class DatabaseRepository:
    def __init__(self, db_path: str = "data/jarvis_brain.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            # Tabela de Interações
            conn.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts REAL,
                    user_text TEXT,
                    assistant_text TEXT,
                    system_flag INTEGER
                )
            """)
            # Tabela de Conhecimento (RAG/Research)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT UNIQUE,
                    content TEXT,
                    source TEXT,
                    category TEXT,
                    last_updated REAL
                )
            """)
            conn.commit()

    def add_interaction(self, user: str, assistant: str, system: bool = False):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO interactions (ts, user_text, assistant_text, system_flag) VALUES (?, ?, ?, ?)",
                (time.time(), user, assistant, 1 if system else 0)
            )

    def add_knowledge(self, topic: str, content: str, source: str = "research", category: str = "general"):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO knowledge (topic, content, source, category, last_updated) 
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(topic) DO UPDATE SET 
                    content=excluded.content, 
                    last_updated=excluded.last_updated
            """, (topic, content, source, category, time.time()))

    def query_interactions(self, limit: int = 50) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM interactions ORDER BY ts DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_knowledge_graph_data(self) -> Dict[str, Any]:
        """Retorna dados REAIS para visualização de grafos baseados no banco."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            # Buscar nós
            nodes_cursor = conn.execute("SELECT topic, category FROM knowledge")
            nodes = [{"id": row["topic"], "group": row["category"]} for row in nodes_cursor.fetchall() if row["topic"]]
            
            # Buscar links (Simplificado: conecta tópicos da mesma categoria)
            links = []
            if nodes:
                categories = {}
                for n in nodes:
                    cat = n["group"]
                    if cat not in categories: categories[cat] = []
                    categories[cat].append(n["id"])
                
                for cat, topics in categories.items():
                    # Conectar o primeiro da categoria aos outros (estrela)
                    if len(topics) > 1:
                        root = topics[0]
                        for other in topics[1:]:
                            links.append({"source": root, "target": other, "value": 1})

            return {"nodes": nodes, "links": links}

    def clear_knowledge(self):
        """Apaga todos os registros de conhecimento minerado."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM knowledge")
            conn.commit()

# Singleton
db = DatabaseRepository()
