"""
Predictive Engine for JARVIS AGI Machine Learning Core.

This module implements pattern prediction using LSTM/Transformer models,
context gathering, confidence scoring, and real-time pattern updates.
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from collections import deque, defaultdict
import pickle

try:
    import torch
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    optim = None
    # Mock classes for when torch is not available
    class torch:
        """Mock torch module."""
        class Tensor:
            """Mock Tensor class."""
            pass
        @staticmethod
        def randn(*args, **kwargs):
            return None
        @staticmethod
        def zeros(*args, **kwargs):
            return None
        @staticmethod
        def tensor(*args, **kwargs):
            return None
        @staticmethod
        def save(*args, **kwargs):
            pass
        @staticmethod
        def load(*args, **kwargs):
            return None
    
    class nn:
        """Mock nn module."""
        class Module:
            """Mock Module class."""
            pass
        class LSTM:
            """Mock LSTM class."""
            pass
        class Linear:
            """Mock Linear class."""
            pass
        class MultiheadAttention:
            """Mock MultiheadAttention class."""
            pass
    class Dataset:
        """Mock Dataset class."""
        pass
    DataLoader = None

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ContextState:
    """Represents the current context state."""
    timestamp: str
    time_of_day: str  # morning, afternoon, evening, night
    day_of_week: int  # 0-6
    active_applications: List[str]
    recent_commands: List[str]
    user_activity: str  # active, idle, away
    system_metrics: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_feature_vector(self) -> List[float]:
        """Convert to numerical feature vector for ML."""
        features = []
        
        # Time features
        hour = int(self.timestamp.split('T')[1].split(':')[0])
        features.extend([
            hour / 24.0,  # Normalized hour
            self.day_of_week / 7.0,  # Normalized day
        ])
        
        # Time of day one-hot encoding
        time_encoding = {
            'morning': [1, 0, 0, 0],
            'afternoon': [0, 1, 0, 0],
            'evening': [0, 0, 1, 0],
            'night': [0, 0, 0, 1]
        }
        features.extend(time_encoding.get(self.time_of_day, [0, 0, 0, 0]))
        
        # Activity one-hot encoding
        activity_encoding = {
            'active': [1, 0, 0],
            'idle': [0, 1, 0],
            'away': [0, 0, 1]
        }
        features.extend(activity_encoding.get(self.user_activity, [0, 0, 0]))
        
        # System metrics (normalized)
        cpu = self.system_metrics.get('cpu_percent', 0.0) / 100.0
        memory = self.system_metrics.get('memory_percent', 0.0) / 100.0
        features.extend([cpu, memory])
        
        # Application count (normalized by max expected)
        app_count = len(self.active_applications) / 10.0
        features.append(min(app_count, 1.0))
        
        # Recent command count
        cmd_count = len(self.recent_commands) / 5.0
        features.append(min(cmd_count, 1.0))
        
        return features
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContextState":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Prediction:
    """Represents a prediction made by the engine."""
    prediction_id: str
    predicted_action: str
    confidence: float
    context_at_prediction: ContextState
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    actual_action: Optional[str] = None
    was_correct: Optional[bool] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['context_at_prediction'] = self.context_at_prediction.to_dict()
        return data


class PatternLSTM(nn.Module):
    """LSTM model for pattern prediction."""
    
    def __init__(
        self,
        input_size: int,
        hidden_size: int = 128,
        num_layers: int = 2,
        num_classes: int = 50,
        dropout: float = 0.2
    ):
        """
        Initialize LSTM model.
        
        Args:
            input_size: Size of input features
            hidden_size: Size of LSTM hidden state
            num_layers: Number of LSTM layers
            num_classes: Number of output classes (actions)
            dropout: Dropout rate
        """
        super(PatternLSTM, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size, num_classes)
        self.softmax = nn.Softmax(dim=1)
    
    def forward(self, x: torch.Tensor, hidden: Optional[Tuple] = None):
        """
        Forward pass.
        
        Args:
            x: Input tensor of shape (batch, seq_len, input_size)
            hidden: Optional hidden state tuple (h, c)
            
        Returns:
            Output logits and hidden state
        """
        # LSTM forward
        lstm_out, hidden = self.lstm(x, hidden)
        
        # Take the last output
        last_output = lstm_out[:, -1, :]
        
        # Apply dropout and fully connected layer
        out = self.dropout(last_output)
        out = self.fc(out)
        
        return out, hidden
    
    def predict(self, x: torch.Tensor, hidden: Optional[Tuple] = None):
        """
        Make prediction with confidence scores.
        
        Args:
            x: Input tensor
            hidden: Optional hidden state
            
        Returns:
            Predicted class, confidence, and hidden state
        """
        self.eval()
        with torch.no_grad():
            logits, hidden = self.forward(x, hidden)
            probs = self.softmax(logits)
            confidence, predicted = torch.max(probs, 1)
        
        return predicted.item(), confidence.item(), hidden


class ContextGatherer:
    """Gathers context information from the system."""
    
    def __init__(self):
        """Initialize context gatherer."""
        self.recent_commands = deque(maxlen=10)
        self.active_apps: List[str] = []
    
    def gather_context(self) -> ContextState:
        """
        Gather current context information.
        
        Returns:
            ContextState object
        """
        now = datetime.now()
        
        # Determine time of day
        hour = now.hour
        if 6 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 22:
            time_of_day = "evening"
        else:
            time_of_day = "night"
        
        # Get system metrics
        system_metrics = self._get_system_metrics()
        
        # Determine user activity based on CPU/input
        user_activity = self._determine_user_activity(system_metrics)
        
        context = ContextState(
            timestamp=now.isoformat(),
            time_of_day=time_of_day,
            day_of_week=now.weekday(),
            active_applications=list(self.active_apps),
            recent_commands=list(self.recent_commands),
            user_activity=user_activity,
            system_metrics=system_metrics
        )
        
        return context
    
    def _get_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics."""
        if not PSUTIL_AVAILABLE:
            return {
                "cpu_percent": 0.0,
                "memory_percent": 0.0,
                "disk_usage": 0.0
            }
        
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {
                "cpu_percent": 0.0,
                "memory_percent": 0.0,
                "disk_usage": 0.0
            }
    
    def _determine_user_activity(self, metrics: Dict[str, float]) -> str:
        """Determine user activity level from metrics."""
        cpu = metrics.get("cpu_percent", 0.0)
        
        if cpu > 30.0:
            return "active"
        elif cpu > 5.0:
            return "idle"
        else:
            return "away"
    
    def update_command_history(self, command: str) -> None:
        """Update recent command history."""
        self.recent_commands.append(command)
    
    def update_active_apps(self, apps: List[str]) -> None:
        """Update list of active applications."""
        self.active_apps = apps


