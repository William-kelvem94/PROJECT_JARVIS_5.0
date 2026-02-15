#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Resource Pool Manager
==================================
FASE 1.5: Gerenciador de pools de recursos (conexões, buffers, handles) otimizado.

Responsibilities:
- Pool management com redimensionamento dinâmico
- Health checking automático de recursos
- Circuit breakers para recursos defeituosos
- Metrics e observabilidade de utilização
- Cleanup automático de recursos vazados

Philosophy:
- Recursos caros são reutilizados
- Health checking proativo
- Auto-scaling baseado em demanda
- Observabilidade completa de recursos
- Prevenção de vazamentos (leaks)
"""

import asyncio
import logging
import threading
import time
import weakref
import inspect
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Callable, Union, TypeVar, Generic, Set, Tuple
from dataclasses import dataclass, field
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor, Future
from threading import RLock, Event as ThreadingEvent, Condition
from contextlib import contextmanager, asynccontextmanager
import uuid
import psutil
import sqlite3
import socket
import pickle

logger = logging.getLogger(__name__)

T = TypeVar('T')  # Generic resource type

class ResourceState(Enum):
    """Estados de um recurso no pool"""
    AVAILABLE = "available"      # Disponível para uso
    IN_USE = "in_use"           # Em uso
    CHECKING = "checking"        # Sendo verificado (health check)
    UNHEALTHY = "unhealthy"     # Falhando health checks
    EXPIRED = "expired"         # Expirado (TTL)
    DESTROYED = "destroyed"     # Destruído

class PoolState(Enum):
    """Estados de um pool de recursos"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    SCALING_UP = "scaling_up"
    SCALING_DOWN = "scaling_down"
    DRAINING = "draining"       # Paralisação gradual
    STOPPED = "stopped"

@dataclass
class ResourceMetrics:
    """Métricas de um recurso"""
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    last_health_check: Optional[datetime] = None
    total_uses: int = 0
    health_check_failures: int = 0
    health_check_successes: int = 0
    total_usage_time: float = 0.0
    average_usage_time: float = 0.0
    
    def record_usage(self, duration_seconds: float):
        """Record resource usage"""
        self.last_used = datetime.now()
        self.total_uses += 1
        self.total_usage_time += duration_seconds
        self.average_usage_time = self.total_usage_time / self.total_uses
    
    @property
    def idle_time(self) -> float:
        """Time since last use in seconds"""
        if self.last_used:
            return (datetime.now() - self.last_used).total_seconds()
        return (datetime.now() - self.created_at).total_seconds()
    
    @property
    def health_check_success_rate(self) -> float:
        """Health check success rate (0.0 to 1.0)"""
        total_checks = self.health_check_failures + self.health_check_successes
        if total_checks == 0:
            return 1.0
        return self.health_check_successes / total_checks

@dataclass
class PooledResource(Generic[T]):
    """Wrapper para recursos no pool"""
    resource_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    resource: Optional[T] = None
    state: ResourceState = ResourceState.AVAILABLE
    pool_name: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metrics: ResourceMetrics = field(default_factory=ResourceMetrics)
    
    # Usage tracking
    current_user: Optional[str] = None
    usage_start: Optional[datetime] = None
    
    def acquire(self, user_id: Optional[str] = None) -> bool:
        """Acquire resource for use"""
        if self.state != ResourceState.AVAILABLE:
            return False
        
        self.state = ResourceState.IN_USE
        self.current_user = user_id
        self.usage_start = datetime.now()
        return True
    
    def release(self) -> float:
        """Release resource, return usage duration"""
        if self.state != ResourceState.IN_USE or not self.usage_start:
            return 0.0
        
        duration = (datetime.now() - self.usage_start).total_seconds()
        self.metrics.record_usage(duration)
        
        self.state = ResourceState.AVAILABLE
        self.current_user = None
        self.usage_start = None
        
        return duration
    
    def is_expired(self) -> bool:
        """Check if resource is expired"""
        return bool(self.expires_at and datetime.now() > self.expires_at)
    
    def mark_unhealthy(self):
        """Mark resource as unhealthy"""
        self.state = ResourceState.UNHEALTHY
        self.metrics.health_check_failures += 1
    
    def mark_healthy(self):
        """Mark resource as healthy"""
        if self.state == ResourceState.UNHEALTHY:
            self.state = ResourceState.AVAILABLE
        self.metrics.health_check_successes += 1
        self.metrics.last_health_check = datetime.now()

