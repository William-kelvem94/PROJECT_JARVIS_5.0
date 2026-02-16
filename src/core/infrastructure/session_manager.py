#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Multithread Session Manager
========================================
FASE 1.4: Gerenciamento de sessões threadsafe com pools de threads e shared memory.

Responsibilities:
- Gerenciamento de sessões de usuário threadsafe
- Pools de threads para processamento paralelo
- Shared memory para comunicação entre threads
- Session lifecycle com cleanup automático
- Metrics e observabilidade de performance

Philosophy:
- Sessões isoladas mas eficientes
- Threading seguro com locks granulares
- Shared memory para performance crítica
- Cleanup automático de recursos
- Observabilidade completa de threading
"""

import logging
import threading
import time
import multiprocessing
import mmap
import tempfile
import os
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from threading import RLock, Event as ThreadingEvent
import uuid
import psutil

logger = logging.getLogger(__name__)


class SessionManager:
    """Stub for SessionManager functionality"""

    def __init__(self):
        logger.warning("⚠️ SessionManager is a stub - functionality not implemented")

    def start(self):
        pass

    def stop(self):
        pass

    def create_session(self, session_id):
        return None

    def end_session(self, session_id):
        pass

    def get_manager_stats(self):
        return {}


# Singleton instance
session_manager = SessionManager()


class SessionState(Enum):
    """Estados de uma sessão"""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    IDLE = "idle"
    SUSPENDED = "suspended"
    TERMINATING = "terminating"
    TERMINATED = "terminated"


class ThreadPoolType(Enum):
    """Tipos de thread pools"""

    IO_BOUND = "io_bound"  # Para operações I/O (rede, disco)
    CPU_BOUND = "cpu_bound"  # Para processamento pesado
    UI_UPDATES = "ui_updates"  # Para atualizações de UI
    AI_PROCESSING = "ai_processing"  # Para processamento de IA
    BACKGROUND = "background"  # Para tarefas em background


@dataclass
class ThreadPoolConfig:
    """Configuração de um thread pool"""

    pool_type: ThreadPoolType
    min_workers: int = 1
    max_workers: int = 10
    keepalive_seconds: float = 60.0
    queue_size: int = 1000
    thread_name_prefix: str = ""


@dataclass
class SessionMetrics:
    """Métricas de uma sessão"""

    session_start: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    total_requests: int = 0
    active_threads: int = 0
    peak_threads: int = 0
    total_thread_time: float = 0.0
    memory_peak_mb: float = 0.0
    errors_count: int = 0

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()

    @property
    def session_duration(self) -> float:
        """Session duration in seconds"""
        return (datetime.now() - self.session_start).total_seconds()

    @property
    def idle_time(self) -> float:
        """Time since last activity in seconds"""
        return (datetime.now() - self.last_activity).total_seconds()


class SharedMemoryManager:
    """Manager para shared memory entre threads"""

    def __init__(self, max_size_mb: int = 100):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self._memory_regions: Dict[str, Tuple[mmap.mmap, int]] = {}
        self._lock = RLock()
        self._total_allocated = 0

    def allocate(self, key: str, size_bytes: int) -> Optional[mmap.mmap]:
        """Allocate shared memory region"""
        with self._lock:
            if key in self._memory_regions:
                logger.warning(f"Memory region '{key}' already exists")
                return self._memory_regions[key][0]

            if self._total_allocated + size_bytes > self.max_size_bytes:
                logger.error(f"Cannot allocate {size_bytes} bytes - would exceed limit")
                return None

            try:
                # Create temporary file for memory mapping
                fd, temp_path = tempfile.mkstemp()
                os.ftruncate(fd, size_bytes)

                # Create memory map
                mm = mmap.mmap(fd, size_bytes)
                os.close(fd)  # Close file descriptor, keep mapping
                os.unlink(temp_path)  # Remove temp file

                self._memory_regions[key] = (mm, size_bytes)
                self._total_allocated += size_bytes

                logger.debug(f"Allocated {size_bytes} bytes for region '{key}'")
                return mm

            except Exception as e:
                logger.error(f"Failed to allocate memory region: {e}")
                return None

    def get_region(self, key: str) -> Optional[mmap.mmap]:
        """Get existing memory region"""
        with self._lock:
            region_info = self._memory_regions.get(key)
            return region_info[0] if region_info else None

    def deallocate(self, key: str) -> bool:
        """Deallocate memory region"""
        with self._lock:
            if key not in self._memory_regions:
                return False

            mm, size = self._memory_regions[key]
            try:
                mm.close()
                del self._memory_regions[key]
                self._total_allocated -= size

                logger.debug(f"Deallocated memory region '{key}' ({size} bytes)")
                return True

            except Exception as e:
                logger.error(f"Error deallocating memory region '{key}': {e}")
                return False

    def get_stats(self) -> Dict[str, Any]:
        """Get memory manager statistics"""
        with self._lock:
            return {
                "total_regions": len(self._memory_regions),
                "total_allocated_bytes": self._total_allocated,
                "total_allocated_mb": self._total_allocated / (1024 * 1024),
                "max_size_mb": self.max_size_bytes / (1024 * 1024),
                "utilization_percent": (self._total_allocated / self.max_size_bytes)
                * 100,
                "regions": list(self._memory_regions.keys()),
            }


class ThreadSafeCache:
    """Cache threadsafe para dados de sessão"""

    def __init__(self, max_size: int = 1000, ttl_seconds: float = 3600):
        self._cache: Dict[str, Tuple[Any, float]] = {}  # key -> (value, timestamp)
        self._lock = RLock()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._hits = 0
        self._misses = 0

    def get(self, key: str, default: Any = None) -> Any:
        """Get item from cache"""
        with self._lock:
            if key in self._cache:
                value, timestamp = self._cache[key]

                # Check TTL
                if time.time() - timestamp < self.ttl_seconds:
                    self._hits += 1
                    return value
                else:
                    # Expired
                    del self._cache[key]

            self._misses += 1
            return default

    def set(self, key: str, value: Any) -> None:
        """Set item in cache"""
        with self._lock:
            # Cleanup if at max size
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._cleanup_expired()

                # If still at capacity, remove oldest items
                if len(self._cache) >= self.max_size:
                    oldest_keys = sorted(
                        self._cache.keys(), key=lambda k: self._cache[k][1]
                    )[:10]
                    for old_key in oldest_keys:
                        del self._cache[old_key]

            self._cache[key] = (value, time.time())

    def delete(self, key: str) -> bool:
        """Delete item from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def _cleanup_expired(self) -> None:
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key
            for key, (_, timestamp) in self._cache.items()
            if current_time - timestamp >= self.ttl_seconds
        ]

        for key in expired_keys:
            del self._cache[key]

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            self._cleanup_expired()

            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate_percent": hit_rate,
                "ttl_seconds": self.ttl_seconds,
            }


