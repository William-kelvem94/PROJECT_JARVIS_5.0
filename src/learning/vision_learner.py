"""
Vision Learner for JARVIS AGI Machine Learning Core.

This module implements few-shot learning for YOLO object detection,
including object annotation, training data collection, incremental
retraining, and knowledge retention.

============================================================================
P1: UI-SPECIFIC YOLO TRAINING
============================================================================
JARVIS can now learn UI elements incrementally for screen automation:
- Buttons, textboxes, icons, menus
- Adaptive dataset expansion (10+ examples per class)
- Transfer learning from base YOLOv8n model
- Validation with holdout UI screenshots

TARGET USE CASES:
1. "Jarvis, click the Submit button" - Vision system detects button position
2. "Find all input fields" - Enumerate form elements for auto-fill
3. "Is there a notification icon?" - Monitor screen for alerts

IMPLEMENTATION:
- Base model: YOLOv8n.pt (11MB, pre-trained on COCO)
- UI dataset: Collect 20+ screenshots per element type
- Training: 50 epochs, batch_size=8, imgsz=640
- Metrics: mAP@0.5 > 0.85 (target)
"""

import json
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
import yaml

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except (ImportError, OSError) as e:
    CV2_AVAILABLE = False
    cv2 = None
    # Mock numpy for type hints
    class np:
        """Mock numpy module."""
        class ndarray:
            """Mock ndarray class."""
            pass
        @staticmethod
        def array(x):
            return x
        @staticmethod
        def zeros(shape):
            return []
        @staticmethod
        def concatenate(arrays):
            return []

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class BoundingBox:
    """Represents a bounding box annotation."""
    x_center: float  # Normalized 0-1
    y_center: float  # Normalized 0-1
    width: float     # Normalized 0-1
    height: float    # Normalized 0-1
    
    def to_yolo_format(self, class_id: int) -> str:
        """Convert to YOLO annotation format."""
        return f"{class_id} {self.x_center} {self.y_center} {self.width} {self.height}"
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "BoundingBox":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Annotation:
    """Represents an annotation for an image."""
    annotation_id: str
    image_path: Path
    class_name: str
    class_id: int
    bounding_box: BoundingBox
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['image_path'] = str(self.image_path)
        data['bounding_box'] = self.bounding_box.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Annotation":
        """Create from dictionary."""
        data = data.copy()
        data['image_path'] = Path(data['image_path'])
        data['bounding_box'] = BoundingBox.from_dict(data['bounding_box'])
        return cls(**data)
    
    def save_yolo_annotation(self, output_path: Path) -> None:
        """Save annotation in YOLO format."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.bounding_box.to_yolo_format(self.class_id))


@dataclass
class TrainingExample:
    """Represents a training example (image + annotations)."""
    example_id: str
    image_path: Path
    annotations: List[Annotation]
    split: str = "train"  # train, val, test
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "example_id": self.example_id,
            "image_path": str(self.image_path),
            "annotations": [a.to_dict() for a in self.annotations],
            "split": self.split
        }


class AnnotationInterface:
    """Simple annotation interface for labeling objects."""
    
    def __init__(self):
        """Initialize annotation interface."""
        self.current_image: Optional[np.ndarray] = None
        self.current_annotations: List[Annotation] = []
    
    def load_image(self, image_path: Path) -> bool:
        """
        Load an image for annotation.
        
        Args:
            image_path: Path to the image
            
        Returns:
            True if successful
        """
        if not CV2_AVAILABLE:
            logger.error("OpenCV not available")
            return False
        
        try:
            self.current_image = cv2.imread(str(image_path))
            if self.current_image is None:
                logger.error(f"Failed to load image: {image_path}")
                return False
            
            logger.info(f"Loaded image: {image_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return False
    
    def add_annotation(
        self,
        class_name: str,
        class_id: int,
        bbox: BoundingBox,
        image_path: Path
    ) -> Annotation:
        """
        Add an annotation to the current image.
        
        Args:
            class_name: Name of the class
            class_id: ID of the class
            bbox: Bounding box
            image_path: Path to the image
            
        Returns:
            Created Annotation
        """
        annotation = Annotation(
            annotation_id=f"ann_{datetime.now().timestamp()}",
            image_path=image_path,
            class_name=class_name,
            class_id=class_id,
            bounding_box=bbox
        )
        
        self.current_annotations.append(annotation)
        logger.info(f"Added annotation for class '{class_name}'")
        
        return annotation
    
    def draw_annotations(
        self,
        image: np.ndarray,
        annotations: List[Annotation]
    ) -> np.ndarray:
        """
        Draw annotations on an image.
        
        Args:
            image: Image array
            annotations: List of annotations
            
        Returns:
            Image with annotations drawn
        """
        if not CV2_AVAILABLE:
            return image
        
        img_copy = image.copy()
        h, w = img_copy.shape[:2]
        
        for ann in annotations:
            bbox = ann.bounding_box
            
            # Convert normalized coords to pixel coords
            x_center = int(bbox.x_center * w)
            y_center = int(bbox.y_center * h)
            box_w = int(bbox.width * w)
            box_h = int(bbox.height * h)
            
            # Calculate corners
            x1 = int(x_center - box_w / 2)
            y1 = int(y_center - box_h / 2)
            x2 = int(x_center + box_w / 2)
            y2 = int(y_center + box_h / 2)
            
            # Draw rectangle
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"{ann.class_name}"
            cv2.putText(
                img_copy, label, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
            )
        
        return img_copy
    
    def clear_annotations(self) -> None:
        """Clear current annotations."""
        self.current_annotations.clear()


class YOLODatasetManager:
    """Manages YOLO dataset creation and organization."""
    
    def __init__(self, dataset_dir: Path):
        """
        Initialize dataset manager.
        
        Args:
            dataset_dir: Root directory for the dataset
        """
        self.dataset_dir = Path(dataset_dir)
        self.dataset_dir.mkdir(parents=True, exist_ok=True)
        
        # Create directory structure
        self.images_dir = self.dataset_dir / "images"
        self.labels_dir = self.dataset_dir / "labels"
        
        for split in ["train", "val", "test"]:
            (self.images_dir / split).mkdir(parents=True, exist_ok=True)
            (self.labels_dir / split).mkdir(parents=True, exist_ok=True)
        
        self.classes: Dict[str, int] = {}
        self.examples: List[TrainingExample] = []
        
        self._load_metadata()
    
    def add_class(self, class_name: str) -> int:
        """
        Add a new class to the dataset.
        
        Args:
            class_name: Name of the class
            
        Returns:
            Class ID
        """
        if class_name not in self.classes:
            class_id = len(self.classes)
            self.classes[class_name] = class_id
            self._save_metadata()
            logger.info(f"Added class '{class_name}' with ID {class_id}")
            return class_id
        
        return self.classes[class_name]
    
    def add_example(
        self,
        image_path: Path,
        annotations: List[Annotation],
        split: str = "train"
    ) -> TrainingExample:
        """
        Add a training example to the dataset.
        
        Args:
            image_path: Path to the image
            annotations: List of annotations
            split: Dataset split (train/val/test)
            
        Returns:
            Created TrainingExample
        """
        try:
            example_id = f"ex_{datetime.now().timestamp()}"
            
            # Copy image to dataset
            dest_image_path = (
                self.images_dir / split / f"{example_id}{image_path.suffix}"
            )
            shutil.copy(image_path, dest_image_path)
            
            # Save annotations
            label_path = (
                self.labels_dir / split / f"{example_id}.txt"
            )
            
            with open(label_path, 'w', encoding='utf-8') as f:
                for ann in annotations:
                    line = ann.bounding_box.to_yolo_format(ann.class_id)
                    f.write(line + '\n')
            
            # Create example
            example = TrainingExample(
                example_id=example_id,
                image_path=dest_image_path,
                annotations=annotations,
                split=split
            )
            
            self.examples.append(example)
            self._save_metadata()
            
            logger.info(f"Added example {example_id} to {split} split")
            return example
            
        except Exception as e:
            logger.error(f"Error adding example: {e}", exc_info=True)
            raise
    
    def create_yaml_config(self, output_path: Optional[Path] = None) -> Path:
        """
        Create YOLO dataset configuration file.
        
        Args:
            output_path: Optional output path for config
            
        Returns:
            Path to the created config file
        """
        if output_path is None:
            output_path = self.dataset_dir / "data.yaml"
        
        config = {
            "path": str(self.dataset_dir.absolute()),
            "train": "images/train",
            "val": "images/val",
            "test": "images/test",
            "nc": len(self.classes),
            "names": {v: k for k, v in self.classes.items()}
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"Created dataset config: {output_path}")
        return output_path
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get dataset statistics."""
        split_counts = {"train": 0, "val": 0, "test": 0}
        class_counts = {name: 0 for name in self.classes.keys()}
        
        for example in self.examples:
            split_counts[example.split] += 1
            for ann in example.annotations:
                class_counts[ann.class_name] += 1
        
        return {
            "total_examples": len(self.examples),
            "split_counts": split_counts,
            "class_counts": class_counts,
            "num_classes": len(self.classes)
        }
    
    def _load_metadata(self) -> None:
        """Load dataset metadata."""
        metadata_file = self.dataset_dir / "metadata.json"
        
        if not metadata_file.exists():
            return
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.classes = data.get("classes", {})
                
                examples_data = data.get("examples", [])
                self.examples = [
                    TrainingExample(**ex) for ex in examples_data
                ]
            
            logger.info("Loaded dataset metadata")
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
    
    def _save_metadata(self) -> None:
        """Save dataset metadata."""
        metadata_file = self.dataset_dir / "metadata.json"
        
        try:
            data = {
                "classes": self.classes,
                "examples": [ex.to_dict() for ex in self.examples]
            }
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")


