#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Circuit Breaker Pattern Implementation
==================================================
FASE 1.7: Implementação do padrão Circuit Breaker para resiliência contra falhas.

Responsibilities:
- Circuit breakers para todas operações críticas
- Auto-recovery com backoff exponencial
- Fallback strategies para degradação graciosa
- Metrics e alertas de falhas
- Health checking proativo

Philosophy:
- Falhar rápido para preservar sistema
- Auto-recovery inteligente
- Fallbacks para continuidade de serviço
- Observabilidade completa de falhas
- Prevenção de falhas em cascata
"""

import asyncio
import logging
import threading
import time
import functools
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Callable, Union, Awaitable, TypeVar, Generic
from dataclasses import dataclass, field
from collections import deque, defaultdict
import uuid
import statistics
import inspect

logger = logging.getLogger(__name__)

T = TypeVar('T')

class CircuitState(Enum):
    """Estados do circuit breaker"""
    CLOSED = "closed"           # Funcionando normalmente
    OPEN = "open"              # Bloqueando chamadas (muitas falhas)
    HALF_OPEN = "half_open"    # Testando se pode voltar ao normal

class FailureType(Enum):
    """Tipos de falhas"""
    TIMEOUT = "timeout"
    EXCEPTION = "exception"
    INVALID_RESPONSE = "invalid_response"
    RATE_LIMIT = "rate_limit"
    SERVICE_UNAVAILABLE = "service_unavailable"

@dataclass
class CircuitBreakerConfig:
    """Configuração do circuit breaker"""
    name: str
    
    # Failure thresholds
    failure_threshold: int = 5              # Falhas para abrir circuito
    success_threshold: int = 3              # Sucessos para fechar circuito
    timeout_seconds: float = 30.0           # Timeout para operações
    
    # Recovery settings
    recovery_timeout_seconds: float = 60.0  # Tempo para tentar half-open
    max_recovery_timeout: float = 300.0     # Máximo tempo de recovery
    backoff_multiplier: float = 2.0         # Multiplicador de backoff
    
    # Monitoring window
    window_size_seconds: float = 60.0       # Janela de monitoramento
    min_calls_threshold: int = 10           # Mínimo de calls para avaliar
    
    # Health checking
    health_check_enabled: bool = True
    health_check_interval_seconds: float = 30.0
    
    # Fallback
    fallback_enabled: bool = True

@dataclass
class CallResult:
    """Resultado de uma chamada"""
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    duration_seconds: float = 0.0
    failure_type: Optional[FailureType] = None
    error_message: Optional[str] = None
    response_data: Any = None

@dataclass 
class CircuitMetrics:
    """Métricas do circuit breaker"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    timeout_calls: int = 0
    rejected_calls: int = 0              # Calls rejeitadas enquanto aberto
    
    # Timing metrics
    total_response_time: float = 0.0
    fastest_response: float = float('inf')
    slowest_response: float = 0.0
    
    # State transitions
    times_opened: int = 0
    times_closed: int = 0
    times_half_opened: int = 0
    
    # Current state info
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    state_since: datetime = field(default_factory=datetime.now)
    
    # Recent call history (sliding window)
    recent_calls: deque = field(default_factory=lambda: deque(maxlen=100))
    
    def record_call(self, result: CallResult):
        """Record call result"""
        self.total_calls += 1
        self.recent_calls.append(result)
        
        if result.success:
            self.successful_calls += 1
            self.last_success_time = result.timestamp
        else:
            self.failed_calls += 1
            self.last_failure_time = result.timestamp
            
            if result.failure_type == FailureType.TIMEOUT:
                self.timeout_calls += 1
        
        # Update timing metrics
        if result.duration_seconds > 0:
            self.total_response_time += result.duration_seconds
            self.fastest_response = min(self.fastest_response, result.duration_seconds)
            self.slowest_response = max(self.slowest_response, result.duration_seconds)
    
    def record_rejected_call(self):
        """Record a rejected call (circuit open)"""
        self.rejected_calls += 1
    
    def record_state_change(self, new_state: CircuitState):
        """Record state change"""
        if new_state == CircuitState.OPEN:
            self.times_opened += 1
        elif new_state == CircuitState.CLOSED:
            self.times_closed += 1
        elif new_state == CircuitState.HALF_OPEN:
            self.times_half_opened += 1
        
        self.state_since = datetime.now()
    
    @property
    def failure_rate(self) -> float:
        """Current failure rate (0.0 to 1.0)"""
        if self.total_calls == 0:
            return 0.0
        return self.failed_calls / self.total_calls
    
    @property
    def avg_response_time(self) -> float:
        """Average response time"""
        if self.successful_calls == 0:
            return 0.0
        return self.total_response_time / self.successful_calls
    
    @property
    def recent_failure_rate(self) -> float:
        """Recent failure rate in sliding window"""
        if not self.recent_calls:
            return 0.0
        
        recent_failures = sum(1 for call in self.recent_calls if not call.success)
        return recent_failures / len(self.recent_calls)

