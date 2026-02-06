"""
Autonomy Core for JARVIS AGI Machine Learning Core.

This module implements the AI consciousness layer including decision engine,
confidence assessment, mode management, exploration vs exploitation,
and meta-learning controller.
"""

import json
import logging
import random
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import deque, defaultdict

logger = logging.getLogger(__name__)


class AutonomyMode(Enum):
    """Operating modes for the autonomy system."""
    ACTIVE = "active"          # Proactively suggests and acts
    PASSIVE = "passive"        # Only responds to direct requests
    LEARNING = "learning"      # Observes and learns without acting
    EXPLORATION = "exploration"  # Actively explores new behaviors
    SLEEP = "sleep"           # Minimal activity, background only


class DecisionType(Enum):
    """Types of decisions the autonomy can make."""
    RESPOND = "respond"       # Respond to user input
    OBSERVE = "observe"       # Observe without responding
    LEARN = "learn"          # Learn from the situation
    SUGGEST = "suggest"      # Proactively suggest action
    ACT = "act"             # Autonomously perform action
    DEFER = "defer"         # Defer to user or other system


@dataclass
class DecisionContext:
    """Context information for decision making."""
    user_input: Optional[str] = None
    current_task: Optional[str] = None
    recent_interactions: List[str] = field(default_factory=list)
    system_state: Dict[str, Any] = field(default_factory=dict)
    time_of_day: str = ""
    user_activity: str = "unknown"
    confidence_history: List[float] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Decision:
    """Represents a decision made by the autonomy system."""
    decision_id: str
    decision_type: DecisionType
    action: str
    confidence: float
    reasoning: str
    context: DecisionContext
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    executed: bool = False
    outcome: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['decision_type'] = self.decision_type.value
        data['context'] = self.context.to_dict()
        return data


