# ============================================================================
# JARVIS SINGULARITY - Performance Optimizer (Phase 5: Final Phase)
# ============================================================================
# OtimizaÃ§Ãµes para respostas rÃ¡pidas (<5s) e uso eficiente de recursos
# ============================================================================

import logging
import time
import hashlib
import pickle
from typing import Any, Dict, Optional, Callable
from pathlib import Path
from functools import wraps
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)


# ============================================================================
# RESPONSE CACHE
# ============================================================================
class ResponseCache:
    """
    Cache de respostas para comandos similares.
    Evita reprocessamento de comandos repetidos.
    """
    
    def __init__(self, cache_dir: str = "data/cache", ttl_minutes: int = 60):
        """
        Inicializa o cache.
        
        Args:
            cache_dir: DiretÃ³rio para cache
            ttl_minutes: Time-to-live em minutos
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(minutes=ttl_minutes)
        self.memory_cache = {}  # Cache em memÃ³ria (rÃ¡pido)
        
        logger.info(f"ðŸ’¾ Cache inicializado - TTL: {ttl_minutes}min")
    
    def _get_key(self, command: str) -> str:
        """Gera chave hash do comando"""
        return hashlib.md5(command.lower().encode()).hexdigest()
    
    def get(self, command: str) -> Optional[str]:
        """Busca resposta no cache"""
        key = self._get_key(command)
        
        # 1. Tentar memÃ³ria primeiro (mais rÃ¡pido)
        if key in self.memory_cache:
            cached = self.memory_cache[key]
            if datetime.now() - cached['timestamp'] < self.ttl:
                logger.info(f"âš¡ Cache HIT (memÃ³ria): {command[:30]}...")
                return cached['response']
            else:
                del self.memory_cache[key]
        
        # 2. Tentar disco
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    cached = pickle.load(f)
                
                if datetime.now() - cached['timestamp'] < self.ttl:
                    # Promover para memÃ³ria
                    self.memory_cache[key] = cached
                    logger.info(f"âš¡ Cache HIT (disco): {command[:30]}...")
                    return cached['response']
                else:
                    cache_file.unlink()
            except Exception as e:
                logger.warning(f"âš ï¸ Erro ao ler cache: {e}")
        
        return None
    
    def set(self, command: str, response: str):
        """Salva resposta no cache"""
        key = self._get_key(command)
        cached = {
            'command': command,
            'response': response,
            'timestamp': datetime.now()
        }
        
        # Salvar em memÃ³ria
        self.memory_cache[key] = cached
        
        # Salvar em disco (assÃ­ncrono)
        cache_file = self.cache_dir / f"{key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(cached, f)
        except Exception as e:
            logger.warning(f"âš ï¸ Erro ao salvar cache: {e}")
    
    def clear_old(self):
        """Remove entradas expiradas"""
        count = 0
        
        # Limpar memÃ³ria
        expired_keys = [
            k for k, v in self.memory_cache.items()
            if datetime.now() - v['timestamp'] >= self.ttl
        ]
        for k in expired_keys:
            del self.memory_cache[k]
            count += 1
        
        # Limpar disco
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                with open(cache_file, 'rb') as f:
                    cached = pickle.load(f)
                if datetime.now() - cached['timestamp'] >= self.ttl:
                    cache_file.unlink()
                    count += 1
            except:
                pass
        
        if count > 0:
            logger.info(f"ðŸ—‘ï¸ Removidas {count} entradas expiradas do cache")


# ============================================================================
# PERFORMANCE OPTIMIZER
# ============================================================================
class PerformanceOptimizer:
    """
    Otimizador de performance do JARVIS.
    
    OTIMIZAÃ‡Ã•ES:
    - Cache de respostas
    - Preload de modelos
    - MediÃ§Ã£o de tempo
    - Throttling de recursos
    """
    
    def __init__(self):
        """Inicializa o otimizador"""
        logger.info("âš¡ Inicializando Performance Optimizer...")
        
        self.cache = ResponseCache(ttl_minutes=60)
        self.metrics = {
            'total_requests': 0,
            'cache_hits': 0,
            'avg_response_time': 0.0,
            'response_times': []
        }
        self._lock = threading.Lock()
        
        logger.info("âœ… Performance Optimizer online")
    
    def measure_time(self, func: Callable) -> Callable:
        """
        Decorator para medir tempo de execuÃ§Ã£o.
        
        Usage:
            @optimizer.measure_time
            def my_function():
                pass
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            
            self._record_time(elapsed)
            
            if elapsed > 5.0:
                logger.warning(f"âš ï¸ {func.__name__} demorou {elapsed:.2f}s (meta: <5s)")
            else:
                logger.info(f"âš¡ {func.__name__} completou em {elapsed:.2f}s")
            
            return result
        return wrapper
    
    def _record_time(self, elapsed: float):
        """Registra tempo de resposta"""
        with self._lock:
            self.metrics['response_times'].append(elapsed)
            
            # Manter apenas Ãºltimas 100 mediÃ§Ãµes
            if len(self.metrics['response_times']) > 100:
                self.metrics['response_times'].pop(0)
            
            # Recalcular mÃ©dia
            self.metrics['avg_response_time'] = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
    
    def get_cached_response(self, command: str) -> Optional[str]:
        """
        Tenta obter resposta do cache.
        
        Args:
            command: Comando do usuÃ¡rio
        
        Returns:
            Resposta em cache ou None
        """
        with self._lock:
            self.metrics['total_requests'] += 1
        
        response = self.cache.get(command)
        
        if response:
            with self._lock:
                self.metrics['cache_hits'] += 1
        
        return response
    
    def cache_response(self, command: str, response: str):
        """
        Salva resposta no cache.
        
        Args:
            command: Comando do usuÃ¡rio
            response: Resposta gerada
        """
        self.cache.set(command, response)
    
    def get_stats(self) -> Dict[str, Any]:
        """ObtÃ©m estatÃ­sticas de performance"""
        with self._lock:
            cache_hit_rate = 0.0
            if self.metrics['total_requests'] > 0:
                cache_hit_rate = (self.metrics['cache_hits'] / self.metrics['total_requests']) * 100
            
            return {
                'total_requests': self.metrics['total_requests'],
                'cache_hits': self.metrics['cache_hits'],
                'cache_hit_rate': f"{cache_hit_rate:.1f}%",
                'avg_response_time': f"{self.metrics['avg_response_time']:.2f}s",
                'last_10_times': [f"{t:.2f}s" for t in self.metrics['response_times'][-10:]],
                'meets_target': self.metrics['avg_response_time'] < 5.0 if self.metrics['response_times'] else None
            }
    
    def optimize_startup(self):
        """
        Otimiza tempo de inicializaÃ§Ã£o.
        Carrega modelos crÃ­ticos em paralelo.
        """
        logger.info("ðŸš€ Otimizando startup...")
        
        def preload_models():
            """Preload de modelos em background"""
            try:
                # Aqui vocÃª pode adicionar preload de modelos pesados
                # Por exemplo: YOLO, embeddings, etc.
                logger.info("ðŸ“¦ Preloading modelos...")
                time.sleep(0.1)  # Placeholder
                logger.info("âœ… Modelos preloaded")
            except Exception as e:
                logger.warning(f"âš ï¸ Erro no preload: {e}")
        
        # Executar em thread separada
        thread = threading.Thread(target=preload_models, daemon=True)
        thread.start()
    
    def cleanup(self):
        """Limpeza de recursos"""
        logger.info("ðŸ§¹ Limpando cache antigo...")
        self.cache.clear_old()
        logger.info("âœ… Cleanup completo")


# ============================================================================
# PERFORMANCE DECORATORS
# ============================================================================
def timed(func: Callable) -> Callable:
    """
    Decorator simples para medir tempo.
    
    Usage:
        @timed
        def my_function():
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        logger.info(f"â±ï¸ {func.__name__}: {elapsed:.3f}s")
        return result
    return wrapper


def cached(ttl_minutes: int = 60):
    """
    Decorator para cache de funÃ§Ã£o.
    
    Usage:
        @cached(ttl_minutes=30)
        def expensive_function(arg):
            return result
    """
    cache = {}
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Criar chave do cache
            key = hashlib.md5(
                f"{func.__name__}_{args}_{kwargs}".encode()
            ).hexdigest()
            
            # Verificar cache
            if key in cache:
                cached_result, timestamp = cache[key]
                if datetime.now() - timestamp < timedelta(minutes=ttl_minutes):
                    logger.debug(f"âš¡ Cache hit: {func.__name__}")
                    return cached_result
            
            # Executar funÃ§Ã£o
            result = func(*args, **kwargs)
            
            # Salvar no cache
            cache[key] = (result, datetime.now())
            
            return result
        return wrapper
    return decorator


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================
# InstÃ¢ncia global
performance_optimizer = PerformanceOptimizer()