class FallbackStrategy:
    """Base class for fallback strategies"""
    
    def execute(self, *args, **kwargs) -> Any:
        """Execute fallback strategy"""
        raise NotImplementedError
    
    async def execute_async(self, *args, **kwargs) -> Any:
        """Execute fallback strategy (async)"""
        return self.execute(*args, **kwargs)

class DefaultValueFallback(FallbackStrategy):
    """Fallback that returns a default value"""
    
    def __init__(self, default_value: Any):
        self.default_value = default_value
    
    def execute(self, *args, **kwargs) -> Any:
        return self.default_value

class CachedResponseFallback(FallbackStrategy):
    """Fallback that returns cached response"""
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}
    
    def set_cached_response(self, key: str, value: Any):
        """Set cached response for key"""
        self.cache[key] = value
    
    def execute(self, *args, **kwargs) -> Any:
        # Create cache key from args/kwargs
        cache_key = str(args) + str(sorted(kwargs.items()))
        return self.cache.get(cache_key)

class CallbackFallback(FallbackStrategy):
    """Fallback that executes a callback function"""
    
    def __init__(self, callback: Callable):
        self.callback = callback
    
    def execute(self, *args, **kwargs) -> Any:
        return self.callback(*args, **kwargs)
    
    async def execute_async(self, *args, **kwargs) -> Any:
        if inspect.iscoroutinefunction(self.callback):
            return await self.callback(*args, **kwargs)
        else:
            return self.callback(*args, **kwargs)

class DegradedServiceFallback(FallbackStrategy):
    """Fallback that provides degraded service"""
    
    def __init__(self, degraded_function: Callable):
        self.degraded_function = degraded_function
    
    def execute(self, *args, **kwargs) -> Any:
        return self.degraded_function(*args, **kwargs)
    
    async def execute_async(self, *args, **kwargs) -> Any:
        if inspect.iscoroutinefunction(self.degraded_function):
            return await self.degraded_function(*args, **kwargs)
        else:
            return self.degraded_function(*args, **kwargs)

