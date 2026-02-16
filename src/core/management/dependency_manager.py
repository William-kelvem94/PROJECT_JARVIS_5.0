#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dependency Manager - Safe Import System with Mock Fallbacks
===========================================================

Prevents crashes when importing ML libraries on hardware that doesn't support them.
Uses the system_profile.json to determine what's available and provides mock objects
for unavailable libraries.

Usage:
    from src.core.dependency_manager import safe_import

    torch = safe_import('torch', strategy='OPTIONAL')
    model = torch.load('model.pt')  # Won't crash on LITE profile

Author: JARVIS Singularity Team
Version: 1.0.0
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict
from enum import Enum

logger = logging.getLogger(__name__)


class ImportStrategy(Enum):
    """Strategy for handling imports."""

    REQUIRED = "required"  # Must be available or crash
    OPTIONAL = "optional"  # Mock if unavailable
    PROFILE_DEPENDENT = "profile_dependent"  # Check profile config


class MockObject:
    """
    Mock object that accepts any method call and returns itself.
    Logs warnings instead of crashing.
    """

    def __init__(self, module_name: str, reason: str = "not available"):
        self._mock_module_name = module_name
        self._mock_reason = reason
        logger.warning(f"âš ï¸  Using mock for '{module_name}': {reason}")

    def __call__(self, *args, **kwargs):
        """Accept any call."""
        logger.debug(f"Mock call to {self._mock_module_name}(*args, **kwargs)")
        return self

    def __getattr__(self, name):
        """Return self for any attribute access."""
        logger.debug(f"Mock access: {self._mock_module_name}.{name}")
        return self

    def __repr__(self):
        return f"<MockObject for '{self._mock_module_name}' ({self._mock_reason})>"

    def __bool__(self):
        """Always truthy for if checks."""
        return True

    def __iter__(self):
        """Empty iterator."""
        return iter([])

    def __len__(self):
        """Length 0."""
        return 0


class DependencyManager:
    """Manages safe imports with profile awareness."""

    def __init__(self):
        self.profile_config = self._load_profile_config()
        self.import_cache: Dict[str, Any] = {}
        self.mock_cache: Dict[str, MockObject] = {}

    def _load_profile_config(self) -> Dict:
        """Load system_profile.json if it exists."""
        config_file = Path("config/system_profile.json")

        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load profile config: {e}")

        # Default to LITE profile if no config
        return {
            "profile": "LITE",
            "features": {"training_enabled": False, "full_ml_stack": False},
        }

    def get_profile(self) -> str:
        """Get the current hardware profile."""
        return self.profile_config.get("profile", "LITE")

    def is_training_enabled(self) -> bool:
        """Check if training is enabled."""
        return self.profile_config.get("features", {}).get("training_enabled", False)

    def is_available(self, module_name: str) -> bool:
        """Check if a module is really available (not mocked)."""
        if module_name in self.import_cache:
            obj = self.import_cache[module_name]
            return not isinstance(obj, MockObject)

        try:
            __import__(module_name)
            return True
        except ImportError:
            return False

    def safe_import(
        self, module_name: str, strategy: str = "OPTIONAL", mock_fallback: bool = True
    ) -> Any:
        """
        Safely import a module with fallback to mock if unavailable.

        Args:
            module_name: Name of module to import (e.g., 'torch', 'unsloth')
            strategy: ImportStrategy - REQUIRED, OPTIONAL, or PROFILE_DEPENDENT
            mock_fallback: Whether to return mock object if unavailable

        Returns:
            The imported module or a MockObject

        Raises:
            ImportError: Only if strategy is REQUIRED and module unavailable
        """
        # Check cache first
        if module_name in self.import_cache:
            return self.import_cache[module_name]

        # Check if we should even try to import based on profile
        if strategy == "PROFILE_DEPENDENT":
            if not self._should_import_for_profile(module_name):
                reason = f"Hardware profile {self.get_profile()} doesn't support it"
                mock = MockObject(module_name, reason)
                self.mock_cache[module_name] = mock
                self.import_cache[module_name] = mock
                return mock

        # Try to import
        try:
            module = __import__(module_name)
            self.import_cache[module_name] = module
            logger.debug(f"âœ“ Imported {module_name}")
            return module

        except ImportError as e:
            # Handle import failure
            if strategy == "REQUIRED":
                logger.error(f"âŒ Required module '{module_name}' not available!")
                raise

            if mock_fallback:
                reason = f"not installed ({str(e)})"
                mock = MockObject(module_name, reason)
                self.mock_cache[module_name] = mock
                self.import_cache[module_name] = mock
                logger.info(f"Using mock for '{module_name}'")
                return mock
            else:
                raise

    def _should_import_for_profile(self, module_name: str) -> bool:
        """Check if module should be imported based on profile."""
        profile = self.get_profile()
        training_enabled = self.is_training_enabled()

        # ML training libraries only on profiles with training enabled
        ml_training_libs = ["unsloth", "peft", "deepspeed", "trl", "bitsandbytes"]
        if module_name in ml_training_libs:
            return training_enabled

        # Torch available on HYBRID and ULTIMATE
        if module_name in ["torch", "torchaudio", "transformers"]:
            return profile in ["HYBRID", "ULTIMATE"]

        # Everything else is OK
        return True

    def clear_cache(self):
        """Clear import cache."""
        self.import_cache.clear()
        self.mock_cache.clear()

    def get_statistics(self) -> Dict:
        """Get statistics about imports."""
        return {
            "total_imports": len(self.import_cache),
            "real_imports": len(
                [
                    k
                    for k, v in self.import_cache.items()
                    if not isinstance(v, MockObject)
                ]
            ),
            "mocked_imports": len(self.mock_cache),
            "profile": self.get_profile(),
            "training_enabled": self.is_training_enabled(),
        }


