"""
Feedback Loop for JARVIS AGI Machine Learning Core.

This module implements RLHF/DPO through explicit and implicit feedback
collection, preference pair generation, and feedback database management.
"""

import json
import logging
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import hashlib
import threading

logger = logging.getLogger(__name__)


@dataclass
class FeedbackEntry:
    """Represents a single feedback entry."""
    feedback_id: str
    interaction_id: str
    user_input: str
    ai_response: str
    feedback_type: str  # 'explicit', 'implicit', 'correction'
    feedback_value: float  # -1.0 to 1.0
    correction: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeedbackEntry":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class PreferencePair:
    """Represents a preference pair for DPO training."""
    pair_id: str
    prompt: str
    chosen_response: str
    rejected_response: str
    chosen_score: float
    rejected_score: float
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_dpo_format(self) -> Dict[str, Any]:
        """Convert to DPO training format."""
        return {
            "prompt": self.prompt,
            "chosen": self.chosen_response,
            "rejected": self.rejected_response,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PreferencePair":
        """Create from dictionary."""
        return cls(**data)


class FeedbackDatabase:
    """SQLite database for storing feedback entries."""
    
    def __init__(self, db_path: Path):
        """
        Initialize feedback database.
        
        Args:
            db_path: Path to SQLite database file
        """
        # Ensure path is absolute to avoid CWD issues
        self.db_path = Path(db_path).resolve()
        
        # Ensure parent directory exists with proper error handling
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"ðŸ“ Feedback database path: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to create database directory: {e}")
            # Fallback to temp directory
            import tempfile
            self.db_path = Path(tempfile.gettempdir()) / "jarvis_feedback.db"
            logger.warning(f"âš ï¸ Using fallback database path: {self.db_path}")
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn: Optional[sqlite3.Connection] = None
        self._db_lock = threading.Lock()  # ðŸ”’ ProteÃ§Ã£o contra escritas simultÃ¢neas
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database schema."""
        try:
            # Test if we can write to this location
            test_file = self.db_path.parent / ".write_test"
            try:
                test_file.touch()
                test_file.unlink()
            except Exception as e:
                logger.warning(f"Cannot write to {self.db_path.parent}: {e}. Using temp directory.")
                import tempfile
                self.db_path = Path(tempfile.gettempdir()) / "jarvis_feedback.db"
                
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            
            cursor = self.conn.cursor()
            
            # Feedback entries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    feedback_id TEXT PRIMARY KEY,
                    interaction_id TEXT NOT NULL,
                    user_input TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    feedback_value REAL NOT NULL,
                    correction TEXT,
                    timestamp TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Preference pairs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS preference_pairs (
                    pair_id TEXT PRIMARY KEY,
                    prompt TEXT NOT NULL,
                    chosen_response TEXT NOT NULL,
                    rejected_response TEXT NOT NULL,
                    chosen_score REAL NOT NULL,
                    rejected_score REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_feedback_type 
                ON feedback(feedback_type)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_feedback_timestamp 
                ON feedback(timestamp)
            """)
            
            with self._db_lock:
                self.conn.commit()
            logger.info(f"Database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}", exc_info=True)
            raise
    
    def add_feedback(self, feedback: FeedbackEntry) -> bool:
        """
        Add a feedback entry to the database.
        
        Args:
            feedback: Feedback entry to add
            
        Returns:
            True if successful
        """
        try:
            with self._db_lock:
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT INTO feedback 
                    (feedback_id, interaction_id, user_input, ai_response, 
                     feedback_type, feedback_value, correction, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    feedback.feedback_id,
                    feedback.interaction_id,
                    feedback.user_input,
                    feedback.ai_response,
                    feedback.feedback_type,
                    feedback.feedback_value,
                    feedback.correction,
                    feedback.timestamp,
                    json.dumps(feedback.metadata)
                ))
                self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error adding feedback: {e}", exc_info=True)
            return False
    
    def add_preference_pair(self, pair: PreferencePair) -> bool:
        """
        Add a preference pair to the database.
        
        Args:
            pair: Preference pair to add
            
        Returns:
            True if successful
        """
        try:
            with self._db_lock:
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT INTO preference_pairs
                    (pair_id, prompt, chosen_response, rejected_response,
                     chosen_score, rejected_score, created_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pair.pair_id,
                    pair.prompt,
                    pair.chosen_response,
                    pair.rejected_response,
                    pair.chosen_score,
                    pair.rejected_score,
                    pair.created_at,
                    json.dumps(pair.metadata)
                ))
                self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error adding preference pair: {e}", exc_info=True)
            return False
    
    def get_feedback_by_interaction_id(self, interaction_id: str) -> Optional[FeedbackEntry]:
        """
        Get the most recent feedback entry for an interaction.

        Args:
            interaction_id: Interaction ID to search for

        Returns:
            FeedbackEntry if found, None otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM feedback
                WHERE interaction_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (interaction_id,))

            row = cursor.fetchone()
            if row:
                return self._row_to_feedback(row)
            return None

        except Exception as e:
            logger.error(f"Error getting feedback by interaction_id: {e}")
            return None

    def update_feedback(self, feedback: FeedbackEntry) -> bool:
        """
        Update an existing feedback entry.

        Args:
            feedback: Feedback entry to update

        Returns:
            True if successful
        """
        try:
            with self._db_lock:
                cursor = self.conn.cursor()
                cursor.execute("""
                    UPDATE feedback
                    SET user_input = ?,
                        ai_response = ?,
                        feedback_type = ?,
                        feedback_value = ?,
                        correction = ?,
                        timestamp = ?,
                        metadata = ?
                    WHERE feedback_id = ?
                """, (
                    feedback.user_input,
                    feedback.ai_response,
                    feedback.feedback_type,
                    feedback.feedback_value,
                    feedback.correction,
                    feedback.timestamp,
                    json.dumps(feedback.metadata),
                    feedback.feedback_id
                ))
                self.conn.commit()
                return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Error updating feedback: {e}", exc_info=True)
            return False

    def get_feedback_by_type(self, feedback_type: str) -> List[FeedbackEntry]:
        """Get all feedback of a specific type."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM feedback WHERE feedback_type = ?
            """, (feedback_type,))
            
            rows = cursor.fetchall()
            return [self._row_to_feedback(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting feedback: {e}")
            return []
    
    def get_all_preference_pairs(self) -> List[PreferencePair]:
        """Get all preference pairs."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM preference_pairs")
            
            rows = cursor.fetchall()
            return [self._row_to_preference_pair(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting preference pairs: {e}")
            return []
    
    def _row_to_feedback(self, row: sqlite3.Row) -> FeedbackEntry:
        """Convert database row to FeedbackEntry."""
        metadata = json.loads(row['metadata']) if row['metadata'] else {}
        return FeedbackEntry(
            feedback_id=row['feedback_id'],
            interaction_id=row['interaction_id'],
            user_input=row['user_input'],
            ai_response=row['ai_response'],
            feedback_type=row['feedback_type'],
            feedback_value=row['feedback_value'],
            correction=row['correction'],
            timestamp=row['timestamp'],
            metadata=metadata
        )
    
    def _row_to_preference_pair(self, row: sqlite3.Row) -> PreferencePair:
        """Convert database row to PreferencePair."""
        metadata = json.loads(row['metadata']) if row['metadata'] else {}
        return PreferencePair(
            pair_id=row['pair_id'],
            prompt=row['prompt'],
            chosen_response=row['chosen_response'],
            rejected_response=row['rejected_response'],
            chosen_score=row['chosen_score'],
            rejected_score=row['rejected_score'],
            created_at=row['created_at'],
            metadata=metadata
        )
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


class FeedbackLoop:
    """
    Feedback Loop for RLHF/DPO training.
    
    Captures explicit and implicit feedback, generates preference pairs,
    and prepares datasets for reinforcement learning from human feedback.
    """
    
    def __init__(self, data_dir: Path):
        """
        Initialize the FeedbackLoop.
        
        Args:
            data_dir: Directory for storing feedback data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        db_path = self.data_dir / "feedback.db"
        self.database = FeedbackDatabase(db_path)
        
        # Statistics
        self.stats = {
            "total_feedback": 0,
            "explicit_feedback": 0,
            "implicit_feedback": 0,
            "corrections": 0,
            "preference_pairs": 0,
            "positive_feedback": 0,
            "negative_feedback": 0,
        }
        
        self._load_stats()
        
        logger.info("FeedbackLoop initialized")
    
    def _generate_id(self, text: str) -> str:
        """Generate a unique ID from text."""
        return hashlib.sha256(text.encode()).hexdigest()[:24]
    
    def record_explicit_feedback(
        self,
        interaction_id: str,
        user_input: str,
        ai_response: str,
        rating: float,
        correction: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> FeedbackEntry:
        """
        Record explicit user feedback.
        
        Args:
            interaction_id: ID of the interaction
            user_input: User's input
            ai_response: AI's response
            rating: Feedback rating (-1.0 to 1.0)
            correction: Optional correction from user
            metadata: Optional additional metadata
            
        Returns:
            Created FeedbackEntry
        """
        try:
            # Normalize rating to -1.0 to 1.0
            rating = max(-1.0, min(1.0, rating))
            
            feedback_type = "correction" if correction else "explicit"
            
            feedback_id = self._generate_id(
                f"{interaction_id}_{rating}_{datetime.now().isoformat()}"
            )
            
            feedback = FeedbackEntry(
                feedback_id=feedback_id,
                interaction_id=interaction_id,
                user_input=user_input,
                ai_response=ai_response,
                feedback_type=feedback_type,
                feedback_value=rating,
                correction=correction,
                metadata=metadata or {}
            )
            
            # Save to database
            self.database.add_feedback(feedback)
            
            # Update statistics
            self.stats["total_feedback"] += 1
            self.stats["explicit_feedback"] += 1
            if correction:
                self.stats["corrections"] += 1
            if rating > 0:
                self.stats["positive_feedback"] += 1
            elif rating < 0:
                self.stats["negative_feedback"] += 1
            
            self._save_stats()
            
            logger.info(f"Recorded explicit feedback: {feedback_type} (rating: {rating})")
            
            # Generate preference pair if correction provided
            if correction:
                self._generate_preference_pair_from_correction(
                    user_input, ai_response, correction, rating
                )
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error recording explicit feedback: {e}", exc_info=True)
            raise
    
    def record_implicit_feedback(
        self,
        interaction_id: str,
        user_input: str,
        ai_response: str,
        success: bool,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> FeedbackEntry:
        """
        Record implicit feedback based on interaction success.
        
        Args:
            interaction_id: ID of the interaction
            user_input: User's input
            ai_response: AI's response
            success: Whether the interaction was successful
            confidence: Confidence in the implicit signal (0.0 to 1.0)
            metadata: Optional additional metadata
            
        Returns:
            Created FeedbackEntry
        """
        try:
            # Convert success to rating
            rating = confidence if success else -confidence
            
            feedback_id = self._generate_id(
                f"{interaction_id}_implicit_{datetime.now().isoformat()}"
            )
            
            feedback = FeedbackEntry(
                feedback_id=feedback_id,
                interaction_id=interaction_id,
                user_input=user_input,
                ai_response=ai_response,
                feedback_type="implicit",
                feedback_value=rating,
                metadata=metadata or {"success": success, "confidence": confidence}
            )
            
            # Save to database
            self.database.add_feedback(feedback)
            
            # Update statistics
            self.stats["total_feedback"] += 1
            self.stats["implicit_feedback"] += 1
            if rating > 0:
                self.stats["positive_feedback"] += 1
            elif rating < 0:
                self.stats["negative_feedback"] += 1
            
            self._save_stats()
            
            logger.debug(f"Recorded implicit feedback (success: {success}, confidence: {confidence})")
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error recording implicit feedback: {e}", exc_info=True)
            raise
    
    def _generate_preference_pair_from_correction(
        self,
        user_input: str,
        rejected_response: str,
        chosen_response: str,
        rating: float
    ) -> PreferencePair:
        """
        Generate a preference pair from a correction.
        
        Args:
            user_input: The user's input
            rejected_response: The AI's original (rejected) response
            chosen_response: The user's correction (chosen) response
            rating: Feedback rating
            
        Returns:
            Created PreferencePair
        """
        try:
            pair_id = self._generate_id(
                f"{user_input}_{chosen_response}_{datetime.now().isoformat()}"
            )
            
            pair = PreferencePair(
                pair_id=pair_id,
                prompt=user_input,
                chosen_response=chosen_response,
                rejected_response=rejected_response,
                chosen_score=abs(rating),  # Use absolute value for chosen
                rejected_score=-abs(rating),  # Negative for rejected
                metadata={"source": "correction"}
            )
            
            # Save to database
            self.database.add_preference_pair(pair)
            
            # Update statistics
            self.stats["preference_pairs"] += 1
            self._save_stats()
            
            logger.info(f"Generated preference pair from correction")
            
            return pair
            
        except Exception as e:
            logger.error(f"Error generating preference pair: {e}", exc_info=True)
            raise
    
    def generate_preference_pairs_from_ratings(
        self,
        min_score_difference: float = 0.3
    ) -> List[PreferencePair]:
        """
        Generate preference pairs from feedback ratings.
        
        Groups responses to similar prompts and creates pairs
        based on rating differences.
        
        Args:
            min_score_difference: Minimum score difference to create pair
            
        Returns:
            List of generated PreferencePairs
        """
        try:
            logger.info("Generating preference pairs from ratings")
            
            # Get all feedback entries
            all_feedback = (
                self.database.get_feedback_by_type("explicit") +
                self.database.get_feedback_by_type("implicit")
            )
            
            # Group by similar prompts (simplified: exact match)
            prompt_groups = defaultdict(list)
            for feedback in all_feedback:
                prompt_groups[feedback.user_input].append(feedback)
            
            pairs = []
            
            for prompt, feedback_list in prompt_groups.items():
                # Sort by rating
                sorted_feedback = sorted(
                    feedback_list,
                    key=lambda f: f.feedback_value,
                    reverse=True
                )
                
                # Create pairs from high vs low rated responses
                for i in range(len(sorted_feedback)):
                    for j in range(i + 1, len(sorted_feedback)):
                        chosen = sorted_feedback[i]
                        rejected = sorted_feedback[j]
                        
                        score_diff = chosen.feedback_value - rejected.feedback_value
                        
                        if score_diff >= min_score_difference:
                            pair_id = self._generate_id(
                                f"{prompt}_{chosen.feedback_id}_{rejected.feedback_id}"
                            )
                            
                            pair = PreferencePair(
                                pair_id=pair_id,
                                prompt=prompt,
                                chosen_response=chosen.ai_response,
                                rejected_response=rejected.ai_response,
                                chosen_score=chosen.feedback_value,
                                rejected_score=rejected.feedback_value,
                                metadata={
                                    "source": "rating_comparison",
                                    "score_difference": score_diff
                                }
                            )
                            
                            self.database.add_preference_pair(pair)
                            pairs.append(pair)
            
            # Update statistics
            self.stats["preference_pairs"] += len(pairs)
            self._save_stats()
            
            logger.info(f"Generated {len(pairs)} preference pairs from ratings")
            return pairs
            
        except Exception as e:
            logger.error(f"Error generating preference pairs: {e}", exc_info=True)
            return []
    
    def export_dpo_dataset(
        self,
        output_path: Path,
        min_pairs: int = 10
    ) -> int:
        """
        Export preference pairs as DPO training dataset.
        
        Args:
            output_path: Path to save the dataset
            min_pairs: Minimum number of pairs to export
            
        Returns:
            Number of pairs exported
        """
        try:
            pairs = self.database.get_all_preference_pairs()
            
            if len(pairs) < min_pairs:
                logger.warning(
                    f"Not enough preference pairs ({len(pairs)}/{min_pairs}), "
                    "generating more from ratings"
                )
                self.generate_preference_pairs_from_ratings()
                pairs = self.database.get_all_preference_pairs()
            
            # Convert to DPO format
            dpo_data = [pair.to_dpo_format() for pair in pairs]
            
            # Save to file
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for item in dpo_data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
            
            logger.info(f"Exported {len(dpo_data)} preference pairs to {output_path}")
            return len(dpo_data)
            
        except Exception as e:
            logger.error(f"Error exporting DPO dataset: {e}", exc_info=True)
            raise
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """
        Get feedback statistics.
        
        Returns:
            Dictionary with statistics
        """
        stats = dict(self.stats)
        
        # Calculate additional metrics
        if stats["total_feedback"] > 0:
            stats["positive_ratio"] = (
                stats["positive_feedback"] / stats["total_feedback"]
            )
            stats["correction_ratio"] = (
                stats["corrections"] / stats["total_feedback"]
            )
        else:
            stats["positive_ratio"] = 0.0
            stats["correction_ratio"] = 0.0
        
        return stats
    
    def get_top_corrections(self, limit: int = 10) -> List[FeedbackEntry]:
        """
        Get top corrections by rating.
        
        Args:
            limit: Maximum number of corrections to return
            
        Returns:
            List of FeedbackEntry objects
        """
        corrections = self.database.get_feedback_by_type("correction")
        sorted_corrections = sorted(
            corrections,
            key=lambda c: abs(c.feedback_value),
            reverse=True
        )
        return sorted_corrections[:limit]
    
    def analyze_feedback_trends(
        self,
        time_window_days: int = 7
    ) -> Dict[str, Any]:
        """
        Analyze feedback trends over time.
        
        Args:
            time_window_days: Number of days to analyze
            
        Returns:
            Dictionary with trend analysis
        """
        try:
            # This is a simplified version
            # In a real implementation, would query database with date filtering
            
            all_feedback = (
                self.database.get_feedback_by_type("explicit") +
                self.database.get_feedback_by_type("implicit") +
                self.database.get_feedback_by_type("correction")
            )
            
            # Group by day
            daily_stats = defaultdict(lambda: {
                "count": 0,
                "positive": 0,
                "negative": 0,
                "avg_rating": 0.0
            })
            
            for feedback in all_feedback:
                date = feedback.timestamp.split('T')[0]
                daily_stats[date]["count"] += 1
                
                if feedback.feedback_value > 0:
                    daily_stats[date]["positive"] += 1
                elif feedback.feedback_value < 0:
                    daily_stats[date]["negative"] += 1
                
                # Running average
                current_avg = daily_stats[date]["avg_rating"]
                current_count = daily_stats[date]["count"]
                daily_stats[date]["avg_rating"] = (
                    (current_avg * (current_count - 1) + feedback.feedback_value) / current_count
                )
            
            return {
                "daily_statistics": dict(daily_stats),
                "total_days": len(daily_stats)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing feedback trends: {e}", exc_info=True)
            return {}
    
    def _load_stats(self) -> None:
        """Load statistics from file."""
        stats_file = self.data_dir / "feedback_stats.json"
        
        if not stats_file.exists():
            return
        
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                self.stats = json.load(f)
            logger.info("Loaded feedback statistics")
        except Exception as e:
            logger.error(f"Error loading stats: {e}")
    
    def _save_stats(self) -> None:
        """Save statistics to file."""
        stats_file = self.data_dir / "feedback_stats.json"
        
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving stats: {e}")
    
    def close(self) -> None:
        """Close the feedback loop and cleanup resources."""
        self._save_stats()
        self.database.close()
        logger.info("FeedbackLoop closed")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Initialize feedback loop
    feedback_loop = FeedbackLoop(data_dir=Path("./data/feedback"))
    
    # Record explicit feedback
    feedback_loop.record_explicit_feedback(
        interaction_id="int_001",
        user_input="What is the weather?",
        ai_response="I cannot check the weather.",
        rating=-0.5,
        correction="Let me check the weather API for you. The current temperature is 72Â°F.",
        metadata={"category": "weather"}
    )
    
    # Record implicit feedback
    feedback_loop.record_implicit_feedback(
        interaction_id="int_002",
        user_input="Open Chrome",
        ai_response="Opening Google Chrome.",
        success=True,
        confidence=0.95,
        metadata={"category": "command"}
    )
    
    # Generate preference pairs
    pairs = feedback_loop.generate_preference_pairs_from_ratings()
    print(f"\nGenerated {len(pairs)} preference pairs")
    
    # Export DPO dataset
    feedback_loop.export_dpo_dataset(
        output_path=Path("./data/feedback/dpo_dataset.jsonl"),
        min_pairs=1
    )
    
    # Get statistics
    stats = feedback_loop.get_feedback_statistics()
    print(f"\nFeedback Statistics:")
    print(f"Total feedback: {stats['total_feedback']}")
    print(f"Explicit: {stats['explicit_feedback']}")
    print(f"Implicit: {stats['implicit_feedback']}")
    print(f"Corrections: {stats['corrections']}")
    print(f"Preference pairs: {stats['preference_pairs']}")
    print(f"Positive ratio: {stats['positive_ratio']:.2%}")
    
    # Close
    feedback_loop.close()
    
    print("\nFeedbackLoop example completed!")
