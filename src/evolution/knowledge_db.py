#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Knowledge Database Manager
=======================================
Gerencia a base de conhecimento para o sistema de auto-correção.
Armazena problemas identificados e soluções aplicadas para aprendizado contínuo.

Responsibilities:
- Inicialização e manutenção do schema do banco SQLite
- CRUD operations para problemas e soluções
- Queries para aprendizado (histórico de soluções bem-sucedidas)
- Gestão de feedback humano

Author: JARVIS 5.0 Evolution Layer
"""

import sqlite3
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Default database path
DEFAULT_DB_PATH = (
    Path(__file__).parent.parent.parent / "data" / "learning" / "knowledge.db"
)


class KnowledgeDatabase:
    """
    Gerenciador da base de conhecimento do sistema de auto-correção.
    """

    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._ensure_directory()
        self._initialize_schema()

    def _ensure_directory(self):
        """Garante que o diretório do banco existe"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _get_connection(self):
        """Context manager para conexões com o banco"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def _initialize_schema(self):
        """Cria as tabelas se não existirem"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Tabela de problemas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS problems (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hash TEXT UNIQUE NOT NULL,
                    module TEXT,
                    description TEXT NOT NULL,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    occurrences INTEGER DEFAULT 1,
                    severity TEXT DEFAULT 'medium',
                    problem_data TEXT
                )
            """)

            # Tabela de soluções
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS solutions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    problem_hash TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    files_modified TEXT,
                    code_diff TEXT,
                    success BOOLEAN NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    impact_score REAL DEFAULT 0.0,
                    execution_time_ms INTEGER,
                    error_message TEXT,
                    FOREIGN KEY(problem_hash) REFERENCES problems(hash)
                )
            """)

            # Human feedback table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS human_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    solution_id INTEGER NOT NULL,
                    -- Feedback types:
                    --   'positive': Solution worked well, improved system
                    --   'negative': Solution caused problems or didn't work
                    --   'ignore': Not applicable or false positive
                    feedback TEXT NOT NULL CHECK(feedback IN ('positive', 'negative', 'ignore')),
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(solution_id) REFERENCES solutions(id)
                )
            """)

            # Índices para otimização
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_problems_hash 
                ON problems(hash)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_problems_module 
                ON problems(module)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_solutions_problem_hash 
                ON solutions(problem_hash)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_solutions_success 
                ON solutions(success)
            """)

            logger.info("✅ Knowledge database schema initialized")

    def record_problem(
        self,
        hash_value: str,
        module: str,
        description: str,
        severity: str = "medium",
        problem_data: Optional[Dict] = None,
    ) -> int:
        """
        Registra um novo problema ou atualiza a contagem se já existir.

        Args:
            hash_value: Hash único do problema
            module: Módulo afetado
            description: Descrição do problema
            severity: Gravidade (low, medium, high, critical)
            problem_data: Dados adicionais do problema em formato dict

        Returns:
            ID do problema no banco
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Verificar se o problema já existe
            cursor.execute(
                "SELECT id, occurrences FROM problems WHERE hash = ?", (hash_value,)
            )
            existing = cursor.fetchone()

            if existing:
                # Atualizar contagem e última ocorrência
                cursor.execute(
                    """
                    UPDATE problems 
                    SET occurrences = occurrences + 1,
                        last_seen = CURRENT_TIMESTAMP
                    WHERE hash = ?
                """,
                    (hash_value,),
                )
                return existing["id"]
            else:
                # Inserir novo problema
                problem_data_json = json.dumps(problem_data) if problem_data else None
                cursor.execute(
                    """
                    INSERT INTO problems (hash, module, description, severity, problem_data)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (hash_value, module, description, severity, problem_data_json),
                )
                return cursor.lastrowid

    def record_solution(
        self,
        problem_hash: str,
        action_type: str,
        description: str,
        success: bool,
        files_modified: Optional[List[str]] = None,
        code_diff: Optional[str] = None,
        impact_score: float = 0.0,
        execution_time_ms: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> int:
        """
        Registra uma tentativa de solução.

        Args:
            problem_hash: Hash do problema relacionado
            action_type: Tipo de ação (code, config, restart, etc.)
            description: Descrição da solução
            success: Se a solução foi bem-sucedida
            files_modified: Lista de arquivos modificados
            code_diff: Diff do código alterado
            impact_score: Impacto da solução na estabilidade (0.0 a 1.0)
            execution_time_ms: Tempo de execução em milissegundos
            error_message: Mensagem de erro se falhou

        Returns:
            ID da solução no banco
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            files_json = json.dumps(files_modified) if files_modified else None

            cursor.execute(
                """
                INSERT INTO solutions (
                    problem_hash, action_type, description, success,
                    files_modified, code_diff, impact_score,
                    execution_time_ms, error_message
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    problem_hash,
                    action_type,
                    description,
                    success,
                    files_json,
                    code_diff,
                    impact_score,
                    execution_time_ms,
                    error_message,
                ),
            )

            return cursor.lastrowid

    def get_successful_solutions(
        self, problem_hash: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Busca soluções bem-sucedidas para um problema específico.

        Args:
            problem_hash: Hash do problema
            limit: Número máximo de soluções a retornar

        Returns:
            Lista de soluções ordenadas por impact_score
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM solutions
                WHERE problem_hash = ? AND success = 1
                ORDER BY impact_score DESC, applied_at DESC
                LIMIT ?
            """,
                (problem_hash, limit),
            )

            return [dict(row) for row in cursor.fetchall()]

    def get_problem_by_hash(self, hash_value: str) -> Optional[Dict[str, Any]]:
        """
        Busca um problema pelo hash.

        Args:
            hash_value: Hash do problema

        Returns:
            Dicionário com dados do problema ou None se não encontrado
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM problems WHERE hash = ?", (hash_value,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def add_human_feedback(
        self, solution_id: int, feedback: str, comment: Optional[str] = None
    ) -> int:
        """
        Adiciona feedback humano sobre uma solução.

        Args:
            solution_id: ID da solução
            feedback: Tipo de feedback ('positive', 'negative', 'ignore')
            comment: Comentário opcional

        Returns:
            ID do feedback registrado
        """
        if feedback not in ("positive", "negative", "ignore"):
            raise ValueError(f"Invalid feedback type: {feedback}")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO human_feedback (solution_id, feedback, comment)
                VALUES (?, ?, ?)
            """,
                (solution_id, feedback, comment),
            )
            return cursor.lastrowid

    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas gerais da base de conhecimento.

        Returns:
            Dicionário com estatísticas
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Total de problemas
            cursor.execute("SELECT COUNT(*) as count FROM problems")
            total_problems = cursor.fetchone()["count"]

            # Total de soluções
            cursor.execute("SELECT COUNT(*) as count FROM solutions")
            total_solutions = cursor.fetchone()["count"]

            # Taxa de sucesso
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
                FROM solutions
            """)
            row = cursor.fetchone()
            success_rate = (
                (row["successful"] / row["total"] * 100) if row["total"] > 0 else 0
            )

            # Problemas mais frequentes
            cursor.execute("""
                SELECT module, COUNT(*) as count
                FROM problems
                GROUP BY module
                ORDER BY count DESC
                LIMIT 5
            """)
            top_modules = [dict(row) for row in cursor.fetchall()]

            return {
                "total_problems": total_problems,
                "total_solutions": total_solutions,
                "success_rate": round(success_rate, 2),
                "top_affected_modules": top_modules,
            }

    def cleanup_old_records(self, days: int = 90):
        """
        Remove registros antigos para manter o banco enxuto.

        Args:
            days: Número de dias para manter registros
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Remove problemas não vistos há mais de X dias sem soluções bem-sucedidas
            cursor.execute(
                """
                DELETE FROM problems
                WHERE last_seen < datetime('now', '-' || ? || ' days')
                AND hash NOT IN (
                    SELECT DISTINCT problem_hash 
                    FROM solutions 
                    WHERE success = 1
                )
            """,
                (days,),
            )

            deleted_count = cursor.rowcount
            logger.info(f"🧹 Cleaned up {deleted_count} old problem records")


# Singleton instance
knowledge_db = KnowledgeDatabase()