# Global instance
_dependency_manager = None


def get_dependency_manager() -> DependencyManager:
    """Get or create the global dependency manager."""
    global _dependency_manager
    if _dependency_manager is None:
        _dependency_manager = DependencyManager()
    return _dependency_manager


def safe_import(
    module_name: str, strategy: str = "OPTIONAL", mock_fallback: bool = True
) -> Any:
    """
    Convenience function for safe imports.

    Args:
        module_name: Module to import
        strategy: 'REQUIRED', 'OPTIONAL', or 'PROFILE_DEPENDENT'
        mock_fallback: Return mock if unavailable

    Returns:
        Imported module or MockObject

    Example:
        >>> torch = safe_import('torch', strategy='PROFILE_DEPENDENT')
        >>> model = torch.load('model.pt')  # Won't crash on LITE
    """
    manager = get_dependency_manager()
    return manager.safe_import(module_name, strategy, mock_fallback)


def is_available(module_name: str) -> bool:
    """
    Check if a module is really available (not mocked).

    Example:
        >>> if is_available('torch'):
        >>>     # Use real torch
        >>> else:
        >>>     # Use alternative
    """
    manager = get_dependency_manager()
    return manager.is_available(module_name)


def get_profile() -> str:
    """Get the current hardware profile (LITE/HYBRID/ULTIMATE)."""
    manager = get_dependency_manager()
    return manager.get_profile()


# Example usage
if __name__ == "__main__":
    print("ðŸ›¡ï¸  Dependency Manager Test\n")

    manager = get_dependency_manager()
    print(f"Profile: {manager.get_profile()}")
    print(f"Training Enabled: {manager.is_training_enabled()}\n")

    # Test imports
    print("Testing imports...")

    # This should work everywhere
    psutil = safe_import("psutil", strategy="REQUIRED")
    print(f"psutil: {type(psutil)}")

    # This might be mocked on LITE
    torch = safe_import("torch", strategy="PROFILE_DEPENDENT")
    print(f"torch: {type(torch)}")
    print(f"torch available: {is_available('torch')}")

    # This will definitely be mocked on LITE/HYBRID
    unsloth = safe_import("unsloth", strategy="PROFILE_DEPENDENT")
    print(f"unsloth: {type(unsloth)}")
    print(f"unsloth available: {is_available('unsloth')}")

    # Test that mocked objects don't crash
    print("\nTesting mock behavior...")
    model = unsloth.FastLanguageModel.from_pretrained("test")
    print(f"Mock call result: {type(model)}")

    print("\nâœ… All tests passed! No crashes.")
    print(f"\nStatistics: {manager.get_statistics()}")
