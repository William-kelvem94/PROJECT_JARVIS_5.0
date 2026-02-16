"""
Distributed Training Manager for JARVIS Learning Systems.

Supports multi-GPU training, gradient synchronization, and distributed
data parallelism for efficient training of large models.
"""

import os
import json
import logging
import threading
import torch

try:
    import torch.distributed as dist
    import torch.multiprocessing as mp

    HAS_TORCH_DIST = True
except ImportError:
    HAS_TORCH_DIST = False
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from .dependency_manager import dependency_manager

logger = logging.getLogger(__name__)


@dataclass
class DistributedConfig:
    """Configuration for distributed training."""

    # Multi-GPU settings
    use_distributed: bool = True
    backend: str = "nccl"  # nccl for GPU, gloo for CPU
    init_method: str = "env://"

    # Resource allocation
    num_gpus: int = 0  # Auto-detect if 0
    num_nodes: int = 1
    node_rank: int = 0

    # Training settings
    gradient_accumulation_steps: int = 1
    sync_batch_norm: bool = True
    find_unused_parameters: bool = False

    # Communication
    timeout_seconds: int = 1800  # 30 minutes
    master_addr: str = "localhost"
    master_port: str = "29500"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class TrainingJob:
    """Represents a distributed training job."""

    job_id: str
    config: DistributedConfig
    model_config: Dict[str, Any]
    dataset_path: str
    output_dir: str
    status: str = "pending"  # pending, running, completed, failed
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    gpu_allocation: List[int] = field(default_factory=list)
    process_ids: List[int] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)


class GPUManager:
    """Manages GPU resources and allocation."""

    def __init__(self):
        self.available_gpus = self._detect_gpus()
        self.allocated_gpus: Dict[str, List[int]] = {}  # job_id -> gpu_list
        self._lock = threading.Lock()

    def _detect_gpus(self) -> List[int]:
        """Detect available GPUs."""
        if not dependency_manager.is_available("torch", "gpu"):
            logger.warning("No CUDA-capable GPUs detected")
            return []

        try:
            gpu_count = torch.cuda.device_count()
            gpus = list(range(gpu_count))

            for i in gpus:
                props = torch.cuda.get_device_properties(i)
                memory_gb = props.total_memory / (1024**3)
                logger.info(f"GPU {i}: {props.name} ({memory_gb:.1f}GB)")

            return gpus
        except Exception as e:
            logger.error(f"Failed to detect GPUs: {e}")
            return []

    def allocate_gpus(self, job_id: str, num_gpus: int) -> List[int]:
        """Allocate GPUs for a training job."""
        with self._lock:
            # Find available GPUs
            allocated_flat = [
                gpu for gpu_list in self.allocated_gpus.values() for gpu in gpu_list
            ]
            available = [
                gpu for gpu in self.available_gpus if gpu not in allocated_flat
            ]

            if len(available) < num_gpus:
                raise RuntimeError(
                    f"Not enough GPUs available. Requested: {num_gpus}, Available: {len(available)}"
                )

            # Allocate requested GPUs
            allocated = available[:num_gpus]
            self.allocated_gpus[job_id] = allocated

            logger.info(f"Allocated GPUs {allocated} to job {job_id}")
            return allocated

    def free_gpus(self, job_id: str):
        """Free GPUs allocated to a job."""
        with self._lock:
            if job_id in self.allocated_gpus:
                gpus = self.allocated_gpus[job_id]
                del self.allocated_gpus[job_id]
                logger.info(f"Freed GPUs {gpus} from job {job_id}")

    def get_gpu_utilization(self) -> Dict[int, Dict[str, float]]:
        """Get current GPU utilization."""
        utilization = {}

        for gpu_id in self.available_gpus:
            try:
                torch.cuda.set_device(gpu_id)

                # Memory usage
                memory_reserved = torch.cuda.memory_reserved(gpu_id)
                memory_allocated = torch.cuda.memory_allocated(gpu_id)
                memory_total = torch.cuda.get_device_properties(gpu_id).total_memory

                utilization[gpu_id] = {
                    "memory_used_percent": (memory_allocated / memory_total) * 100,
                    "memory_reserved_percent": (memory_reserved / memory_total) * 100,
                    "memory_total_gb": memory_total / (1024**3),
                    "allocated_to": next(
                        (
                            job
                            for job, gpus in self.allocated_gpus.items()
                            if gpu_id in gpus
                        ),
                        None,
                    ),
                }

            except Exception as e:
                logger.debug(f"Could not get utilization for GPU {gpu_id}: {e}")
                utilization[gpu_id] = {"error": str(e)}

        return utilization


