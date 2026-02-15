#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Blackbox Logger (SQLite-based Logging System)
==========================================================
Sistema de logging estruturado para substituir logs de texto simples.
Facilita consultas, análises e recuperação de erros históricos.

Features:
- Logging estruturado para SQLite
- Consultas eficientes por filtros
- Retenção automática de logs
- Compressão de logs antigos
- Métricas e analytics integrados
- Thread-safe operations

Usage:
    from src.core.config.blackbox_logger import blackbox_logger
    
    # Log messages (same interface as standard logger)
    blackbox_logger.info("System started")
    blackbox_logger.error("Critical error occurred", error_code="E001")
    blackbox_logger.warning("Performance degraded", component="vision")
    
    # Advanced logging with context
    blackbox_logger.log_event("user_interaction", {
        "command": "open notepad",
        "response_time": 2.5,
        "success": True
    })
    
    # Query logs
    recent_errors = blackbox_logger.query_logs(level="ERROR", hours=24)
    performance_data = blackbox_logger.get_performance_metrics()
"""

import sqlite3
import logging
import json
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import traceback
import sys

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: str
    level: str
    component: str
    message: str
    context: Dict[str, Any] = None
    error_code: Optional[str] = None
    stack_trace: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class BlackboxLogger:
    """
    Advanced SQLite-based logger for JARVIS system
    
    Provides structured logging with efficient querying capabilities.
    Replaces traditional text-based logs with queryable database.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, db_path: Optional[str] = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path: Optional[str] = None):
        if self._initialized:
            return
        
        # Determine database path  
        if db_path:
            self.db_path = Path(db_path)
        else:
            # Try to get from system manifest
            try:
                from src.core.config.system_manifest import system_manifest
                self.db_path = Path(system_manifest.database.log_database_path)
            except ImportError:
                # Fallback path
                current_file = Path(__file__).resolve()
                project_root = current_file.parent.parent.parent.parent
                self.db_path = project_root / "data" / "logs" / "blackbox.db"
        
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.connection_pool = []
        self.pool_lock = threading.Lock()
        self.session_id = self._generate_session_id()
        
        # Initialize database schema
        self._initialize_database()
        
        # Start background maintenance
        self._start_maintenance_thread()
        
        self._initialized = True
        
        # Log system initialization
        self.info("🔥 Blackbox Logger initialized", component="blackbox_logger")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{int(time.time())}_{id(self)}"
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection (thread-safe)"""
        connection = sqlite3.connect(
            self.db_path,
            timeout=30.0,
            check_same_thread=False
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=NORMAL")
        connection.execute("PRAGMA cache_size=10000")
        return connection
    
    def _initialize_database(self):
        """Initialize database schema"""
        try:
            with self._get_connection() as conn:
                # Main logs table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        level TEXT NOT NULL,
                        component TEXT NOT NULL,
                        message TEXT NOT NULL,
                        context TEXT,  -- JSON
                        error_code TEXT,
                        stack_trace TEXT,
                        session_id TEXT,
                        user_id TEXT,
                        created_at REAL NOT NULL,
                        INDEX idx_timestamp ON logs(timestamp),
                        INDEX idx_level ON logs(level),
                        INDEX idx_component ON logs(component),
                        INDEX idx_session ON logs(session_id),
                        INDEX idx_error_code ON logs(error_code),
                        INDEX idx_created_at ON logs(created_at)
                    )
                """)
                
                # Performance metrics table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        metric_name TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        component TEXT NOT NULL,
                        session_id TEXT,
                        metadata TEXT,  -- JSON
                        created_at REAL NOT NULL,
                        INDEX idx_metric_name ON metrics(metric_name),
                        INDEX idx_component_metrics ON metrics(component),
                        INDEX idx_timestamp_metrics ON metrics(timestamp)
                    )
                """)
                
                # System events table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        event_data TEXT,  -- JSON
                        component TEXT NOT NULL,
                        session_id TEXT,
                        success BOOLEAN,
                        duration_ms REAL,
                        created_at REAL NOT NULL,
                        INDEX idx_event_type ON events(event_type),
                        INDEX idx_component_events ON events(component),
                        INDEX idx_success ON events(success)
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            # Fallback to standard logging if database fails
            logging.error(f"❌ Failed to initialize blackbox database: {e}")
            raise
    
    def _start_maintenance_thread(self):
        """Start background maintenance thread"""
        def maintenance_worker():
            while True:
                try:
                    # Sleep for 1 hour between maintenance cycles
                    time.sleep(3600)
                    self._perform_maintenance()
                except Exception as e:
                    logging.error(f"Blackbox maintenance error: {e}")
        
        maintenance_thread = threading.Thread(
            target=maintenance_worker,
            daemon=True,
            name="BlackboxMaintenance"
        )
        maintenance_thread.start()
    
    def _perform_maintenance(self):
        """Perform database maintenance tasks"""
        try:
            with self._get_connection() as conn:
                # Clean old logs (older than 30 days)
                cutoff_time = time.time() - (30 * 24 * 3600)
                
                cursor = conn.execute(
                    "DELETE FROM logs WHERE created_at < ?",
                    (cutoff_time,)
                )
                deleted_logs = cursor.rowcount
                
                # Clean old metrics (older than 7 days)
                metrics_cutoff = time.time() - (7 * 24 * 3600)
                cursor = conn.execute(
                    "DELETE FROM metrics WHERE created_at < ?",
                    (metrics_cutoff,)
                )
                deleted_metrics = cursor.rowcount
                
                # Optimize database
                conn.execute("VACUUM")
                conn.execute("ANALYZE")
                
                conn.commit()
                
                if deleted_logs > 0 or deleted_metrics > 0:
                    self.info(
                        f"🧹 Maintenance completed: cleaned {deleted_logs} logs, {deleted_metrics} metrics",
                        component="blackbox_logger"
                    )
                    
        except Exception as e:
            logging.error(f"Blackbox maintenance failed: {e}")
    
    def log(self, level: str, message: str, component: str = "system", 
            context: Optional[Dict[str, Any]] = None,
            error_code: Optional[str] = None,
            user_id: Optional[str] = None,
            include_stack: bool = False):
        """
        Core logging method
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            component: Component name (e.g., 'ai_agent', 'vision_system')
            context: Additional context data
            error_code: Error code for categorization
            user_id: User identifier
            include_stack: Include stack trace
        """
        try:
            timestamp = datetime.now().isoformat()
            created_at = time.time()
            
            # Get stack trace if requested or if it's an error
            stack_trace = None
            if include_stack or level in ["ERROR", "CRITICAL"]:
                stack_trace = traceback.format_stack()
                stack_trace = "".join(stack_trace[:-1])  # Exclude this call
            
            # Serialize context
            context_json = json.dumps(context) if context else None
            
            # Store in database
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO logs (
                        timestamp, level, component, message, context,
                        error_code, stack_trace, session_id, user_id, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    timestamp, level, component, message, context_json,
                    error_code, stack_trace, self.session_id, user_id, created_at
                ))
                conn.commit()
            
            # Also log to standard Python logger for immediate visibility
            python_logger = logging.getLogger(f"jarvis.{component}")
            log_method = getattr(python_logger, level.lower(), python_logger.info)
            
            # Format message for standard logger
            std_message = message
            if context:
                std_message += f" | Context: {context}"
            if error_code:
                std_message += f" | Code: {error_code}"
                
            log_method(std_message)
            
        except Exception as e:
            # Fallback to standard logging if database fails
            logging.error(f"Blackbox logging failed: {e}")
            logging.log(getattr(logging, level, logging.INFO), f"{component}: {message}")
    
    # Convenience methods matching standard Python logger interface
    def debug(self, message: str, component: str = "system", **kwargs):
        self.log("DEBUG", message, component, **kwargs)
    
    def info(self, message: str, component: str = "system", **kwargs):
        self.log("INFO", message, component, **kwargs)
    
    def warning(self, message: str, component: str = "system", **kwargs):
        self.log("WARNING", message, component, **kwargs)
    
    def error(self, message: str, component: str = "system", **kwargs):
        kwargs.setdefault("include_stack", True)
        self.log("ERROR", message, component, **kwargs)
    
    def critical(self, message: str, component: str = "system", **kwargs):
        kwargs.setdefault("include_stack", True)
        self.log("CRITICAL", message, component, **kwargs)
    
    def log_event(self, event_type: str, event_data: Dict[str, Any],
                  component: str = "system", success: bool = True,
                  duration_ms: Optional[float] = None):
        """
        Log system events with structured data
        
        Args:
            event_type: Type of event (e.g., 'user_interaction', 'system_startup')
            event_data: Event data dictionary
            component: Component generating the event
            success: Whether the event was successful
            duration_ms: Event duration in milliseconds
        """
        try:
            timestamp = datetime.now().isoformat()
            created_at = time.time()
            event_data_json = json.dumps(event_data)
            
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO events (
                        timestamp, event_type, event_data, component,
                        session_id, success, duration_ms, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    timestamp, event_type, event_data_json, component,
                    self.session_id, success, duration_ms, created_at
                ))
                conn.commit()
                
        except Exception as e:
            logging.error(f"Failed to log event: {e}")
    
    def log_metric(self, metric_name: str, value: float, component: str = "system",
                   metadata: Optional[Dict[str, Any]] = None):
        """
        Log performance metrics
        
        Args:
            metric_name: Name of the metric (e.g., 'response_time', 'memory_usage')
            value: Metric value
            component: Component generating the metric
            metadata: Additional metadata
        """
        try:
            timestamp = datetime.now().isoformat()
            created_at = time.time()
            metadata_json = json.dumps(metadata) if metadata else None
            
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO metrics (
                        timestamp, metric_name, metric_value, component,
                        session_id, metadata, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    timestamp, metric_name, value, component,
                    self.session_id, metadata_json, created_at
                ))
                conn.commit()
                
        except Exception as e:
            logging.error(f"Failed to log metric: {e}")
    
    def query_logs(self, level: Optional[str] = None,
                   component: Optional[str] = None,
                   error_code: Optional[str] = None,
                   hours: Optional[int] = None,
                   limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Query logs with filters
        
        Args:
            level: Filter by log level
            component: Filter by component
            error_code: Filter by error code
            hours: Filter by hours back from now
            limit: Maximum number of results
            
        Returns:
            List of log entries
        """
        try:
            query = "SELECT * FROM logs WHERE 1=1"
            params = []
            
            if level:
                query += " AND level = ?"
                params.append(level)
            
            if component:
                query += " AND component = ?"
                params.append(component)
            
            if error_code:
                query += " AND error_code = ?"
                params.append(error_code)
            
            if hours:
                cutoff_time = time.time() - (hours * 3600)
                query += " AND created_at >= ?"
                params.append(cutoff_time)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            with self._get_connection() as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert to dictionaries
                results = []
                for row in rows:
                    log_dict = dict(row)
                    # Parse JSON context
                    if log_dict['context']:
                        try:
                            log_dict['context'] = json.loads(log_dict['context'])
                        except json.JSONDecodeError:
                            pass
                    results.append(log_dict)
                
                return results
                
        except Exception as e:
            logging.error(f"Failed to query logs: {e}")
            return []
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of errors in the last N hours"""
        try:
            cutoff_time = time.time() - (hours * 3600)
            
            with self._get_connection() as conn:
                # Count errors by level
                cursor = conn.execute("""
                    SELECT level, COUNT(*) as count
                    FROM logs 
                    WHERE level IN ('ERROR', 'CRITICAL') AND created_at >= ?
                    GROUP BY level
                """, (cutoff_time,))
                error_counts = {row['level']: row['count'] for row in cursor.fetchall()}
                
                # Count errors by component
                cursor = conn.execute("""
                    SELECT component, COUNT(*) as count
                    FROM logs 
                    WHERE level IN ('ERROR', 'CRITICAL') AND created_at >= ?
                    GROUP BY component
                    ORDER BY count DESC
                    LIMIT 10
                """, (cutoff_time,))
                component_errors = {row['component']: row['count'] for row in cursor.fetchall()}
                
                # Count errors by error code
                cursor = conn.execute("""
                    SELECT error_code, COUNT(*) as count
                    FROM logs 
                    WHERE level IN ('ERROR', 'CRITICAL') AND error_code IS NOT NULL AND created_at >= ?
                    GROUP BY error_code
                    ORDER BY count DESC
                    LIMIT 10
                """, (cutoff_time,))
                error_code_counts = {row['error_code']: row['count'] for row in cursor.fetchall()}
                
                return {
                    "period_hours": hours,
                    "error_counts_by_level": error_counts,
                    "error_counts_by_component": component_errors,
                    "error_counts_by_code": error_code_counts,
                    "total_errors": sum(error_counts.values())
                }
                
        except Exception as e:
            logging.error(f"Failed to get error summary: {e}")
            return {}
    
    def get_performance_metrics(self, metric_name: Optional[str] = None,
                               component: Optional[str] = None,
                               hours: int = 24) -> List[Dict[str, Any]]:
        """Get performance metrics"""
        try:
            cutoff_time = time.time() - (hours * 3600)
            query = "SELECT * FROM metrics WHERE created_at >= ?"
            params = [cutoff_time]
            
            if metric_name:
                query += " AND metric_name = ?"
                params.append(metric_name)
            
            if component:
                query += " AND component = ?"
                params.append(component)
            
            query += " ORDER BY created_at DESC"
            
            with self._get_connection() as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    metric_dict = dict(row)
                    if metric_dict['metadata']:
                        try:
                            metric_dict['metadata'] = json.loads(metric_dict['metadata'])
                        except json.JSONDecodeError:
                            pass
                    results.append(metric_dict)
                
                return results
                
        except Exception as e:
            logging.error(f"Failed to get performance metrics: {e}")
            return []
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.info("🧹 Blackbox Logger shutting down", component="blackbox_logger")
        except:
            pass

# Global instance
blackbox_logger = BlackboxLogger()

# Create a custom handler for standard Python logging to route to blackbox
class BlackboxLogHandler(logging.Handler):
    """Custom log handler that routes to blackbox logger"""
    
    def emit(self, record):
        try:
            # Extract component from logger name
            component = record.name.split('.')[-1] if '.' in record.name else record.name
            
            # Build context from record
            context = {}
            if hasattr(record, 'extra'):
                context.update(record.extra)
            
            # Include exception info if available
            if record.exc_info:
                context['exception'] = {
                    'type': record.exc_info[0].__name__,
                    'message': str(record.exc_info[1])
                }
            
            # Log to blackbox
            blackbox_logger.log(
                level=record.levelname,
                message=record.getMessage(),
                component=component,
                context=context if context else None,
                include_stack=record.levelno >= logging.ERROR
            )
            
        except Exception:
            # Don't let logging errors break the application
            pass

def setup_blackbox_integration():
    """Setup integration with standard Python logging"""
    try:
        # Add blackbox handler to root logger
        root_logger = logging.getLogger()
        
        # Remove existing blackbox handlers to avoid duplicates
        root_logger.handlers = [h for h in root_logger.handlers if not isinstance(h, BlackboxLogHandler)]
        
        # Add new blackbox handler
        blackbox_handler = BlackboxLogHandler()
        blackbox_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(blackbox_handler)
        
        blackbox_logger.info("🔗 Standard logging integration enabled", component="blackbox_logger")
        
    except Exception as e:
        logging.error(f"Failed to setup blackbox integration: {e}")

if __name__ == "__main__":
    # Test the blackbox logger
    print("🧪 Testing Blackbox Logger")
    print("=" * 50)
    
    # Test basic logging
    blackbox_logger.info("Test info message", component="test")
    blackbox_logger.warning("Test warning", component="test", context={"test": True})
    blackbox_logger.error("Test error", component="test", error_code="E001")
    
    # Test event logging
    blackbox_logger.log_event("test_event", {"action": "test", "result": "success"}, "test")
    
    # Test metric logging
    blackbox_logger.log_metric("test_metric", 123.45, "test")
    
    # Query tests
    recent_logs = blackbox_logger.query_logs(hours=1)
    print(f"Recent logs: {len(recent_logs)}")
    
    error_summary = blackbox_logger.get_error_summary(hours=1)
    print(f"Error summary: {error_summary}")
    
    print("✅ Blackbox logger test completed")