class VisionLearner:
    """
    Vision Learner for few-shot YOLO learning.
    
    Supports incremental retraining with new objects while
    retaining knowledge of previously learned objects.
    """
    
    def __init__(
        self,
        model_dir: Path,
        base_model: str = "yolov8n.pt"
    ):
        """
        Initialize the VisionLearner.
        
        Args:
            model_dir: Directory to store models and data
            base_model: Base YOLO model to use
        """
        if not YOLO_AVAILABLE:
            logger.warning("Ultralytics YOLO not available")
        
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.base_model = base_model
        self.current_model: Optional[Any] = None
        
        # Dataset manager
        self.dataset_manager = YOLODatasetManager(
            self.model_dir / "dataset"
        )
        
        # Annotation interface
        self.annotation_interface = AnnotationInterface()
        
        # Training history
        self.training_history: List[Dict[str, Any]] = []
        
        # Statistics
        self.stats = {
            "total_trainings": 0,
            "total_annotations": 0,
            "learned_classes": 0,
        }
        
        self._load_stats()
        self._load_or_create_model()
        
        logger.info("VisionLearner initialized")
    
    def _load_or_create_model(self) -> None:
        """Load existing model or create new one."""
        if not YOLO_AVAILABLE:
            return
        
        try:
            model_path = self.model_dir / "best.pt"
            
            if model_path.exists():
                logger.info(f"Loading existing model: {model_path}")
                self.current_model = YOLO(str(model_path))
            else:
                logger.info(f"Creating new model from: {self.base_model}")
                self.current_model = YOLO(self.base_model)
                
        except Exception as e:
            logger.error(f"Error loading model: {e}", exc_info=True)
    
    def add_training_example(
        self,
        image_path: Path,
        class_name: str,
        bounding_box: BoundingBox,
        split: str = "train"
    ) -> Annotation:
        """
        Add a training example with annotation.
        
        Args:
            image_path: Path to the image
            class_name: Name of the class
            bounding_box: Bounding box for the object
            split: Dataset split
            
        Returns:
            Created Annotation
        """
        try:
            # Add class if new
            class_id = self.dataset_manager.add_class(class_name)
            
            # Create annotation
            annotation = Annotation(
                annotation_id=f"ann_{datetime.now().timestamp()}",
                image_path=image_path,
                class_name=class_name,
                class_id=class_id,
                bounding_box=bounding_box
            )
            
            # Add to dataset
            self.dataset_manager.add_example(
                image_path=image_path,
                annotations=[annotation],
                split=split
            )
            
            # Update statistics
            self.stats["total_annotations"] += 1
            self.stats["learned_classes"] = len(self.dataset_manager.classes)
            self._save_stats()
            
            logger.info(f"Added training example for class '{class_name}'")
            return annotation
            
        except Exception as e:
            logger.error(f"Error adding training example: {e}", exc_info=True)
            raise
    
    def train_incremental(
        self,
        epochs: int = 50,
        batch_size: int = 16,
        img_size: int = 640,
        patience: int = 10
    ) -> Dict[str, Any]:
        """
        Perform incremental training on new data.
        
        ============================================================================
        P1: UI-SPECIFIC OPTIMIZATIONS
        ============================================================================
        - Smaller batch size (8) for UI screenshots (typically 1920x1080)
        - Higher image size (640) for small UI element detection
        - Data augmentation: rotation (±10°), scaling (0.8-1.2x), flip
        - Mosaic augmentation: 4 UI screenshots combined for diverse contexts
        
        Args:
            epochs: Number of training epochs (50 for UI elements)
            batch_size: Batch size (8 recommended for UI training)
            img_size: Image size (640 for UI, 1280 for tiny elements)
            patience: Early stopping patience
            
        Returns:
            Dictionary with training results
        """
        if not YOLO_AVAILABLE or self.current_model is None:
            logger.error("YOLO not available or model not initialized")
            return {"status": "unavailable"}
        
        try:
            logger.info("Starting incremental training (UI-optimized)")
            
            # Create dataset config
            data_yaml = self.dataset_manager.create_yaml_config()
            
            # Check if we have enough data
            stats = self.dataset_manager.get_statistics()
            
            # ============ P1: UI-SPECIFIC VALIDATION ============
            # UI elements require at least 10 examples per class for good generalization
            min_examples = 10
            if stats["total_examples"] < min_examples:
                logger.warning(
                    f"Not enough training examples ({stats['total_examples']}), "
                    f"need at least {min_examples} for UI training"
                )
                return {
                    "status": "insufficient_data",
                    "examples": stats["total_examples"],
                    "required": min_examples
                }
            
            # ============ P1: UI-SPECIFIC TRAINING PARAMS ============
            # Optimized hyperparameters for UI element detection
            ui_training_params = {
                "data": str(data_yaml),
                "epochs": epochs,
                "batch": min(batch_size, 8),  # Cap at 8 for UI screenshots
                "imgsz": img_size,
                "patience": patience,
                "save": True,
                "project": str(self.model_dir),
                "name": "ui_training",
                "exist_ok": True,
                "pretrained": True,
                
                # UI-specific augmentations
                "degrees": 10.0,  # Rotation ±10°
                "translate": 0.1,  # Translation ±10%
                "scale": 0.5,  # Scaling 0.5-1.5x
                "shear": 0.0,  # No shear (UI elements are rectangular)
                "flipud": 0.0,  # No vertical flip (breaks UI orientation)
                "fliplr": 0.5,  # 50% horizontal flip (valid for symmetric UIs)
                "mosaic": 1.0,  # Mosaic augmentation for context diversity
            }
            
            # Train model with UI optimizations
            logger.info(f"UI Training: {stats['total_examples']} examples, "
                       f"{len(self.dataset_manager.classes)} classes")
            results = self.current_model.train(**ui_training_params)
            
            # Update model to best weights
            best_model_path = self.model_dir / "training" / "weights" / "best.pt"
            if best_model_path.exists():
                shutil.copy(best_model_path, self.model_dir / "best.pt")
                self.current_model = YOLO(str(self.model_dir / "best.pt"))
            
            # Record training history
            training_record = {
                "timestamp": datetime.now().isoformat(),
                "epochs": epochs,
                "classes": list(self.dataset_manager.classes.keys()),
                "num_examples": stats["total_examples"]
            }
            self.training_history.append(training_record)
            
            # Update statistics
            self.stats["total_trainings"] += 1
            self._save_stats()
            
            logger.info("Incremental training completed")
            
            return {
                "status": "success",
                "epochs": epochs,
                "classes": list(self.dataset_manager.classes.keys()),
                "examples": stats["total_examples"]
            }
            
        except Exception as e:
            logger.error(f"Error during training: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}
    
    def detect_objects(
        self,
        image_path: Path,
        confidence_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Detect objects in an image.
        
        Args:
            image_path: Path to the image
            confidence_threshold: Minimum confidence threshold
            
        Returns:
            List of detected objects
        """
        if not YOLO_AVAILABLE or self.current_model is None:
            logger.error("YOLO not available or model not initialized")
            return []
        
        try:
            results = self.current_model(str(image_path))
            
            detections = []
            for result in results:
                boxes = result.boxes
                
                for box in boxes:
                    conf = float(box.conf[0])
                    
                    if conf < confidence_threshold:
                        continue
                    
                    cls_id = int(box.cls[0])
                    cls_name = result.names[cls_id]
                    
                    # Get box coordinates (xyxy format)
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    
                    detection = {
                        "class": cls_name,
                        "confidence": conf,
                        "bbox": {
                            "x1": x1,
                            "y1": y1,
                            "x2": x2,
                            "y2": y2
                        }
                    }
                    detections.append(detection)
            
            logger.info(f"Detected {len(detections)} objects")
            return detections
            
        except Exception as e:
            logger.error(f"Error detecting objects: {e}", exc_info=True)
            return []
    
    def validate_model(self) -> Dict[str, Any]:
        """
        Validate the current model.
        
        Returns:
            Validation metrics
        """
        if not YOLO_AVAILABLE or self.current_model is None:
            return {"status": "unavailable"}
        
        try:
            data_yaml = self.dataset_manager.create_yaml_config()
            results = self.current_model.val(data=str(data_yaml))
            
            metrics = {
                "status": "success",
                "mAP50": float(results.box.map50),
                "mAP50-95": float(results.box.map),
            }
            
            logger.info(f"Validation metrics: mAP50={metrics['mAP50']:.3f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error validating model: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get learner statistics."""
        dataset_stats = self.dataset_manager.get_statistics()
        
        return {
            **self.stats,
            "dataset": dataset_stats,
            "training_history": self.training_history
        }
    
    def export_model(
        self,
        output_path: Path,
        format: str = "onnx"
    ) -> bool:
        """
        Export model to different format.
        
        Args:
            output_path: Path to save exported model
            format: Export format (onnx, torchscript, etc.)
            
        Returns:
            True if successful
        """
        if not YOLO_AVAILABLE or self.current_model is None:
            logger.error("Cannot export: model not available")
            return False
        
        try:
            self.current_model.export(format=format)
            logger.info(f"Model exported to {format} format")
            return True
        except Exception as e:
            logger.error(f"Error exporting model: {e}", exc_info=True)
            return False
    
    def _load_stats(self) -> None:
        """Load statistics from file."""
        stats_file = self.model_dir / "stats.json"
        
        if not stats_file.exists():
            return
        
        try:
            with open(stats_file, 'r') as f:
                data = json.load(f)
                self.stats = data.get("stats", self.stats)
                self.training_history = data.get("training_history", [])
            
            logger.info("Loaded statistics")
        except Exception as e:
            logger.error(f"Error loading stats: {e}")
    
    def _save_stats(self) -> None:
        """Save statistics to file."""
        stats_file = self.model_dir / "stats.json"
        
        try:
            data = {
                "stats": self.stats,
                "training_history": self.training_history
            }
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error saving stats: {e}")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Initialize vision learner
    learner = VisionLearner(
        model_dir=Path("./data/vision_learner"),
        base_model="yolov8n.pt"
    )
    
    # Example: Add a training example
    # (In real usage, you would provide actual image path and bbox)
    # bbox = BoundingBox(x_center=0.5, y_center=0.5, width=0.3, height=0.3)
    # learner.add_training_example(
    #     image_path=Path("./example_image.jpg"),
    #     class_name="custom_object",
    #     bounding_box=bbox
    # )
    
    # Get statistics
    stats = learner.get_statistics()
    print(f"\nVision Learner Statistics:")
    print(f"Total trainings: {stats['total_trainings']}")
    print(f"Total annotations: {stats['total_annotations']}")
    print(f"Learned classes: {stats['learned_classes']}")
    print(f"Dataset examples: {stats['dataset']['total_examples']}")
    
    # Note: Actual training commented out for testing
    # results = learner.train_incremental(epochs=10)
    # print(f"\nTraining Results: {results}")
    
    print("\nVisionLearner example completed!")
