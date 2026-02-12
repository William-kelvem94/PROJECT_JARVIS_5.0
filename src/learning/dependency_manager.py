"""
Dependency Manager for JARVIS Learning Systems.

Centralizes optional dependency handling to avoid scattered try/except blocks
and provides graceful degradation when ML libraries are not available.
"""

import logging
from typing import Dict, Any, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class DependencyStatus:
    """Status of a dependency and its capabilities."""
    available: bool
    version: Optional[str] = None
    error: Optional[str] = None
    fallback_available: bool = False
    capabilities: Set[str] = field(default_factory=set)

class DependencyManager:
    """Manages optional dependencies for learning systems."""
    
    def __init__(self):
        self._status: Dict[str, DependencyStatus] = {}
        self._check_all_dependencies()
    
    def _check_all_dependencies(self):
        """Check all optional dependencies."""
        self._check_torch()
        self._check_transformers()
        self._check_peft()
        self._check_database()
        self._check_vision()
        self._check_audio()
        self._check_monitoring()
    
    def _check_torch(self):
        """Check PyTorch availability."""
        try:
            import torch
            self._status['torch'] = DependencyStatus(
                available=True,
                version=torch.__version__,
                capabilities={'training', 'inference', 'gpu' if torch.cuda.is_available() else 'cpu'}
            )
            logger.debug(f"✅ PyTorch {torch.__version__} available with {'GPU' if torch.cuda.is_available() else 'CPU'}")
        except Exception as e:
            self._status['torch'] = DependencyStatus(
                available=False,
                error=str(e),
                fallback_available=True,  # Can use CPU-only inference
                capabilities=set()
            )
            logger.warning(f"⚠️ PyTorch not available: {e}")
    
    def _check_transformers(self):
        """Check Transformers library."""
        try:
            import transformers
            self._status['transformers'] = DependencyStatus(
                available=True,
                version=transformers.__version__,
                capabilities={'llm_training', 'tokenization', 'inference'}
            )
        except Exception as e:
            self._status['transformers'] = DependencyStatus(
                available=False,
                error=str(e),
                capabilities=set()
            )
    
    def _check_peft(self):
        """Check PEFT (Parameter Efficient Fine-Tuning) library."""
        try:
            import peft
            self._status['peft'] = DependencyStatus(
                available=True,
                version=peft.__version__,
                capabilities={'lora', 'qlora', 'adapters'}
            )
        except Exception as e:
            self._status['peft'] = DependencyStatus(
                available=False,
                error=str(e),
                fallback_available=True,  # Can do full fine-tuning without PEFT
                capabilities=set()
            )
    
    def _check_database(self):
        """Check database options."""
        capabilities = set()
        
        # Check PostgreSQL
        try:
            import psycopg2
            capabilities.add('postgresql')
        except ImportError:
            pass
        
        # Check ChromaDB (Vector Database)
        try:
            import chromadb
            capabilities.add('vector_db')
        except ImportError:
            pass
        
        # SQLite is always available
        capabilities.add('sqlite')
        
        self._status['database'] = DependencyStatus(
            available=True,
            capabilities=capabilities,
            fallback_available=True  # SQLite always works
        )
    
    def _check_vision(self):
        """Check computer vision libraries."""
        capabilities = set()
        
        try:
            import ultralytics
            capabilities.add('yolo')
        except ImportError:
            pass
        
        try:
            import cv2
            capabilities.add('opencv')
        except ImportError:
            pass
        
        try:
            from PIL import Image
            capabilities.add('pil')
        except ImportError:
            pass
        
        self._status['vision'] = DependencyStatus(
            available=len(capabilities) > 0,
            capabilities=capabilities,
            fallback_available=len(capabilities) > 0
        )
    
    def _check_audio(self):
        """Check audio processing libraries."""
        capabilities = set()
        
        try:
            import librosa
            capabilities.add('audio_processing')
        except ImportError:
            pass
        
        try:
            import soundfile
            capabilities.add('audio_io')
        except ImportError:
            pass
        
        self._status['audio'] = DependencyStatus(
            available=len(capabilities) > 0,
            capabilities=capabilities
        )
    
    def _check_monitoring(self):
        """Check system monitoring libraries."""
        capabilities = set()
        
        try:
            import psutil
            capabilities.add('system_stats')
        except ImportError:
            pass
        
        try:
            import schedule  # type: ignore
            capabilities.add('scheduling')
        except ImportError:
            pass
        
        self._status['monitoring'] = DependencyStatus(
            available=len(capabilities) > 0,
            capabilities=capabilities,
            fallback_available=True  # Can use basic Python threading
        )
    
    def is_available(self, dependency: str, capability: Optional[str] = None) -> bool:
        """Check if a dependency and optional capability is available."""
        if dependency not in self._status:
            return False
        
        status = self._status[dependency]
        if not status.available:
            return False
        
        if capability and status.capabilities:
            return capability in status.capabilities
        
        return True
    
    def get_status(self, dependency: str) -> Optional[DependencyStatus]:
        """Get detailed status of a dependency."""
        return self._status.get(dependency)
    
    def get_capabilities(self, dependency: str) -> Set[str]:
        """Get available capabilities for a dependency."""
        status = self._status.get(dependency)
        return status.capabilities if status else set()
    
    def has_fallback(self, dependency: str) -> bool:
        """Check if a fallback is available for a dependency."""
        status = self._status.get(dependency)
        return status.fallback_available if status else False
    
    def get_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of all dependencies."""
        return {
            name: {
                'available': status.available,
                'version': status.version,
                'capabilities': list(status.capabilities) if status.capabilities else [],
                'fallback': status.fallback_available
            }
            for name, status in self._status.items()
        }
    
    def ensure_capability(self, dependency: str, capability: str, error_msg: Optional[str] = None):
        """Raise ImportError if capability is not available."""
        if not self.is_available(dependency, capability):
            if error_msg:
                raise ImportError(error_msg)
            else:
                raise ImportError(f"Required capability '{capability}' not available for '{dependency}'")

# Global dependency manager instance
dependency_manager = DependencyManager()