class PatternDatabase:
    """Database for storing pattern history."""
    
    def __init__(self, db_path: Path, max_patterns: int = 10000):
        """
        Initialize pattern database.
        
        Args:
            db_path: Path to store pattern data
            max_patterns: Maximum number of patterns to keep
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.max_patterns = max_patterns
        self.patterns: List[Dict[str, Any]] = []
        self.action_to_id: Dict[str, int] = {}
        self.id_to_action: Dict[int, str] = {}
        
        self._load()
    
    def add_pattern(
        self,
        context: ContextState,
        action: str
    ) -> None:
        """
        Add a pattern to the database.
        
        Args:
            context: Context state
            action: Action taken
        """
        # Assign action ID
        if action not in self.action_to_id:
            action_id = len(self.action_to_id)
            self.action_to_id[action] = action_id
            self.id_to_action[action_id] = action
        
        pattern = {
            "context": context.to_dict(),
            "action": action,
            "action_id": self.action_to_id[action],
            "timestamp": datetime.now().isoformat()
        }
        
        self.patterns.append(pattern)
        
        # Keep only recent patterns
        if len(self.patterns) > self.max_patterns:
            self.patterns = self.patterns[-self.max_patterns:]
        
        # Save periodically (every 10 patterns)
        if len(self.patterns) % 10 == 0:
            self._save()
    
    def get_training_data(
        self,
        sequence_length: int = 5
    ) -> List[Tuple[List[ContextState], str]]:
        """
        Get training data as sequences.
        
        Args:
            sequence_length: Length of context sequences
            
        Returns:
            List of (context_sequence, action) tuples
        """
        if len(self.patterns) < sequence_length + 1:
            return []
        
        sequences = []
        
        for i in range(len(self.patterns) - sequence_length):
            context_seq = []
            for j in range(i, i + sequence_length):
                context = ContextState.from_dict(self.patterns[j]["context"])
                context_seq.append(context)
            
            next_action = self.patterns[i + sequence_length]["action"]
            sequences.append((context_seq, next_action))
        
        return sequences
    
    def _load(self) -> None:
        """Load patterns from disk."""
        if not self.db_path.exists():
            return
        
        try:
            with open(self.db_path, 'rb') as f:
                data = pickle.load(f)
                self.patterns = data.get("patterns", [])
                self.action_to_id = data.get("action_to_id", {})
                self.id_to_action = data.get("id_to_action", {})
            logger.info(f"Loaded {len(self.patterns)} patterns from database")
        except Exception as e:
            logger.error(f"Error loading pattern database: {e}")
    
    def _save(self) -> None:
        """Save patterns to disk."""
        try:
            data = {
                "patterns": self.patterns,
                "action_to_id": self.action_to_id,
                "id_to_action": self.id_to_action
            }
            with open(self.db_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            logger.error(f"Error saving pattern database: {e}")


class PredictiveEngine:
    """
    Predictive Engine for pattern prediction.
    
    Uses LSTM to predict user actions based on context patterns.
    Continuously learns from user behavior.
    """
    
    def __init__(
        self,
        model_dir: Path,
        sequence_length: int = 5,
        hidden_size: int = 128,
        learning_rate: float = 0.001
    ):
        """
        Initialize the PredictiveEngine.
        
        Args:
            model_dir: Directory to store model and data
            sequence_length: Length of context sequences for prediction
            hidden_size: Size of LSTM hidden state
            learning_rate: Learning rate for training
        """
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch not available, using fallback mode")
        
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.sequence_length = sequence_length
        self.hidden_size = hidden_size
        self.learning_rate = learning_rate
        
        # Components
        self.context_gatherer = ContextGatherer()
        self.pattern_db = PatternDatabase(
            db_path=self.model_dir / "patterns.pkl"
        )
        
        # Context history
        self.context_history = deque(maxlen=sequence_length)
        
        # Model
        self.model: Optional[PatternLSTM] = None
        self.optimizer: Optional[optim.Optimizer] = None
        self.criterion: Optional[nn.Module] = None
        self.hidden_state: Optional[Tuple] = None
        
        # Feature size (from ContextState.to_feature_vector)
        self.feature_size = 13  # Updated based on to_feature_vector output
        
        # Statistics
        self.stats = {
            "total_predictions": 0,
            "correct_predictions": 0,
            "total_trainings": 0,
            "avg_confidence": 0.0,
        }
        
        self._initialize_model()
        self._load_stats()
        
        logger.info("PredictiveEngine initialized")
    
    def _initialize_model(self) -> None:
        """Initialize the neural network model."""
        if not TORCH_AVAILABLE:
            return
        
        try:
            # Get number of unique actions
            num_classes = max(len(self.pattern_db.action_to_id), 50)
            
            self.model = PatternLSTM(
                input_size=self.feature_size,
                hidden_size=self.hidden_size,
                num_classes=num_classes
            )
            
            self.optimizer = optim.Adam(
                self.model.parameters(),
                lr=self.learning_rate
            )
            
            self.criterion = nn.CrossEntropyLoss()
            
            # Try to load existing model
            model_path = self.model_dir / "model.pt"
            if model_path.exists():
                self._load_model(model_path)
            
            logger.info(f"Model initialized with {num_classes} action classes")
            
        except Exception as e:
            logger.error(f"Error initializing model: {e}", exc_info=True)
    
    def predict_next_action(
        self,
        current_context: Optional[ContextState] = None
    ) -> Optional[Prediction]:
        """
        Predict the next likely action.
        
        Args:
            current_context: Current context (gathered if not provided)
            
        Returns:
            Prediction object or None if cannot predict
        """
        try:
            # Gather context if not provided
            if current_context is None:
                current_context = self.context_gatherer.gather_context()
            
            # Add to history
            self.context_history.append(current_context)
            
            # Need full sequence to predict
            if len(self.context_history) < self.sequence_length:
                logger.debug(
                    f"Not enough context history "
                    f"({len(self.context_history)}/{self.sequence_length})"
                )
                return None
            
            if not TORCH_AVAILABLE or self.model is None:
                # Fallback: simple frequency-based prediction
                return self._fallback_predict(current_context)
            
            # Prepare input tensor
            feature_sequence = []
            for ctx in self.context_history:
                features = ctx.to_feature_vector()
                feature_sequence.append(features)
            
            x = torch.tensor([feature_sequence], dtype=torch.float32)
            
            # Predict
            predicted_id, confidence, self.hidden_state = self.model.predict(
                x, self.hidden_state
            )
            
            # Get action from ID
            predicted_action = self.pattern_db.id_to_action.get(
                predicted_id,
                "unknown_action"
            )
            
            # Create prediction
            prediction = Prediction(
                prediction_id=f"pred_{datetime.now().timestamp()}",
                predicted_action=predicted_action,
                confidence=confidence,
                context_at_prediction=current_context
            )
            
            # Update statistics
            self.stats["total_predictions"] += 1
            current_avg = self.stats["avg_confidence"]
            total = self.stats["total_predictions"]
            self.stats["avg_confidence"] = (
                (current_avg * (total - 1) + confidence) / total
            )
            
            self._save_stats()
            
            logger.info(
                f"Predicted action: {predicted_action} "
                f"(confidence: {confidence:.2f})"
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting next action: {e}", exc_info=True)
            return None
    
    def _fallback_predict(
        self,
        current_context: ContextState
    ) -> Optional[Prediction]:
        """Fallback prediction using simple frequency analysis."""
        # Get patterns matching similar time of day
        matching_patterns = [
            p for p in self.pattern_db.patterns
            if ContextState.from_dict(p["context"]).time_of_day == current_context.time_of_day
        ]
        
        if not matching_patterns:
            return None
        
        # Count action frequencies
        action_counts = defaultdict(int)
        for pattern in matching_patterns:
            action_counts[pattern["action"]] += 1
        
        # Get most common action
        most_common_action = max(action_counts, key=action_counts.get)
        total = len(matching_patterns)
        confidence = action_counts[most_common_action] / total
        
        prediction = Prediction(
            prediction_id=f"pred_{datetime.now().timestamp()}",
            predicted_action=most_common_action,
            confidence=confidence,
            context_at_prediction=current_context
        )
        
        return prediction
    
    def record_action(
        self,
        action: str,
        context: Optional[ContextState] = None
    ) -> None:
        """
        Record an action taken by the user.
        
        Args:
            action: Action that was taken
            context: Context when action was taken
        """
        try:
            if context is None:
                context = self.context_gatherer.gather_context()
            
            # Add to pattern database
            self.pattern_db.add_pattern(context, action)
            
            # Update command history if it's a command
            self.context_gatherer.update_command_history(action)
            
            logger.debug(f"Recorded action: {action}")
            
        except Exception as e:
            logger.error(f"Error recording action: {e}", exc_info=True)
    
    def update_prediction_result(
        self,
        prediction: Prediction,
        actual_action: str
    ) -> None:
        """
        Update prediction with actual result.
        
        Args:
            prediction: The prediction that was made
            actual_action: The actual action that occurred
        """
        prediction.actual_action = actual_action
        prediction.was_correct = (prediction.predicted_action == actual_action)
        
        if prediction.was_correct:
            self.stats["correct_predictions"] += 1
        
        accuracy = (
            self.stats["correct_predictions"] / self.stats["total_predictions"]
            if self.stats["total_predictions"] > 0 else 0.0
        )
        
        logger.info(
            f"Prediction {'correct' if prediction.was_correct else 'incorrect'} "
            f"(accuracy: {accuracy:.2%})"
        )
        
        self._save_stats()
    
    def train_model(
        self,
        epochs: int = 10,
        batch_size: int = 32
    ) -> Dict[str, float]:
        """
        Train the prediction model.
        
        Args:
            epochs: Number of training epochs
            batch_size: Batch size for training
            
        Returns:
            Dictionary with training metrics
        """
        if not TORCH_AVAILABLE or self.model is None:
            logger.warning("Cannot train: PyTorch not available or model not initialized")
            return {"status": "unavailable"}
        
        try:
            logger.info("Starting model training")
            
            # Get training data
            sequences = self.pattern_db.get_training_data(self.sequence_length)
            
            if len(sequences) < batch_size:
                logger.warning(f"Not enough training data ({len(sequences)} sequences)")
                return {"status": "insufficient_data", "sequences": len(sequences)}
            
            # Prepare data
            X_train = []
            y_train = []
            
            for context_seq, action in sequences:
                features = [ctx.to_feature_vector() for ctx in context_seq]
                X_train.append(features)
                
                action_id = self.pattern_db.action_to_id.get(action, 0)
                y_train.append(action_id)
            
            X = torch.tensor(X_train, dtype=torch.float32)
            y = torch.tensor(y_train, dtype=torch.long)
            
            # Training loop
            self.model.train()
            total_loss = 0.0
            
            for epoch in range(epochs):
                epoch_loss = 0.0
                
                # Mini-batch training
                for i in range(0, len(X), batch_size):
                    batch_X = X[i:i+batch_size]
                    batch_y = y[i:i+batch_size]
                    
                    # Forward pass
                    self.optimizer.zero_grad()
                    outputs, _ = self.model(batch_X)
                    loss = self.criterion(outputs, batch_y)
                    
                    # Backward pass
                    loss.backward()
                    self.optimizer.step()
                    
                    epoch_loss += loss.item()
                
                epoch_loss /= (len(X) / batch_size)
                total_loss += epoch_loss
                
                if (epoch + 1) % 2 == 0:
                    logger.info(f"Epoch {epoch+1}/{epochs}, Loss: {epoch_loss:.4f}")
            
            avg_loss = total_loss / epochs
            
            # Save model
            self._save_model()
            
            # Update statistics
            self.stats["total_trainings"] += 1
            self._save_stats()
            
            logger.info(f"Training completed. Average loss: {avg_loss:.4f}")
            
            return {
                "status": "success",
                "epochs": epochs,
                "avg_loss": avg_loss,
                "training_samples": len(sequences)
            }
            
        except Exception as e:
            logger.error(f"Error training model: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}
    
    def _save_model(self) -> None:
        """Save model to disk."""
        if self.model is None:
            return
        
        try:
            model_path = self.model_dir / "model.pt"
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'optimizer_state_dict': self.optimizer.state_dict(),
                'action_to_id': self.pattern_db.action_to_id,
                'id_to_action': self.pattern_db.id_to_action,
            }, model_path)
            logger.info(f"Model saved to {model_path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def _load_model(self, model_path: Path) -> None:
        """Load model from disk."""
        try:
            checkpoint = torch.load(model_path)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.pattern_db.action_to_id = checkpoint.get('action_to_id', {})
            self.pattern_db.id_to_action = checkpoint.get('id_to_action', {})
            logger.info(f"Model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics."""
        stats = dict(self.stats)
        
        if stats["total_predictions"] > 0:
            stats["accuracy"] = (
                stats["correct_predictions"] / stats["total_predictions"]
            )
        else:
            stats["accuracy"] = 0.0
        
        stats["patterns_stored"] = len(self.pattern_db.patterns)
        stats["unique_actions"] = len(self.pattern_db.action_to_id)
        
        return stats
    
    def _load_stats(self) -> None:
        """Load statistics from file."""
        stats_file = self.model_dir / "stats.json"
        if stats_file.exists():
            try:
                with open(stats_file, 'r') as f:
                    self.stats = json.load(f)
            except Exception as e:
                logger.error(f"Error loading stats: {e}")
    
    def _save_stats(self) -> None:
        """Save statistics to file."""
        stats_file = self.model_dir / "stats.json"
        try:
            with open(stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving stats: {e}")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Initialize engine
    engine = PredictiveEngine(
        model_dir=Path("./data/predictive_engine"),
        sequence_length=5,
        hidden_size=64
    )
    
    # Simulate recording some actions
    actions = [
        ("open_chrome", "morning"),
        ("check_email", "morning"),
        ("open_ide", "afternoon"),
        ("run_tests", "afternoon"),
        ("check_email", "evening"),
    ]
    
    for action, time_of_day in actions:
        # Create a mock context
        context = ContextState(
            timestamp=datetime.now().isoformat(),
            time_of_day=time_of_day,
            day_of_week=1,
            active_applications=["chrome", "vscode"],
            recent_commands=[action],
            user_activity="active",
            system_metrics={"cpu_percent": 30.0, "memory_percent": 50.0, "disk_usage": 60.0}
        )
        
        engine.record_action(action, context)
    
    # Get statistics
    stats = engine.get_statistics()
    print(f"\nPredictive Engine Statistics:")
    print(f"Patterns stored: {stats['patterns_stored']}")
    print(f"Unique actions: {stats['unique_actions']}")
    print(f"Total predictions: {stats['total_predictions']}")
    print(f"Average confidence: {stats['avg_confidence']:.2%}")
    
    # Try to make a prediction (need more data in real scenario)
    # prediction = engine.predict_next_action()
    # if prediction:
    #     print(f"\nPredicted action: {prediction.predicted_action}")
    #     print(f"Confidence: {prediction.confidence:.2%}")
    
    print("\nPredictiveEngine example completed!")
