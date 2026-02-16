#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Optimized YOLO Detection Pipeline
==============================================
FASE 1.8: Pipeline de detecção YOLO otimizado com batching, caching e workers dedicados.

Responsibilities:
- YOLO inference com batching inteligente
- Caching de resultados com TTL
- Workers dedicados para eliminar GIL blocking
- Pipeline assíncrono com circuit breakers
- Metrics de performance e observabilidade

Philosophy:
- Maximizar throughput com batching
- Minimizar latência com caching inteligente  
- Eliminar GIL blocking com process workers
- Observabilidade completa de performance
- Resiliência contra falhas de modelo
"""

import asyncio
import logging
import threading
import time
import hashlib
import pickle
import numpy as np
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from collections import deque, defaultdict
from pathlib import Path
import uuid
import cv2
import psutil

# Import JARVIS infrastructure
from src.core.infrastructure.resource_pool_manager import (
    ResourcePool, PoolConfig, ResourceFactory, resource_pool_manager
)
from src.core.infrastructure.process_worker_factory import (
    ProcessWorkerFactory, WorkerType, TaskPriority, WorkerConfig, process_worker_factory
)
from src.core.infrastructure.circuit_breaker import (
    CircuitBreaker, CircuitBreakerConfig, circuit_breaker_manager, circuit_breaker
)
from src.core.infrastructure.async_event_bus import event_bus, EventType, EventPriority

logger = logging.getLogger(__name__)

class DetectionMode(Enum):
    """Modos de detecção"""
    SINGLE = "single"           # Uma imagem por vez
    BATCH = "batch"            # Múltiplas imagens em lote
    STREAMING = "streaming"     # Stream contínuo
    CACHED = "cached"          # Com cache inteligente

class DetectionQuality(Enum):
    """Qualidade de detecção vs velocidade"""
    FAST = "fast"              # YOLOv8n - mais rápido
    BALANCED = "balanced"      # YOLOv8s - balanceado
    ACCURATE = "accurate"      # YOLOv8m - mais preciso
    PRECISION = "precision"    # YOLOv8l - máxima precisão

@dataclass
class DetectionRequest:
    """Request de detecção"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    image: Optional[np.ndarray] = None
    image_hash: Optional[str] = None
    mode: DetectionMode = DetectionMode.SINGLE
    quality: DetectionQuality = DetectionQuality.FAST
    confidence_threshold: float = 0.5
    iou_threshold: float = 0.45
    max_detections: int = 100
    class_filter: Optional[List[str]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    priority: TaskPriority = TaskPriority.NORMAL
    callback: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Detection:
    """Resultado de detecção individual"""
    class_name: str
    class_id: int
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    center: Tuple[float, float]
    area: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'class_name': self.class_name,
            'class_id': self.class_id,
            'confidence': self.confidence,
            'bbox': self.bbox,
            'center': self.center,
            'area': self.area
        }

@dataclass
class DetectionResult:
    """Resultado completo de detecção"""
    request_id: str
    detections: List[Detection]
    inference_time_ms: float
    total_time_ms: float
    image_shape: Tuple[int, int, int]
    model_version: str
    cache_hit: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'request_id': self.request_id,
            'detections': [d.to_dict() for d in self.detections],
            'inference_time_ms': self.inference_time_ms,
            'total_time_ms': self.total_time_ms,
            'image_shape': self.image_shape,
            'model_version': self.model_version,
            'cache_hit': self.cache_hit,
            'timestamp': self.timestamp.isoformat()
        }