class DistributedTrainer:
    """Handles distributed training setup and execution."""

    def __init__(self, config: DistributedConfig):
        self.config = config
        self.gpu_manager = GPUManager()
        self.active_jobs: Dict[str, TrainingJob] = {}
        self._setup_environment()

    def _setup_environment(self):
        """Setup environment variables for distributed training."""
        os.environ["MASTER_ADDR"] = self.config.master_addr
        os.environ["MASTER_PORT"] = self.config.master_port

        # Auto-detect GPU count if not specified
        if self.config.num_gpus == 0:
            self.config.num_gpus = len(self.gpu_manager.available_gpus)

        logger.info(f"Distributed trainer configured for {self.config.num_gpus} GPUs")

    def create_training_job(
        self,
        model_config: Dict[str, Any],
        dataset_path: str,
        output_dir: str,
        num_gpus: Optional[int] = None,
    ) -> str:
        """Create a new distributed training job."""
        import uuid

        job_id = str(uuid.uuid4())

        if num_gpus is None:
            num_gpus = min(self.config.num_gpus, len(self.gpu_manager.available_gpus))

        # Allocate GPUs
        try:
            allocated_gpus = self.gpu_manager.allocate_gpus(job_id, num_gpus)
        except RuntimeError as e:
            logger.error(f"Failed to allocate GPUs for job {job_id}: {e}")
            return ""

        # Create job
        job = TrainingJob(
            job_id=job_id,
            config=self.config,
            model_config=model_config,
            dataset_path=dataset_path,
            output_dir=output_dir,
            gpu_allocation=allocated_gpus,
        )

        self.active_jobs[job_id] = job
        logger.info(f"Created training job {job_id} with {num_gpus} GPUs")

        return job_id

    def start_training_job(self, job_id: str) -> bool:
        """Start a distributed training job."""
        if job_id not in self.active_jobs:
            logger.error(f"Job {job_id} not found")
            return False

        job = self.active_jobs[job_id]

        try:
            # Update job status
            job.status = "running"
            job.start_time = datetime.now().isoformat()

            # Start distributed processes
            if len(job.gpu_allocation) > 1 and HAS_TORCH_DIST:
                # Multi-GPU distributed training
                try:
                    # Use spawn method if available
                    spawn_func = getattr(mp, "spawn", None)
                    if spawn_func:
                        spawn_func(
                            self._run_distributed_worker,
                            args=(job,),
                            nprocs=len(job.gpu_allocation),
                            join=False,  # Non-blocking
                        )
                    else:
                        logger.warning(
                            "torch.multiprocessing.spawn not available, using single GPU"
                        )
                        self._run_single_gpu_worker(job, 0)
                except Exception as e:
                    logger.error(f"Failed to start distributed training: {e}")
                    self._run_single_gpu_worker(job, 0)
            else:
                # Single GPU training
                self._run_single_gpu_worker(job, 0)

            logger.info(f"Started distributed training job {job_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to start training job {job_id}: {e}")
            job.status = "failed"
            return False

    def _run_distributed_worker(self, rank: int, job: TrainingJob):
        """Worker function for distributed training."""
        try:
            # Set GPU device
            gpu_id = job.gpu_allocation[rank]
            torch.cuda.set_device(gpu_id)

            # Initialize process group
            if HAS_TORCH_DIST:
                dist.init_process_group(
                    backend=self.config.backend,
                    init_method=self.config.init_method,
                    world_size=len(job.gpu_allocation),
                    rank=rank,
                    timeout=(
                        getattr(torch, "distributed", {}).get("default_store_timeout")
                        if hasattr(torch, "distributed")
                        else None
                    ),
                )

            logger.info(
                f"Initialized worker {rank} on GPU {gpu_id} for job {job.job_id}"
            )

            # Load and setup model
            model = self._create_distributed_model(job.model_config, rank)

            # Load dataset with distributed sampler
            train_loader = self._create_distributed_dataloader(
                job.dataset_path, rank, len(job.gpu_allocation)
            )

            # Training loop
            self._distributed_training_loop(model, train_loader, job, rank)

            # Cleanup
            if HAS_TORCH_DIST and dist.is_initialized():
                dist.destroy_process_group()

        except Exception as e:
            logger.error(f"Worker {rank} failed for job {job.job_id}: {e}")
            job.status = "failed"

    def _run_single_gpu_worker(self, job: TrainingJob, rank: int):
        """Worker function for single GPU training."""
        try:
            # Check if GPUs are allocated
            if not job.gpu_allocation:
                logger.warning(
                    f"No GPUs allocated for job {job.job_id}, skipping GPU training"
                )
                job.status = (
                    "completed"  # Mark as completed since no GPU training needed
                )
                return

            gpu_id = job.gpu_allocation[0]
            torch.cuda.set_device(gpu_id)

            logger.info(
                f"Started single GPU training on GPU {gpu_id} for job {job.job_id}"
            )

            # Create model
            model = self._create_single_gpu_model(job.model_config)

            # Load dataset
            train_loader = self._create_single_gpu_dataloader(job.dataset_path)

            # Training loop
            self._single_gpu_training_loop(model, train_loader, job)

        except Exception as e:
            logger.error(f"Single GPU training failed for job {job.job_id}: {e}")
            job.status = "failed"

    def _create_distributed_model(self, model_config: Dict[str, Any], rank: int):
        """Create model for distributed training."""
        try:
            # Import training components
            from .trainer import LocalTrainer, TrainingConfig

            # Create trainer config
            config = TrainingConfig(**model_config)

            # Initialize trainer
            trainer = LocalTrainer(
                config=config, output_dir=Path(model_config.get("output_dir", "/tmp"))
            )

            # Load model
            model, tokenizer = trainer.load_model_and_tokenizer()

            # Move model to GPU
            model = model.cuda()

            # Wrap with DistributedDataParallel
            model = torch.nn.parallel.DistributedDataParallel(
                model,
                device_ids=[torch.cuda.current_device()],
                find_unused_parameters=self.config.find_unused_parameters,
            )

            return model

        except Exception as e:
            logger.error(f"Failed to create distributed model: {e}")
            raise

    def _create_single_gpu_model(self, model_config: Dict[str, Any]):
        """Create model for single GPU training."""
        try:
            from .trainer import LocalTrainer, TrainingConfig

            config = TrainingConfig(**model_config)
            trainer = LocalTrainer(
                config=config, output_dir=Path(model_config.get("output_dir", "/tmp"))
            )

            model, tokenizer = trainer.load_model_and_tokenizer()
            model = model.cuda()

            return model

        except Exception as e:
            logger.error(f"Failed to create single GPU model: {e}")
            raise

    def _create_distributed_dataloader(
        self, dataset_path: str, rank: int, world_size: int
    ):
        """Create distributed dataloader."""
        try:
            from torch.utils.data import DataLoader
            from torch.utils.data.distributed import DistributedSampler

            # Load dataset (placeholder - implement based on your dataset format)
            dataset = self._load_dataset(dataset_path)

            # Create distributed sampler
            sampler = DistributedSampler(
                dataset, num_replicas=world_size, rank=rank, shuffle=True
            )

            # Create dataloader
            dataloader = DataLoader(
                dataset,
                batch_size=32,  # Per-GPU batch size
                sampler=sampler,
                num_workers=4,
                pin_memory=True,
            )

            return dataloader

        except Exception as e:
            logger.error(f"Failed to create distributed dataloader: {e}")
            raise

    def _create_single_gpu_dataloader(self, dataset_path: str):
        """Create single GPU dataloader."""
        try:
            from torch.utils.data import DataLoader

            dataset = self._load_dataset(dataset_path)

            dataloader = DataLoader(
                dataset, batch_size=32, shuffle=True, num_workers=4, pin_memory=True
            )

            return dataloader

        except Exception as e:
            logger.error(f"Failed to create single GPU dataloader: {e}")
            raise

    def _load_dataset(self, dataset_path: str):
        """Load dataset from path."""
        # Placeholder implementation
        # In practice, this would load your specific dataset format
        from torch.utils.data import TensorDataset

        # Create dummy dataset for now
        dummy_data = torch.randn(1000, 512)
        dummy_targets = torch.randint(0, 2, (1000,))

        return TensorDataset(dummy_data, dummy_targets)

    def _distributed_training_loop(
        self, model, train_loader, job: TrainingJob, rank: int
    ):
        """Distributed training loop."""
        try:
            from torch.optim import AdamW  # type: ignore

            optimizer = AdamW(model.parameters(), lr=2e-5)
            criterion = torch.nn.CrossEntropyLoss()

            model.train()

            for epoch in range(5):  # Configurable
                train_loader.sampler.set_epoch(
                    epoch
                )  # Important for distributed training

                total_loss = 0
                num_batches = 0

                for batch_idx, (data, targets) in enumerate(train_loader):
                    data, targets = data.cuda(), targets.cuda()

                    optimizer.zero_grad()

                    # Forward pass
                    outputs = model(data)
                    loss = criterion(outputs, targets)

                    # Backward pass
                    loss.backward()

                    # Gradient synchronization happens automatically with DDP
                    optimizer.step()

                    total_loss += loss.item()
                    num_batches += 1

                    if rank == 0 and batch_idx % 10 == 0:
                        logger.info(
                            f"Job {job.job_id} Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.4f}"
                        )

                # Log epoch metrics (only on rank 0)
                if rank == 0:
                    avg_loss = total_loss / num_batches
                    job.metrics[f"epoch_{epoch}_loss"] = avg_loss
                    logger.info(
                        f"Job {job.job_id} Epoch {epoch} completed, Avg Loss: {avg_loss:.4f}"
                    )

            # Save model (only on rank 0)
            if rank == 0:
                self._save_distributed_model(model, job)
                job.status = "completed"
                job.end_time = datetime.now().isoformat()

        except Exception as e:
            logger.error(f"Distributed training loop failed: {e}")
            job.status = "failed"

    def _single_gpu_training_loop(self, model, train_loader, job: TrainingJob):
        """Single GPU training loop."""
        try:
            from torch.optim import AdamW  # type: ignore

            optimizer = AdamW(model.parameters(), lr=2e-5)
            criterion = torch.nn.CrossEntropyLoss()

            model.train()

            for epoch in range(5):
                total_loss = 0
                num_batches = 0

                for batch_idx, (data, targets) in enumerate(train_loader):
                    data, targets = data.cuda(), targets.cuda()

                    optimizer.zero_grad()
                    outputs = model(data)
                    loss = criterion(outputs, targets)
                    loss.backward()
                    optimizer.step()

                    total_loss += loss.item()
                    num_batches += 1

                    if batch_idx % 10 == 0:
                        logger.info(
                            f"Job {job.job_id} Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.4f}"
                        )

                avg_loss = total_loss / num_batches
                job.metrics[f"epoch_{epoch}_loss"] = avg_loss
                logger.info(
                    f"Job {job.job_id} Epoch {epoch} completed, Avg Loss: {avg_loss:.4f}"
                )

            # Save model
            self._save_single_gpu_model(model, job)
            job.status = "completed"
            job.end_time = datetime.now().isoformat()

        except Exception as e:
            logger.error(f"Single GPU training loop failed: {e}")
            job.status = "failed"

    def _save_distributed_model(self, model, job: TrainingJob):
        """Save distributed model."""
        try:
            output_dir = Path(job.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save the module (unwrap DDP)
            model_to_save = model.module if hasattr(model, "module") else model

            # Save model state
            torch.save(model_to_save.state_dict(), output_dir / "pytorch_model.bin")

            # Save job metadata
            job_metadata = {
                "job_id": job.job_id,
                "model_config": job.model_config,
                "metrics": job.metrics,
                "gpu_allocation": job.gpu_allocation,
                "training_time": job.end_time,
            }

            with open(output_dir / "training_metadata.json", "w") as f:
                json.dump(job_metadata, f, indent=2)

            logger.info(f"Saved distributed model for job {job.job_id} to {output_dir}")

        except Exception as e:
            logger.error(f"Failed to save distributed model: {e}")

    def _save_single_gpu_model(self, model, job: TrainingJob):
        """Save single GPU model."""
        try:
            output_dir = Path(job.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            torch.save(model.state_dict(), output_dir / "pytorch_model.bin")

            job_metadata = {
                "job_id": job.job_id,
                "model_config": job.model_config,
                "metrics": job.metrics,
                "gpu_allocation": job.gpu_allocation,
                "training_time": job.end_time,
            }

            with open(output_dir / "training_metadata.json", "w") as f:
                json.dump(job_metadata, f, indent=2)

            logger.info(f"Saved single GPU model for job {job.job_id} to {output_dir}")

        except Exception as e:
            logger.error(f"Failed to save single GPU model: {e}")

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a training job."""
        if job_id not in self.active_jobs:
            return None

        job = self.active_jobs[job_id]

        return {
            "job_id": job.job_id,
            "status": job.status,
            "start_time": job.start_time,
            "end_time": job.end_time,
            "gpu_allocation": job.gpu_allocation,
            "metrics": job.metrics,
            "output_dir": job.output_dir,
        }

    def list_active_jobs(self) -> List[Dict[str, Any]]:
        """List all active training jobs."""
        jobs = []
        for job_id in self.active_jobs.keys():
            status = self.get_job_status(job_id)
            if status:
                jobs.append(status)
        return jobs

    def terminate_job(self, job_id: str) -> bool:
        """Terminate a running training job."""
        if job_id not in self.active_jobs:
            logger.error(f"Job {job_id} not found")
            return False

        try:
            job = self.active_jobs[job_id]

            # Kill processes (if running)
            for pid in job.process_ids:
                try:
                    os.kill(pid, 9)  # SIGKILL
                except ProcessLookupError:
                    pass  # Process already dead

            # Free GPUs
            self.gpu_manager.free_gpus(job_id)

            # Update job status
            job.status = "terminated"
            job.end_time = datetime.now().isoformat()

            logger.info(f"Terminated training job {job_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to terminate job {job_id}: {e}")
            return False

    def cleanup_completed_jobs(self, max_age_hours: int = 24):
        """Clean up completed jobs older than max_age_hours."""
        from datetime import timedelta

        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        to_remove = []
        for job_id, job in self.active_jobs.items():
            if job.status in ["completed", "failed", "terminated"] and job.end_time:
                try:
                    end_time = datetime.fromisoformat(job.end_time)
                    if end_time < cutoff_time:
                        to_remove.append(job_id)
                except ValueError:
                    pass  # Invalid timestamp

        for job_id in to_remove:
            self.gpu_manager.free_gpus(job_id)
            del self.active_jobs[job_id]
            logger.info(f"Cleaned up old job {job_id}")

        return len(to_remove)