class ResourceFactory(Generic[T]):
    """Factory para criação e validação de recursos"""
    
    def create_resource(self) -> T:
        """Create a new resource instance"""
        raise NotImplementedError("Subclasses must implement create_resource")
    
    def destroy_resource(self, resource: T) -> None:
        """Destroy a resource instance"""
        # Default implementation - subclasses can override
        if hasattr(resource, 'close'):
            resource.close()
    
    async def health_check(self, resource: T) -> bool:
        """Check if resource is healthy"""
        # Default implementation - always healthy
        return True
    
    def validate_resource(self, resource: T) -> bool:
        """Validate resource before returning to pool"""
        return True

class DatabaseConnectionFactory(ResourceFactory[sqlite3.Connection]):
    """Factory for SQLite database connections"""
    
    def __init__(self, db_path: str, **kwargs):
        self.db_path = db_path
        self.connection_kwargs = kwargs
    
    def create_resource(self) -> sqlite3.Connection:
        """Create database connection"""
        conn = sqlite3.connect(self.db_path, **self.connection_kwargs)
        conn.row_factory = sqlite3.Row
        return conn
    
    def destroy_resource(self, resource: sqlite3.Connection) -> None:
        """Close database connection"""
        try:
            resource.close()
        except Exception as e:
            logger.warning(f"Error closing database connection: {e}")
    
    async def health_check(self, resource: sqlite3.Connection) -> bool:
        """Check if database connection is healthy"""
        try:
            # Simple query to test connection
            cursor = resource.execute("SELECT 1")
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            logger.debug(f"Database health check failed: {e}")
            return False
    
    def validate_resource(self, resource: sqlite3.Connection) -> bool:
        """Validate database connection"""
        try:
            # Check if connection is still valid
            resource.execute("SELECT 1")
            return True
        except Exception:
            return False