class DetectionCache:
    """Cache inteligente para resultados de detecção"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: float = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Tuple[DetectionResult, float]] = {}
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
        self._evictions = 0
    
    def _compute_cache_key(self, request: DetectionRequest) -> str:
        """Compute cache key for request"""
        if request.image_hash:
            key_data = f"{request.image_hash}_{request.quality.value}_{request.confidence_threshold}_{request.iou_threshold}"
        elif request.image is not None and request.image.size > 0:
            # Fallback to image content hash
            key_data = f"{hashlib.md5(request.image.tobytes()).hexdigest()}_{request.quality.value}_{request.confidence_threshold}_{request.iou_threshold}"
        else:
            key_data = f"empty_{request.request_id}"
        
        if request.class_filter:
            key_data += f"_{'_'.join(sorted(request.class_filter))}"
        
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]
    
    def get(self, request: DetectionRequest) -> Optional[DetectionResult]:
        """Get cached result if available"""
        cache_key = self._compute_cache_key(request)
        
        with self._lock:
            if cache_key in self._cache:
                result, cached_at = self._cache[cache_key]
                
                # Check TTL
                if time.time() - cached_at < self.ttl_seconds:
                    self._hits += 1
                    # Clone result with new request_id
                    cached_result = DetectionResult(
                        request_id=request.request_id,
                        detections=result.detections,
                        inference_time_ms=result.inference_time_ms,
                        total_time_ms=0.1,  # Cache retrieval is very fast
                        image_shape=result.image_shape,
                        model_version=result.model_version,
                        cache_hit=True,
                        timestamp=datetime.now()
                    )
                    return cached_result
                else:
                    # Expired
                    del self._cache[cache_key]
            
            self._misses += 1
            return None
    
    def put(self, request: DetectionRequest, result: DetectionResult):
        """Cache detection result"""
        cache_key = self._compute_cache_key(request)
        
        with self._lock:
            # Evict if at capacity
            if len(self._cache) >= self.max_size and cache_key not in self._cache:
                # Remove oldest entry
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
                del self._cache[oldest_key]
                self._evictions += 1
            
            self._cache[cache_key] = (result, time.time())
    
    def clear(self):
        """Clear cache"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            self._evictions = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._hits,
                'misses': self._misses,
                'evictions': self._evictions,
                'hit_rate_percent': hit_rate,
                'ttl_seconds': self.ttl_seconds
            }

class YOLOModelResource:
    """Resource wrapper for YOLO models"""
    
    def __init__(self, model_path: str, device: str = "cpu"):
        self.model_path = model_path
        self.device = device
        self.model = None
        self.load_time = None
        self.inference_count = 0
    
    def load(self):
        """Load YOLO model"""
        try:
            try:
                from ultralytics import YOLO
            except ImportError:
                # Fallback for older versions or structure
                from ultralytics.yolo.engine.model import YOLO
            
            start_time = time.time()
            self.model = YOLO(self.model_path)
            self.model.to(self.device)
            self.load_time = time.time() - start_time
            
            logger.info(f"🎯 Loaded YOLO model {Path(self.model_path).name} on {self.device} ({self.load_time:.2f}s)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load YOLO model {self.model_path}: {e}")
            return False
    
    def predict(self, image: np.ndarray, **kwargs) -> List[Any]:
        """Run inference"""
        if not self.model:
            raise RuntimeError("Model not loaded")
        
        self.inference_count += 1
        return self.model(image, **kwargs)
    
    def close(self):
        """Clean up model"""
        if self.model:
            del self.model
            self.model = None
    
    def unload(self):
        """Unload model to free memory"""
        if self.model:
            logger.info(f"Unloading YOLO model {Path(self.model_path).name}")
            del self.model
            self.model = None
            # Force GPU memory cleanup if available
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass
            import gc
            gc.collect()

class YOLOModelFactory(ResourceFactory[YOLOModelResource]):
    """Factory for YOLO model resources"""
    
    def __init__(self, models_dir: Path, device: str = "cpu"):
        self.models_dir = models_dir
        self.device = device
        
        # Model paths by quality
        self.model_paths = {
            DetectionQuality.FAST: models_dir / "vision" / "yolov8n.pt",
            DetectionQuality.BALANCED: models_dir / "vision" / "yolov8s.pt",
            DetectionQuality.ACCURATE: models_dir / "vision" / "yolov8m.pt",
            DetectionQuality.PRECISION: models_dir / "vision" / "yolov8l.pt"
        }
    
    def create_resource(self) -> YOLOModelResource:
        """Create YOLO model resource"""
        # Start with fast model by default
        model_path = str(self.model_paths[DetectionQuality.FAST])
        resource = YOLOModelResource(model_path, self.device)
        
        if resource.load():
            return resource
        else:
            raise RuntimeError(f"Failed to create YOLO model resource")
    
    def destroy_resource(self, resource: YOLOModelResource) -> None:
        """Destroy YOLO model resource"""
        resource.close()
    
    async def health_check(self, resource: YOLOModelResource) -> bool:
        """Check if model resource is healthy"""
        try:
            if not resource.model:
                return False
            
            # Create small test image
            test_image = np.zeros((640, 640, 3), dtype=np.uint8)
            
            # Run quick inference test
            results = resource.predict(test_image, verbose=False)
            return len(results) > 0
            
        except Exception as e:
            logger.debug(f"YOLO health check failed: {e}")
            return False

