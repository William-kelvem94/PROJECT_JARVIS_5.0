"""
Model Registry for JARVIS Learning Systems.

Provides versioning, rollback, A/B testing, and lifecycle management
for trained models with metadata tracking and performance monitoring.
"""

import json
import logging
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class ModelStatus(Enum):
    """Model lifecycle status."""

    TRAINING = "training"
    VALIDATION = "validation"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ModelType(Enum):
    """Model types supported by JARVIS."""

    LLM_BASE = "llm_base"
    LLM_FINETUNED = "llm_finetuned"
    LORA_ADAPTER = "lora_adapter"
    VISION_YOLO = "vision_yolo"
    AUDIO_CLASSIFIER = "audio_classifier"
    EMBEDDING = "embedding"


@dataclass
class ModelMetadata:
    """Comprehensive model metadata."""

    model_id: str
    name: str
    version: str
    model_type: ModelType
    status: ModelStatus

    # Training details
    base_model: str
    training_config: Dict[str, Any] = field(default_factory=dict)
    dataset_info: Dict[str, Any] = field(default_factory=dict)

    # Performance metrics
    metrics: Dict[str, float] = field(default_factory=dict)
    validation_results: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    description: str = ""
    tags: List[str] = field(default_factory=list)
    author: str = "JARVIS-AUTO"

    # Lifecycle
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    deployed_at: Optional[str] = None

    # Files
    model_path: str = ""
    config_path: str = ""
    tokenizer_path: str = ""

    # Checksums for integrity
    checksums: Dict[str, str] = field(default_factory=dict)

    # Dependencies
    dependencies: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        data = asdict(self)
        data["model_type"] = self.model_type.value
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelMetadata":
        """Create from dictionary."""
        data = data.copy()
        data["model_type"] = ModelType(data["model_type"])
        data["status"] = ModelStatus(data["status"])
        return cls(**data)


@dataclass
class DeploymentConfig:
    """Configuration for model deployment."""

    model_id: str
    environment: str  # production, staging, development
    traffic_percentage: int = 100  # For A/B testing
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    health_checks: Dict[str, Any] = field(default_factory=dict)
    rollback_conditions: Dict[str, Any] = field(default_factory=dict)