class SessionData:
    """Dados threadsafe de uma sessão"""

    def __init__(self, session_id: str, user_id: Optional[str] = None):
        self.session_id = session_id
        self.user_id = user_id
        self.state = SessionState.INITIALIZING
        self.created_at = datetime.now()

        # Thread safety
        self._lock = RLock()
        self._data_lock = RLock()

        # Session data storage
        self._data: Dict[str, Any] = {}
        self._cache = ThreadSafeCache()

        # Thread management
        self._thread_pools: Dict[ThreadPoolType, ThreadPoolExecutor] = {}
        self._active_futures: Set[Future] = set()
        self._cleanup_event = ThreadingEvent()

        # Metrics
        self.metrics = SessionMetrics()

        # Shared memory for this session
        self._shared_memory_keys: Set[str] = set()

        logger.debug(f"🆕 Session created: {session_id[:8]}")

    def set_state(self, new_state: SessionState):
        """Set session state threadsafely"""
        with self._lock:
            old_state = self.state
            self.state = new_state
            self.metrics.update_activity()
            logger.debug(
                f"📊 Session {self.session_id[:8]}: {old_state.value} -> {new_state.value}"
            )

    def get_data(self, key: str, default: Any = None) -> Any:
        """Get session data threadsafely"""
        with self._data_lock:
            # Try cache first
            cached = self._cache.get(key)
            if cached is not None:
                return cached

            # Get from main storage
            value = self._data.get(key, default)
            if value != default:
                self._cache.set(key, value)

            return value

    def set_data(self, key: str, value: Any) -> None:
        """Set session data threadsafely"""
        with self._data_lock:
            self._data[key] = value
            self._cache.set(key, value)
            self.metrics.update_activity()

    def delete_data(self, key: str) -> bool:
        """Delete session data threadsafely"""
        with self._data_lock:
            self._cache.delete(key)
            if key in self._data:
                del self._data[key]
                self.metrics.update_activity()
                return True
            return False

    def get_all_data(self) -> Dict[str, Any]:
        """Get copy of all session data"""
        with self._data_lock:
            return self._data.copy()

    def get_thread_pool(
        self, pool_type: ThreadPoolType, max_workers: Optional[int] = None
    ) -> ThreadPoolExecutor:
        """Get or create thread pool for this session"""
        with self._lock:
            if pool_type not in self._thread_pools:
                # Default configurations
                default_configs = {
                    ThreadPoolType.IO_BOUND: ThreadPoolConfig(pool_type, 2, 10),
                    ThreadPoolType.CPU_BOUND: ThreadPoolConfig(
                        pool_type, 1, multiprocessing.cpu_count()
                    ),
                    ThreadPoolType.UI_UPDATES: ThreadPoolConfig(pool_type, 1, 2),
                    ThreadPoolType.AI_PROCESSING: ThreadPoolConfig(pool_type, 1, 4),
                    ThreadPoolType.BACKGROUND: ThreadPoolConfig(pool_type, 1, 5),
                }

                config = default_configs.get(pool_type, ThreadPoolConfig(pool_type))
                if max_workers:
                    config.max_workers = max_workers

                # Create thread pool
                self._thread_pools[pool_type] = ThreadPoolExecutor(
                    max_workers=config.max_workers,
                    thread_name_prefix=f"session_{self.session_id[:8]}_{pool_type.value}",
                )

                logger.debug(
                    f"🧵 Created {pool_type.value} thread pool for session {self.session_id[:8]}"
                )

            return self._thread_pools[pool_type]

    def submit_task(
        self, pool_type: ThreadPoolType, func: Callable, *args, **kwargs
    ) -> Future:
        """Submit task to thread pool"""
        pool = self.get_thread_pool(pool_type)
        future = pool.submit(func, *args, **kwargs)

        with self._lock:
            self._active_futures.add(future)
            self.metrics.total_requests += 1
            self.metrics.active_threads = len(self._active_futures)
            self.metrics.peak_threads = max(
                self.metrics.peak_threads, self.metrics.active_threads
            )
            self.metrics.update_activity()

        # Add done callback to clean up future
        future.add_done_callback(self._on_future_done)

        return future

    def _on_future_done(self, future: Future):
        """Callback when future completes"""
        with self._lock:
            self._active_futures.discard(future)
            self.metrics.active_threads = len(self._active_futures)

            # Track errors
            if future.exception():
                self.metrics.errors_count += 1
                logger.warning(
                    f"Task error in session {self.session_id[:8]}: {future.exception()}"
                )

    def wait_for_tasks(self, timeout: Optional[float] = None) -> bool:
        """Wait for all active tasks to complete"""
        start_time = time.time()

        while self._active_futures:
            if timeout and (time.time() - start_time) > timeout:
                logger.warning(
                    f"Timeout waiting for tasks in session {self.session_id[:8]}"
                )
                return False

            # Wait for any future to complete
            if self._active_futures:
                try:
                    next(as_completed(list(self._active_futures), timeout=1.0))
                except:
                    continue

            time.sleep(0.1)

        return True

    def allocate_shared_memory(
        self, key: str, size_bytes: int, memory_manager: SharedMemoryManager
    ) -> Optional[mmap.mmap]:
        """Allocate shared memory for this session"""
        full_key = f"{self.session_id}_{key}"
        mm = memory_manager.allocate(full_key, size_bytes)

        if mm:
            with self._lock:
                self._shared_memory_keys.add(full_key)

        return mm

    def get_shared_memory(
        self, key: str, memory_manager: SharedMemoryManager
    ) -> Optional[mmap.mmap]:
        """Get shared memory region"""
        full_key = f"{self.session_id}_{key}"
        return memory_manager.get_region(full_key)

    def cleanup(self, memory_manager: SharedMemoryManager):
        """Cleanup session resources"""
        logger.info(f"🧹 Cleaning up session {self.session_id[:8]}")

        with self._lock:
            self.set_state(SessionState.TERMINATING)

            # Cancel active tasks
            for future in list(self._active_futures):
                future.cancel()

            # Wait briefly for tasks to complete
            self.wait_for_tasks(timeout=5.0)

            # Shutdown thread pools
            for pool_type, pool in self._thread_pools.items():
                try:
                    pool.shutdown(wait=True)
                    logger.debug(
                        f"Shutdown {pool_type.value} pool for session {self.session_id[:8]}"
                    )
                except Exception as e:
                    logger.error(f"Error shutting down {pool_type.value} pool: {e}")

            self._thread_pools.clear()

            # Clean up shared memory
            for memory_key in list(self._shared_memory_keys):
                memory_manager.deallocate(memory_key)
            self._shared_memory_keys.clear()

            # Clear caches and data
            self._cache.clear()
            self._data.clear()

            self.set_state(SessionState.TERMINATED)

        logger.info(f"✅ Session {self.session_id[:8]} cleanup complete")

    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        with self._lock:
            # Update memory usage
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            self.metrics.memory_peak_mb = max(self.metrics.memory_peak_mb, memory_mb)

            thread_pool_stats = {}
            for pool_type, pool in self._thread_pools.items():
                thread_pool_stats[pool_type.value] = {
                    "max_workers": pool._max_workers,
                    "active_threads": len([t for t in pool._threads if t.is_alive()]),
                    "queue_size": pool._work_queue.qsize(),
                }

            return {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "state": self.state.value,
                "duration_seconds": self.metrics.session_duration,
                "idle_seconds": self.metrics.idle_time,
                "total_requests": self.metrics.total_requests,
                "active_threads": self.metrics.active_threads,
                "peak_threads": self.metrics.peak_threads,
                "errors_count": self.metrics.errors_count,
                "memory_peak_mb": self.metrics.memory_peak_mb,
                "cache_stats": self._cache.get_stats(),
                "thread_pools": thread_pool_stats,
                "shared_memory_regions": len(self._shared_memory_keys),
                "data_keys": len(self._data),
            }