class OptimizedYOLOPipeline:
    """
    Optimized YOLO Detection Pipeline for JARVIS 5.0
    
    Features:
    - Async processing with batching
    - Intelligent caching
    - Process workers for GIL elimination
    - Circuit breakers for resilience  
    - Comprehensive metrics
    """
    
    def __init__(self, models_dir: Path, device: str = "cpu"):
        self.models_dir = models_dir
        self.device = device
        
        # Core components
        self.cache = DetectionCache()
        self._model_pool: Optional[ResourcePool] = None
        
        # Request queues by priority
        self._request_queues: Dict[TaskPriority, asyncio.Queue] = {
            priority: asyncio.Queue() for priority in TaskPriority
        }
        
        # Batching
        self._batch_size = 4
        self._batch_timeout_ms = 50  # Max time to wait for batch
        self._pending_batches: Dict[DetectionQuality, List[DetectionRequest]] = defaultdict(list)
        
        # Processing
        self._running = False
        self._processor_task: Optional[asyncio.Task] = None
        self._batch_processor_task: Optional[asyncio.Task] = None
        
        # Metrics
        self.total_requests = 0
        self.total_detections = 0
        self.total_inference_time = 0.0
        self.avg_inference_time = 0.0
        self.cache_hits = 0
        self.batch_count = 0
        self.start_time: Optional[datetime] = None
        
        # Configuration
        self.enable_batching = True
        self.enable_caching = True
        self.enable_process_workers = True
        
        # Auto-unload configuration
        self.auto_unload_timeout = 300  # 5 minutes of inactivity
        self.last_activity = datetime.now()
        self._unload_task: Optional[asyncio.Task] = None
        
        logger.info("🎯 Optimized YOLO Pipeline initialized")
    
    async def initialize(self):
        """Initialize pipeline components"""
        try:
            # Create YOLO model pool
            model_factory = YOLOModelFactory(self.models_dir, self.device)
            
            pool_config = PoolConfig(
                name="yolo_models",
                min_size=1,
                max_size=3,
                initial_size=2,
                health_check_interval_seconds=120,
                max_idle_seconds=600,
                acquire_timeout_seconds=10.0
            )
            
            self._model_pool = ResourcePool(pool_config, model_factory)
            await self._model_pool.start()
            
            # Register with global manager
            resource_pool_manager.register_pool(self._model_pool)
            
            # Configure process workers for YOLO inference
            if self.enable_process_workers:
                yolo_worker_config = WorkerConfig(
                    worker_type=WorkerType.VISION_ANALYZER,
                    max_memory_mb=1024,
                    max_concurrent_tasks=2,
                    task_timeout_seconds=30.0
                )
                process_worker_factory.configure_worker_type(WorkerType.VISION_ANALYZER, yolo_worker_config)
            
            logger.info("✅ YOLO Pipeline components initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize YOLO pipeline: {e}")
            raise
    
    async def start(self):
        """Start the pipeline"""
        if self._running:
            return
        
        logger.info("🚀 Starting Optimized YOLO Pipeline")
        
        self._running = True
        self.start_time = datetime.now()
        
        # Start processing tasks
        self._processor_task = asyncio.create_task(self._process_requests())
        
        if self.enable_batching:
            self._batch_processor_task = asyncio.create_task(self._process_batches())
        
        # Emit startup event
        event_bus.publish(
            EventType.VISION_CAPTURE,
            {"action": "pipeline_started", "device": self.device},
            priority=EventPriority.NORMAL,
            source="yolo_pipeline"
        )
        
        logger.info("✅ Optimized YOLO Pipeline started")
    
    def _update_activity(self):
        """Update last activity timestamp and schedule auto-unload"""
        self.last_activity = datetime.now()
        
        # Cancel existing unload task
        if self._unload_task and not self._unload_task.done():
            self._unload_task.cancel()
        
        # Schedule new unload task
        self._unload_task = asyncio.create_task(self._auto_unload_after_timeout())
    
    async def _auto_unload_after_timeout(self):
        """Auto-unload models after inactivity timeout"""
        try:
            await asyncio.sleep(self.auto_unload_timeout)
            
            # Check if still inactive
            if (datetime.now() - self.last_activity).total_seconds() >= self.auto_unload_timeout:
                logger.info("🧠 YOLO Pipeline: Auto-unloading models due to inactivity")
                await self._unload_models()
                
        except asyncio.CancelledError:
            pass  # Normal cancellation when activity resumes
    
    async def _unload_models(self):
        """Unload all models to free memory"""
        if self._model_pool:
            try:
                # Get all resources and unload them
                resources = []
                async for resource in self._model_pool._resources.values():
                    if hasattr(resource, 'unload'):
                        resource.unload()
                    resources.append(resource)
                
                logger.info(f"🧠 Unloaded {len(resources)} YOLO models")
                
            except Exception as e:
                logger.error(f"Error unloading YOLO models: {e}")
    
    async def stop(self):
        """Stop the pipeline"""
        if not self._running:
            return
        
        logger.info("🛑 Stopping Optimized YOLO Pipeline")
        self._running = False
        
        # Cancel processing tasks
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        
        if self._batch_processor_task:
            self._batch_processor_task.cancel()
            try:
                await self._batch_processor_task
            except asyncio.CancelledError:
                pass
        
        # Stop model pool
        if self._model_pool:
            await self._model_pool.stop()
        
        logger.info("✅ Optimized YOLO Pipeline stopped")
    
    @circuit_breaker("yolo_detection", failure_threshold=5, timeout_seconds=10.0)
    async def detect(self, request: DetectionRequest) -> DetectionResult:
        """Main detection method with circuit breaker"""
        # Update activity timestamp
        self._update_activity()
