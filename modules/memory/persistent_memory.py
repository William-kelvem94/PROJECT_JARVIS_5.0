"""
Sistema de Memória Persistente
Gerencia contexto, histórico e preferências do usuário entre sessões
"""

import json
import sqlite3
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from core.logger import logger

class PersistentMemory:
    """
    Sistema de memória persistente usando SQLite.
    Armazena:
    - Histórico de conversas
    - Preferências do usuário
    - Estado do sistema
    - Contexto de sessões
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Inicializa o sistema de memória persistente.
        
        Args:
            db_path: Caminho do banco de dados (padrão: ./data/memory.db)
        """
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path("./data/memory.db")
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializar banco de dados
        self._init_database()
        
        logger.info(f"PersistentMemory inicializado: {self.db_path}")
    
    def _init_database(self):
        """Cria as tabelas necessárias no banco de dados."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela de histórico de conversas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    message_type TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            # Tabela de preferências do usuário
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de estado do sistema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de contexto de sessões
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS session_context (
                    session_id TEXT PRIMARY KEY,
                    context_data TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def save_context(self, key: str, value: Any) -> bool:
        """
        Salva um valor no contexto do sistema.
        
        Args:
            key: Chave do contexto
            value: Valor a salvar (será convertido para JSON)
        
        Returns:
            True se salvou com sucesso
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                value_json = json.dumps(value, default=str)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO system_state (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (key, value_json))
                
                conn.commit()
                logger.debug(f"Contexto salvo: {key}")
                return True
        except Exception as e:
            logger.error(f"Erro ao salvar contexto {key}: {e}")
            return False
    
    def get_context(self, key: str, default: Any = None) -> Optional[Any]:
        """
        Recupera um valor do contexto do sistema.
        
        Args:
            key: Chave do contexto
            default: Valor padrão se não encontrado
        
        Returns:
            Valor recuperado ou default
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT value FROM system_state WHERE key = ?', (key,))
                row = cursor.fetchone()
                
                if row:
                    return json.loads(row[0])
                return default
        except Exception as e:
            logger.error(f"Erro ao recuperar contexto {key}: {e}")
            return default
    
    def save_conversation(self, role: str, content: str, message_type: str = "text", metadata: Optional[Dict] = None):
        """
        Salva uma mensagem no histórico de conversas.
        
        Args:
            role: "user" ou "assistant"
            content: Conteúdo da mensagem
            message_type: Tipo da mensagem (text, voice, etc.)
            metadata: Metadados adicionais
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                metadata_json = json.dumps(metadata) if metadata else None
                
                cursor.execute('''
                    INSERT INTO conversation_history (role, content, message_type, metadata)
                    VALUES (?, ?, ?, ?)
                ''', (role, content, message_type, metadata_json))
                
                conn.commit()
                logger.debug(f"Conversa salva: {role}")
        except Exception as e:
            logger.error(f"Erro ao salvar conversa: {e}")
    
    def get_conversation_history(self, limit: int = 50, role: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Recupera histórico de conversas.
        
        Args:
            limit: Número máximo de mensagens
            role: Filtrar por role (None para todas)
        
        Returns:
            Lista de mensagens
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if role:
                    cursor.execute('''
                        SELECT role, content, message_type, timestamp, metadata
                        FROM conversation_history
                        WHERE role = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ''', (role, limit))
                else:
                    cursor.execute('''
                        SELECT role, content, message_type, timestamp, metadata
                        FROM conversation_history
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ''', (limit,))
                
                rows = cursor.fetchall()
                
                history = []
                for row in reversed(rows):  # Reverter para ordem cronológica
                    history.append({
                        "role": row[0],
                        "content": row[1],
                        "message_type": row[2],
                        "timestamp": row[3],
                        "metadata": json.loads(row[4]) if row[4] else None
                    })
                
                return history
        except Exception as e:
            logger.error(f"Erro ao recuperar histórico: {e}")
            return []
    
    def save_user_preference(self, key: str, value: Any) -> bool:
        """
        Salva uma preferência do usuário.
        
        Args:
            key: Chave da preferência
            value: Valor (será convertido para JSON)
        
        Returns:
            True se salvou com sucesso
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                value_json = json.dumps(value, default=str)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO user_preferences (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (key, value_json))
                
                conn.commit()
                logger.debug(f"Preferência salva: {key}")
                return True
        except Exception as e:
            logger.error(f"Erro ao salvar preferência {key}: {e}")
            return False
    
    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """
        Recupera uma preferência do usuário.
        
        Args:
            key: Chave da preferência
            default: Valor padrão
        
        Returns:
            Valor da preferência ou default
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT value FROM user_preferences WHERE key = ?', (key,))
                row = cursor.fetchone()
                
                if row:
                    return json.loads(row[0])
                return default
        except Exception as e:
            logger.error(f"Erro ao recuperar preferência {key}: {e}")
            return default
    
    def save_session_context(self, session_id: str, context_data: Dict[str, Any]) -> bool:
        """
        Salva contexto de uma sessão.
        
        Args:
            session_id: ID da sessão
            context_data: Dados do contexto
        
        Returns:
            True se salvou com sucesso
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                context_json = json.dumps(context_data, default=str)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO session_context 
                    (session_id, context_data, last_accessed)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (session_id, context_json))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Erro ao salvar contexto de sessão: {e}")
            return False
    
    def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera contexto de uma sessão.
        
        Args:
            session_id: ID da sessão
        
        Returns:
            Dados do contexto ou None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT context_data FROM session_context WHERE session_id = ?', (session_id,))
                row = cursor.fetchone()
                
                if row:
                    # Atualizar último acesso
                    cursor.execute('''
                        UPDATE session_context 
                        SET last_accessed = CURRENT_TIMESTAMP 
                        WHERE session_id = ?
                    ''', (session_id,))
                    conn.commit()
                    
                    return json.loads(row[0])
                return None
        except Exception as e:
            logger.error(f"Erro ao recuperar contexto de sessão: {e}")
            return None
    
    def cleanup_old_conversations(self, days: int = 30):
        """
        Remove conversas antigas do banco.
        
        Args:
            days: Número de dias para manter
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM conversation_history
                    WHERE timestamp < datetime('now', '-' || ? || ' days')
                ''', (days,))
                
                deleted = cursor.rowcount
                conn.commit()
                
                logger.info(f"{deleted} conversas antigas removidas")
                return deleted
        except Exception as e:
            logger.error(f"Erro ao limpar conversas antigas: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do banco de dados."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Contar conversas
                cursor.execute('SELECT COUNT(*) FROM conversation_history')
                conversation_count = cursor.fetchone()[0]
                
                # Contar preferências
                cursor.execute('SELECT COUNT(*) FROM user_preferences')
                preferences_count = cursor.fetchone()[0]
                
                # Contar sessões
                cursor.execute('SELECT COUNT(*) FROM session_context')
                sessions_count = cursor.fetchone()[0]
                
                return {
                    "conversations": conversation_count,
                    "preferences": preferences_count,
                    "sessions": sessions_count,
                    "db_path": str(self.db_path),
                    "db_size_mb": self.db_path.stat().st_size / (1024 * 1024)
                }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}