class MultithreadSessionManager:
    """
    Session Manager multithread para JARVIS 5.0

    Gerencia sessões de usuário com pools de threads dedicados,
    shared memory e cleanup automático. Threading totalmente seguro.
    """

    def __init__(
        self,
        max_sessions: int = 100,
        session_timeout_minutes: float = 60,
        cleanup_interval_seconds: float = 300,  # 5 minutes
        shared_memory_mb: int = 100,
    ):

        # Core state
        self._sessions: Dict[str, SessionData] = {}
        self._user_sessions: Dict[str, Set[str]] = defaultdict(
            set
        )  # user_id -> session_ids

        # Thread safety
        self._lock = RLock()
        self._cleanup_lock = RLock()

        # Configuration
        self.max_sessions = max_sessions
        self.session_timeout_seconds = session_timeout_minutes * 60
        self.cleanup_interval_seconds = cleanup_interval_seconds

        # Shared resources
        self.shared_memory = SharedMemoryManager(shared_memory_mb)

        # Background cleanup
        self._cleanup_thread: Optional[threading.Thread] = None
        self._running = False
        self._cleanup_event = ThreadingEvent()

        # Metrics
        self.total_sessions_created = 0
        self.total_sessions_cleaned = 0
        self.manager_start_time = datetime.now()

        logger.info("👥 Multithread Session Manager initialized")

    def start(self):
        """Start the session manager"""
        if self._running:
            return

        self._running = True

        # Start cleanup thread
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop, name="session_cleanup", daemon=True
        )
        self._cleanup_thread.start()

        logger.info("🚀 Session Manager started")

    def stop(self, timeout: float = 30.0):
        """Stop the session manager"""
        if not self._running:
            return

        logger.info("🛑 Stopping Session Manager...")
        self._running = False
        self._cleanup_event.set()

        # Wait for cleanup thread
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5.0)

        # Cleanup all sessions
        with self._lock:
            session_ids = list(self._sessions.keys())

        for session_id in session_ids:
            self.end_session(session_id)

        logger.info("✅ Session Manager stopped")

    def create_session(
        self,
        user_id: Optional[str] = None,
        session_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create new session"""
        with self._lock:
            # Check session limit
            if len(self._sessions) >= self.max_sessions:
                # Try to clean up expired sessions
                self._cleanup_expired_sessions()

                if len(self._sessions) >= self.max_sessions:
                    raise RuntimeError(
                        f"Maximum sessions limit reached ({self.max_sessions})"
                    )

            # Create session
            session_id = str(uuid.uuid4())
            session = SessionData(session_id, user_id)

            # Set initial data
            if session_data:
                for key, value in session_data.items():
                    session.set_data(key, value)

            # Register session
            self._sessions[session_id] = session
            if user_id:
                self._user_sessions[user_id].add(session_id)

            self.total_sessions_created += 1
            session.set_state(SessionState.ACTIVE)

            logger.info(f"🆕 Created session {session_id[:8]} for user {user_id}")
            return session_id

    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session by ID"""
        with self._lock:
            session = self._sessions.get(session_id)
            if session and session.state not in [
                SessionState.TERMINATED,
                SessionState.TERMINATING,
            ]:
                session.metrics.update_activity()
                return session
            return None

    def get_user_sessions(self, user_id: str) -> List[SessionData]:
        """Get all active sessions for a user"""
        with self._lock:
            session_ids = self._user_sessions.get(user_id, set())
            sessions = []

            for session_id in list(
                session_ids
            ):  # Copy to avoid modification during iteration
                session = self._sessions.get(session_id)
                if session and session.state not in [
                    SessionState.TERMINATED,
                    SessionState.TERMINATING,
                ]:
                    sessions.append(session)
                else:
                    # Clean up stale reference
                    self._user_sessions[user_id].discard(session_id)

            return sessions

    def end_session(self, session_id: str) -> bool:
        """End a session"""
        with self._cleanup_lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            # Clean up resources
            session.cleanup(self.shared_memory)

            # Remove from tracking
            with self._lock:
                del self._sessions[session_id]
                if session.user_id:
                    self._user_sessions[session.user_id].discard(session_id)
                    if not self._user_sessions[session.user_id]:
                        del self._user_sessions[session.user_id]

            self.total_sessions_cleaned += 1
            logger.info(f"🏁 Ended session {session_id[:8]}")
            return True

    def end_user_sessions(self, user_id: str) -> int:
        """End all sessions for a user"""
        sessions = self.get_user_sessions(user_id)
        count = 0

        for session in sessions:
            if self.end_session(session.session_id):
                count += 1

        return count

    def suspend_session(self, session_id: str) -> bool:
        """Suspend a session (reduce memory footprint)"""
        session = self.get_session(session_id)
        if not session:
            return False

        session.set_state(SessionState.SUSPENDED)
        # Could serialize and cache data to disk here
        logger.debug(f"💤 Suspended session {session_id[:8]}")
        return True

    def resume_session(self, session_id: str) -> bool:
        """Resume a suspended session"""
        session = self.get_session(session_id)
        if not session or session.state != SessionState.SUSPENDED:
            return False

        session.set_state(SessionState.ACTIVE)
        # Could deserialize data from disk here
        logger.debug(f"🔄 Resumed session {session_id[:8]}")
        return True

    def submit_task_to_session(
        self,
        session_id: str,
        pool_type: ThreadPoolType,
        func: Callable,
        *args,
        **kwargs,
    ) -> Optional[Future]:
        """Submit task to a specific session's thread pool"""
        session = self.get_session(session_id)
        if not session:
            return None

        return session.submit_task(pool_type, func, *args, **kwargs)

    def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed statistics for a session"""
        session = self.get_session(session_id)
        if not session:
            return None

        return session.get_stats()

    def get_manager_stats(self) -> Dict[str, Any]:
        """Get comprehensive manager statistics"""
        with self._lock:
            # Count sessions by state
            state_counts = defaultdict(int)
            total_threads = 0
            total_requests = 0
            total_errors = 0

            for session in self._sessions.values():
                state_counts[session.state.value] += 1
                total_threads += session.metrics.active_threads
                total_requests += session.metrics.total_requests
                total_errors += session.metrics.errors_count

            uptime = (datetime.now() - self.manager_start_time).total_seconds()

            return {
                "running": self._running,
                "uptime_seconds": uptime,
                "total_sessions": len(self._sessions),
                "max_sessions": self.max_sessions,
                "total_created": self.total_sessions_created,
                "total_cleaned": self.total_sessions_cleaned,
                "total_active_threads": total_threads,
                "total_requests": total_requests,
                "total_errors": total_errors,
                "sessions_by_state": dict(state_counts),
                "session_timeout_seconds": self.session_timeout_seconds,
                "shared_memory": self.shared_memory.get_stats(),
            }

    def get_all_session_stats(self) -> List[Dict[str, Any]]:
        """Get stats for all sessions"""
        with self._lock:
            return [session.get_stats() for session in self._sessions.values()]

    def _cleanup_loop(self):
        """Background cleanup loop"""
        while self._running:
            try:
                self._cleanup_expired_sessions()

                # Wait for next cleanup or stop signal
                self._cleanup_event.wait(timeout=self.cleanup_interval_seconds)
                self._cleanup_event.clear()

            except Exception as e:
                logger.error(f"Session cleanup error: {e}")

    def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.now()
        expired_sessions = []

        with self._lock:
            for session_id, session in self._sessions.items():
                # Check if session is expired
                if (
                    session.metrics.idle_time > self.session_timeout_seconds
                    and session.state in [SessionState.IDLE, SessionState.ACTIVE]
                ):
                    expired_sessions.append(session_id)

        # Clean up expired sessions (outside the main lock)
        for session_id in expired_sessions:
            logger.info(f"⏰ Cleaning expired session {session_id[:8]}")
            self.end_session(session_id)


# Global instance
session_manager = MultithreadSessionManager()

if __name__ == "__main__":
    # Test the session manager
    def test_session_manager():
        print("🧪 Testing Multithread Session Manager")
        print("=" * 50)

        # Start manager
        session_manager.start()

        # Create test session
        session_id = session_manager.create_session("test_user", {"test": "data"})
        print(f"📋 Created session: {session_id[:8]}")

        # Get session and test thread pool
        session = session_manager.get_session(session_id)
        if session:
            # Test CPU-bound task
            def cpu_task(n):
                result = sum(i * i for i in range(n))
                print(f"🧮 CPU task result: {result}")
                return result

            future = session.submit_task(ThreadPoolType.CPU_BOUND, cpu_task, 1000000)
            print(f"🔄 Submitted CPU task, result: {future.result()}")

            # Test shared memory
            mm = session.allocate_shared_memory(
                "test_data", 1024, session_manager.shared_memory
            )
            if mm:
                mm.write(b"Hello, shared memory!")
                mm.seek(0)
                data = mm.read(22).decode()
                print(f"💾 Shared memory data: {data}")

            # Show session stats
            stats = session.get_stats()
            print("📊 Session stats:")
            for key, value in stats.items():
                if isinstance(value, dict):
                    print(f"  {key}:")
                    for k, v in value.items():
                        print(f"    {k}: {v}")
                else:
                    print(f"  {key}: {value}")

        # Show manager stats
        print("\n📊 Manager Stats:")
        manager_stats = session_manager.get_manager_stats()
        for key, value in manager_stats.items():
            if isinstance(value, dict):
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value}")

        # Clean up
        session_manager.end_session(session_id)
        session_manager.stop()

        print("✅ Test completed")

    test_session_manager()