class CircuitBreaker:
    """
    Circuit Breaker implementation with monitoring and recovery
    """
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.metrics = CircuitMetrics()
        
        # State management
        self._lock = threading.RLock()
        self._last_state_change = datetime.now()
        self._consecutive_successes = 0
        self._consecutive_failures = 0
        
        # Recovery management
        self._current_recovery_timeout = config.recovery_timeout_seconds
        
        # Fallback strategies
        self._fallback_strategies: List[FallbackStrategy] = []
        
        # Health checking
        self._health_check_function: Optional[Callable] = None
        self._last_health_check = None
        self._health_check_thread: Optional[threading.Thread] = None
        self._running = False
        
        logger.debug(f"🔌 Circuit breaker '{config.name}' created")
    
    def start(self):
        """Start the circuit breaker (enables health checking)"""
        if self._running:
            return
        
        self._running = True
        
        if self.config.health_check_enabled and self._health_check_function:
            self._health_check_thread = threading.Thread(
                target=self._health_check_loop,
                name=f"health_check_{self.config.name}",
                daemon=True
            )
            self._health_check_thread.start()
        
        logger.debug(f"🚀 Circuit breaker '{self.config.name}' started")
    
    def stop(self):
        """Stop the circuit breaker"""
        if not self._running:
            return
        
        self._running = False
        
        if self._health_check_thread:
            self._health_check_thread.join(timeout=5.0)
        
        logger.debug(f"🛑 Circuit breaker '{self.config.name}' stopped")
    
    def add_fallback(self, fallback: FallbackStrategy):
        """Add fallback strategy"""
        self._fallback_strategies.append(fallback)
    
    def set_health_check(self, health_check_func: Callable):
        """Set health check function"""
        self._health_check_function = health_check_func
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker (sync)"""
        with self._lock:
            if self._should_reject_call():
                self.metrics.record_rejected_call()
                return self._execute_fallback(*args, **kwargs)
        
        # Execute function with monitoring
        start_time = time.time()
        result = None
        error = None
        
        try:
            if self.config.timeout_seconds:
                # For sync functions, we can't easily implement timeout
                # In real implementation, could use signal.alarm on Unix
                result = func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Record success
            duration = time.time() - start_time
            call_result = CallResult(
                success=True,
                duration_seconds=duration,
                response_data=result
            )
            
            self._record_success(call_result)
            return result
            
        except Exception as e:
            error = e
            duration = time.time() - start_time
            
            # Determine failure type
            failure_type = self._classify_error(e)
            
            call_result = CallResult(
                success=False,
                duration_seconds=duration,
                failure_type=failure_type,
                error_message=str(e)
            )
            
            self._record_failure(call_result)
            
            # Return fallback or re-raise
            if self.config.fallback_enabled:
                return self._execute_fallback(*args, **kwargs)
            else:
                raise
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function through circuit breaker"""
        with self._lock:
            if self._should_reject_call():
                self.metrics.record_rejected_call()
                return await self._execute_fallback_async(*args, **kwargs)
        
        # Execute function with monitoring and timeout
        start_time = time.time()
        result = None
        error = None
        
        try:
            if self.config.timeout_seconds:
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.config.timeout_seconds
                )
            else:
                result = await func(*args, **kwargs)
            
            # Record success
            duration = time.time() - start_time
            call_result = CallResult(
                success=True,
                duration_seconds=duration,
                response_data=result
            )
            
            self._record_success(call_result)
            return result
            
        except asyncio.TimeoutError as e:
            error = e
            duration = time.time() - start_time
            
            call_result = CallResult(
                success=False,
                duration_seconds=duration,
                failure_type=FailureType.TIMEOUT,
                error_message="Operation timeout"
            )
            
            self._record_failure(call_result)
            
            # Return fallback or re-raise
            if self.config.fallback_enabled:
                return await self._execute_fallback_async(*args, **kwargs)
            else:
                raise
        
        except Exception as e:
            error = e
            duration = time.time() - start_time
            
            # Determine failure type
            failure_type = self._classify_error(e)
            
            call_result = CallResult(
                success=False,
                duration_seconds=duration,
                failure_type=failure_type,
                error_message=str(e)
            )
            
            self._record_failure(call_result)
            
            # Return fallback or re-raise
            if self.config.fallback_enabled:
                return await self._execute_fallback_async(*args, **kwargs)
            else:
                raise
    
    def _should_reject_call(self) -> bool:
        """Check if call should be rejected based on circuit state"""
        if self.state == CircuitState.CLOSED:
            return False
        
        if self.state == CircuitState.OPEN:
            # Check if enough time has passed to try half-open
            if self._should_attempt_reset():
                self._transition_to_half_open()
                return False
            return True
        
        if self.state == CircuitState.HALF_OPEN:
            # Allow limited calls through
            return False
        
        return False
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset to half-open"""
        elapsed = (datetime.now() - self._last_state_change).total_seconds()
        return elapsed >= self._current_recovery_timeout
    
    def _record_success(self, result: CallResult):
        """Record successful call"""
        with self._lock:
            self.metrics.record_call(result)
            self._consecutive_successes += 1
            self._consecutive_failures = 0
            
            # Check for state transitions
            if self.state == CircuitState.HALF_OPEN:
                if self._consecutive_successes >= self.config.success_threshold:
                    self._transition_to_closed()
    
    def _record_failure(self, result: CallResult):
        """Record failed call"""
        with self._lock:
            self.metrics.record_call(result)
            self._consecutive_failures += 1
            self._consecutive_successes = 0
            
            # Check for state transitions
            if self.state == CircuitState.CLOSED:
                if self._should_open_circuit():
                    self._transition_to_open()
            
            elif self.state == CircuitState.HALF_OPEN:
                # Any failure in half-open goes back to open
                self._transition_to_open()
    
    def _should_open_circuit(self) -> bool:
        """Check if circuit should be opened"""
        # Must have minimum number of calls
        if self.metrics.total_calls < self.config.min_calls_threshold:
            return False
        
        # Check failure threshold
        if self._consecutive_failures >= self.config.failure_threshold:
            return True
        
        # Check failure rate in recent window
        if self.metrics.recent_failure_rate > 0.5:  # 50% failure rate
            return True
        
        return False
    
    def _transition_to_open(self):
        """Transition to OPEN state"""
        if self.state != CircuitState.OPEN:
            logger.warning(f"🔴 Circuit breaker '{self.config.name}' OPENED (failures: {self._consecutive_failures})")
            
            self.state = CircuitState.OPEN
            self._last_state_change = datetime.now()
            self.metrics.record_state_change(CircuitState.OPEN)
            
            # Apply exponential backoff
            self._current_recovery_timeout = min(
                self._current_recovery_timeout * self.config.backoff_multiplier,
                self.config.max_recovery_timeout
            )
    
    def _transition_to_half_open(self):
        """Transition to HALF_OPEN state"""
        logger.info(f"🟡 Circuit breaker '{self.config.name}' HALF-OPEN (attempting recovery)")
        
        self.state = CircuitState.HALF_OPEN
        self._last_state_change = datetime.now()
        self.metrics.record_state_change(CircuitState.HALF_OPEN)
        self._consecutive_successes = 0
        self._consecutive_failures = 0
    
    def _transition_to_closed(self):
        """Transition to CLOSED state"""
        logger.info(f"🟢 Circuit breaker '{self.config.name}' CLOSED (recovery successful)")
        
        self.state = CircuitState.CLOSED
        self._last_state_change = datetime.now()
        self.metrics.record_state_change(CircuitState.CLOSED)
        
        # Reset recovery timeout to initial value
        self._current_recovery_timeout = self.config.recovery_timeout_seconds
    
    def _classify_error(self, error: Exception) -> FailureType:
        """Classify error type"""
        if isinstance(error, asyncio.TimeoutError):
            return FailureType.TIMEOUT
        elif isinstance(error, ConnectionError):
            return FailureType.SERVICE_UNAVAILABLE
        elif "rate limit" in str(error).lower():
            return FailureType.RATE_LIMIT
        else:
            return FailureType.EXCEPTION
    
    def _execute_fallback(self, *args, **kwargs) -> Any:
        """Execute fallback strategy (sync)"""
        for fallback in self._fallback_strategies:
            try:
                result = fallback.execute(*args, **kwargs)
                if result is not None:
                    logger.debug(f"🔄 Fallback executed for '{self.config.name}'")
                    return result
            except Exception as e:
                logger.warning(f"Fallback failed for '{self.config.name}': {e}")
                continue
        
        # No fallback available
        raise CircuitBreakerOpenError(f"Circuit breaker '{self.config.name}' is open and no fallback available")
    
    async def _execute_fallback_async(self, *args, **kwargs) -> Any:
        """Execute fallback strategy (async)"""
        for fallback in self._fallback_strategies:
            try:
                result = await fallback.execute_async(*args, **kwargs)
                if result is not None:
                    logger.debug(f"🔄 Async fallback executed for '{self.config.name}'")
                    return result
            except Exception as e:
                logger.warning(f"Async fallback failed for '{self.config.name}': {e}")
                continue
        
        # No fallback available
        raise CircuitBreakerOpenError(f"Circuit breaker '{self.config.name}' is open and no fallback available")
    
    def _health_check_loop(self):
        """Background health check loop"""
        while self._running:
            try:
                if self._health_check_function:
                    start_time = time.time()
                    
                    try:
                        if inspect.iscoroutinefunction(self._health_check_function):
                            # Async health check
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            is_healthy = loop.run_until_complete(self._health_check_function())
                            loop.close()
                        else:
                            # Sync health check
                            is_healthy = self._health_check_function()
                        
                        duration = time.time() - start_time
                        
                        # Record health check result
                        result = CallResult(
                            success=bool(is_healthy),
                            duration_seconds=duration,
                            failure_type=None if is_healthy else FailureType.SERVICE_UNAVAILABLE,
                            error_message=None if is_healthy else "Health check failed"
                        )
                        
                        if is_healthy:
                            self._record_success(result)
                        else:
                            self._record_failure(result)
                        
                        self._last_health_check = datetime.now()
                        
                    except Exception as e:
                        logger.error(f"Health check error for '{self.config.name}': {e}")
                        
                        result = CallResult(
                            success=False,
                            duration_seconds=time.time() - start_time,
                            failure_type=FailureType.EXCEPTION,
                            error_message=str(e)
                        )
                        self._record_failure(result)
                
                time.sleep(self.config.health_check_interval_seconds)
                
            except Exception as e:
                logger.error(f"Health check loop error for '{self.config.name}': {e}")
                time.sleep(5.0)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        with self._lock:
            return {
                "name": self.config.name,
                "state": self.state.value,
                "state_duration_seconds": (datetime.now() - self._last_state_change).total_seconds(),
                "consecutive_successes": self._consecutive_successes,
                "consecutive_failures": self._consecutive_failures,
                "current_recovery_timeout": self._current_recovery_timeout,
                "fallback_strategies": len(self._fallback_strategies),
                "metrics": {
                    "total_calls": self.metrics.total_calls,
                    "successful_calls": self.metrics.successful_calls,
                    "failed_calls": self.metrics.failed_calls,
                    "rejected_calls": self.metrics.rejected_calls,
                    "failure_rate": self.metrics.failure_rate,
                    "recent_failure_rate": self.metrics.recent_failure_rate,
                    "avg_response_time": self.metrics.avg_response_time,
                    "fastest_response": self.metrics.fastest_response if self.metrics.fastest_response != float('inf') else 0,
                    "slowest_response": self.metrics.slowest_response,
                    "times_opened": self.metrics.times_opened,
                    "last_failure": self.metrics.last_failure_time.isoformat() if self.metrics.last_failure_time else None,
                    "last_success": self.metrics.last_success_time.isoformat() if self.metrics.last_success_time else None
                },
                "config": {
                    "failure_threshold": self.config.failure_threshold,
                    "success_threshold": self.config.success_threshold,
                    "timeout_seconds": self.config.timeout_seconds,
                    "recovery_timeout_seconds": self.config.recovery_timeout_seconds,
                    "health_check_enabled": self.config.health_check_enabled,
                    "fallback_enabled": self.config.fallback_enabled
                }
            }
    
    def reset(self):
        """Manually reset circuit breaker to closed state"""
        with self._lock:
            logger.info(f"🔄 Manually resetting circuit breaker '{self.config.name}'")
            self._transition_to_closed()
            self._consecutive_failures = 0
            self._consecutive_successes = 0

class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open"""
    pass