<<<<<<< Updated upstream
        
        start_time = time.time()
        
=======

        start_time = time.time()  # noqa: F841

>>>>>>> Stashed changes
        try:
            # Check cache first
            if self.enable_caching and request.mode != DetectionMode.STREAMING:
                cached_result = self.cache.get(request)
                if cached_result:
                    self.cache_hits += 1
                    
                    # Emit cache hit event
                    event_bus.publish(
                        EventType.VISION_DETECT,
                        {"action": "cache_hit", "request_id": request.request_id},
                        priority=EventPriority.LOW,
                        source="yolo_pipeline"
                    )
                    
                    return cached_result
            
            # Add to processing queue
            self.total_requests += 1
            
            # Create future for result
            result_future = asyncio.Future()
            request.callback = lambda result: result_future.set_result(result)
            
            # Queue request by priority
            await self._request_queues[request.priority].put(request)
            
            # Wait for result
            result = await result_future
            
            # Update metrics
            self.total_detections += len(result.detections)
            self.total_inference_time += result.inference_time_ms
            self.avg_inference_time = self.total_inference_time / max(1, self.total_requests)
            
            # Cache result
            if self.enable_caching and request.mode != DetectionMode.STREAMING:
                self.cache.put(request, result)
            
            # Emit detection event
            event_bus.publish(
                EventType.VISION_DETECT,
                {
                    "action": "detection_complete",
                    "request_id": request.request_id,
                    "detections": len(result.detections),
                    "inference_time_ms": result.inference_time_ms
                },
                priority=EventPriority.NORMAL,
                source="yolo_pipeline"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Detection failed for request {request.request_id}: {e}")
            raise
    
    async def detect_batch(self, requests: List[DetectionRequest]) -> List[DetectionResult]:
        """Batch detection for multiple requests"""
        if not requests:
            return []
        
        # Process all requests concurrently
        tasks = []
        for request in requests:
            task = asyncio.create_task(self.detect(request))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch detection failed for request {requests[i].request_id}: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def _process_requests(self):
        """Process detection requests by priority"""
        while self._running:
            try:
                request_processed = False
                
                # Process by priority (highest first)
                for priority in TaskPriority:
                    queue = self._request_queues[priority]
                    
                    try:
                        request = await asyncio.wait_for(queue.get(), timeout=0.1)
                        
                        if self.enable_batching and request.mode == DetectionMode.BATCH:
                            # Add to batch
                            self._pending_batches[request.quality].append(request)
                        else:
                            # Process immediately
                            await self._process_single_request(request)
                        
                        request_processed = True
                        break
                        
                    except asyncio.TimeoutError:
                        continue
                
                # Small delay if no requests processed
                if not request_processed:
                    await asyncio.sleep(0.01)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Request processor error: {e}")
                await asyncio.sleep(1.0)
    
    async def _process_batches(self):
        """Process batched requests for better throughput"""
        while self._running:
            try:
                # Check each quality level for ready batches
                for quality, pending_requests in self._pending_batches.items():
                    if len(pending_requests) >= self._batch_size:
                        # Process full batch
                        batch = pending_requests[:self._batch_size]
                        self._pending_batches[quality] = pending_requests[self._batch_size:]
                        
                        await self._process_request_batch(batch)
                        self.batch_count += 1
                    
                    elif pending_requests:
                        # Check if oldest request is timing out
                        oldest_request = pending_requests[0]
                        age_ms = (datetime.now() - oldest_request.timestamp).total_seconds() * 1000
                        
                        if age_ms > self._batch_timeout_ms:
                            # Process partial batch
                            batch = pending_requests.copy()
                            self._pending_batches[quality].clear()
                            
                            await self._process_request_batch(batch)
                            self.batch_count += 1
                
                await asyncio.sleep(0.01)  # 100 Hz check rate
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Batch processor error: {e}")
                await asyncio.sleep(1.0)
    
    async def _process_single_request(self, request: DetectionRequest):
        """Process individual detection request"""
        try:
            if self.enable_process_workers:
                # Use process worker for CPU-intensive inference
                task_id = process_worker_factory.submit_task(
                    WorkerType.VISION_ANALYZER,
                    "yolo_inference",
                    request.image,
                    request.confidence_threshold,
                    request.iou_threshold,
                    priority=request.priority
                )
                
                # Get result from worker
                worker_result = process_worker_factory.get_task_result(task_id, timeout=30.0)
                
                if worker_result and worker_result.get('success'):
                    raw_detections = worker_result.get('result', [])
                    
                    # Convert to Detection objects
                    detections = []
                    for det in raw_detections:
                        detection = Detection(
                            class_name=det.get('class_name', ''),
                            class_id=det.get('class_id', 0),
                            confidence=det.get('confidence', 0.0),
                            bbox=det.get('bbox', [0, 0, 0, 0]),
                            center=det.get('center', (0, 0)),
                            area=det.get('area', 0.0)
                        )
                        detections.append(detection)
                    
                    result = DetectionResult(
                        request_id=request.request_id,
                        detections=detections,
                        inference_time_ms=worker_result.get('duration_seconds', 0) * 1000,
                        total_time_ms=worker_result.get('duration_seconds', 0) * 1000,
                        image_shape=request.image.shape,
                        model_version="yolov8_worker"
                    )
                else:
                    # Fallback to local inference
                    result = await self._run_inference_local(request)
            else:
                # Local inference
                result = await self._run_inference_local(request)
            
            # Call callback if provided
            if request.callback:
                request.callback(result)
                
        except Exception as e:
            logger.error(f"Failed to process request {request.request_id}: {e}")
            
            # Return empty result on error
            error_result = DetectionResult(
                request_id=request.request_id,
                detections=[],
                inference_time_ms=0.0,
                total_time_ms=0.0,
                image_shape=(int(request.image.shape[0]), int(request.image.shape[1]), int(request.image.shape[2])) if request.image is not None else (0, 0, 0),
                model_version="error"
            )
            
            if request.callback:
                request.callback(error_result)
    
    async def _process_request_batch(self, batch: List[DetectionRequest]):
        """Process a batch of requests together"""
        try:
            start_time = time.time()
            
            # Group by image shape for optimal batching
            shape_groups = defaultdict(list)
            for request in batch:
                if request.image is None:
                    continue
                shape_key = request.image.shape[:2]  # (height, width)
                shape_groups[shape_key].append(request)
            
            # Process each shape group
            all_results = []
            for shape_key, shape_requests in shape_groups.items():
                if self._model_pool:
                    # Use resource pool
                    async with self._model_pool.acquire() as model_resource:
                        if model_resource:
                            batch_results = await self._run_batch_inference(shape_requests, model_resource)
                            all_results.extend(batch_results)
                else:
                    # Local fallback
                    for request in shape_requests:
                        result = await self._run_inference_local(request)
                        all_results.append(result)
            
            # Call callbacks
            for result in all_results:
                for request in batch:
                    if request.request_id == result.request_id and request.callback:
                        request.callback(result)
                        break
            
            batch_time = (time.time() - start_time) * 1000
            logger.debug(f"Processed batch of {len(batch)} requests in {batch_time:.1f}ms")
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            
            # Process individually as fallback
            for request in batch:
                await self._process_single_request(request)
    
    async def _run_batch_inference(self, requests: List[DetectionRequest], model_resource: YOLOModelResource) -> List[DetectionResult]:
        """Run batch inference on model resource"""
        try:
            # Filter valid images
            valid_requests = [req for req in requests if req.image is not None]
            if not valid_requests:
                return []
                
            # Stack images into batch
            images = [req.image for req in valid_requests]
            batch_array = np.stack(images)
            
            # Run batch inference
            start_time = time.time()
            results = model_resource.predict(
                batch_array,
                conf=requests[0].confidence_threshold,
                iou=requests[0].iou_threshold,
                verbose=False
            )
            inference_time = (time.time() - start_time) * 1000
            
            # Process results
            detection_results = []
            for i, (request, result) in enumerate(zip(requests, results)):
                # Extract detections from YOLO result
                detections = []
                if hasattr(result, 'boxes') and result.boxes is not None:
                    for box in result.boxes:
                        bbox = box.xyxy[0].tolist()
                        center = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
                        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                        
                        detection = Detection(
                            class_name=result.names[int(box.cls)],
                            class_id=int(box.cls),
                            confidence=float(box.conf),
                            bbox=bbox,
                            center=center,
                            area=area
                        )
                        detections.append(detection)
                
                # Filter by class if specified
                if request.class_filter:
                    detections = [d for d in detections if d.class_name in request.class_filter]
                
                # Limit detections
                detections = detections[:request.max_detections]
                
                result_obj = DetectionResult(
                    request_id=request.request_id,
                    detections=detections,
                    inference_time_ms=inference_time / len(requests),  # Divide by batch size
                    total_time_ms=inference_time / len(requests),
                    image_shape=request.image.shape,
                    model_version=f"yolov8_batch"
                )
                
                detection_results.append(result_obj)
            
            return detection_results
            
        except Exception as e:
            logger.error(f"Batch inference failed: {e}")
            
            # Fallback to individual processing
            fallback_results = []
            for request in requests:
                result = await self._run_inference_local(request)
                fallback_results.append(result)
            
            return fallback_results
    
    async def _run_inference_local(self, request: DetectionRequest) -> DetectionResult:
        """Run inference locally using model pool"""
        try:
            if self._model_pool:
                async with self._model_pool.acquire() as model_resource:
                    start_time = time.time()
                    
                    results = model_resource.predict(
                        request.image,
                        conf=request.confidence_threshold,
                        iou=request.iou_threshold,
                        verbose=False
                    )
                    
                    inference_time = (time.time() - start_time) * 1000
                    
                    # Process results
                    detections = []
                    for result in results:
                        if hasattr(result, 'boxes') and result.boxes is not None:
                            for box in result.boxes:
                                bbox = box.xyxy[0].tolist()
                                center = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
                                area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                                
                                detection = Detection(
                                    class_name=result.names[int(box.cls)],
                                    class_id=int(box.cls),
                                    confidence=float(box.conf),
                                    bbox=bbox,
                                    center=center,
                                    area=area
                                )
                                detections.append(detection)
                    
                    # Filter and limit
                    if request.class_filter:
                        detections = [d for d in detections if d.class_name in request.class_filter]
                    
                    detections = detections[:request.max_detections]
                    
                    return DetectionResult(
                        request_id=request.request_id,
                        detections=detections,
                        inference_time_ms=inference_time,
                        total_time_ms=inference_time,
                        image_shape=request.image.shape,
                        model_version="yolov8_local"
                    )
            else:
                # No model pool - return empty result
                return DetectionResult(
                    request_id=request.request_id,
                    detections=[],
                    inference_time_ms=0.0,
                    total_time_ms=0.0,
                    image_shape=request.image.shape,
                    model_version="no_model"
                )
                
        except Exception as e:
            logger.error(f"Local inference failed: {e}")
            
            return DetectionResult(
                request_id=request.request_id,
                detections=[],
                inference_time_ms=0.0,
                total_time_ms=0.0,
                image_shape=request.image.shape,
                model_version="error"
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive pipeline statistics"""
        uptime = None
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
        
        # Queue sizes
        queue_sizes = {}
        for priority, queue in self._request_queues.items():
            queue_sizes[priority.name] = queue.qsize()
        
        # Pending batches
        batch_sizes = {}
        for quality, requests in self._pending_batches.items():
            batch_sizes[quality.value] = len(requests)
        
        stats = {
            "pipeline": {
                "running": self._running,
                "uptime_seconds": uptime,
                "total_requests": self.total_requests,
                "total_detections": self.total_detections,
                "avg_inference_time_ms": self.avg_inference_time,
                "cache_hits": self.cache_hits,
                "batch_count": self.batch_count,
                "requests_per_second": self.total_requests / max(1, uptime or 1)
            },
            "configuration": {
                "device": self.device,
                "enable_batching": self.enable_batching,
                "enable_caching": self.enable_caching,
                "enable_process_workers": self.enable_process_workers,
                "batch_size": self._batch_size,
                "batch_timeout_ms": self._batch_timeout_ms
            },
            "queues": {
                "request_queues": queue_sizes,
                "pending_batches": batch_sizes
            },
            "cache": self.cache.get_stats(),
            "model_pool": self._model_pool.get_stats() if self._model_pool else None
        }
        
        return stats

# Global instance
optimized_yolo_pipeline: Optional[OptimizedYOLOPipeline] = None

async def initialize_yolo_pipeline(models_dir: Path, device: str = "cpu") -> OptimizedYOLOPipeline:
    """Initialize global YOLO pipeline"""
    global optimized_yolo_pipeline
    
    if optimized_yolo_pipeline is None:
        optimized_yolo_pipeline = OptimizedYOLOPipeline(models_dir, device)
        await optimized_yolo_pipeline.initialize()
        await optimized_yolo_pipeline.start()
        
        logger.info("🎯 Global YOLO pipeline initialized")
    
    return optimized_yolo_pipeline

def get_yolo_pipeline() -> Optional[OptimizedYOLOPipeline]:
    """Get global YOLO pipeline instance"""
    return optimized_yolo_pipeline

if __name__ == "__main__":
    # Test the optimized pipeline
    async def test_yolo_pipeline():
        print("🧪 Testing Optimized YOLO Pipeline")
        print("=" * 50)
        
        # Mock test setup
        models_dir = Path("models")  # Would be real path in production
        
        # Create test images
        test_images = []
        for i in range(5):
            # Create random test image
            image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
            test_images.append(image)
        
        try:
            # Initialize pipeline (would fail without real models)
            pipeline = OptimizedYOLOPipeline(models_dir, "cpu")
            print("✅ Pipeline created")
            
            # Test request creation
            requests = []
            for i, image in enumerate(test_images):
                request = DetectionRequest(
                    image=image,
                    mode=DetectionMode.BATCH,
                    quality=DetectionQuality.FAST,
                    confidence_threshold=0.5,
                    priority=TaskPriority.NORMAL
                )
                requests.append(request)
            
            print(f"📋 Created {len(requests)} test requests")
            
            # Test cache
            cache_stats = pipeline.cache.get_stats()
            print(f"💾 Cache stats: {cache_stats}")
            
            # Test configuration
            stats = pipeline.get_stats()
            print(f"📊 Pipeline stats: {stats['configuration']}")
            
            print("✅ Test completed (limited without real models)")
            
        except Exception as e:
            print(f"❌ Test failed (expected without real models): {e}")
    
    asyncio.run(test_yolo_pipeline())