@dataclass
class LearningGoal:
    """Represents a learning goal for the system."""
    goal_id: str
    description: str
    priority: int  # 1-10
    progress: float = 0.0  # 0.0-1.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class ConfidenceAssessor:
    """Assesses confidence levels for decisions and actions."""
    
    def __init__(self):
        """Initialize confidence assessor."""
        self.history: deque = deque(maxlen=100)
        self.success_rate = 0.5  # Start neutral
    
    def assess_confidence(
        self,
        context: DecisionContext,
        action_type: str,
        factors: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Assess confidence for a potential action.
        
        Args:
            context: Current decision context
            action_type: Type of action being considered
            factors: Optional confidence factors
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        confidence = 0.5  # Base confidence
        
        # Factor in historical success rate
        confidence *= (0.5 + self.success_rate * 0.5)
        
        # Factor in recent performance
        if context.confidence_history:
            recent_avg = sum(context.confidence_history[-10:]) / len(context.confidence_history[-10:])
            confidence *= (0.7 + recent_avg * 0.3)
        
        # Apply custom factors
        if factors:
            for factor_name, factor_value in factors.items():
                confidence *= (0.8 + factor_value * 0.2)
        
        # Ensure within bounds
        confidence = max(0.0, min(1.0, confidence))
        
        return confidence
    
    def update_from_outcome(self, decision: Decision, success: bool) -> None:
        """
        Update assessor from decision outcome.
        
        Args:
            decision: The decision that was made
            success: Whether it was successful
        """
        self.history.append({
            "decision_id": decision.decision_id,
            "confidence": decision.confidence,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update success rate
        recent_successes = sum(
            1 for h in list(self.history)[-20:]
            if h.get("success", False)
        )
        recent_total = min(len(self.history), 20)
        
        if recent_total > 0:
            self.success_rate = recent_successes / recent_total
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get confidence statistics."""
        if not self.history:
            return {
                "success_rate": self.success_rate,
                "total_decisions": 0,
                "avg_confidence": 0.0
            }
        
        recent_history = list(self.history)[-50:]
        
        avg_confidence = sum(h["confidence"] for h in recent_history) / len(recent_history)
        
        return {
            "success_rate": self.success_rate,
            "total_decisions": len(self.history),
            "avg_confidence": avg_confidence,
            "recent_successes": sum(1 for h in recent_history if h.get("success", False))
        }


class DecisionEngine:
    """Makes decisions about how to respond to situations."""
    
    def __init__(
        self,
        mode: AutonomyMode = AutonomyMode.ACTIVE,
        confidence_threshold: float = 0.6
    ):
        """
        Initialize decision engine.
        
        Args:
            mode: Initial operating mode
            confidence_threshold: Minimum confidence to act
        """
        self.mode = mode
        self.confidence_threshold = confidence_threshold
        self.confidence_assessor = ConfidenceAssessor()
        
        # Decision strategies for each mode
        self.mode_strategies = {
            AutonomyMode.ACTIVE: self._active_strategy,
            AutonomyMode.PASSIVE: self._passive_strategy,
            AutonomyMode.LEARNING: self._learning_strategy,
            AutonomyMode.EXPLORATION: self._exploration_strategy,
            AutonomyMode.SLEEP: self._sleep_strategy,
        }
    
    def make_decision(
        self,
        context: DecisionContext
    ) -> Decision:
        """
        Make a decision based on context and current mode.
        
        Args:
            context: Decision context
            
        Returns:
            Decision object
        """
        # Get strategy for current mode
        strategy = self.mode_strategies.get(
            self.mode,
            self._passive_strategy
        )
        
        # Execute strategy
        decision = strategy(context)
        
        logger.info(
            f"Decision made: {decision.decision_type.value} "
            f"(confidence: {decision.confidence:.2f}, mode: {self.mode.value})"
        )
        
        return decision
    
    def _active_strategy(self, context: DecisionContext) -> Decision:
        """Strategy for active mode."""
        # Proactively respond and suggest
        if context.user_input:
            # User provided input - respond
            confidence = self.confidence_assessor.assess_confidence(
                context, "respond"
            )
            
            if confidence >= self.confidence_threshold:
                return Decision(
                    decision_id=self._generate_decision_id(),
                    decision_type=DecisionType.RESPOND,
                    action="generate_response",
                    confidence=confidence,
                    reasoning="User input requires response",
                    context=context
                )
            else:
                return Decision(
                    decision_id=self._generate_decision_id(),
                    decision_type=DecisionType.DEFER,
                    action="request_clarification",
                    confidence=confidence,
                    reasoning="Confidence too low, need clarification",
                    context=context
                )
        else:
            # No user input - check if should suggest
            confidence = self.confidence_assessor.assess_confidence(
                context, "suggest"
            )
            
            # Randomly suggest based on confidence
            if random.random() < confidence * 0.3:  # 30% of confidence
                return Decision(
                    decision_id=self._generate_decision_id(),
                    decision_type=DecisionType.SUGGEST,
                    action="proactive_suggestion",
                    confidence=confidence,
                    reasoning="Proactive assistance opportunity detected",
                    context=context
                )
            else:
                return Decision(
                    decision_id=self._generate_decision_id(),
                    decision_type=DecisionType.OBSERVE,
                    action="monitor",
                    confidence=1.0,
                    reasoning="Monitoring for opportunities",
                    context=context
                )
    
    def _passive_strategy(self, context: DecisionContext) -> Decision:
        """Strategy for passive mode."""
        # Only respond to direct requests
        if context.user_input:
            confidence = self.confidence_assessor.assess_confidence(
                context, "respond"
            )
            
            return Decision(
                decision_id=self._generate_decision_id(),
                decision_type=DecisionType.RESPOND,
                action="generate_response",
                confidence=confidence,
                reasoning="Responding to direct user request",
                context=context
            )
        else:
            return Decision(
                decision_id=self._generate_decision_id(),
                decision_type=DecisionType.OBSERVE,
                action="wait",
                confidence=1.0,
                reasoning="Passive mode: waiting for user input",
                context=context
            )
    
    def _learning_strategy(self, context: DecisionContext) -> Decision:
        """Strategy for learning mode."""
        # Observe and learn without acting
        confidence = self.confidence_assessor.assess_confidence(
            context, "learn"
        )
        
        return Decision(
            decision_id=self._generate_decision_id(),
            decision_type=DecisionType.LEARN,
            action="observe_and_record",
            confidence=confidence,
            reasoning="Learning mode: observing for patterns",
            context=context
        )
    
    def _exploration_strategy(self, context: DecisionContext) -> Decision:
        """Strategy for exploration mode."""
        # Try new behaviors to learn
        confidence = self.confidence_assessor.assess_confidence(
            context, "explore",
            factors={"exploration_bonus": 0.8}
        )
        
        # Randomly choose between different actions
        exploration_actions = [
            (DecisionType.SUGGEST, "try_new_suggestion"),
            (DecisionType.LEARN, "explore_patterns"),
            (DecisionType.RESPOND, "experimental_response"),
        ]
        
        decision_type, action = random.choice(exploration_actions)
        
        return Decision(
            decision_id=self._generate_decision_id(),
            decision_type=decision_type,
            action=action,
            confidence=confidence,
            reasoning="Exploration mode: trying new behaviors",
            context=context
        )
    
    def _sleep_strategy(self, context: DecisionContext) -> Decision:
        """Strategy for sleep mode."""
        # Minimal activity
        return Decision(
            decision_id=self._generate_decision_id(),
            decision_type=DecisionType.OBSERVE,
            action="minimal_monitoring",
            confidence=1.0,
            reasoning="Sleep mode: minimal activity",
            context=context
        )
    
    def _generate_decision_id(self) -> str:
        """Generate unique decision ID."""
        return f"dec_{datetime.now().timestamp()}_{random.randint(1000, 9999)}"
    
    def update_mode(self, new_mode: AutonomyMode) -> None:
        """Update operating mode."""
        old_mode = self.mode
        self.mode = new_mode
        logger.info(f"Mode changed: {old_mode.value} -> {new_mode.value}")


class ExplorationManager:
    """Manages exploration vs exploitation balance."""
    
    def __init__(
        self,
        initial_epsilon: float = 0.3,
        min_epsilon: float = 0.05,
        decay_rate: float = 0.995
    ):
        """
        Initialize exploration manager.
        
        Args:
            initial_epsilon: Initial exploration rate
            min_epsilon: Minimum exploration rate
            decay_rate: Rate at which exploration decays
        """
        self.epsilon = initial_epsilon
        self.min_epsilon = min_epsilon
        self.decay_rate = decay_rate
        
        self.total_actions = 0
        self.exploration_actions = 0
        self.exploitation_actions = 0
    
    def should_explore(self) -> bool:
        """
        Decide whether to explore or exploit.
        
        Returns:
            True if should explore
        """
        self.total_actions += 1
        
        should_explore = random.random() < self.epsilon
        
        if should_explore:
            self.exploration_actions += 1
        else:
            self.exploitation_actions += 1
        
        # Decay epsilon
        self.epsilon = max(self.min_epsilon, self.epsilon * self.decay_rate)
        
        return should_explore
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get exploration statistics."""
        return {
            "current_epsilon": self.epsilon,
            "total_actions": self.total_actions,
            "exploration_actions": self.exploration_actions,
            "exploitation_actions": self.exploitation_actions,
            "exploration_rate": (
                self.exploration_actions / self.total_actions
                if self.total_actions > 0 else 0.0
            )
        }


class MetaLearningController:
    """Controls meta-learning and self-improvement."""
    
    def __init__(self):
        """Initialize meta-learning controller."""
        self.learning_goals: List[LearningGoal] = []
        self.performance_history: deque = deque(maxlen=1000)
        
        self.meta_metrics = {
            "learning_rate": 0.0,
            "adaptation_speed": 0.0,
            "knowledge_retention": 1.0,
        }
    
    def add_learning_goal(
        self,
        description: str,
        priority: int = 5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LearningGoal:
        """
        Add a new learning goal.
        
        Args:
            description: Description of the goal
            priority: Priority level (1-10)
            metadata: Optional metadata
            
        Returns:
            Created LearningGoal
        """
        goal = LearningGoal(
            goal_id=f"goal_{datetime.now().timestamp()}",
            description=description,
            priority=priority,
            metadata=metadata or {}
        )
        
        self.learning_goals.append(goal)
        logger.info(f"Added learning goal: {description} (priority: {priority})")
        
        return goal
    
    def update_goal_progress(
        self,
        goal_id: str,
        progress: float
    ) -> None:
        """
        Update progress on a learning goal.
        
        Args:
            goal_id: ID of the goal
            progress: Progress value (0.0 to 1.0)
        """
        for goal in self.learning_goals:
            if goal.goal_id == goal_id:
                goal.progress = progress
                
                if progress >= 1.0:
                    goal.completed = True
                    logger.info(f"Learning goal completed: {goal.description}")
                
                break
    
    def get_active_goals(self) -> List[LearningGoal]:
        """Get active (incomplete) learning goals."""
        return [g for g in self.learning_goals if not g.completed]
    
    def analyze_performance_trends(
        self,
        window_size: int = 100
    ) -> Dict[str, float]:
        """
        Analyze recent performance trends.
        
        Args:
            window_size: Number of recent records to analyze
            
        Returns:
            Dictionary with trend metrics
        """
        if not self.performance_history:
            return {
                "trend": 0.0,
                "volatility": 0.0,
                "improvement_rate": 0.0
            }
        
        recent = list(self.performance_history)[-window_size:]
        
        if len(recent) < 2:
            return {
                "trend": 0.0,
                "volatility": 0.0,
                "improvement_rate": 0.0
            }
        
        # Calculate trend
        values = [r["performance"] for r in recent]
        trend = (values[-1] - values[0]) / len(values)
        
        # Calculate volatility (std dev)
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        volatility = variance ** 0.5
        
        # Calculate improvement rate (recent vs older)
        mid_point = len(values) // 2
        older_avg = sum(values[:mid_point]) / mid_point
        recent_avg = sum(values[mid_point:]) / (len(values) - mid_point)
        improvement_rate = (recent_avg - older_avg) / max(older_avg, 0.001)
        
        return {
            "trend": trend,
            "volatility": volatility,
            "improvement_rate": improvement_rate
        }
    
    def record_performance(
        self,
        task: str,
        performance: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a performance measurement.
        
        Args:
            task: Task that was performed
            performance: Performance score (0.0 to 1.0)
            metadata: Optional metadata
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "performance": performance,
            "metadata": metadata or {}
        }
        
        self.performance_history.append(record)
    
    def get_meta_metrics(self) -> Dict[str, float]:
        """Get meta-learning metrics."""
        trends = self.analyze_performance_trends()
        
        # Update meta metrics based on trends
        self.meta_metrics["learning_rate"] = max(0.0, trends["improvement_rate"])
        self.meta_metrics["adaptation_speed"] = 1.0 - trends["volatility"]
        
        return dict(self.meta_metrics)


class AutonomyCore:
    """
    Main autonomy core - the AI consciousness layer.
    
    Manages decision making, mode switching, exploration/exploitation,
    and meta-learning for continuous self-improvement.
    """
    
    def __init__(
        self,
        data_dir: Path,
        initial_mode: AutonomyMode = AutonomyMode.PASSIVE,
        confidence_threshold: float = 0.6
    ):
        """
        Initialize the AutonomyCore.
        
        Args:
            data_dir: Directory for storing autonomy data
            initial_mode: Initial operating mode
            confidence_threshold: Confidence threshold for actions
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Core components
        self.decision_engine = DecisionEngine(
            mode=initial_mode,
            confidence_threshold=confidence_threshold
        )
        self.exploration_manager = ExplorationManager()
        self.meta_learning_controller = MetaLearningController()
        
        # State
        self.current_mode = initial_mode
        self.decision_history: deque = deque(maxlen=1000)
        self.active = False
        
        # Threading for background operations
        self.background_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Statistics
        self.stats = {
            "total_decisions": 0,
            "decisions_by_type": defaultdict(int),
            "mode_changes": 0,
            "successful_actions": 0,
            "failed_actions": 0,
        }
        
        self._load_state()
        
        logger.info(f"AutonomyCore initialized in {initial_mode.value} mode")
    
    def start(self) -> None:
        """Start the autonomy core."""
        if self.active:
            logger.warning("AutonomyCore already active")
            return
        
        self.active = True
        self.stop_event.clear()
        
        # Start background thread
        self.background_thread = threading.Thread(
            target=self._background_loop,
            daemon=True,
            name="AutonomyCoreBackground"
        )
        self.background_thread.start()
        
        logger.info("AutonomyCore started")
    
    def stop(self) -> None:
        """Stop the autonomy core."""
        if not self.active:
            logger.warning("AutonomyCore not active")
            return
        
        logger.info("Stopping AutonomyCore...")
        self.active = False
        self.stop_event.set()
        
        if self.background_thread:
            self.background_thread.join(timeout=5.0)
        
        self._save_state()
        logger.info("AutonomyCore stopped")
    
    def process_situation(
        self,
        context: DecisionContext,
        execute_callback: Optional[Callable[[Decision], bool]] = None
    ) -> Decision:
        """
        Process a situation and make a decision.
        
        Args:
            context: Current decision context
            execute_callback: Optional callback to execute the decision
            
        Returns:
            Decision object
        """
        try:
            # Make decision
            decision = self.decision_engine.make_decision(context)
            
            # Record decision
            self.decision_history.append(decision)
            self.stats["total_decisions"] += 1
            self.stats["decisions_by_type"][decision.decision_type.value] += 1
            
            # Execute if callback provided and decision should be executed
            if execute_callback and self._should_execute(decision):
                try:
                    success = execute_callback(decision)
                    decision.executed = True
                    decision.outcome = "success" if success else "failure"
                    
                    # Update confidence assessor
                    self.decision_engine.confidence_assessor.update_from_outcome(
                        decision, success
                    )
                    
                    # Update stats
                    if success:
                        self.stats["successful_actions"] += 1
                    else:
                        self.stats["failed_actions"] += 1
                    
                    # Record performance for meta-learning
                    self.meta_learning_controller.record_performance(
                        task=decision.action,
                        performance=1.0 if success else 0.0
                    )
                    
                except Exception as e:
                    logger.error(f"Error executing decision: {e}", exc_info=True)
                    decision.outcome = f"error: {str(e)}"
            
            # Periodic state save
            if self.stats["total_decisions"] % 100 == 0:
                self._save_state()
            
            return decision
            
        except Exception as e:
            logger.error(f"Error processing situation: {e}", exc_info=True)
            raise
    
    def _should_execute(self, decision: Decision) -> bool:
        """Determine if a decision should be executed."""
        # Don't execute observations or deferrals
        if decision.decision_type in [DecisionType.OBSERVE, DecisionType.DEFER]:
            return False
        
        # Check confidence threshold
        if decision.confidence < self.decision_engine.confidence_threshold:
            return False
        
        # In learning mode, don't execute
        if self.current_mode == AutonomyMode.LEARNING:
            return False
        
        return True
    
    def change_mode(
        self,
        new_mode: AutonomyMode,
        reason: str = ""
    ) -> None:
        """
        Change operating mode.
        
        Args:
            new_mode: New mode to switch to
            reason: Reason for mode change
        """
        if new_mode == self.current_mode:
            return
        
        old_mode = self.current_mode
        self.current_mode = new_mode
        self.decision_engine.update_mode(new_mode)
        
        self.stats["mode_changes"] += 1
        
        logger.info(
            f"Mode changed: {old_mode.value} -> {new_mode.value} "
            f"(reason: {reason or 'manual'})"
        )
    
    def auto_adjust_mode(self, context: DecisionContext) -> None:
        """
        Automatically adjust mode based on context.
        
        Args:
            context: Current decision context
        """
        # Example heuristics for mode adjustment
        
        # Switch to passive at night
        if context.time_of_day == "night":
            if self.current_mode != AutonomyMode.PASSIVE:
                self.change_mode(AutonomyMode.PASSIVE, "night time")
        
        # Switch to learning if performance is poor
        performance_trends = self.meta_learning_controller.analyze_performance_trends()
        if performance_trends["improvement_rate"] < -0.1:
            if self.current_mode != AutonomyMode.LEARNING:
                self.change_mode(AutonomyMode.LEARNING, "poor performance trend")
        
        # Switch to exploration if stuck
        confidence_stats = self.decision_engine.confidence_assessor.get_statistics()
        if confidence_stats["success_rate"] < 0.3:
            if self.current_mode != AutonomyMode.EXPLORATION:
                self.change_mode(AutonomyMode.EXPLORATION, "low success rate")
    
    def _background_loop(self) -> None:
        """Background loop for periodic tasks."""
        logger.info("Background loop started")
        
        while not self.stop_event.is_set():
            try:
                # Periodic meta-learning analysis
                self._perform_meta_learning()
                
                # Check and update learning goals
                self._update_learning_goals()
                
                # Sleep
                self.stop_event.wait(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in background loop: {e}", exc_info=True)
                self.stop_event.wait(60)
        
        logger.info("Background loop ended")
    
    def _perform_meta_learning(self) -> None:
        """Perform meta-learning analysis."""
        try:
            # Analyze performance trends
            trends = self.meta_learning_controller.analyze_performance_trends()
            
            # Update meta metrics
            meta_metrics = self.meta_learning_controller.get_meta_metrics()
            
            # Log if significant changes
            if abs(trends["improvement_rate"]) > 0.1:
                logger.info(
                    f"Meta-learning: improvement_rate={trends['improvement_rate']:.3f}, "
                    f"learning_rate={meta_metrics['learning_rate']:.3f}"
                )
                
        except Exception as e:
            logger.error(f"Error in meta-learning: {e}")
    
    def _update_learning_goals(self) -> None:
        """Update learning goals progress."""
        try:
            active_goals = self.meta_learning_controller.get_active_goals()
            
            # Update goals based on performance
            for goal in active_goals:
                # Simplified progress update
                # In real implementation, would track specific metrics
                if "metadata" in goal.metadata:
                    goal.progress += 0.01  # Incremental progress
                    
                    if goal.progress >= 1.0:
                        self.meta_learning_controller.update_goal_progress(
                            goal.goal_id, 1.0
                        )
                        
        except Exception as e:
            logger.error(f"Error updating learning goals: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current autonomy core status.
        
        Returns:
            Dictionary with status information
        """
        confidence_stats = self.decision_engine.confidence_assessor.get_statistics()
        exploration_stats = self.exploration_manager.get_statistics()
        meta_metrics = self.meta_learning_controller.get_meta_metrics()
        
        return {
            "active": self.active,
            "mode": self.current_mode.value,
            "statistics": dict(self.stats),
            "confidence": confidence_stats,
            "exploration": exploration_stats,
            "meta_learning": meta_metrics,
            "active_learning_goals": len(
                self.meta_learning_controller.get_active_goals()
            ),
            "recent_decisions": len(self.decision_history)
        }
    
    def get_recent_decisions(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent decisions.
        
        Args:
            limit: Maximum number of decisions to return
            
        Returns:
            List of decision dictionaries
        """
        recent = list(self.decision_history)[-limit:]
        return [d.to_dict() for d in recent]
    
    def _load_state(self) -> None:
        """Load autonomy state from disk."""
        state_file = self.data_dir / "autonomy_state.json"
        
        if not state_file.exists():
            return
        
        try:
            with open(state_file, 'r') as f:
                data = json.load(f)
                self.stats = data.get("stats", self.stats)
                
                # Load mode
                mode_str = data.get("mode", "passive")
                self.current_mode = AutonomyMode(mode_str)
                self.decision_engine.mode = self.current_mode
            
            logger.info("Loaded autonomy state")
        except Exception as e:
            logger.error(f"Error loading state: {e}")
    
    def _save_state(self) -> None:
        """Save autonomy state to disk."""
        state_file = self.data_dir / "autonomy_state.json"
        
        try:
            data = {
                "stats": dict(self.stats),
                "mode": self.current_mode.value,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(state_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving state: {e}")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Initialize autonomy core
    autonomy = AutonomyCore(
        data_dir=Path("./data/autonomy"),
        initial_mode=AutonomyMode.ACTIVE,
        confidence_threshold=0.5
    )
    
    # Add a learning goal
    autonomy.meta_learning_controller.add_learning_goal(
        description="Improve response accuracy for weather queries",
        priority=8
    )
    
    # Create a decision context
    context = DecisionContext(
        user_input="What's the weather like?",
        time_of_day="morning",
        user_activity="active",
        system_state={"cpu_usage": 30.0}
    )
    
    # Process the situation
    def execute_callback(decision: Decision) -> bool:
        print(f"Executing: {decision.action}")
        return True  # Simulate success
    
    decision = autonomy.process_situation(context, execute_callback)
    
    print(f"\nDecision made:")
    print(f"Type: {decision.decision_type.value}")
    print(f"Action: {decision.action}")
    print(f"Confidence: {decision.confidence:.2f}")
    print(f"Reasoning: {decision.reasoning}")
    
    # Get status
    status = autonomy.get_status()
    print(f"\nAutonomy Status:")
    print(f"Mode: {status['mode']}")
    print(f"Total decisions: {status['statistics']['total_decisions']}")
    print(f"Success rate: {status['confidence']['success_rate']:.2%}")
    
    # Start background operations
    # autonomy.start()
    
    print("\nAutonomyCore example completed!")