class SocketConnectionFactory(ResourceFactory[socket.socket]):
    """Factory for socket connections"""
    
    def __init__(self, host: str, port: int, timeout: float = 30.0):
        self.host = host
        self.port = port
        self.timeout = timeout
    
    def create_resource(self) -> socket.socket:
        """Create socket connection"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        sock.connect((self.host, self.port))
        return sock
    
    def destroy_resource(self, resource: socket.socket) -> None:
        """Close socket connection"""
        try:
            resource.close()
        except Exception as e:
            logger.warning(f"Error closing socket: {e}")
    
    async def health_check(self, resource: socket.socket) -> bool:
        """Check if socket is healthy"""
        try:
            # Try to get socket state
            resource.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            return True
        except Exception:
            return False

class BufferFactory(ResourceFactory[bytearray]):
    """Factory for byte buffers"""
    
    def __init__(self, size: int):
        self.size = size
    
    def create_resource(self) -> bytearray:
        """Create byte buffer"""
        return bytearray(self.size)
    
    def destroy_resource(self, resource: bytearray) -> None:
        """Clear buffer (not really necessary for bytearray)"""
        pass
    
    async def health_check(self, resource: bytearray) -> bool:
        """Buffers are always healthy"""
        return True
    
    def validate_resource(self, resource: bytearray) -> bool:
        """Validate buffer size"""
        return len(resource) == self.size

@dataclass
class PoolConfig:
    """Configuração de um pool de recursos"""
    name: str
    min_size: int = 1
    max_size: int = 10
    initial_size: int = 1
    
    # Timeouts and TTL
    max_idle_seconds: float = 300      # 5 minutes
    resource_ttl_seconds: Optional[float] = None  # No expiration by default
    acquire_timeout_seconds: float = 30
    
    # Health checking
    health_check_interval_seconds: float = 60
    health_check_on_acquire: bool = True
    health_check_on_release: bool = False
    max_health_check_failures: int = 3
    
    # Scaling
    scale_up_threshold: float = 0.8    # Scale up when 80% utilization
    scale_down_threshold: float = 0.2  # Scale down when 20% utilization
    scale_check_interval_seconds: float = 30
    
    # Circuit breaker
    circuit_breaker_enabled: bool = True
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: float = 60

class ResourcePool(Generic[T]):
    """
    Pool de recursos genérico com health checking e auto-scaling
    """
    
    def __init__(self, config: PoolConfig, factory: ResourceFactory[T]):
        self.config = config
        self.factory = factory
        self.state = PoolState.INITIALIZING
        
        # Resource storage
        self._resources: Dict[str, PooledResource[T]] = {}
        self._available_queue = deque()  # Resource IDs
        self._lock = RLock()
        
        # Condition for waiting threads
        self._resource_available = Condition(self._lock)
        
        # Background tasks
        self._health_check_thread: Optional[threading.Thread] = None
        self._scaling_thread: Optional[threading.Thread] = None
        self._cleanup_thread: Optional[threading.Thread] = None
        self._running = False
        self._stop_event = ThreadingEvent()
        
        # Circuit breaker state
        self._circuit_breaker_failures = 0
        self._circuit_breaker_last_failure = None
        self._circuit_breaker_open = False
        
        # Metrics
        self.total_created = 0
        self.total_destroyed = 0
        self.total_acquisitions = 0
        self.total_releases = 0
        self.total_health_checks = 0
        self.pool_start_time: Optional[datetime] = None
        
        logger.info(f"🏊 Resource pool '{config.name}' initialized")
    
    async def start(self):
        """Start the resource pool"""
        if self._running:
            return
        
        logger.info(f"🚀 Starting resource pool '{self.config.name}'")
        
        self._running = True
        self.pool_start_time = datetime.now()
        self.state = PoolState.ACTIVE
        
        # Create initial resources
        await self._create_initial_resources()
        
        # Start background threads
        self._health_check_thread = threading.Thread(
            target=self._health_check_loop,
            name=f"health_check_{self.config.name}",
            daemon=True
        )
        self._health_check_thread.start()
        
        self._scaling_thread = threading.Thread(
            target=self._scaling_loop,
            name=f"scaling_{self.config.name}",
            daemon=True
        )
        self._scaling_thread.start()
        
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            name=f"cleanup_{self.config.name}",
            daemon=True
        )
        self._cleanup_thread.start()
        
        logger.info(f"✅ Resource pool '{self.config.name}' started")
    
    async def stop(self, timeout: float = 30.0):
        """Stop the resource pool"""
        if not self._running:
            return
        
        logger.info(f"🛑 Stopping resource pool '{self.config.name}'")
        self.state = PoolState.DRAINING
        
        self._running = False
        self._stop_event.set()
        
        # Wait for background threads
        for thread in [self._health_check_thread, self._scaling_thread, self._cleanup_thread]:
            if thread:
                thread.join(timeout=5.0)
        
        # Destroy all resources
        await self._destroy_all_resources()
        
        self.state = PoolState.STOPPED
        logger.info(f"✅ Resource pool '{self.config.name}' stopped")
    
    @asynccontextmanager
    async def acquire(self, user_id: Optional[str] = None, timeout: Optional[float] = None):
        """Acquire resource with context manager"""
        timeout = timeout or self.config.acquire_timeout_seconds
        resource = await self._acquire_resource(user_id, timeout)
        
        try:
            yield resource.resource
        finally:
            await self._release_resource(resource)
    
    async def _acquire_resource(self, user_id: Optional[str], timeout: float) -> PooledResource[T]:
        """Acquire a resource from the pool"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check circuit breaker
            if self._is_circuit_breaker_open():
                raise RuntimeError(f"Circuit breaker open for pool '{self.config.name}'")
            
            with self._lock:
                # Try to get available resource
                if self._available_queue:
                    resource_id = self._available_queue.popleft()
                    resource = self._resources.get(resource_id)
                    
                    if resource and resource.state == ResourceState.AVAILABLE:
                        # Check expiration
                        if resource.is_expired():
                            await self._destroy_resource(resource)
                            continue
                        
                        # Health check on acquire if configured
                        if self.config.health_check_on_acquire:
                            if not await self._check_resource_health(resource):
                                continue
                        
                        # Acquire resource
                        if resource.acquire(user_id):
                            self.total_acquisitions += 1
                            logger.debug(f"🔓 Acquired resource {resource_id[:8]} from pool '{self.config.name}'")
                            return resource
                
                # No available resources - try to create new one if under limit
                if len(self._resources) < self.config.max_size:
                    try:
                        resource = await self._create_resource()
                        if resource.acquire(user_id):
                            self.total_acquisitions += 1
                            return resource
                    except Exception as e:
                        logger.error(f"Failed to create resource in pool '{self.config.name}': {e}")
                        self._record_circuit_breaker_failure()
            
            # Wait for resource to become available
            with self._lock:
                self._resource_available.wait(timeout=0.1)
        
        raise TimeoutError(f"Timeout acquiring resource from pool '{self.config.name}'")
    
    async def _release_resource(self, resource: PooledResource[T]):
        """Release resource back to pool"""
        duration = resource.release()
        
        with self._lock:
            # Health check on release if configured
            if self.config.health_check_on_release:
                if not await self._check_resource_health(resource):
                    await self._destroy_resource(resource)
                    self._resource_available.notify_all()
                    return
            
            # Validate resource
            if resource.resource is not None and not self.factory.validate_resource(resource.resource):
                logger.warning(f"Resource {resource.resource_id[:8]} failed validation")
                await self._destroy_resource(resource)
                self._resource_available.notify_all()
                return
            
            # Return to available queue
            if resource.state == ResourceState.AVAILABLE:
                self._available_queue.append(resource.resource_id)
                self.total_releases += 1
                self._resource_available.notify_all()
                
                logger.debug(f"🔐 Released resource {resource.resource_id[:8]} to pool '{self.config.name}' (used {duration:.2f}s)")
    
    async def _create_initial_resources(self):
        """Create initial pool of resources"""
        tasks = []
        for _ in range(self.config.initial_size):
            tasks.append(self._create_resource())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _create_resource(self) -> PooledResource[T]:
        """Create a new resource"""
        try:
            # Create resource using factory
            resource_instance = self.factory.create_resource()
            
            # Set expiration if configured
            expires_at = None
            if self.config.resource_ttl_seconds:
                expires_at = datetime.now() + timedelta(seconds=self.config.resource_ttl_seconds)
            
            # Wrap in PooledResource
            resource = PooledResource(
                resource=resource_instance,
                pool_name=self.config.name,
                expires_at=expires_at
            )
            
            # Store in pool
            with self._lock:
                self._resources[resource.resource_id] = resource
                self._available_queue.append(resource.resource_id)
            
            self.total_created += 1
            logger.debug(f"➕ Created resource {resource.resource_id[:8]} in pool '{self.config.name}'")
            
            return resource
            
        except Exception as e:
            logger.error(f"Failed to create resource for pool '{self.config.name}': {e}")
            self._record_circuit_breaker_failure()
            raise
    
    async def _destroy_resource(self, resource: PooledResource[T]):
        """Destroy a resource"""
        try:
            # Remove from tracking
            with self._lock:
                self._resources.pop(resource.resource_id, None)
                try:
                    self._available_queue.remove(resource.resource_id)
                except ValueError:
                    pass  # Not in available queue
            
            # Destroy using factory
            resource.state = ResourceState.DESTROYED
            if resource.resource is not None:
                self.factory.destroy_resource(resource.resource)
            
            self.total_destroyed += 1
            logger.debug(f"❌ Destroyed resource {resource.resource_id[:8]} from pool '{self.config.name}'")
            
        except Exception as e:
            logger.error(f"Error destroying resource {resource.resource_id[:8]}: {e}")
    
    async def _destroy_all_resources(self):
        """Destroy all resources in pool"""
        with self._lock:
            resource_list = list(self._resources.values())
        
        for resource in resource_list:
            await self._destroy_resource(resource)
    
    async def _check_resource_health(self, resource: PooledResource[T]) -> bool:
        """Check if resource is healthy"""
        try:
            resource.state = ResourceState.CHECKING
            if resource.resource is not None:
                is_healthy = await self.factory.health_check(resource.resource)
            else:
                is_healthy = False
            
            if is_healthy:
                resource.mark_healthy()
            else:
                resource.mark_unhealthy()
                if resource.metrics.health_check_failures >= self.config.max_health_check_failures:
                    logger.warning(f"Resource {resource.resource_id[:8]} exceeded health check failures")
                    await self._destroy_resource(resource)
                    return False
            
            self.total_health_checks += 1
            return is_healthy
            
        except Exception as e:
            logger.error(f"Health check error for resource {resource.resource_id[:8]}: {e}")
            resource.mark_unhealthy()
            return False
    
    def _health_check_loop(self):
        """Background health checking loop"""
        while self._running:
            try:
                asyncio.run(self._run_health_checks())
                
                self._stop_event.wait(timeout=self.config.health_check_interval_seconds)
                
            except Exception as e:
                logger.error(f"Health check loop error for pool '{self.config.name}': {e}")
                time.sleep(5.0)
    
    async def _run_health_checks(self):
        """Run health checks on idle resources"""
        with self._lock:
            idle_resources = [
                resource for resource in self._resources.values()
                if resource.state == ResourceState.AVAILABLE and 
                resource.metrics.idle_time > self.config.health_check_interval_seconds
            ]
        
        for resource in idle_resources:
            await self._check_resource_health(resource)
    
    def _scaling_loop(self):
        """Background scaling loop"""
        while self._running:
            try:
                asyncio.run(self._check_scaling())
                
                self._stop_event.wait(timeout=self.config.scale_check_interval_seconds)
                
            except Exception as e:
                logger.error(f"Scaling loop error for pool '{self.config.name}': {e}")
                time.sleep(5.0)
    
    async def _check_scaling(self):
        """Check if pool needs scaling"""
        with self._lock:
            total_resources = len(self._resources)
            available_resources = len(self._available_queue)
            in_use_resources = total_resources - available_resources
            
            if total_resources == 0:
                return
            
            utilization = in_use_resources / total_resources
            
            # Scale up
            if (utilization > self.config.scale_up_threshold and 
                total_resources < self.config.max_size):
                
                self.state = PoolState.SCALING_UP
                scale_up_count = min(2, self.config.max_size - total_resources)
                
                logger.info(f"📈 Scaling up pool '{self.config.name}' by {scale_up_count} resources (utilization: {utilization:.2%})")
                
                for _ in range(scale_up_count):
                    try:
                        await self._create_resource()
                    except Exception as e:
                        logger.error(f"Failed to scale up pool '{self.config.name}': {e}")
                        break
                
                self.state = PoolState.ACTIVE
            
            # Scale down
            elif (utilization < self.config.scale_down_threshold and 
                  total_resources > self.config.min_size):
                
                self.state = PoolState.SCALING_DOWN
                scale_down_count = min(2, total_resources - self.config.min_size)
                
                logger.info(f"📉 Scaling down pool '{self.config.name}' by {scale_down_count} resources (utilization: {utilization:.2%})")
                
                # Remove oldest idle resources
                idle_resources = sorted([
                    resource for resource in self._resources.values()
                    if resource.state == ResourceState.AVAILABLE
                ], key=lambda r: r.metrics.last_used or r.created_at)
                
                for resource in idle_resources[:scale_down_count]:
                    await self._destroy_resource(resource)
                
                self.state = PoolState.ACTIVE
    
    def _cleanup_loop(self):
        """Background cleanup loop"""
        while self._running:
            try:
                asyncio.run(self._cleanup_expired_resources())
                
                self._stop_event.wait(timeout=60.0)  # Check every minute
                
            except Exception as e:
                logger.error(f"Cleanup loop error for pool '{self.config.name}': {e}")
                time.sleep(5.0)
    
    async def _cleanup_expired_resources(self):
        """Clean up expired and idle resources"""
        current_time = datetime.now()
        
        with self._lock:
            resources_to_cleanup = []
            
            for resource in self._resources.values():
                # Check expiration
                if resource.is_expired():
                    resources_to_cleanup.append(resource)
                    continue
                
                # Check idle timeout
                if (resource.state == ResourceState.AVAILABLE and
                    resource.metrics.idle_time > self.config.max_idle_seconds):
                    # Don't remove if we'd go below minimum
                    if len(self._resources) > self.config.min_size:
                        resources_to_cleanup.append(resource)
        
        # Clean up resources (outside the lock)
        for resource in resources_to_cleanup:
            logger.debug(f"🧹 Cleaning up resource {resource.resource_id[:8]} from pool '{self.config.name}'")
            await self._destroy_resource(resource)
    
    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open"""
        if not self.config.circuit_breaker_enabled:
            return False
        
        if not self._circuit_breaker_open:
            return False
        
        # Check if recovery timeout has passed
        if self._circuit_breaker_last_failure:
            elapsed = (datetime.now() - self._circuit_breaker_last_failure).total_seconds()
            if elapsed > self.config.circuit_breaker_recovery_timeout:
                logger.info(f"🔄 Circuit breaker recovering for pool '{self.config.name}'")
                self._circuit_breaker_open = False
                self._circuit_breaker_failures = 0
                return False
        
        return True
    
    def _record_circuit_breaker_failure(self):
        """Record a failure for circuit breaker"""
        if not self.config.circuit_breaker_enabled:
            return
        
        self._circuit_breaker_failures += 1
        self._circuit_breaker_last_failure = datetime.now()
        
        if self._circuit_breaker_failures >= self.config.circuit_breaker_failure_threshold:
            if not self._circuit_breaker_open:
                logger.error(f"💥 Circuit breaker opened for pool '{self.config.name}' after {self._circuit_breaker_failures} failures")
                self._circuit_breaker_open = True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        with self._lock:
            total_resources = len(self._resources)
            available_resources = len(self._available_queue)
            in_use_resources = total_resources - available_resources
            
            # Resource states breakdown
            state_counts = defaultdict(int)
            healthy_resources = 0
            unhealthy_resources = 0
            
            for resource in self._resources.values():
                state_counts[resource.state.value] += 1
                if resource.metrics.health_check_success_rate > 0.8:
                    healthy_resources += 1
                else:
                    unhealthy_resources += 1
            
            utilization = (in_use_resources / total_resources * 100) if total_resources > 0 else 0
            
            uptime = None
            if self.pool_start_time:
                uptime = (datetime.now() - self.pool_start_time).total_seconds()
            
            return {
                "name": self.config.name,
                "state": self.state.value,
                "uptime_seconds": uptime,
                "total_resources": total_resources,
                "available_resources": available_resources,
                "in_use_resources": in_use_resources,
                "utilization_percent": utilization,
                "healthy_resources": healthy_resources,
                "unhealthy_resources": unhealthy_resources,
                "resource_states": dict(state_counts),
                "total_created": self.total_created,
                "total_destroyed": self.total_destroyed,
                "total_acquisitions": self.total_acquisitions,
                "total_releases": self.total_releases,
                "total_health_checks": self.total_health_checks,
                "circuit_breaker": {
                    "enabled": self.config.circuit_breaker_enabled,
                    "open": self._circuit_breaker_open,
                    "failures": self._circuit_breaker_failures
                },
                "config": {
                    "min_size": self.config.min_size,
                    "max_size": self.config.max_size,
                    "max_idle_seconds": self.config.max_idle_seconds,
                    "health_check_interval": self.config.health_check_interval_seconds
                }
            }

class ResourcePoolManager:
    """
    Resource Pool Manager for JARVIS 5.0
    
    Central manager for all resource pools with monitoring and coordination.
    """
    
    def __init__(self):
        self._pools: Dict[str, ResourcePool] = {}
        self._lock = RLock()
        self.manager_start_time = datetime.now()
        
        logger.info("🏊‍♂️ Resource Pool Manager initialized")
    
    def register_pool(self, pool: ResourcePool) -> str:
        """Register a resource pool"""
        with self._lock:
            pool_name = pool.config.name
            self._pools[pool_name] = pool
            logger.info(f"📋 Registered pool '{pool_name}'")
            return pool_name
    
    def unregister_pool(self, pool_name: str) -> bool:
        """Unregister a resource pool"""
        with self._lock:
            if pool_name in self._pools:
                del self._pools[pool_name]
                logger.info(f"🚫 Unregistered pool '{pool_name}'")
                return True
            return False
    
    def get_pool(self, pool_name: str) -> Optional[ResourcePool]:
        """Get a resource pool by name"""
        with self._lock:
            return self._pools.get(pool_name)
    
    async def start_all_pools(self):
        """Start all registered pools"""
        logger.info("🚀 Starting all resource pools")
        
        start_tasks = []
        with self._lock:
            for pool in self._pools.values():
                start_tasks.append(pool.start())
        
        if start_tasks:
            await asyncio.gather(*start_tasks, return_exceptions=True)
        
        logger.info("✅ All resource pools started")
    
    async def stop_all_pools(self, timeout: float = 30.0):
        """Stop all registered pools"""
        logger.info("🛑 Stopping all resource pools")
        
        stop_tasks = []
        with self._lock:
            for pool in self._pools.values():
                stop_tasks.append(pool.stop(timeout))
        
        if stop_tasks:
            await asyncio.gather(*stop_tasks, return_exceptions=True)
        
        logger.info("✅ All resource pools stopped")
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all pools"""
        with self._lock:
            pools_stats = {}
            total_resources = 0
            total_acquisitions = 0
            
            for pool_name, pool in self._pools.items():
                stats = pool.get_stats()
                pools_stats[pool_name] = stats
                total_resources += stats.get("total_resources", 0)
                total_acquisitions += stats.get("total_acquisitions", 0)
            
            uptime = (datetime.now() - self.manager_start_time).total_seconds()
            
            return {
                "manager": {
                    "uptime_seconds": uptime,
                    "total_pools": len(self._pools),
                    "total_resources_across_pools": total_resources,
                    "total_acquisitions_across_pools": total_acquisitions
                },
                "pools": pools_stats
            }

# Global instance
resource_pool_manager = ResourcePoolManager()

if __name__ == "__main__":
    pass