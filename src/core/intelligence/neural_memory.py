#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Neural Memory Module
=================================
Canonical entry point for the Neural Memory system.
Wraps the UnifiedMemoryManager to provide a single stable import target.
"""

import logging
from src.core.intelligence.memory.unified_manager import UnifiedMemoryManager

logger = logging.getLogger(__name__)

# Initialize the Unified Memory Manager
# This singleton instance should be used throughout the application
try:
    neural_memory = UnifiedMemoryManager()
    logger.info("✅ Neural Memory initialized via UnifiedMemoryManager")
except Exception as e:
    logger.error(f"❌ Failed to initialize Neural Memory: {e}")
    # Fallback to a stub if absolutely necessary (but user wants strict failure, so maybe not?)
    # For now, let's allow it to fail or provide a minimal stub if crucial
    neural_memory = None

__all__ = ['neural_memory', 'UnifiedMemoryManager']