class CircuitBreakerManager:
    """
    Centralized manager for all circuit breakers in JARVIS 5.0
    """
    
    def __init__(self):
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._lock = threading.RLock()
        self._running = False
        
        # Monitoring
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        logger.info("🔌 Circuit Breaker Manager initialized")
    
    def create_circuit_breaker(self, config: CircuitBreakerConfig) -> CircuitBreaker:
        """Create and register a new circuit breaker"""
        with self._lock:
            circuit_breaker = CircuitBreaker(config)
            self._circuit_breakers[config.name] = circuit_breaker
            
            if self._running:
                circuit_breaker.start()
            
            logger.info(f"➕ Created circuit breaker '{config.name}'")
            return circuit_breaker
    
    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name"""
        with self._lock:
            return self._circuit_breakers.get(name)
    
    def remove_circuit_breaker(self, name: str) -> bool:
        """Remove circuit breaker"""
        with self._lock:
            if name in self._circuit_breakers:
                circuit_breaker = self._circuit_breakers[name]
                circuit_breaker.stop()
                del self._circuit_breakers[name]
                logger.info(f"➖ Removed circuit breaker '{name}'")
                return True
            return False
    
    def start(self):
        """Start circuit breaker manager"""
        if self._running:
            return
        
        self._running = True
        
        # Start all circuit breakers
        with self._lock:
            for circuit_breaker in self._circuit_breakers.values():
                circuit_breaker.start()
        
        # Start monitoring thread
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="circuit_breaker_monitor",
            daemon=True
        )
        self._monitor_thread.start()
        
        logger.info("🚀 Circuit Breaker Manager started")
    
    def stop(self):
        """Stop circuit breaker manager"""
        if not self._running:
            return
        
        logger.info("🛑 Stopping Circuit Breaker Manager")
        self._running = False
        self._stop_event.set()
        
        # Wait for monitor thread
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        
        # Stop all circuit breakers
        with self._lock:
            for circuit_breaker in self._circuit_breakers.values():
                circuit_breaker.stop()
        
        logger.info("✅ Circuit Breaker Manager stopped")
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all circuit breakers"""
        with self._lock:
            stats = {}
            total_calls = 0
            total_failures = 0
            open_circuits = 0
            
            for name, circuit_breaker in self._circuit_breakers.items():
                circuit_stats = circuit_breaker.get_stats()
                stats[name] = circuit_stats
                
                total_calls += circuit_stats['metrics']['total_calls']
                total_failures += circuit_stats['metrics']['failed_calls']
                
                if circuit_stats['state'] == 'open':
                    open_circuits += 1
            
            return {
                "summary": {
                    "total_circuit_breakers": len(self._circuit_breakers),
                    "open_circuits": open_circuits,
                    "total_calls": total_calls,
                    "total_failures": total_failures,
                    "overall_failure_rate": (total_failures / max(1, total_calls)) * 100
                },
                "circuit_breakers": stats
            }
    
    def reset_all(self):
        """Reset all circuit breakers to closed state"""
        with self._lock:
            for circuit_breaker in self._circuit_breakers.values():
                circuit_breaker.reset()
        
        logger.info("🔄 Reset all circuit breakers")
    
    def _monitor_loop(self):
        """Monitor circuit breakers and log alerts"""
        while self._running:
            try:
                with self._lock:
                    for name, circuit_breaker in self._circuit_breakers.items():
                        stats = circuit_breaker.get_stats()
                        
                        # Alert on state changes
                        if stats['state'] == 'open':
                            failure_rate = stats['metrics']['failure_rate'] * 100
                            logger.warning(f"🚨 Circuit breaker '{name}' is OPEN (failure rate: {failure_rate:.1f}%)")
                        
                        # Alert on high failure rates
                        elif stats['metrics']['recent_failure_rate'] > 0.3:  # 30%
                            recent_rate = stats['metrics']['recent_failure_rate'] * 100
                            logger.warning(f"⚠️ Circuit breaker '{name}' high failure rate: {recent_rate:.1f}%")
                
                self._stop_event.wait(timeout=30.0)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"Circuit breaker monitor error: {e}")
                time.sleep(5.0)

