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
    Atua como substituto único para mem0.py e vault_memory.py.
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
        # Garante estrutura no Cérebro Interno (Projeto)
        for sub in subs:
            os.makedirs(os.path.join(INTERNAL_BRAIN_DIR, sub), exist_ok=True)
        
        # Garante estrutura no Vault Global (Obsidian)
        if JARVIS_VAULT_DIR and os.path.isdir(JARVIS_VAULT_DIR):
            for sub in subs:
                os.makedirs(os.path.join(JARVIS_VAULT_DIR, sub), exist_ok=True)

    def _slugify(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_]+', '-', text)
        return text[:60]

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

    async def save_session(self, user_id: str, messages: list, summary: str):
        """Salva resumo da sessão no SQLite e nos Diários (Interno + Global)."""
        now = datetime.datetime.now().isoformat()
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        hora_str = datetime.datetime.now().strftime("%H:%M")
        
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO sessions (user_id, summary, msg_count, created_at) VALUES (?,?,?,?)",
                (user_id, summary, len(messages), now)
            )

        # Diário Sincronizado
        entry = f"\n### Sessão — {hora_str}\n- **Resumo:** {summary}\n"
        self._write_to_both(f"Memorias/Diario/{date_str}.md", entry, append=True)
        logger.info(f"[UnifiedMemory] Sessão {date_str} sincronizada nos dois cérebros.")

    async def save_episodic(self, title: str, content: str, project: str = "", importance: str = "MEDIA", keywords: List[str] = []) -> str:
        """Salva uma memória episódica formatada (estilo Obsidian) tanto local quanto global."""
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
        self._write_to_both(rel_path, body, append=False)
        return rel_path

    async def append_diary(self, summary: str, facts_saved: int = 0) -> str:
        """Acrescenta entrada ao diário diário."""
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        hora_str = now.strftime("%H:%M")
        rel_path = f"Memorias/Diario/{date_str}.md"
        
        entry = f"\n### Sessão — {hora_str}\n- **Resumo:** {summary}\n- **Fatos novos:** {facts_saved}\n"
        self._write_to_both(rel_path, entry, append=True)
        return rel_path

    async def save_learning(self, fact: str, category: str = "tecnico") -> bool:
        """Registra um aprendizado no índice de aprendizado."""
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        rel_path = "Aprendizado/INDEX.md"
        
        entry = f"| {date} | {category} | {fact[:120]} |\n"
        
        # Se o arquivo não existir, cria com cabeçalho
        path_local = os.path.join(INTERNAL_BRAIN_DIR, rel_path)
        if not os.path.exists(path_local):
            header = "# 🎓 Índice de Aprendizado\n\n| Data | Categoria | Fato |\n|---|---|---|\n"
            self._write_to_both(rel_path, header, append=False)
            
        self._write_to_both(rel_path, entry, append=True)
        return True

    async def update_current_state(self, project: str, done: str, next_action: str, notes: str = ""):
        """Atualiza o arquivo de estado atual do sistema."""
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
        self._write_to_both(rel_path, body, append=False)
        return rel_path

    # --- LEITURA E BUSCA ---

    async def get_all(self, user_id: str = "Chefe") -> List[Dict[str, Any]]:
        """Retorna todos os fatos do SQLite (compatível com o antigo mem0.py)."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT content as memory, updated_at FROM memories WHERE user_id = ? ORDER BY updated_at DESC", 
                (user_id,)
            ).fetchall()
            return [dict(r) for r in rows]

    async def get_context(self, user_id: str, query: str = None, limit: int = 15) -> str:
        """Busca o contexto unificado para injeção no prompt da IA."""
        memories = []
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
        """Busca semântica aprimorada em ambos os vaults de markdown."""
        sources = [INTERNAL_BRAIN_DIR]
        if JARVIS_VAULT_DIR and os.path.isdir(JARVIS_VAULT_DIR):
            sources.append(JARVIS_VAULT_DIR)
            
        all_files = []
        for src in sources:
            all_files.extend(glob.glob(os.path.join(src, "**", "*.md"), recursive=True))
        
        # Remove duplicatas baseadas no nome do arquivo
        unique_files = {os.path.basename(f): f for f in all_files}
        
        results = []
        if not query:
            # Se não houver query, pega as 3 notas mais recentes
            latest = sorted(unique_files.values(), key=os.path.getmtime, reverse=True)[:3]
            for f in latest:
                try:
                    c = Path(f).read_text(encoding="utf-8", errors='ignore')
                    results.append(f"[{os.path.basename(f)}]: {c[:500]}")
                except: continue
        else:
            # Busca por relevância (contagem de palavras encontradas)
            query_words = set(re.findall(r'\w+', query.lower()))
            matches = []
            
            for f_path in unique_files.values():
                try:
                    content = Path(f_path).read_text(encoding='utf-8', errors='ignore').lower()
                    score = sum(1 for word in query_words if word in content)
                    if score > 0:
                        matches.append((score, f_path))
                except: continue
            
            # Ordena por score e pega os 3 melhores
            matches.sort(key=lambda x: x[0], reverse=True)
            for score, f_path in matches[:3]:
                try:
                    c = Path(f_path).read_text(encoding="utf-8", errors='ignore')
                    results.append(f"[{os.path.basename(f_path)}]: {c[:700]}")
                except: continue
                
        return "\n\n".join(results)

    def is_vault_available(self) -> bool:
        return JARVIS_VAULT_DIR is not None and os.path.isdir(JARVIS_VAULT_DIR)

    def get_stats(self) -> dict:
        """Retorna estatísticas rápidas do ecossistema de memória."""
        stats = {
            "available": self.is_vault_available(),
            "internal_brain_path": INTERNAL_BRAIN_DIR,
            "vault_path": JARVIS_VAULT_DIR
        }
        
        # Conta arquivos em subpastas
        subs = ["Memorias/Episodicas", "Memorias/Diario", "Aprendizado"]
        for sub in subs:
            path = os.path.join(INTERNAL_BRAIN_DIR, sub)
            files = glob.glob(os.path.join(path, "*.md"))
            stats[sub.split("/")[-1].lower()] = len(files)
            
        with self._conn() as conn:
            row = conn.execute("SELECT COUNT(*) as count FROM memories").fetchone()
            stats["sqlite_facts"] = row["count"]
            
        return stats

# Singleton global para o sistema
memory = UnifiedMemory()
