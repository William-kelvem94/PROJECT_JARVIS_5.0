"""
Local Trainer for JARVIS AGI Machine Learning Core.

This module handles LoRA/QLoRA fine-tuning for various LLMs including
Llama-3, Mistral, Phi, and Gemma. Supports 4-bit/8-bit quantization,
checkpoint management, and complete training pipelines.
"""

import json
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field, asdict
import shutil

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except (ImportError, OSError) as e:
    TORCH_AVAILABLE = False
    torch = None
    Dataset = None
    DataLoader = None

try:
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        TrainingArguments,
        Trainer,
        DataCollatorForLanguageModeling,
        EarlyStoppingCallback,
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    AutoModelForCausalLM = None
    AutoTokenizer = None
    TrainingArguments = None
    Trainer = None
    DataCollatorForLanguageModeling = None
    EarlyStoppingCallback = None

try:
    from peft import (
        LoraConfig,
        get_peft_model,
        prepare_model_for_kbit_training,
        PeftModel,
    )
    PEFT_AVAILABLE = True
except ImportError:
    PEFT_AVAILABLE = False
    LoraConfig = None
    get_peft_model = None
    prepare_model_for_kbit_training = None
    PeftModel = None

try:
    from bitsandbytes import BitsAndBytesConfig
    BNB_AVAILABLE = True
except ImportError:
    BNB_AVAILABLE = False
    BitsAndBytesConfig = None

try:
    from unsloth import FastLanguageModel
    UNSLOTH_AVAILABLE = True
except ImportError:
    UNSLOTH_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class TrainingConfig:
    """Configuration for model training."""
    # Model settings
    model_name: str = "meta-llama/Llama-3-8B"
    model_max_length: int = 2048
    load_in_4bit: bool = True
    load_in_8bit: bool = False
    
    # LoRA settings
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: List[str] = field(default_factory=lambda: ["q_proj", "k_proj", "v_proj", "o_proj"])
    lora_bias: str = "none"
    
    # Training hyperparameters
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 4
    per_device_eval_batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    weight_decay: float = 0.01
    max_grad_norm: float = 1.0
    warmup_ratio: float = 0.05
    
    # Optimization
    optimizer: str = "adamw_8bit"
    lr_scheduler_type: str = "cosine"
    fp16: bool = False
    bf16: bool = True
    
    # Logging and checkpointing
    logging_steps: int = 10
    eval_steps: int = 100
    save_steps: int = 500
    save_total_limit: int = 3
    evaluation_strategy: str = "steps"
    
    # Early stopping
    early_stopping_patience: int = 3
    early_stopping_threshold: float = 0.01
    
    # Other
    seed: int = 42
    use_unsloth: bool = False
    gradient_checkpointing: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrainingConfig":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class TrainingMetrics:
    """Metrics from a training run."""
    epoch: int
    step: int
    loss: float
    learning_rate: float
    eval_loss: Optional[float] = None
    perplexity: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class TrainingDataset(Dataset):
    """Custom dataset for training."""
    
    def __init__(
        self,
        data: List[Dict[str, str]],
        tokenizer: Any,
        max_length: int = 2048,
        format: str = "alpaca"
    ):
        """
        Initialize dataset.
        
        Args:
            data: List of training examples
            tokenizer: Tokenizer to use
            max_length: Maximum sequence length
            format: Data format ('alpaca', 'sharegpt', 'instruct')
        """
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.format = format
    
    def __len__(self) -> int:
        """Get dataset length."""
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        """Get item at index."""
        item = self.data[idx]
        
        # Format the text based on format type
        if self.format == "alpaca":
            text = self._format_alpaca(item)
        elif self.format == "sharegpt":
            text = self._format_sharegpt(item)
        elif self.format == "instruct":
            text = item.get("text", "")
        else:
            raise ValueError(f"Unknown format: {self.format}")
        
        # Tokenize
        encodings = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt"
        )
        
        return {
            "input_ids": encodings["input_ids"].squeeze(),
            "attention_mask": encodings["attention_mask"].squeeze(),
            "labels": encodings["input_ids"].squeeze()
        }
    
    def _format_alpaca(self, item: Dict[str, str]) -> str:
        """Format Alpaca-style item."""
        instruction = item.get("instruction", "")
        input_text = item.get("input", "")
        output = item.get("output", "")
        
        if input_text:
            prompt = f"### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n{output}"
        else:
            prompt = f"### Instruction:\n{instruction}\n\n### Response:\n{output}"
        
        return prompt
    
    def _format_sharegpt(self, item: Dict[str, Any]) -> str:
        """Format ShareGPT-style item."""
        conversations = item.get("conversations", [])
        formatted = []
        
        for conv in conversations:
            role = conv.get("from", "")
            value = conv.get("value", "")
            
            if role == "system":
                formatted.append(f"System: {value}")
            elif role == "human":
                formatted.append(f"Human: {value}")
            elif role == "gpt":
                formatted.append(f"Assistant: {value}")
        
        return "\n\n".join(formatted)


