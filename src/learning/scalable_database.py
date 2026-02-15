"""
Advanced Database Layer for JARVIS Learning Systems.

Provides scalable database backends with automatic migration from SQLite
to PostgreSQL/ChromaDB based on data volume and performance requirements.
"""

import json
import logging
import sqlite3
import threading
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from .dependency_manager import dependency_manager

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration."""
    backend: str = "sqlite"  # sqlite, postgresql, vector_db
    host: str = "localhost"
    port: int = 5432
    database: str = "jarvis_learning"
    username: str = "jarvis"
    password: str = ""
    connection_pool_size: int = 10
    auto_migrate_threshold: int = 1000000  # Migrate to PostgreSQL after 1M records

class DatabaseInterface(ABC):
    """Abstract interface for database operations."""
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to database."""
        pass
    
    @abstractmethod
    def create_tables(self) -> bool:
        """Create necessary tables."""
        pass
    
    @abstractmethod
    def add_feedback(self, user_input: str, ai_response: str, feedback_value: float,
                    feedback_type: str = "explicit", correction: str = None,
                    metadata: Dict[str, Any] = None) -> str:
        """Add feedback entry."""
        pass
    
    @abstractmethod
    def get_feedback_count(self) -> int:
        """Get total number of feedback entries."""
        pass
    
    @abstractmethod
    def get_recent_feedback(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent feedback entries."""
        pass
    
    @abstractmethod
    def generate_preference_pairs(self, n_pairs: int = 100) -> List[Dict[str, Any]]:
        """Generate preference pairs for DPO training."""
        pass
    
    @abstractmethod
    def close(self):
        """Close database connection."""
        pass

class SQLiteDatabase(DatabaseInterface):
    """SQLite implementation for smaller datasets."""
    
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self._lock = threading.Lock()
    
    def connect(self) -> bool:
        """Connect to SQLite database."""
        try:
            self.connection = sqlite3.connect(
                self.db_path, 
                check_same_thread=False,
                timeout=30.0
            )
            self.connection.row_factory = sqlite3.Row
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            return False
    
    def create_tables(self) -> bool:
        """Create SQLite tables."""
        try:
            with self._lock:
                cursor = self.connection.cursor()
                
                # Feedback table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS feedback (
                        id TEXT PRIMARY KEY,
                        interaction_id TEXT,
                        user_input TEXT NOT NULL,
                        ai_response TEXT NOT NULL,
                        feedback_type TEXT NOT NULL,
                        feedback_value REAL NOT NULL,
                        correction TEXT,
                        timestamp TEXT NOT NULL,
                        metadata TEXT
                    )
                """)
                
                # Preference pairs table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS preference_pairs (
                        id TEXT PRIMARY KEY,
                        prompt TEXT NOT NULL,
                        chosen_response TEXT NOT NULL,
                        rejected_response TEXT NOT NULL,
                        preference_strength REAL,
                        timestamp TEXT NOT NULL,
                        metadata TEXT
                    )
                """)
                
                # Indexes for performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON feedback(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback(feedback_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_value ON feedback(feedback_value)")
                
                self.connection.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to create SQLite tables: {e}")
            return False
    
    def add_feedback(self, user_input: str, ai_response: str, feedback_value: float,
                    feedback_type: str = "explicit", correction: str = None,
                    metadata: Dict[str, Any] = None) -> str:
        """Add feedback to SQLite."""
        import uuid
        
        feedback_id = str(uuid.uuid4())
        interaction_id = str(uuid.uuid4())
        
        try:
            with self._lock:
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO feedback 
                    (id, interaction_id, user_input, ai_response, feedback_type, 
                     feedback_value, correction, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    feedback_id,
                    interaction_id,
                    user_input,
                    ai_response,
                    feedback_type,
                    feedback_value,
                    correction,
                    datetime.now().isoformat(),
                    json.dumps(metadata) if metadata else None
                ))
                self.connection.commit()
                return feedback_id
        except Exception as e:
            logger.error(f"Failed to add feedback: {e}")
            return ""
    
    def get_feedback_count(self) -> int:
        """Get feedback count."""
        try:
            with self._lock:
                cursor = self.connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM feedback")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Failed to get feedback count: {e}")
            return 0
    
    def get_recent_feedback(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent feedback."""
        try:
            with self._lock:
                cursor = self.connection.cursor()
                cursor.execute("""
                    SELECT * FROM feedback 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
                
                results = []
                for row in cursor.fetchall():
                    data = dict(row)
                    if data['metadata']:
                        data['metadata'] = json.loads(data['metadata'])
                    results.append(data)
                
                return results
        except Exception as e:
            logger.error(f"Failed to get recent feedback: {e}")
            return []
    
    def generate_preference_pairs(self, n_pairs: int = 100) -> List[Dict[str, Any]]:
        """Generate preference pairs for DPO."""
        try:
            with self._lock:
                cursor = self.connection.cursor()
                
                # Get pairs of responses for similar prompts
                cursor.execute("""
                    SELECT f1.user_input, f1.ai_response, f1.feedback_value,
                           f2.ai_response, f2.feedback_value
                    FROM feedback f1
                    JOIN feedback f2 ON f1.user_input = f2.user_input
                    WHERE f1.id != f2.id 
                    AND abs(f1.feedback_value - f2.feedback_value) > 0.3
                    ORDER BY RANDOM()
                    LIMIT ?
                """, (n_pairs,))
                
                pairs = []
                for row in cursor.fetchall():
                    prompt, resp1, val1, resp2, val2 = row
                    
                    # Higher value is preferred
                    if val1 > val2:
                        chosen, rejected = resp1, resp2
                        strength = val1 - val2
                    else:
                        chosen, rejected = resp2, resp1
                        strength = val2 - val1
                    
                    pairs.append({
                        'prompt': prompt,
                        'chosen_response': chosen,
                        'rejected_response': rejected,
                        'preference_strength': strength
                    })
                
                return pairs
                
        except Exception as e:
            logger.error(f"Failed to generate preference pairs: {e}")
            return []
    
    def close(self):
        """Close SQLite connection."""
        if self.connection:
            self.connection.close()

class PostgreSQLDatabase(DatabaseInterface):
    """PostgreSQL implementation for larger datasets."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection = None
        self.connection_pool = None
        
        # Check if PostgreSQL is available
        if not dependency_manager.is_available('database', 'postgresql'):
            raise ImportError("PostgreSQL support requires psycopg2: pip install psycopg2-binary")
    
    def connect(self) -> bool:
        """Connect to PostgreSQL."""
        try:
            import psycopg2
            from psycopg2 import pool
            
            # Create connection pool
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=self.config.connection_pool_size,
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password
            )
            
            # Test connection
            conn = self.connection_pool.getconn()
            conn.close()
            self.connection_pool.putconn(conn)
            
            logger.info(f"âœ… Connected to PostgreSQL: {self.config.database}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            return False
    
    def create_tables(self) -> bool:
        """Create PostgreSQL tables."""
        try:
            conn = self.connection_pool.getconn()
            try:
                with conn.cursor() as cursor:
                    # Feedback table with better indexing
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS feedback (
                            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                            interaction_id UUID,
                            user_input TEXT NOT NULL,
                            ai_response TEXT NOT NULL,
                            feedback_type VARCHAR(50) NOT NULL,
                            feedback_value DECIMAL(3,2) NOT NULL,
                            correction TEXT,
                            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            metadata JSONB,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                        )
                    """)
                    
                    # Preference pairs table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS preference_pairs (
                            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                            prompt TEXT NOT NULL,
                            chosen_response TEXT NOT NULL,
                            rejected_response TEXT NOT NULL,
                            preference_strength DECIMAL(3,2),
                            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            metadata JSONB,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                        )
                    """)
                    
                    # Advanced indexes for performance
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_timestamp_btree ON feedback USING btree(timestamp)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_type_hash ON feedback USING hash(feedback_type)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_value_btree ON feedback USING btree(feedback_value)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_metadata_gin ON feedback USING gin(metadata)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_text_gin ON feedback USING gin(to_tsvector('english', user_input || ' ' || ai_response))")
                    
                    conn.commit()
                    return True
            finally:
                self.connection_pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL tables: {e}")
            return False
    
    def add_feedback(self, user_input: str, ai_response: str, feedback_value: float,
                    feedback_type: str = "explicit", correction: str = None,
                    metadata: Dict[str, Any] = None) -> str:
        """Add feedback to PostgreSQL."""
        try:
            conn = self.connection_pool.getconn()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO feedback 
                        (user_input, ai_response, feedback_type, feedback_value, correction, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        user_input,
                        ai_response,
                        feedback_type,
                        feedback_value,
                        correction,
                        json.dumps(metadata) if metadata else None
                    ))
                    
                    feedback_id = str(cursor.fetchone()[0])
                    conn.commit()
                    return feedback_id
            finally:
                self.connection_pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"Failed to add PostgreSQL feedback: {e}")
            return ""
    
    def get_feedback_count(self) -> int:
        """Get feedback count."""
        try:
            conn = self.connection_pool.getconn()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM feedback")
                    return cursor.fetchone()[0]
            finally:
                self.connection_pool.putconn(conn)
        except Exception as e:
            logger.error(f"Failed to get PostgreSQL feedback count: {e}")
            return 0
    
    def get_recent_feedback(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent feedback from PostgreSQL."""
        try:
            conn = self.connection_pool.getconn()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, interaction_id, user_input, ai_response, 
                               feedback_type, feedback_value, correction, 
                               timestamp, metadata
                        FROM feedback 
                        ORDER BY timestamp DESC 
                        LIMIT %s
                    """, (limit,))
                    
                    results = []
                    for row in cursor.fetchall():
                        data = {
                            'id': str(row[0]),
                            'interaction_id': str(row[1]) if row[1] else None,
                            'user_input': row[2],
                            'ai_response': row[3],
                            'feedback_type': row[4],
                            'feedback_value': float(row[5]),
                            'correction': row[6],
                            'timestamp': row[7].isoformat() if row[7] else None,
                            'metadata': json.loads(row[8]) if row[8] else None
                        }
                        results.append(data)
                    
                    return results
            finally:
                self.connection_pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"Failed to get PostgreSQL recent feedback: {e}")
            return []
    
    def generate_preference_pairs(self, n_pairs: int = 100) -> List[Dict[str, Any]]:
        """Generate preference pairs using PostgreSQL advanced queries."""
        try:
            conn = self.connection_pool.getconn()
            try:
                with conn.cursor() as cursor:
                    # Use similarity search and window functions for better pairs
                    cursor.execute("""
                        WITH similar_prompts AS (
                            SELECT 
                                f1.user_input,
                                f1.ai_response as response1,
                                f1.feedback_value as value1,
                                f2.ai_response as response2,
                                f2.feedback_value as value2,
                                similarity(f1.user_input, f2.user_input) as sim_score
                            FROM feedback f1
                            JOIN feedback f2 ON f1.id != f2.id
                            WHERE similarity(f1.user_input, f2.user_input) > 0.3
                            AND abs(f1.feedback_value - f2.feedback_value) > 0.3
                        )
                        SELECT user_input, response1, value1, response2, value2, sim_score
                        FROM similar_prompts
                        ORDER BY sim_score DESC, abs(value1 - value2) DESC
                        LIMIT %s
                    """, (n_pairs,))
                    
                    pairs = []
                    for row in cursor.fetchall():
                        prompt, resp1, val1, resp2, val2, sim = row
                        
                        if val1 > val2:
                            chosen, rejected = resp1, resp2
                            strength = val1 - val2
                        else:
                            chosen, rejected = resp2, resp1
                            strength = val2 - val1
                        
                        pairs.append({
                            'prompt': prompt,
                            'chosen_response': chosen,
                            'rejected_response': rejected,
                            'preference_strength': strength,
                            'similarity_score': sim
                        })
                    
                    return pairs
            finally:
                self.connection_pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"Failed to generate PostgreSQL preference pairs: {e}")
            return []
    
    def close(self):
        """Close PostgreSQL connections."""
        if self.connection_pool:
            self.connection_pool.closeall()