# Decorator for applying circuit breaker to functions
def circuit_breaker(name: str, 
                   failure_threshold: int = 5,
                   timeout_seconds: float = 30.0,
                   fallback: Optional[FallbackStrategy] = None):
    """Decorator to apply circuit breaker to a function"""
    
    def decorator(func):
        # Create circuit breaker config
        config = CircuitBreakerConfig(
            name=name,
            failure_threshold=failure_threshold,
            timeout_seconds=timeout_seconds
        )
        
        # Get or create circuit breaker
        cb = circuit_breaker_manager.get_circuit_breaker(name)
        if not cb:
            cb = circuit_breaker_manager.create_circuit_breaker(config)
        
        # Add fallback if provided
        if fallback:
            cb.add_fallback(fallback)
        
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await cb.call_async(func, *args, **kwargs)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                return cb.call(func, *args, **kwargs)
            return sync_wrapper
    
    return decorator

# Global instance
circuit_breaker_manager = CircuitBreakerManager()

if __name__ == "__main__":
    # Test circuit breaker implementation
    async def test_circuit_breaker():
        print("🧪 Testing Circuit Breaker Pattern")
        print("=" * 50)
        
        # Start manager
        circuit_breaker_manager.start()
        
        # Create test circuit breaker
        config = CircuitBreakerConfig(
            name="test_service",
            failure_threshold=3,
            success_threshold=2,
            timeout_seconds=1.0,
            recovery_timeout_seconds=5.0
        )
        
        cb = circuit_breaker_manager.create_circuit_breaker(config)
        
        # Add fallback
        fallback = DefaultValueFallback("fallback_response")
        cb.add_fallback(fallback)
        
        # Test function that fails sometimes
        call_count = 0
        async def test_function(should_fail=False):
            nonlocal call_count
            call_count += 1
            
            if should_fail:
                raise Exception(f"Simulated failure #{call_count}")
            
            return f"Success #{call_count}"
        
        # Test normal operation
        print("\n✅ Testing normal operation:")
        for i in range(3):
            result = await cb.call_async(test_function, should_fail=False)
            print(f"Call {i+1}: {result}")
        
        # Test failures leading to circuit opening
        print("\n❌ Testing failures:")
        for i in range(5):
            try:
                result = await cb.call_async(test_function, should_fail=True)
                print(f"Failure {i+1}: {result}")
            except Exception as e:
                print(f"Failure {i+1}: Exception - {e}")
        
        # Check if circuit is open
        stats = cb.get_stats()
        print(f"\n📊 Circuit state after failures: {stats['state']}")
        
        # Test circuit open behavior (should return fallback)
        print("\n🔄 Testing circuit open (fallback):")
        try:
            result = await cb.call_async(test_function, should_fail=False)
            print(f"Result while open: {result}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Wait for recovery attempt
        print("\n⏳ Waiting for recovery...")
        await asyncio.sleep(6)
        
        # Test recovery
        print("\n🔄 Testing recovery:")
        for i in range(3):
            result = await cb.call_async(test_function, should_fail=False)
            print(f"Recovery call {i+1}: {result}")
        
        # Final stats
        print("\n📊 Final Circuit Breaker Stats:")
        final_stats = cb.get_stats()
        
        print(f"State: {final_stats['state']}")
        print(f"Total calls: {final_stats['metrics']['total_calls']}")
        print(f"Success rate: {(1 - final_stats['metrics']['failure_rate']) * 100:.1f}%")
        print(f"Times opened: {final_stats['metrics']['times_opened']}")
        
        # Test decorator
        print("\n🎭 Testing decorator:")
        
        @circuit_breaker("decorated_service", failure_threshold=2, timeout_seconds=0.5)
        async def decorated_function(x):
            await asyncio.sleep(0.1)
            if x > 5:
                raise Exception("Value too high")
            return f"Processed: {x}"
        
        # Test decorator
        for i in range(8):
            try:
                result = await decorated_function(i)
                print(f"Decorated call {i}: {result}")
            except Exception as e:
                print(f"Decorated call {i}: Error - {e}")
        
        # Show all stats
        print("\n📊 All Circuit Breaker Stats:")
        all_stats = circuit_breaker_manager.get_all_stats()
        
        print(f"Summary: {all_stats['summary']}")
        
        for name, stats in all_stats['circuit_breakers'].items():
            print(f"\n{name.upper()}:")
            print(f"  State: {stats['state']}")
            print(f"  Calls: {stats['metrics']['total_calls']}")
            print(f"  Failures: {stats['metrics']['failed_calls']}")
            print(f"  Success rate: {(1 - stats['metrics']['failure_rate']) * 100:.1f}%")
        
        # Stop manager
        circuit_breaker_manager.stop()
        
        print("\n✅ Test completed")
    
    asyncio.run(test_circuit_breaker())