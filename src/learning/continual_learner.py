"""
JARVIS 5.0 - Continual Learner System
Automates the feedback-to-training loop using DPO and preference pairs.
"""
import logging
import threading
import time
import json
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("JARVIS-LEARNER")

class ContinualLearner:
    def __init__(self, data_dir: Path, feedback_threshold=100, check_interval=3600):
        """
        Initialize the Continual Learner.
        
        Args:
            data_dir: The directory where data and models are stored.
            feedback_threshold: Number of feedbacks required to trigger a training cycle.
            check_interval: Interval in seconds to check for new feedback.
        """
        self.data_dir = Path(data_dir)
        self.feedback_threshold = feedback_threshold
        self.check_interval = check_interval
        self.is_running = False
        self.training_cycles = 0
        
        # Internal components (Lazy Load)
        self.feedback_db = None
        self.trainer = None
        
    def _ensure_dependencies(self):
        """Lazy load internal AI/DB components to avoid circular imports and boot slowdowns"""
        if self.feedback_db and self.trainer:
            return True
            
        try:
            from src.learning.feedback_loop import FeedbackDatabase
            self.feedback_db = FeedbackDatabase(self.data_dir / "feedback.db")
            
            from src.learning.trainer import LocalTrainer, TrainingConfig
            config = TrainingConfig(
                model_name="Qwen/Qwen2.5-1.5B-Instruct",
                load_in_4bit=True, 
                num_train_epochs=1,
                per_device_train_batch_size=2,
                gradient_accumulation_steps=2,
                save_steps=100,
                eval_steps=50,
                logging_steps=5
            )
            # Targeting the 1.5B model we just upgraded to
            self.trainer = LocalTrainer(
                config=config,
                output_dir=self.data_dir / "models" / "continual"
            )
            return True
        except Exception as e:
            logger.error(f"âŒ Could not initialize learner dependencies: {e}")
            return False

    def start(self):
        """Start the autonomous monitoring loop in a background thread"""
        if not self._ensure_dependencies():
            logger.warning("ðŸ§  Learning systems hibernating (missing components)")
            return
            
        self.is_running = True
        thread = threading.Thread(target=self._monitoring_loop, daemon=True, name="ContinualLearner-Pulse")
        thread.start()
        logger.info("ðŸ§  JARVIS Learning Systems: Engaged (Threshold: %d)", self.feedback_threshold)

    def _monitoring_loop(self):
        """Checks for feedback clusters and executes training cycles"""
        while self.is_running:
            try:
                # Assuming feedback_db has a count_pending() method
                pending = self.feedback_db.count_pending() if hasattr(self.feedback_db, 'count_pending') else 0
                
                if pending >= self.feedback_threshold:
                    logger.info(f"ðŸŽ¯ Significant feedback cluster detected: {pending} interactions. Initiating cycle...")
                    self._execute_training_cycle()
                
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Learner Loop Error: {e}")
                time.sleep(60)

    def _execute_training_cycle(self):
        """Executes a DPO training session and updates the model index"""
        logger.info("ðŸš€ [TRAINING CYCLE START] Optimizing Neural Weights...")
        start_time = time.time()
        
        try:
            # Generate preference pairs (DPO format)
            pairs = self.feedback_db.generate_preference_pairs(n_pairs=self.feedback_threshold)
            
            if len(pairs) < 10:
                logger.warning("âš ï¸ Insufficient valid preference pairs for quality DPO. Skipping cycle.")
                return
                
            # Prepare dataset
            dpo_data = []
            for p in pairs:
                dpo_data.append({
                    "prompt": p.get("prompt"),
                    "chosen": p.get("chosen"),
                    "rejected": p.get("rejected")
                })
                
            # Save temporary training data
            train_dir = self.data_dir / "training_dataset"
            train_dir.mkdir(parents=True, exist_ok=True)
            train_file = train_dir / f"dpo_cycle_{self.training_cycles}_{int(time.time())}.json"
            
            with open(train_file, 'w', encoding='utf-8') as f:
                json.dump(dpo_data, f, indent=2, ensure_ascii=False)
                
            # Execute Training
            self.trainer.train_dpo(str(train_file))
            
            # Flush feedback database
            if hasattr(self.feedback_db, 'mark_trained'):
                self.feedback_db.mark_trained(limit=len(pairs))
                
            self.training_cycles += 1
            duration = time.time() - start_time
            logger.info(f"âœ… [TRAINING CYCLE COMPLETE] Cycle {self.training_cycles} successful. Duration: {duration:.2f}s")
            
        except Exception as e:
            logger.error(f"âŒ Critical failure during training cycle: {e}")

# Singleton Pattern
_learner = None
def get_continual_learner(data_dir: Path):
    global _learner
    if not _learner:
        _learner = ContinualLearner(data_dir)
    return _learner