class VectorDatabase(DatabaseInterface):
    """ChromaDB implementation for semantic search capabilities."""
    
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.client = None
        self.collection = None
        
        if not dependency_manager.is_available('database', 'vector_db'):
            raise ImportError("Vector database support requires chromadb: pip install chromadb")
    
    def connect(self) -> bool:
        """Connect to ChromaDB."""
        try:
            import chromadb
            
            self.client = chromadb.PersistentClient(path=str(self.db_path))
            self.collection = self.client.get_or_create_collection(
                name="feedback",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"âœ… Connected to ChromaDB: {self.db_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            return False
    
    def create_tables(self) -> bool:
        """Create ChromaDB collections."""
        # ChromaDB creates collections automatically
        return True
    
    def add_feedback(self, user_input: str, ai_response: str, feedback_value: float,
                    feedback_type: str = "explicit", correction: str = None,
                    metadata: Dict[str, Any] = None) -> str:
        """Add feedback to ChromaDB."""
        import uuid
        
        feedback_id = str(uuid.uuid4())
        
        try:
            # Combine user input and AI response for embedding
            document = f"User: {user_input}\nAI: {ai_response}"
            
            # Prepare metadata
            meta = {
                'feedback_type': feedback_type,
                'feedback_value': feedback_value,
                'timestamp': datetime.now().isoformat()
            }
            
            if correction:
                meta['correction'] = correction
            
            if metadata:
                meta.update(metadata)
            
            # Add to collection
            self.collection.add(
                documents=[document],
                ids=[feedback_id],
                metadatas=[meta]
            )
            
            return feedback_id
            
        except Exception as e:
            logger.error(f"Failed to add ChromaDB feedback: {e}")
            return ""
    
    def get_feedback_count(self) -> int:
        """Get feedback count from ChromaDB."""
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Failed to get ChromaDB feedback count: {e}")
            return 0
    
    def get_recent_feedback(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent feedback from ChromaDB."""
        try:
            result = self.collection.get(limit=limit)
            
            feedback = []
            for i, doc_id in enumerate(result['ids']):
                data = {
                    'id': doc_id,
                    'document': result['documents'][i],
                    'metadata': result['metadatas'][i]
                }
                feedback.append(data)
            
            return feedback
            
        except Exception as e:
            logger.error(f"Failed to get ChromaDB recent feedback: {e}")
            return []
    
    def generate_preference_pairs(self, n_pairs: int = 100) -> List[Dict[str, Any]]:
        """Generate preference pairs using semantic similarity."""
        try:
            # Get all feedback
            all_feedback = self.collection.get()
            
            pairs = []
            processed = set()
            
            for i, doc1 in enumerate(all_feedback['documents'][:n_pairs * 2]):
                id1 = all_feedback['ids'][i]
                meta1 = all_feedback['metadatas'][i]
                val1 = meta1.get('feedback_value', 0.0)
                
                # Find semantically similar documents
                similar = self.collection.query(
                    query_texts=[doc1],
                    n_results=5
                )
                
                for j, doc2 in enumerate(similar['documents'][0][1:]):  # Skip first (same doc)
                    id2 = similar['ids'][0][j + 1]
                    
                    if f"{id1}-{id2}" in processed or f"{id2}-{id1}" in processed:
                        continue
                    
                    meta2 = similar['metadatas'][0][j + 1]
                    val2 = meta2.get('feedback_value', 0.0)
                    
                    if abs(val1 - val2) > 0.3:  # Significant difference
                        # Extract prompt and response from document
                        lines1 = doc1.split('\n')
                        lines2 = doc2.split('\n')
                        
                        if len(lines1) >= 2 and len(lines2) >= 2:
                            prompt = lines1[0].replace("User: ", "")
                            resp1 = lines1[1].replace("AI: ", "")
                            resp2 = lines2[1].replace("AI: ", "")
                            
                            if val1 > val2:
                                chosen, rejected = resp1, resp2
                                strength = val1 - val2
                            else:
                                chosen, rejected = resp2, resp1
                                strength = val2 - val1
                            
                            pairs.append({
                                'prompt': prompt,
                                'chosen_response': chosen,
                                'rejected_response': rejected,
                                'preference_strength': strength,
                                'similarity_score': similar['distances'][0][j + 1]
                            })
                            
                            processed.add(f"{id1}-{id2}")
                            
                            if len(pairs) >= n_pairs:
                                break
                
                if len(pairs) >= n_pairs:
                    break
            
            return pairs[:n_pairs]
            
        except Exception as e:
            logger.error(f"Failed to generate ChromaDB preference pairs: {e}")
            return []
    
    def close(self):
        """Close ChromaDB client."""
        # ChromaDB handles cleanup automatically
        pass

class ScalableDatabase:
    """
    Auto-scaling database that starts with SQLite and migrates to 
    PostgreSQL/ChromaDB when data volume increases.
    """
    
    def __init__(self, data_dir: Path, config: DatabaseConfig = None):
        self.data_dir = Path(data_dir)
        self.config = config or DatabaseConfig()
        self.current_backend = None
        self._lock = threading.Lock()
        
        # Start with SQLite by default
        self._initialize_backend()
    
    def _initialize_backend(self):
        """Initialize appropriate database backend."""
        from src.utils.config import config
        sqlite_path = config.FEEDBACK_FILE
        
        # Check current data volume
        if sqlite_path.exists():
            try:
                conn = sqlite3.connect(sqlite_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM feedback")
                count = cursor.fetchone()[0]
                conn.close()
                
                # Auto-migrate if threshold exceeded and PostgreSQL available
                if (count > self.config.auto_migrate_threshold and 
                    dependency_manager.is_available('database', 'postgresql')):
                    logger.info(f"ðŸ”„ Auto-migrating to PostgreSQL ({count:,} records)")
                    self._migrate_to_postgresql()
                    return
                    
            except Exception as e:
                logger.debug(f"Could not check SQLite count: {e}")
        
        # Default to SQLite
        try:
            self.current_backend = SQLiteDatabase(sqlite_path)
            if self.current_backend.connect():
                self.current_backend.create_tables()
                logger.info("ðŸ“Š Using SQLite database backend")
            else:
                logger.error("Failed to initialize SQLite backend")
        except Exception as e:
            logger.error(f"Failed to initialize SQLite: {e}")
    
    def _migrate_to_postgresql(self):
        """Migrate data from SQLite to PostgreSQL."""
        try:
            # Initialize PostgreSQL
            pg_backend = PostgreSQLDatabase(self.config)
            if not pg_backend.connect():
                logger.error("Failed to connect to PostgreSQL for migration")
                return
            
            pg_backend.create_tables()
            
            # Migrate data
            sqlite_backend = SQLiteDatabase(self.data_dir / "feedback.db")
            if sqlite_backend.connect():
                old_data = sqlite_backend.get_recent_feedback(limit=10000000)  # Get all
                
                for entry in old_data:
                    pg_backend.add_feedback(
                        user_input=entry['user_input'],
                        ai_response=entry['ai_response'],
                        feedback_value=entry['feedback_value'],
                        feedback_type=entry['feedback_type'],
                        correction=entry.get('correction'),
                        metadata=entry.get('metadata')
                    )
                
                # Backup old SQLite file
                import shutil
                backup_path = self.data_dir / f"feedback_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                shutil.copy2(sqlite_backend.db_path, backup_path)
                
                sqlite_backend.close()
                self.current_backend = pg_backend
                
                logger.info(f"âœ… Migration complete. Backup saved: {backup_path}")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            # Fallback to SQLite
            self._initialize_backend()
    
    def add_feedback(self, *args, **kwargs) -> str:
        """Add feedback using current backend."""
        with self._lock:
            return self.current_backend.add_feedback(*args, **kwargs)
    
    def get_feedback_count(self) -> int:
        """Get feedback count."""
        return self.current_backend.get_feedback_count()
    
    def get_recent_feedback(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent feedback."""
        return self.current_backend.get_recent_feedback(limit)
    
    def generate_preference_pairs(self, n_pairs: int = 100) -> List[Dict[str, Any]]:
        """Generate preference pairs."""
        return self.current_backend.generate_preference_pairs(n_pairs)
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get information about current backend."""
        backend_type = type(self.current_backend).__name__
        count = self.get_feedback_count()
        
        return {
            'backend_type': backend_type,
            'record_count': count,
            'can_migrate': (
                backend_type == "SQLiteDatabase" and 
                count > self.config.auto_migrate_threshold and
                dependency_manager.is_available('database', 'postgresql')
            ),
            'migration_threshold': self.config.auto_migrate_threshold
        }
    
    def close(self):
        """Close current backend."""
        if self.current_backend:
            self.current_backend.close()