class ModelRegistry:
    """Centralized registry for model lifecycle management."""

    def __init__(self, registry_path: Path):
        self.registry_path = Path(registry_path)
        self.models_dir = self.registry_path / "models"
        self.metadata_dir = self.registry_path / "metadata"
        self.deployments_dir = self.registry_path / "deployments"

        # Create directories
        for dir_path in [
                self.models_dir,
                self.metadata_dir,
                self.deployments_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Load existing models
        self._models: Dict[str, ModelMetadata] = {}
        self._deployments: Dict[str, DeploymentConfig] = {}
        self._load_registry()

    def _load_registry(self):
        """Load existing models and deployments."""
        try:
            # Load models
            for metadata_file in self.metadata_dir.glob("*.json"):
                with open(metadata_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    model = ModelMetadata.from_dict(data)
                    self._models[model.model_id] = model

            # Load deployments
            for deploy_file in self.deployments_dir.glob("*.json"):
                with open(deploy_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    deployment = DeploymentConfig(**data)
                    self._deployments[
                        f"{deployment.model_id}_{deployment.environment}"
                    ] = deployment

            logger.info(
                f"ðŸ“š Loaded {len(self._models)} models and {len(self._deployments)} deployments"
            )

        except Exception as e:
            logger.error(f"Failed to load model registry: {e}")

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate file checksum for integrity checking."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.warning(
                f"Failed to calculate checksum for {file_path}: {e}")
            return ""

    def register_model(
        self,
        model_path: Path,
        name: str,
        model_type: ModelType,
        base_model: str,
        training_config: Optional[Dict[str, Any]] = None,
        dataset_info: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, float]] = None,
        description: str = "",
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Register a new model version.

        Returns:
            model_id: Unique identifier for the registered model
        """
        try:
            # Generate model ID and version
            model_id = (
                f"{model_type.value}_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            version = (
                f"v{len([m for m in self._models.values() if m.name == name]) + 1}"
            )

            # Create model directory
            model_dir = self.models_dir / model_id
            model_dir.mkdir(parents=True, exist_ok=True)

            # Copy model files
            if model_path.is_file():
                # Single file
                dest_path = model_dir / model_path.name
                shutil.copy2(model_path, dest_path)
                model_file_path = str(
                    dest_path.relative_to(
                        self.registry_path))

                # Calculate checksum
                checksums = {
                    model_path.name: self._calculate_checksum(dest_path)}

            elif model_path.is_dir():
                # Directory with multiple files
                shutil.copytree(
                    model_path,
                    model_dir / "model",
                    dirs_exist_ok=True)
                model_file_path = str(
                    (model_dir / "model").relative_to(self.registry_path)
                )

                # Calculate checksums for all files
                checksums = {}
                for file_path in (model_dir / "model").rglob("*"):
                    if file_path.is_file():
                        rel_path = file_path.relative_to(model_dir / "model")
                        checksums[str(rel_path)] = self._calculate_checksum(
                            file_path)
            else:
                raise ValueError(f"Invalid model path: {model_path}")

            # Detect additional files (config, tokenizer)
            config_path = ""
            tokenizer_path = ""

            if model_path.is_dir():
                config_files = list(model_path.glob("*config*.json"))
                if config_files:
                    config_path = str(
                        (model_dir /
                         "model" /
                         config_files[0].name).relative_to(
                            self.registry_path))

                tokenizer_files = list(model_path.glob("tokenizer*"))
                if tokenizer_files:
                    tokenizer_path = str(
                        (model_dir / "model").relative_to(self.registry_path)
                    )

            # Create metadata
            metadata = ModelMetadata(
                model_id=model_id,
                name=name,
                version=version,
                model_type=model_type,
                status=ModelStatus.STAGING,
                base_model=base_model,
                training_config=training_config or {},
                dataset_info=dataset_info or {},
                metrics=metrics or {},
                description=description,
                tags=tags or [],
                model_path=model_file_path,
                config_path=config_path,
                tokenizer_path=tokenizer_path,
                checksums=checksums,
            )

            # Save metadata
            metadata_file = self.metadata_dir / f"{model_id}.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata.to_dict(), f, indent=2, ensure_ascii=False)

            # Store in memory
            self._models[model_id] = metadata

            logger.info(f"âœ… Registered model: {model_id} ({name} {version})")
            return model_id

        except Exception as e:
            logger.error(f"Failed to register model: {e}")
            return ""

    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        """Get model metadata by ID."""
        return self._models.get(model_id)

    def list_models(
        self,
        model_type: Optional[ModelType] = None,
        status: Optional[ModelStatus] = None,
        name: Optional[str] = None,
    ) -> List[ModelMetadata]:
        """List models with optional filtering."""
        models = list(self._models.values())

        if model_type:
            models = [m for m in models if m.model_type == model_type]

        if status:
            models = [m for m in models if m.status == status]

        if name:
            models = [m for m in models if name.lower() in m.name.lower()]

        # Sort by creation date (newest first)
        models.sort(key=lambda m: m.created_at, reverse=True)
        return models

    def get_model_versions(self, name: str) -> List[ModelMetadata]:
        """Get all versions of a model by name."""
        versions = [m for m in self._models.values() if m.name == name]
        versions.sort(key=lambda m: m.version, reverse=True)
        return versions

    def update_model_status(self, model_id: str, status: ModelStatus) -> bool:
        """Update model status."""
        if model_id not in self._models:
            logger.error(f"Model {model_id} not found")
            return False

        try:
            self._models[model_id].status = status
            self._models[model_id].updated_at = datetime.now().isoformat()

            if status == ModelStatus.PRODUCTION:
                self._models[model_id].deployed_at = datetime.now().isoformat()

            # Save metadata
            metadata_file = self.metadata_dir / f"{model_id}.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(
                    self._models[model_id].to_dict(),
                    f,
                    indent=2,
                    ensure_ascii=False)

            logger.info(
                f"âœ… Updated model {model_id} status to {status.value}")
            return True

        except Exception as e:
            logger.error(f"Failed to update model status: {e}")
            return False

    def deploy_model(
        self,
        model_id: str,
        environment: str = "production",
        traffic_percentage: int = 100,
        resource_requirements: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Deploy model to specified environment."""
        if model_id not in self._models:
            logger.error(f"Model {model_id} not found")
            return False

        try:
            # Create deployment config
            deployment = DeploymentConfig(
                model_id=model_id,
                environment=environment,
                traffic_percentage=traffic_percentage,
                resource_requirements=resource_requirements or {},
            )

            # Save deployment config
            deploy_file = self.deployments_dir / \
                f"{model_id}_{environment}.json"
            with open(deploy_file, "w", encoding="utf-8") as f:
                json.dump(asdict(deployment), f, indent=2, ensure_ascii=False)

            # Store in memory
            key = f"{model_id}_{environment}"
            self._deployments[key] = deployment

            # Update model status if deploying to production
            if environment == "production":
                self.update_model_status(model_id, ModelStatus.PRODUCTION)

            logger.info(
                f"âœ… Deployed model {model_id} to {environment} ({traffic_percentage}% traffic)"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to deploy model: {e}")
            return False

    def rollback_deployment(
        self, environment: str, target_model_id: Optional[str] = None
    ) -> bool:
        """
        Rollback to previous model version or specific model.

        Args:
            environment: Environment to rollback
            target_model_id: Optional specific model to rollback to
        """
        try:
            # Find current deployment
            current_deployments = [
                d for d in self._deployments.values() if d.environment == environment]

            if not current_deployments:
                logger.error(
                    f"No deployments found for environment {environment}")
                return False

            current_deployment = current_deployments[
                0
            ]  # Assume single deployment per env
            current_model = self._models.get(current_deployment.model_id)

            if not current_model:
                logger.error(
                    f"Current model {current_deployment.model_id} not found")
                return False

            # Find target model
            if target_model_id:
                target_model = self._models.get(target_model_id)
                if not target_model:
                    logger.error(f"Target model {target_model_id} not found")
                    return False
            else:
                # Find previous version of same model
                versions = self.get_model_versions(current_model.name)
                if len(versions) < 2:
                    logger.error(
                        f"No previous version found for {current_model.name}")
                    return False

                # Get the version before current
                current_idx = next(
                    (
                        i
                        for i, v in enumerate(versions)
                        if v.model_id == current_model.model_id
                    ),
                    -1,
                )
                if current_idx == -1 or current_idx == len(versions) - 1:
                    logger.error("Cannot find previous version for rollback")
                    return False

                target_model = versions[current_idx + 1]

            # Perform rollback
            success = self.deploy_model(
                model_id=target_model.model_id,
                environment=environment,
                traffic_percentage=100,
            )

            if success:
                # Mark current model as deprecated
                self.update_model_status(
                    current_model.model_id, ModelStatus.DEPRECATED)
                logger.info(
                    f"ðŸ”„ Rolled back {environment} from {current_model.model_id} to {target_model.model_id}"
                )

            return success

        except Exception as e:
            logger.error(f"Failed to rollback deployment: {e}")
            return False

    def setup_ab_test(
        self,
        model_a_id: str,
        model_b_id: str,
        traffic_split: int = 50,
        environment: str = "production",
    ) -> bool:
        """
        Setup A/B test between two models.

        Args:
            model_a_id: First model (will get traffic_split% of traffic)
            model_b_id: Second model (will get remaining traffic)
            traffic_split: Percentage of traffic for model A (0-100)
            environment: Environment for A/B test
        """
        try:
            # Validate models exist
            if model_a_id not in self._models or model_b_id not in self._models:
                logger.error("One or both models not found for A/B test")
                return False

            # Deploy model A
            success_a = self.deploy_model(
                model_id=model_a_id,
                environment=f"{environment}_a",
                traffic_percentage=traffic_split,
            )

            # Deploy model B
            success_b = self.deploy_model(
                model_id=model_b_id,
                environment=f"{environment}_b",
                traffic_percentage=100 - traffic_split,
            )

            if success_a and success_b:
                logger.info(
                    f"ðŸ§ª A/B test setup: {model_a_id} ({traffic_split}%) vs {model_b_id} ({100-traffic_split}%)"
                )

                # Create A/B test metadata
                ab_test_file = self.deployments_dir / \
                    f"ab_test_{environment}.json"
                ab_test_data = {
                    "model_a": model_a_id,
                    "model_b": model_b_id,
                    "traffic_split": traffic_split,
                    "environment": environment,
                    "start_time": datetime.now().isoformat(),
                    "status": "active",
                }

                with open(ab_test_file, "w", encoding="utf-8") as f:
                    json.dump(ab_test_data, f, indent=2, ensure_ascii=False)

            return success_a and success_b

        except Exception as e:
            logger.error(f"Failed to setup A/B test: {e}")
            return False

    def get_production_model(
        self, model_type: Optional[ModelType] = None
    ) -> Optional[ModelMetadata]:
        """Get currently deployed production model."""
        production_models = [
            m for m in self._models.values() if m.status == ModelStatus.PRODUCTION]

        if model_type:
            production_models = [
                m for m in production_models if m.model_type == model_type
            ]

        if not production_models:
            return None

        # Return most recently deployed
        production_models.sort(
            key=lambda m: m.deployed_at or m.created_at, reverse=True
        )
        return production_models[0]

    def validate_model_integrity(self, model_id: str) -> bool:
        """Validate model file integrity using checksums."""
        model = self.get_model(model_id)
        if not model:
            return False

        try:
            model_dir = self.registry_path / model.model_path

            for file_rel_path, expected_checksum in model.checksums.items():
                file_path = (
                    model_dir / file_rel_path
                    if "/" in file_rel_path
                    else model_dir.parent / file_rel_path
                )

                if not file_path.exists():
                    logger.error(f"Model file missing: {file_path}")
                    return False

                actual_checksum = self._calculate_checksum(file_path)
                if actual_checksum != expected_checksum:
                    logger.error(f"Checksum mismatch for {file_path}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Failed to validate model integrity: {e}")
            return False

    def cleanup_old_models(self, keep_versions: int = 3) -> int:
        """
        Cleanup old model versions, keeping only the most recent ones.

        Args:
            keep_versions: Number of versions to keep per model name

        Returns:
            Number of models cleaned up
        """
        try:
            cleaned_count = 0
            model_groups = {}

            # Group models by name
            for model in self._models.values():
                if model.name not in model_groups:
                    model_groups[model.name] = []
                model_groups[model.name].append(model)

            # Process each group
            for name, models in model_groups.items():
                # Sort by version (newest first)
                models.sort(key=lambda m: m.created_at, reverse=True)

                # Skip production models and recent models
                to_cleanup = []
                for i, model in enumerate(models):
                    if i >= keep_versions and model.status not in [
                        ModelStatus.PRODUCTION,
                        ModelStatus.STAGING,
                    ]:
                        to_cleanup.append(model)

                # Cleanup old models
                for model in to_cleanup:
                    try:
                        # Remove files
                        model_dir = self.registry_path / model.model_path
                        if model_dir.exists():
                            if model_dir.is_file():
                                model_dir.unlink()
                            else:
                                shutil.rmtree(model_dir.parent)

                        # Remove metadata
                        metadata_file = self.metadata_dir / \
                            f"{model.model_id}.json"
                        if metadata_file.exists():
                            metadata_file.unlink()

                        # Remove from memory
                        del self._models[model.model_id]
                        cleaned_count += 1

                        logger.info(
                            f"ðŸ—‘ï¸ Cleaned up old model: {model.model_id}")

                    except Exception as e:
                        logger.error(
                            f"Failed to cleanup model {model.model_id}: {e}")

            return cleaned_count

        except Exception as e:
            logger.error(f"Failed to cleanup models: {e}")
            return 0

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        total_models = len(self._models)
        by_status = {}
        by_type = {}
        total_size = 0

        for model in self._models.values():
            # Count by status
            status = model.status.name
            by_status[status] = by_status.get(status, 0) + 1

            # Count by type
            model_type = model.model_type.name
            by_type[model_type] = by_type.get(model_type, 0) + 1

            # Calculate size
            try:
                model_path = self.registry_path / model.model_path
                if model_path.exists():
                    if model_path.is_file():
                        total_size += model_path.stat().st_size
                    else:
                        for file_path in model_path.rglob("*"):
                            if file_path.is_file():
                                total_size += file_path.stat().st_size
            except Exception:
                pass

        return {
            "total_models": total_models,
            "by_status": by_status,
            "by_type": by_type,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_deployments": len(self._deployments),
        }
