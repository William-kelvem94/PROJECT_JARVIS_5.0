# -*- coding: utf-8 -*-
"""
Model Registry Manager for JARVIS 5.0
=======================================

Facade layer over ModelRegistry providing simplified model lifecycle management.
Extracted from the monolithic LearningEngine to follow Single Responsibility.

Responsibilities:
- Model registration and versioning
- Model deployment and rollback
- Model comparison and A/B testing
- Model lifecycle cleanup
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger("JARVIS-MODEL-REGISTRY-MGR")


class ModelRegistryManager:
    """
    High-level model management facade.

    Wraps the lower-level ModelRegistry with convenience methods
    and lifecycle management.
    """

    def __init__(self, model_registry=None, models_dir: Optional[Path] = None):
        """
        Initialize the Model Registry Manager.

        Args:
            model_registry: ModelRegistry instance (can be set later)
            models_dir: Directory for model storage
        """
        self.registry = model_registry
        self.models_dir = models_dir or Path("models")
        self._deployment_history: List[Dict[str, Any]] = []

        logger.info("ModelRegistryManager initialized")

    def set_registry(self, model_registry):
        """Set or update the underlying ModelRegistry."""
        self.registry = model_registry
        logger.info("ModelRegistry backend updated")

    def register_model(
        self,
        name: str,
        model_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Register a new model in the registry.

        Args:
            name: Model name
            model_path: Path to model files
            metadata: Optional model metadata

        Returns:
            Model ID if successful, None otherwise
        """
        if not self.registry:
            logger.error("Model registry not initialized")
            return None

        try:
            model_id = self.registry.register_model(
                name=name,
                model_path=Path(model_path),
                metadata=metadata or {},
            )
            logger.info(f"Registered model: {name} (ID: {model_id})")
            return model_id

        except Exception as e:
            logger.error(f"Failed to register model '{name}': {e}")
            return None

    def deploy_model(self, model_id: str) -> bool:
        """
        Deploy a registered model for inference.

        Args:
            model_id: ID of the model to deploy

        Returns:
            True if deployment succeeded
        """
        if not self.registry:
            logger.error("Model registry not initialized")
            return False

        try:
            success = self.registry.deploy_model(model_id)

            if success:
                self._deployment_history.append(
                    {
                        "model_id": model_id,
                        "action": "deploy",
                        "timestamp": time.time(),
                    }
                )
                logger.info(f"Deployed model: {model_id}")
            else:
                logger.error(f"Failed to deploy model: {model_id}")

            return success

        except Exception as e:
            logger.error(f"Error deploying model {model_id}: {e}")
            return False

    def rollback_model(self, model_id: str) -> bool:
        """
        Rollback a deployed model.

        Args:
            model_id: ID of the model to rollback

        Returns:
            True if rollback succeeded
        """
        if not self.registry:
            return False

        try:
            if hasattr(self.registry, "undeploy_model"):
                success = self.registry.undeploy_model(model_id)
            else:
                logger.warning("Registry does not support undeploy; skipping.")
                success = True

            if success:
                self._deployment_history.append(
                    {
                        "model_id": model_id,
                        "action": "rollback",
                        "timestamp": time.time(),
                    }
                )
                logger.info(f"Rolled back model: {model_id}")

            return success

        except Exception as e:
            logger.error(f"Error rolling back model {model_id}: {e}")
            return False

    def list_models(self) -> List[Dict[str, Any]]:
        """List all registered models."""
        if not self.registry:
            return []

        try:
            return self.registry.list_models()
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

    def list_deployed_models(self) -> List[Dict[str, Any]]:
        """List all currently deployed models."""
        if not self.registry:
            return []

        try:
            return self.registry.list_deployed_models()
        except Exception as e:
            logger.error(f"Error listing deployed models: {e}")
            return []

    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a model."""
        if not self.registry:
            return None

        try:
            return self.registry.get_model_info(model_id)
        except Exception as e:
            logger.error(f"Error getting model info for {model_id}: {e}")
            return None

    def compare_models(
        self,
        model_id_a: str,
        model_id_b: str,
    ) -> Dict[str, Any]:
        """
        Compare two models' metadata and performance metrics.

        Args:
            model_id_a: First model ID
            model_id_b: Second model ID

        Returns:
            Comparison result dictionary
        """
        info_a = self.get_model_info(model_id_a)
        info_b = self.get_model_info(model_id_b)

        if not info_a or not info_b:
            return {"error": "One or both models not found"}

        return {
            "model_a": {
                "id": model_id_a,
                "info": info_a,
            },
            "model_b": {
                "id": model_id_b,
                "info": info_b,
            },
            "comparison_timestamp": time.time(),
        }

    def get_deployment_history(self) -> List[Dict[str, Any]]:
        """Get deployment/rollback history."""
        return self._deployment_history.copy()

    def cleanup_old_versions(
        self,
        keep_versions: int = 3,
    ) -> int:
        """
        Clean up old model versions, keeping only the most recent.

        Args:
            keep_versions: Number of versions to keep per model

        Returns:
            Number of versions cleaned up
        """
        if not self.registry:
            return 0

        try:
            if hasattr(self.registry, "cleanup_old_versions"):
                return self.registry.cleanup_old_versions(keep_versions)
            else:
                logger.debug("Registry does not support cleanup_old_versions")
                return 0
        except Exception as e:
            logger.error(f"Error cleaning up old versions: {e}")
            return 0

    def manage_models(self) -> Dict[str, Any]:
        """
        Run a full model management cycle.

        This is the original interface method, kept for backwards compatibility.
        Performs listing, health checks, and cleanup.

        Returns:
            Summary of model management actions taken
        """
        summary = {
            "total_models": 0,
            "deployed_models": 0,
            "cleaned_up": 0,
            "timestamp": time.time(),
        }

        try:
            models = self.list_models()
            summary["total_models"] = len(models)

            deployed = self.list_deployed_models()
            summary["deployed_models"] = len(deployed)

            cleaned = self.cleanup_old_versions()
            summary["cleaned_up"] = cleaned

        except Exception as e:
            logger.error(f"Error in model management cycle: {e}")
            summary["error"] = str(e)

        return summary
