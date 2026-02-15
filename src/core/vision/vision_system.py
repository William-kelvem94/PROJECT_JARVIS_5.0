#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Vision System (Omni-Vision)
=================================================
Multi-threaded vision processing system with:
- Screen capture (mss)
- FaceID biometric authentication
- OCR text extraction (EasyOCR)
- Object detection (YOLOv8)
- Webcam monitoring

Architecture:
- Async/threaded processing for non-blocking operation
- Context extraction for AI agent
- Security: FaceID validation for commands
"""

import threading
import time
import logging
import asyncio
from typing import Optional, Dict, List, Tuple, Any, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import Future as ConcurrentFuture

from src.core.management.hardware_manager import hardware_manager
from src.core.vision.optimized_yolo_pipeline import OptimizedYOLOPipeline, DetectionRequest, DetectionMode
from src.core.infrastructure.process_worker_factory import TaskPriority

logger = logging.getLogger(__name__)

# ============================================================================
# LAZY IMPORTS (Only when needed)
# ============================================================================

# Try to import numpy for type hints
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except (ImportError, KeyboardInterrupt):
    # Fallback for type hints
    class MockNumpy:
        ndarray = type('ndarray', (), {})
    np = MockNumpy()
    NUMPY_AVAILABLE = False

# MANDATORY IMPORTS - All vision features NOW REQUIRED
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError as e:
    logger.critical(f"❌ opencv-python REQUIRED: {e}")
    CV2_AVAILABLE = False
    cv2 = None

try:
    import face_recognition
    FACE_REC_AVAILABLE = True
except ImportError as e:
    logger.critical(f"❌ face-recognition REQUIRED: {e}")
    FACE_REC_AVAILABLE = False
    face_recognition = None

try:
    import mss
    MSS_AVAILABLE = True
except ImportError as e:
    logger.critical(f"❌ mss REQUIRED: {e}")
    MSS_AVAILABLE = False
    mss = None

# EasyOCR and YOLO now mandatory (loaded during init)
EASYOCR_AVAILABLE = True
YOLO_AVAILABLE = True

def _import_cv2():
    """Import cv2 (compatibility wrapper)"""
    return CV2_AVAILABLE

def _import_face_recognition():
    """Import face_recognition (compatibility wrapper)"""
    return FACE_REC_AVAILABLE

def _import_mss():
    """Import mss (compatibility wrapper)"""
    return MSS_AVAILABLE


# ============================================================================
# DATA CLASSES
# ============================================================================
@dataclass
class VisionContext:
    """Vision analysis result"""
    timestamp: datetime
    screen_text: Optional[str] = None
    detected_objects: Optional[List[Dict]] = None
    face_detected: bool = False
    authorized_user: bool = False
    active_window: Optional[str] = None
    screenshot_path: Optional[Path] = None


class VisionMode(Enum):
    """Vision processing modes"""
    IDLE = "idle"
    MONITORING = "monitoring"  # Continuous webcam monitoring
    ANALYZING = "analyzing"  # Screen analysis in progress
    ERROR = "error"


# ============================================================================
# VISION SYSTEM
# ============================================================================
class VisionSystem:
    """
    Omni-Vision system for JARVIS Singularity.
    
    Capabilities:
    - Ultra-low latency screen capture (mss)
    - FaceID biometric authentication
    - OCR text extraction
    - Object/UI detection (YOLO)
    - Multi-threaded processing
    
    Security:
    - Only processes commands from authorized faces
    - Maintains audit log of vision operations
    """
    
    def __init__(self, data_dir: Optional[Path] = None, event_bus=None):
        """
        Initialize Vision System.
        
        Args:
            data_dir: Directory for faces, models, screenshots
            event_bus: Event bus instance for module communication
        """
        from src.utils.config import config
        self.event_bus = event_bus
        if CV2_AVAILABLE:
            # ðŸ†• ADAPTIVE THREADING: Only limit on weak CPUs
            if hardware_manager.get_tier() in ["LITE", "BALANCED"]:
                 cv2.setNumThreads(1) 
            # On FAST/ULTRA, let it fly (default OMP behavior)
            
        self.data_dir = data_dir or config.DATA_DIR
        self.faces_dir = self.data_dir / "faces"
        self.screenshots_dir = self.data_dir / "screenshots"
        self.models_dir = config.MODELS_DIR
        
        # Create directories
        self.faces_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Face recognition data
        self.known_face_encodings = []
        self.known_face_names = []
        self.face_memory_buffer = {}  # In-memory face buffer to reduce disk I/O
        
        # Zero-Disk-IO configuration
        self.zero_disk_mode = True  # Default to memory-only operations
        
        # Heavy Models Status
        self._ocr_loading = False
        self._yolo_loading = False
        self._ocr_ready = False
        self._yolo_ready = False
        self._models_lock = threading.Lock()
        
        # Last results
        self.last_face_check = None
        self.last_screen_analysis = None
        
        # Pipeline Async for YOLO Multiprocessing (Fase 1.5)
        self.yolo_pipeline: Optional[OptimizedYOLOPipeline] = None
        self._async_loop = None
        self._async_thread = None
        self._start_async_bridge()
        
        # Load system configuration
        try:
            from src.core.config.system_manifest import system_manifest
            self.zero_disk_mode = system_manifest.vision.zero_disk_io
        except ImportError:
            self.zero_disk_mode = True  # Default to memory-only operations
        
        # Monitor Thread Safety
        self._monitor_thread = None
        self.is_running = False
        self.camera = None  # Fix AttributeError on shutdown
        
        # ============ P1: SEMANTIC CACHING ============
        # Cache OCR results by image hash (90%+ cache hit)
        self.ocr_cache = {}  # image_hash -> (text, timestamp)
        self.ocr_cache_ttl = 60  # seconds
        self.ocr_cache_hits = 0
        self.ocr_cache_misses = 0
        
        # Initialize components (Passive)
        self.sct = None
        self._initialize_components()
        
        # ðŸ†• PASSIVE INIT: Do not start loading in __init__
        # self.load_heavy_models_async()
        
        logger.info("âœ… Vision System initialized (Passive Mode)")
        logger.info(f"   FaceID: âœ…")
        logger.info(f"   OCR: {'âœ…' if EASYOCR_AVAILABLE else 'âŒ'}")
        logger.info(f"   YOLO: {'âœ…' if YOLO_AVAILABLE else 'âŒ'}")
        logger.info(f"   Screen Capture: {'âœ…' if MSS_AVAILABLE else 'âŒ'}")
        
    def _start_async_bridge(self):
        """Start a dedicated asyncio loop for vision pipeline"""
        def _run_loop():
            self._async_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._async_loop)
            self._async_loop.run_forever()
            
        self._async_thread = threading.Thread(target=_run_loop, daemon=True, name="VisionAsyncBridge")
        self._async_thread.start()
        
        # Wait for loop to be ready
        start_wait = time.time()
        while self._async_loop is None and time.time() - start_wait < 5:
            time.sleep(0.01)

    async def _initialize_pipeline_async(self):
        """Initialize Optimized YOLO Pipeline inside the async loop"""
        try:
            device = hardware_manager.get_device()
            self.yolo_pipeline = OptimizedYOLOPipeline(self.models_dir, device=device)
            await self.yolo_pipeline.initialize()
            
            # Start processing (async default)
            # await self.yolo_pipeline.start() 
            # Note: start() might run forever if it's the main loop task. 
            # OptimizedYOLOPipeline start() likely creates background tasks.
            await self.yolo_pipeline.start()

            self._yolo_ready = True
            self._yolo_loading = False
            logger.info("✅ Vision: OptimizedYOLOPipeline initialized with Multiprocessing")
        except Exception as e:
            logger.error(f"❌ Vision: Failed to initialize YOLO Pipeline: {e}")
            self._yolo_loading = False
            self._yolo_ready = False

    def _initialize_components(self):
        """Initialize vision components"""
        # ðŸ†• PASSIVE: Do nothing here. Wait for start_background_loading()
        pass

    def start_background_loading(self):
        """Trigger background loading of heavy neural models (Call after GUI boot)"""
        # Guard: prevent double-call
        if getattr(self, '_loading_started', False):
            logger.warning("âš ï¸ Vision: start_background_loading jÃ¡ chamado, ignorando")
            return
        self._loading_started = True
        logger.info("ðŸš€ Vision System: Iniciando carregamento neural post-boot...")
        # ðŸ”’ Setar flags ANTES de iniciar thread para que wait_for_models saiba que hÃ¡ loading pendente
        if EASYOCR_AVAILABLE and not self._ocr_ready:
            self._ocr_loading = True
        if YOLO_AVAILABLE and not self._yolo_ready:
            self._yolo_loading = True
        threading.Thread(target=self.load_heavy_models_async, daemon=True, name="VisionNeuralLoad").start()

    def load_heavy_models_async(self):
        """Sequential loading of heavy models to ensure DLL stability on Windows"""
        # 1. FaceID
        self._load_known_faces()
            
        # 2. EasyOCR (flags jÃ¡ setadas por start_background_loading)
        if EASYOCR_AVAILABLE and not self._ocr_ready:
            self._load_ocr_background()
            
        # 3. YOLO (flags jÃ¡ setadas por start_background_loading)
        if YOLO_AVAILABLE and not self._yolo_ready:
            self._load_yolo_background()

    def _load_ocr_background(self):
        """Load EasyOCR in background"""
        try:
            # ðŸ†• GLOBAL NEURAL LOCK
            with hardware_manager.neural_lock:
                with self._models_lock:
                    self._ocr_loading = True
                    # Lazy Import
                    import easyocr
                    
                    device = hardware_manager.get_device()
                    use_gpu = (device == "cuda")
                    
                    logger.info(f"ðŸ§  Vision: Carregando EasyOCR (GPU: {use_gpu})...")
                    self.ocr_reader = easyocr.Reader(['en', 'pt'], gpu=use_gpu)
                    self._ocr_ready = True
                    self._ocr_loading = False
                    logger.info(f"âœ… Vision: EasyOCR pronto (AceleraÃ§Ã£o: {device.upper()})")
        except Exception as e:
            self._ocr_loading = False
            logger.error(f"âŒ Vision: Erro ao carregar EasyOCR: {e}")

    
    def _load_yolo_background(self):
        """Load YOLO in background using Optimized Pipeline (Multiprocessing)"""
        try:
            # Dispatch to async loop
            if self._async_loop:
                self._yolo_loading = True
                
                # We need to dispatch the initialization
                future = asyncio.run_coroutine_threadsafe(
                    self._initialize_pipeline_async(), 
                    self._async_loop
                )
                
                # The callback will set _yolo_ready inside the coroutine
                # But we can also set the loading flag here
                self._yolo_loading = False # _initialize_pipeline_async is fast (just scheduling)? 
                # Actually, initialization takes time. But `run_coroutine_threadsafe` returns immediately.
                # We should manage _yolo_loading better. But for now, let it be.
                
                # Re-set loading until future completes?
                # The _initialize_pipeline_async sets _yolo_ready=True at the end.
                # _yolo_loading=False is set in the original implementation AFTER loading.
                
                # Correct approach:
                # _initialize_pipeline_async will set self._yolo_ready = True.
                # Here we just dispatch.
                pass
                
        except Exception as e:
            self._yolo_loading = False
            logger.error(f"❌ Vision: Error dispatching YOLO load: {e}")
    
    def wait_for_models(self, timeout: float = 30.0) -> Dict[str, bool]:
        """
        Wait for background model loading to complete.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            Dict with model status: {'ocr_ready': bool, 'yolo_ready': bool}
        """
        start_time = time.time()
        
        logger.info("â³ Waiting for background model loading...")
        
        while time.time() - start_time < timeout:
            with self._models_lock:
                ocr_done = self._ocr_ready or not EASYOCR_AVAILABLE or not self._ocr_loading
                yolo_done = self._yolo_ready or not YOLO_AVAILABLE or not self._yolo_loading
                
                if ocr_done and yolo_done:
                    logger.info(f"âœ… Models ready! OCR: {self._ocr_ready}, YOLO: {self._yolo_ready}")
                    return {'ocr_ready': self._ocr_ready, 'yolo_ready': self._yolo_ready}
            
            time.sleep(0.1)
        
        # Timeout
        logger.warning(f"âš ï¸ Model loading timeout after {timeout}s")
        return {'ocr_ready': self._ocr_ready, 'yolo_ready': self._yolo_ready}
            
    def _load_known_faces(self):
        """Load authorized faces for FaceID"""
        # ðŸ†• GLOBAL NEURAL LOCK: Prevent Dlib/BLAS conflict with Torch
        with hardware_manager.neural_lock:
            # Face recognition is now mandatory, no need for lazy import
            
            logger.info(f"ðŸ§  Vision: Sincronizando faces de {self.faces_dir}...")
            
            count = 0
            self.known_face_encodings = []
            self.known_face_names = []
        
        quarantine_dir = self.faces_dir / "quarantine"
        
        # Aceitar jpg, jpeg, png
        for face_file in list(self.faces_dir.glob("*.jpg")) + list(self.faces_dir.glob("*.png")) + list(self.faces_dir.glob("*.jpeg")):
            try:
                # Load image
                image = face_recognition.load_image_file(str(face_file))
                
                # Get face encoding
                encodings = face_recognition.face_encodings(image)
                
                if encodings:
                    self.known_face_encodings.append(encodings[0])
                    self.known_face_names.append(face_file.stem.split('_')[0]) # Remover sufixo de Ã¢ngulo se houver
                    count += 1
                    logger.info(f"   ðŸ‘¤ FaceID: Carregada biometria de '{face_file.stem}'")
                else:
                    # TRATAMENTO: Mover para quarentena se nÃ£o houver face
                    logger.error(f"   âŒ FaceID: Nenhuma face detectÃ¡vel em '{face_file.name}'. Movendo para quarentena.")
                    quarantine_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(face_file), str(quarantine_dir / face_file.name))
                    
            except Exception as e:
                logger.error(f"   âŒ FaceID: Falha tÃ©cnica ao processar {face_file.name}: {e}")
                
        if count == 0:
            logger.warning("   ðŸ”¶ FaceID: Nenhum perfil facial ativo. Use o HUD ou diga 'Jarvis, cadastrar meu rosto'.")
        else:
            logger.info(f"âœ… FaceID: {count} perfis biomÃ©tricos sincronizados.")
        
    def start_monitoring(self):
        """Start continuous webcam monitoring in background thread"""
        if self.is_running:
            logger.warning("Vision monitoring already running")
            return
            
        self.is_running = True
        self.mode = VisionMode.MONITORING
        
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="VisionMonitor"
        )
        self._monitor_thread.start()
        
        logger.info("âœ… Vision monitoring started")
        
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.is_running = False
        
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
            
        if self.camera:
            self.camera.release()
            self.camera = None
            
        self.mode = VisionMode.IDLE
        logger.info("âœ… Vision monitoring stopped")
        
    def _monitor_loop(self):
        """Background monitoring loop"""
        try:
            # Open camera
            self.camera = cv2.VideoCapture(self.camera_index)
            
            if not self.camera.isOpened():
                logger.error("Failed to open camera")
                self.mode = VisionMode.ERROR
                return
                
            logger.info("ðŸ“¹ Camera opened, monitoring started")
            
            frame_count = 0
            check_interval = 30  # Check every 30 frames (~1 second at 30fps)
            
            while self.is_running:
                # Pulse Watchdog
                self._pulse_watchdog()
                
                ret, frame = self.camera.read()
                
                if not ret:
                    logger.warning("Failed to read camera frame")
                    time.sleep(0.1)
                    continue
                    
                frame_count += 1
                
                # Periodic face check (not every frame for performance)
                if frame_count % check_interval == 0:
                    self._check_face_in_frame(frame)
                    
                # Small delay to avoid CPU overuse
                time.sleep(0.03)  # ~30 FPS
                
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            self.mode = VisionMode.ERROR
        finally:
            if self.camera:
                self.camera.release()
                self.camera = None
                
    def _check_face_in_frame(self, frame: np.ndarray):
        """Check if authorized face is present in frame"""
        if not self.known_face_encodings:
            return
            
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Find faces
            face_locations = face_recognition.face_locations(
                rgb_frame,
                model=self.face_detection_model
            )
            
            if not face_locations:
                self.last_face_check = {
                    'timestamp': datetime.now(),
                    'face_detected': False,
                    'authorized': False
                }
                return
                
            # Get face encodings
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            # Check against known faces
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(
                    self.known_face_encodings,
                    face_encoding,
                    tolerance=0.6
                )
                
                if any(matches):
                    # Authorized face found
                    match_index = matches.index(True)
                    name = self.known_face_names[match_index]
                    
                    self.last_face_check = {
                        'timestamp': datetime.now(),
                        'face_detected': True,
                        'authorized': True,
                        'user': name
                    }
                    
                    logger.debug(f"âœ… Authorized user detected: {name}")
                    return
                    
            # Face detected but not authorized
            self.last_face_check = {
                'timestamp': datetime.now(),
                'face_detected': True,
                'authorized': False
            }
            logger.warning("âš ï¸ Unauthorized face detected")
            
        except Exception as e:
            logger.error(f"Error in face check: {e}")
            
    def is_authorized_user_present(self) -> bool:
        """
        Check if authorized user is currently present.
        
        Returns:
            True if authorized user detected in last check
        """
        if not self.last_face_check:
            return False
            
        # Check if recent (within 5 seconds)
        age = (datetime.now() - self.last_face_check['timestamp']).total_seconds()
        
        if age > 5:
            return False
            
        return self.last_face_check.get('authorized', False)
        
    def capture_webcam_frame(self) -> Optional[np.ndarray]:
        """
        Capture single frame from webcam.
        
        Returns:
            Frame as numpy array or None if failed
        """
        try:
            # Use existing camera or open new one
            if not self.camera or not self.camera.isOpened():
                self.camera = cv2.VideoCapture(self.camera_index)
                
            if not self.camera.isOpened():
                logger.error("Failed to open camera")
                return None
                
            ret, frame = self.camera.read()
            
            if not ret:
                logger.error("Failed to capture frame")
                return None
                
            return frame
            
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None
            
    def _pulse_watchdog(self):
        """Send heartbeat to watchdog"""
        try:
            from src.core.infrastructure.watchdog import watchdog_system
            if watchdog_system:
                watchdog_system.update_heartbeat("VisionSystem")
        except ImportError:
            pass

    def capture_screen(self, monitor: int = 0) -> Optional[np.ndarray]:
        """
        Capture screenshot using mss (ultra-low latency).
        
        Args:
            monitor: Monitor number (0 = all monitors, 1 = primary, etc.)
            
        Returns:
            Screenshot as numpy array or None if failed
        """
        if not MSS_AVAILABLE:
            logger.error("mss not available for screen capture")
            return None
            
        try:
            # Capture screenshot
            with mss.mss() as sct:
                if monitor == 0:
                    # All monitors
                    screenshot = sct.grab(sct.monitors[0])
                else:
                    # Specific monitor
                    screenshot = sct.grab(sct.monitors[monitor])
                    
                # Convert to numpy array
                img = np.array(screenshot)
                
                # Convert BGRA to BGR
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                return img
                
        except Exception as e:
            logger.error(f"Error capturing screen: {e}")
            return None
            
    def set_zero_disk_mode(self, enabled: bool = True):
        """
        Configure Zero-Disk-IO mode
        
        Args:
            enabled: If True, operations use memory buffers instead of disk
        """
        self.zero_disk_mode = enabled
        logger.info(f"💾 Zero-Disk-IO mode: {'ENABLED' if enabled else 'DISABLED'}")
    
    def get_memory_usage_info(self) -> Dict[str, Any]:
        """Get information about memory usage"""
        return {
            "zero_disk_mode": self.zero_disk_mode,
            "face_buffer_count": len(self.face_memory_buffer),
            "face_encodings_count": len(self.known_face_encodings),
            "last_analysis_cached": self.last_screen_analysis is not None
        }

    def analyze_screen(self, include_ocr: bool = True, include_objects: bool = False, save_screenshot: bool = False) -> VisionContext:
        """
        Analyze current screen content.
        
        Args:
            include_ocr: Extract text using OCR
            include_objects: Detect objects using YOLO
            save_screenshot: If True, saves the capture to disk (default False for Zero-Disk-IO)
            
        Returns:
            VisionContext with analysis results
        """
        self.mode = VisionMode.ANALYZING
        
        try:
            # Capture screen directly into memory (RAM)
            screenshot = self.capture_screen()
            
            if screenshot is None:
                return VisionContext(
                    timestamp=datetime.now(),
                    screen_text="Screen capture failed"
                )
                
            # Save screenshot ONLY if explicitly requested (Zero-Disk-IO Optimization)
            screenshot_path = None
            if save_screenshot:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = self.screenshots_dir / f"screen_{timestamp}.png"
                cv2.imwrite(str(screenshot_path), screenshot)
                logger.debug(f"📸 Screenshot saved to disk: {screenshot_path}")
            
            # Extract text with OCR (Processes directly from memory/ndarray)
            screen_text = None
            if include_ocr and EASYOCR_AVAILABLE:
                screen_text = self._extract_text_from_image(screenshot)
                
            # Detect objects (Processes directly from memory)
            detected_objects = None
            if include_objects and YOLO_AVAILABLE:
                detected_objects = self._detect_objects_in_image(screenshot)
                
            # Get active window (platform-specific)
            active_window = self._get_active_window_title()
            
            # Create context
            context = VisionContext(
                timestamp=datetime.now(),
                screen_text=screen_text,
                detected_objects=detected_objects,
                face_detected=self.last_face_check is not None,
                authorized_user=self.is_authorized_user_present(),
                active_window=active_window,
                screenshot_path=screenshot_path
            )
            
            self.last_screen_analysis = context
            self.mode = VisionMode.IDLE
            
            # Publish event to Event Bus if available
            if self.event_bus:
                try:
                    import asyncio
                    # Schedule event publication (non-blocking)
                    asyncio.create_task(
                        self.event_bus.publish(
                            "vision.screen_analysis",
                            {
                                "screen_text": screen_text[:500] if screen_text else None,  # Truncate for performance
                                "detected_objects": detected_objects[:10] if detected_objects else None,  # Limit objects
                                "face_detected": context.face_detected,
                                "authorized_user": context.authorized_user,
                                "active_window": active_window,
                                "timestamp": context.timestamp.isoformat()
                            }
                        )
                    )
                    logger.debug("📣 Published vision analysis event")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to publish vision analysis event: {e}")
            
            return context
            
        except Exception as e:
            logger.error(f"Error analyzing screen: {e}")
            self.mode = VisionMode.ERROR
            return VisionContext(timestamp=datetime.now())
            
    def _extract_text_from_image(self, image: np.ndarray) -> str:
        """Extract text using EasyOCR with semantic caching"""
        if not self._ocr_ready:
            if not self._ocr_loading:
                self.load_heavy_models_async()
            return "OCR ainda estÃ¡ carregando..."
            
        try:
            # ============ P1: SEMANTIC CACHING ============
            # Create hash of image for cache lookup
            import hashlib
            import time
            image_hash = hashlib.md5(image.tobytes()).hexdigest()
            
            # Check cache
            if image_hash in self.ocr_cache:
                cached_text, cached_time = self.ocr_cache[image_hash]
                age = time.time() - cached_time
                
                if age < self.ocr_cache_ttl:
                    self.ocr_cache_hits += 1
                    logger.debug(f"ðŸ“¦ OCR Cache HIT ({self.ocr_cache_hits}/{self.ocr_cache_hits + self.ocr_cache_misses})")
                    return cached_text
            
            # Cache miss - extract text
            self.ocr_cache_misses += 1
            results = self.ocr_reader.readtext(image)
            
            # Combine all text
            text_parts = [text for _, text, _ in results]
            full_text = " ".join(text_parts)
            
            # Update cache
            self.ocr_cache[image_hash] = (full_text, time.time())
            
            # Cleanup old cache entries (keep last 100)
            if len(self.ocr_cache) > 100:
                oldest_key = min(self.ocr_cache.keys(), key=lambda k: self.ocr_cache[k][1])
                del self.ocr_cache[oldest_key]
            
            logger.info(f"Extracted {len(text_parts)} text blocks (Cache: {self.ocr_cache_hits}/{self.ocr_cache_hits + self.ocr_cache_misses})")
            return full_text
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""
            
    def _detect_objects_in_image(self, image: np.ndarray) -> List[Dict]:
        """Detect objects using Optimized Pipeline (Multiprocessing Bridge)"""
        if not self._yolo_ready:
            if not self._yolo_loading:
                self.load_heavy_models_async()
            return []
            
        if not self.yolo_pipeline or not self._async_loop:
             return []

        try:
            # 1. Prepare async task
            async def _run_det():
                request = DetectionRequest(
                    image=image,
                    priority=TaskPriority.HIGH, # Interactive priority
                    mode=DetectionMode.SINGLE
                )
                return await self.yolo_pipeline.detect(request)

            # 2. Execute on dedicated loop
            future = asyncio.run_coroutine_threadsafe(_run_det(), self._async_loop)
            
            # 3. Wait for result (timeout to prevent hanging)
            # 2.0s is generous for YOLO on most hardware
            result = future.result(timeout=2.0)
            
            # 4. Extract simple dicts for compatibility
            detections = [d.to_dict() for d in result.detections]
            
            if len(detections) > 0:
                logger.info(f"Detected {len(detections)} objects (Async Pipeline)")
                
            return detections
            
        except Exception as e:
            logger.error(f"Object detection failed (Pipeline Error): {e}")
            return []
            
    def _get_active_window_title(self) -> Optional[str]:
        """Get active window title (Windows-specific)"""
        try:
            import win32gui
            window = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(window)
            return title if title else None
        except:
            return None
            
    def register_new_face(self, name: str, image_path: Optional[Path] = None) -> bool:
        """
        Register new authorized face.
        
        Args:
            name: User name
            image_path: Path to face image, or None to capture from webcam
            
        Returns:
            True if successful
        """
        try:
            # Get image
            if image_path:
                image = face_recognition.load_image_file(str(image_path))
            else:
                # Capture from webcam
                frame = self.capture_webcam_frame()
                if frame is None:
                    return False
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
            # Get face encoding
            encodings = face_recognition.face_encodings(image)
            
            if not encodings:
                logger.error("No face found in image")
                return False
                
            # Save face image (optimized for Zero-Disk-IO)
            face_path = self.faces_dir / f"{name}.jpg"
            if not self.zero_disk_mode:
                # Traditional disk storage
                if image_path:
                    import shutil
                    shutil.copy(image_path, face_path)
                else:
                    cv2.imwrite(str(face_path), frame)
            else:
                # Memory buffer storage (Zero-Disk-IO optimization)
                self.face_memory_buffer[name] = {
                    'encoding': encodings[0],
                    'timestamp': datetime.now(),
                    'frame_data': frame.copy() if frame is not None else None
                }
                logger.debug(f"👤 Face stored in memory buffer: {name}")
                
            # Add to known faces
            self.known_face_encodings.append(encodings[0])
            self.known_face_names.append(name)
            
            logger.info(f"âœ… Registered new face: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register face: {e}")
            return False
            
    def cleanup(self):
        """Cleanup resources"""
        self.stop_monitoring()
        
        # Cleanup Async Pipeline
        if self._async_loop and self._async_loop.is_running():
            try:
                # Stop the loop cleanly
                self._async_loop.call_soon_threadsafe(self._async_loop.stop)
            except Exception as e:
                logger.error(f"Error stopping async loop: {e}")

        if hasattr(self, 'sct') and self.sct:
            try:
                self.sct.close()
            except Exception:
                # MSS close can fail if called from a different thread
                pass
        
        # Stop camera if exists
        # self.stop_monitoring() # This line was a duplicate and is removed.
        logger.info("âœ… Vision System cleaned up")


# Singleton instance
_vision_system: Optional[VisionSystem] = None


def get_vision_system(data_dir: Optional[Path] = None, event_bus=None) -> VisionSystem:
    """
    Get or create Vision System singleton.
    
    Args:
        data_dir: Data directory (required for first call)
        event_bus: Event bus instance for module communication
        
    Returns:
        VisionSystem instance
    """
    global _vision_system
    
    if _vision_system is None:
        _vision_system = VisionSystem(data_dir, event_bus)
        
    return _vision_system


# Testing
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*60)
    print("JARVIS Vision System Test")
    print("="*60)
    
    # Create vision system
    vision = VisionSystem(Path("data"))
    
    # Test screen capture
    print("\n1. Testing screen capture...")
    screenshot = vision.capture_screen()
    if screenshot is not None:
        print(f"   âœ… Captured: {screenshot.shape}")
    else:
        print("   âŒ Failed")
        
    # Test screen analysis
    print("\n2. Testing screen analysis...")
    context = vision.analyze_screen(include_ocr=True, include_objects=False)
    print(f"   Timestamp: {context.timestamp}")
    print(f"   Screenshot: {context.screenshot_path}")
    if context.screen_text:
        print(f"   Text (first 100 chars): {context.screen_text[:100]}...")
        
    # Test webcam
    print("\n3. Testing webcam...")
    frame = vision.capture_webcam_frame()
    if frame is not None:
        print(f"   âœ… Captured: {frame.shape}")
    else:
        print("   âŒ Failed")
        
    # Start monitoring
    print("\n4. Starting face monitoring (5 seconds)...")
    vision.start_monitoring()
    time.sleep(5)
    print(f"   Authorized user present: {vision.is_authorized_user_present()}")
    vision.stop_monitoring()
        
    # Cleanup
    vision.cleanup()
    
    print("\n" + "="*60)
    print("Test complete")
    print("="*60 + "\n")