class CheckpointManager:
    """Manages training checkpoints."""
    
    def __init__(
        self,
        checkpoint_dir: Path,
        max_checkpoints: int = 3,
        best_metric: str = "eval_loss"
    ):
        """
        Initialize checkpoint manager.
        
        Args:
            checkpoint_dir: Directory to store checkpoints
            max_checkpoints: Maximum number of checkpoints to keep
            best_metric: Metric to use for best checkpoint selection
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_checkpoints = max_checkpoints
        self.best_metric = best_metric
        self.checkpoints: List[Dict[str, Any]] = []
        self.best_checkpoint: Optional[Dict[str, Any]] = None
        
        self._load_checkpoint_info()
    
    def _load_checkpoint_info(self) -> None:
        """Load checkpoint information from disk."""
        info_file = self.checkpoint_dir / "checkpoint_info.json"
        if info_file.exists():
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.checkpoints = data.get("checkpoints", [])
                    self.best_checkpoint = data.get("best_checkpoint")
            except Exception as e:
                logger.error(f"Error loading checkpoint info: {e}")
    
    def _save_checkpoint_info(self) -> None:
        """Save checkpoint information to disk."""
        info_file = self.checkpoint_dir / "checkpoint_info.json"
        try:
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "checkpoints": self.checkpoints,
                    "best_checkpoint": self.best_checkpoint
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving checkpoint info: {e}")
    
    def add_checkpoint(
        self,
        step: int,
        epoch: int,
        metrics: Dict[str, float],
        checkpoint_path: Path
    ) -> None:
        """
        Add a new checkpoint.
        
        Args:
            step: Training step
            epoch: Training epoch
            metrics: Metrics at this checkpoint
            checkpoint_path: Path to checkpoint directory
        """
        checkpoint_info = {
            "step": step,
            "epoch": epoch,
            "metrics": metrics,
            "path": str(checkpoint_path),
            "timestamp": datetime.now().isoformat()
        }
        
        self.checkpoints.append(checkpoint_info)
        
        # Update best checkpoint
        if self.best_metric in metrics:
            metric_value = metrics[self.best_metric]
            is_better = (
                self.best_checkpoint is None or
                metric_value < self.best_checkpoint["metrics"].get(self.best_metric, float('inf'))
            )
            
            if is_better:
                self.best_checkpoint = checkpoint_info
                logger.info(f"New best checkpoint at step {step} ({self.best_metric}: {metric_value:.4f})")
        
        # Remove old checkpoints if over limit
        if len(self.checkpoints) > self.max_checkpoints:
            old_checkpoint = self.checkpoints.pop(0)
            old_path = Path(old_checkpoint["path"])
            
            # Don't delete if it's the best checkpoint
            if old_checkpoint != self.best_checkpoint:
                if old_path.exists():
                    try:
                        shutil.rmtree(old_path)
                        logger.info(f"Removed old checkpoint: {old_path}")
                    except Exception as e:
                        logger.error(f"Error removing checkpoint: {e}")
        
        self._save_checkpoint_info()
    
    def get_best_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Get the best checkpoint."""
        return self.best_checkpoint
    
    def get_latest_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Get the latest checkpoint."""
        return self.checkpoints[-1] if self.checkpoints else None


class LocalTrainer:
    """
    Local trainer for fine-tuning LLMs with LoRA/QLoRA.
    
    Supports models: Llama-3, Mistral, Phi, Gemma
    Supports quantization: 4-bit, 8-bit
    Supports optimization: LoRA, QLoRA, unsloth
    """
    
    SUPPORTED_MODELS = {
        "llama-3-8b": "meta-llama/Meta-Llama-3-8B",
        "llama-3-70b": "meta-llama/Meta-Llama-3-70B",
        "mistral-7b": "mistralai/Mistral-7B-v0.1",
        "mistral-7b-instruct": "mistralai/Mistral-7B-Instruct-v0.1",
        "phi-3": "microsoft/Phi-3-mini-4k-instruct",
        "phi-2": "microsoft/phi-2",
        "gemma-2b": "google/gemma-2b",
        "gemma-7b": "google/gemma-7b",
    }
    
    def __init__(
        self,
        config: TrainingConfig,
        output_dir: Path,
        cache_dir: Optional[Path] = None
    ):
        """
        Initialize the LocalTrainer.
        
        Args:
            config: Training configuration
            output_dir: Directory to save outputs
            cache_dir: Directory for model cache
        """
        if not TORCH_AVAILABLE:
            raise ImportError(
                "❌ LocalTrainer requer 'torch'.\n"
                "Instale com: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
            )
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "❌ LocalTrainer requer 'transformers'.\n"
                "Instale com: pip install transformers"
            )
        if not PEFT_AVAILABLE:
            raise ImportError(
                "❌ LocalTrainer requer 'peft' (Parameter-Efficient Fine-Tuning).\n"
                "Instale com: pip install peft"
            )
        
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_dir = Path(cache_dir) if cache_dir else None
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.model = None
        self.tokenizer = None
        self.trainer = None
        
        self.training_history: List[TrainingMetrics] = []
        self.checkpoint_manager = CheckpointManager(
            checkpoint_dir=self.output_dir / "checkpoints",
            max_checkpoints=config.save_total_limit
        )
        
        # Device setup
        self.device = self._setup_device()
        
        logger.info(f"LocalTrainer initialized on device: {self.device}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def _setup_device(self) -> str:
        """Setup compute device."""
        if torch.cuda.is_available():
            device = "cuda"
            logger.info(f"CUDA available: {torch.cuda.get_device_name(0)}")
            logger.info(f"CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = "mps"
            logger.info("Using MPS (Apple Silicon)")
        else:
            device = "cpu"
            logger.warning("No GPU available, using CPU (training will be slow)")
        
        return device
    
    def _get_model_name(self, model_key: str) -> str:
        """Get full model name from key."""
        if model_key in self.SUPPORTED_MODELS:
            return self.SUPPORTED_MODELS[model_key]
        return model_key  # Assume it's already a full model name
    
    def _get_quantization_config(self) -> Optional[Any]:
        """Get quantization configuration."""
        if not BNB_AVAILABLE:
            logger.warning("bitsandbytes not available, quantization disabled")
            return None
        
        if self.config.load_in_4bit:
            return BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16 if self.config.bf16 else torch.float16,
                bnb_4bit_use_double_quant=True,
            )
        elif self.config.load_in_8bit:
            return BitsAndBytesConfig(
                load_in_8bit=True,
            )
        
        return None
    
    def load_model_and_tokenizer(self) -> Tuple[Any, Any]:
        """
        Load model and tokenizer.
        
        Returns:
            Tuple of (model, tokenizer)
        """
        try:
            model_name = self._get_model_name(self.config.model_name)
            logger.info(f"Loading model: {model_name}")
            
            # Use unsloth if available and requested
            if self.config.use_unsloth and UNSLOTH_AVAILABLE:
                logger.info("Using unsloth for optimized loading")
                model, tokenizer = FastLanguageModel.from_pretrained(
                    model_name=model_name,
                    max_seq_length=self.config.model_max_length,
                    load_in_4bit=self.config.load_in_4bit,
                    dtype=None,  # Auto-detect
                )
            else:
                # Standard loading
                quantization_config = self._get_quantization_config()
                
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    quantization_config=quantization_config,
                    device_map="auto" if self.device == "cuda" else None,
                    cache_dir=self.cache_dir,
                    trust_remote_code=True,
                )
                
                tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    cache_dir=self.cache_dir,
                    trust_remote_code=True,
                )
            
            # Setup tokenizer
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            tokenizer.padding_side = "right"
            tokenizer.model_max_length = self.config.model_max_length
            
            # Prepare model for training
            if self.config.load_in_4bit or self.config.load_in_8bit:
                model = prepare_model_for_kbit_training(
                    model,
                    use_gradient_checkpointing=self.config.gradient_checkpointing
                )
            
            self.model = model
            self.tokenizer = tokenizer
            
            logger.info("Model and tokenizer loaded successfully")
            return model, tokenizer
            
        except Exception as e:
            logger.error(f"Error loading model: {e}", exc_info=True)
            raise
    
    def setup_lora(self, model: Any) -> Any:
        """
        Setup LoRA for the model.
        
        Args:
            model: Base model
            
        Returns:
            LoRA model
        """
        try:
            logger.info("Setting up LoRA")
            
            if self.config.use_unsloth and UNSLOTH_AVAILABLE:
                model = FastLanguageModel.get_peft_model(
                    model,
                    r=self.config.lora_r,
                    lora_alpha=self.config.lora_alpha,
                    lora_dropout=self.config.lora_dropout,
                    target_modules=self.config.lora_target_modules,
                    bias=self.config.lora_bias,
                    use_gradient_checkpointing=self.config.gradient_checkpointing,
                )
            else:
                lora_config = LoraConfig(
                    r=self.config.lora_r,
                    lora_alpha=self.config.lora_alpha,
                    lora_dropout=self.config.lora_dropout,
                    target_modules=self.config.lora_target_modules,
                    bias=self.config.lora_bias,
                    task_type="CAUSAL_LM",
                )
                
                model = get_peft_model(model, lora_config)
            
            # Print trainable parameters
            trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
            all_params = sum(p.numel() for p in model.parameters())
            trainable_percent = 100 * trainable_params / all_params
            
            logger.info(f"Trainable parameters: {trainable_params:,} ({trainable_percent:.2f}%)")
            logger.info(f"All parameters: {all_params:,}")
            
            return model
            
        except Exception as e:
            logger.error(f"Error setting up LoRA: {e}", exc_info=True)
            raise
    
    def prepare_training_args(self) -> TrainingArguments:
        """
        Prepare training arguments.
        
        Returns:
            TrainingArguments object
        """
        return TrainingArguments(
            output_dir=str(self.output_dir),
            num_train_epochs=self.config.num_train_epochs,
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            per_device_eval_batch_size=self.config.per_device_eval_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
            max_grad_norm=self.config.max_grad_norm,
            warmup_ratio=self.config.warmup_ratio,
            logging_steps=self.config.logging_steps,
            eval_steps=self.config.eval_steps,
            save_steps=self.config.save_steps,
            save_total_limit=self.config.save_total_limit,
            evaluation_strategy=self.config.evaluation_strategy,
            optim=self.config.optimizer,
            lr_scheduler_type=self.config.lr_scheduler_type,
            fp16=self.config.fp16,
            bf16=self.config.bf16,
            gradient_checkpointing=self.config.gradient_checkpointing,
            seed=self.config.seed,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            report_to="none",  # Disable external reporting
        )
    
    def train(
        self,
        train_data: List[Dict[str, str]],
        eval_data: Optional[List[Dict[str, str]]] = None,
        data_format: str = "alpaca",
        resume_from_checkpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Train the model.
        
        Args:
            train_data: Training data
            eval_data: Evaluation data (optional)
            data_format: Format of the data ('alpaca', 'sharegpt', 'instruct')
            resume_from_checkpoint: Path to checkpoint to resume from
            
        Returns:
            Dictionary with training results
        """
        try:
            start_time = time.time()
            
            # Load model if not already loaded
            if self.model is None or self.tokenizer is None:
                self.load_model_and_tokenizer()
            
            # Setup LoRA
            model = self.setup_lora(self.model)
            
            # Prepare datasets
            logger.info(f"Preparing datasets (format: {data_format})")
            train_dataset = TrainingDataset(
                data=train_data,
                tokenizer=self.tokenizer,
                max_length=self.config.model_max_length,
                format=data_format
            )
            
            eval_dataset = None
            if eval_data:
                eval_dataset = TrainingDataset(
                    data=eval_data,
                    tokenizer=self.tokenizer,
                    max_length=self.config.model_max_length,
                    format=data_format
                )
            
            # Prepare training arguments
            training_args = self.prepare_training_args()
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False
            )
            
            # Create trainer
            callbacks = []
            if self.config.early_stopping_patience > 0 and eval_dataset:
                callbacks.append(
                    EarlyStoppingCallback(
                        early_stopping_patience=self.config.early_stopping_patience,
                        early_stopping_threshold=self.config.early_stopping_threshold
                    )
                )
            
            self.trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                data_collator=data_collator,
                callbacks=callbacks,
            )
            
            # Train
            logger.info("Starting training...")
            train_result = self.trainer.train(resume_from_checkpoint=resume_from_checkpoint)
            
            # Save final model
            logger.info("Saving final model...")
            self.save_model(self.output_dir / "final_model")
            
            # Calculate training time
            training_time = time.time() - start_time
            
            # Prepare results
            results = {
                "train_loss": train_result.training_loss,
                "train_samples": len(train_data),
                "eval_samples": len(eval_data) if eval_data else 0,
                "training_time_seconds": training_time,
                "num_epochs": self.config.num_train_epochs,
                "final_learning_rate": train_result.training_loss,  # Approximation
            }
            
            if eval_dataset:
                eval_results = self.trainer.evaluate()
                results["eval_loss"] = eval_results.get("eval_loss")
                results["eval_perplexity"] = (
                    torch.exp(torch.tensor(eval_results["eval_loss"])).item()
                    if "eval_loss" in eval_results else None
                )
            
            # Save results
            self._save_training_results(results)
            
            logger.info(f"Training completed in {training_time:.2f} seconds")
            logger.info(f"Final train loss: {results['train_loss']:.4f}")
            if "eval_loss" in results:
                logger.info(f"Final eval loss: {results['eval_loss']:.4f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error during training: {e}", exc_info=True)
            raise
    
    def evaluate(
        self,
        eval_data: List[Dict[str, str]],
        data_format: str = "alpaca"
    ) -> Dict[str, float]:
        """
        Evaluate the model.
        
        Args:
            eval_data: Evaluation data
            data_format: Format of the data
            
        Returns:
            Dictionary with evaluation metrics
        """
        try:
            if self.model is None or self.tokenizer is None:
                raise ValueError("Model not loaded. Call load_model_and_tokenizer() first.")
            
            logger.info("Evaluating model...")
            
            eval_dataset = TrainingDataset(
                data=eval_data,
                tokenizer=self.tokenizer,
                max_length=self.config.model_max_length,
                format=data_format
            )
            
            if self.trainer is None:
                # Create a temporary trainer for evaluation
                training_args = self.prepare_training_args()
                data_collator = DataCollatorForLanguageModeling(
                    tokenizer=self.tokenizer,
                    mlm=False
                )
                
                self.trainer = Trainer(
                    model=self.model,
                    args=training_args,
                    eval_dataset=eval_dataset,
                    data_collator=data_collator,
                )
            
            eval_results = self.trainer.evaluate()
            
            # Calculate perplexity
            if "eval_loss" in eval_results:
                eval_results["perplexity"] = (
                    torch.exp(torch.tensor(eval_results["eval_loss"])).item()
                )
            
            logger.info(f"Evaluation results: {eval_results}")
            return eval_results
            
        except Exception as e:
            logger.error(f"Error during evaluation: {e}", exc_info=True)
            raise
    
    def save_model(
        self,
        save_path: Path,
        merge_and_unload: bool = False
    ) -> None:
        """
        Save the trained model.
        
        Args:
            save_path: Path to save the model
            merge_and_unload: Whether to merge LoRA weights and save full model
        """
        try:
            save_path = Path(save_path)
            save_path.mkdir(parents=True, exist_ok=True)
            
            if merge_and_unload:
                logger.info("Merging LoRA weights into base model...")
                if isinstance(self.model, PeftModel):
                    merged_model = self.model.merge_and_unload()
                    merged_model.save_pretrained(save_path)
                else:
                    self.model.save_pretrained(save_path)
            else:
                logger.info("Saving model with LoRA adapters...")
                self.model.save_pretrained(save_path)
            
            # Save tokenizer
            self.tokenizer.save_pretrained(save_path)
            
            # Save config
            config_path = save_path / "training_config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Model saved to {save_path}")
            
        except Exception as e:
            logger.error(f"Error saving model: {e}", exc_info=True)
            raise
    
    def load_checkpoint(self, checkpoint_path: Path) -> None:
        """
        Load a training checkpoint.
        
        Args:
            checkpoint_path: Path to checkpoint
        """
        try:
            checkpoint_path = Path(checkpoint_path)
            
            if not checkpoint_path.exists():
                raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
            
            logger.info(f"Loading checkpoint from {checkpoint_path}")
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(checkpoint_path)
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
            
            # Load config if exists
            config_path = checkpoint_path / "training_config.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_dict = json.load(f)
                    self.config = TrainingConfig.from_dict(config_dict)
            
            logger.info("Checkpoint loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading checkpoint: {e}", exc_info=True)
            raise
    
    def _save_training_results(self, results: Dict[str, Any]) -> None:
        """Save training results to file."""
        try:
            results_path = self.output_dir / "training_results.json"
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Training results saved to {results_path}")
        except Exception as e:
            logger.error(f"Error saving training results: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        if self.model is None:
            return {"status": "not_loaded"}
        
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        
        return {
            "status": "loaded",
            "model_name": self.config.model_name,
            "total_parameters": total_params,
            "trainable_parameters": trainable_params,
            "trainable_percent": 100 * trainable_params / total_params if total_params > 0 else 0,
            "device": self.device,
            "quantization": {
                "4bit": self.config.load_in_4bit,
                "8bit": self.config.load_in_8bit
            }
        }


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create training config
    config = TrainingConfig(
        model_name="phi-2",
        model_max_length=1024,
        load_in_4bit=True,
        num_train_epochs=1,
        per_device_train_batch_size=2,
        learning_rate=2e-4,
    )
    
    # Initialize trainer
    trainer = LocalTrainer(
        config=config,
        output_dir=Path("./models/fine_tuned"),
    )
    
    # Example training data
    train_data = [
        {
            "instruction": "What is machine learning?",
            "input": "",
            "output": "Machine learning is a branch of artificial intelligence..."
        },
        {
            "instruction": "Explain neural networks",
            "input": "",
            "output": "Neural networks are computing systems inspired by biological neural networks..."
        }
    ]
    
    try:
        # Get model info
        info = trainer.get_model_info()
        print(f"\nModel Info: {info}")
        
        # Note: Actual training commented out for testing
        # results = trainer.train(train_data=train_data, data_format="alpaca")
        # print(f"\nTraining Results: {results}")
        
        print("\nLocalTrainer example completed!")
        
    except Exception as e:
        print(f"Error in example: {e}")
