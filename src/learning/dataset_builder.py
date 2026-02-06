"""
Dataset Builder for JARVIS AGI Machine Learning Core.

This module handles logging, formatting, and exporting user-AI interactions
for model fine-tuning. Supports multiple formats (Alpaca, ShareGPT, Instruct)
and includes quality filtering, categorization, and statistics.
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field, asdict
from collections import defaultdict, Counter
import hashlib
import re

try:
    import jsonlines
except ImportError:
    jsonlines = None

logger = logging.getLogger(__name__)


@dataclass
class InteractionMetadata:
    """Metadata for a single interaction."""
    timestamp: str
    session_id: str
    user_id: str = "default_user"
    category: str = "chat"
    success: bool = True
    confidence: float = 1.0
    latency_ms: float = 0.0
    tokens_used: int = 0
    context_length: int = 0
    model_used: str = "unknown"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Interaction:
    """Represents a single user-AI interaction."""
    interaction_id: str
    user_input: str
    ai_response: str
    metadata: InteractionMetadata
    quality_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "interaction_id": self.interaction_id,
            "user_input": self.user_input,
            "ai_response": self.ai_response,
            "metadata": asdict(self.metadata),
            "quality_score": self.quality_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Interaction":
        """Create from dictionary."""
        metadata_dict = data.get("metadata", {})
        metadata = InteractionMetadata(**metadata_dict)
        return cls(
            interaction_id=data["interaction_id"],
            user_input=data["user_input"],
            ai_response=data["ai_response"],
            metadata=metadata,
            quality_score=data.get("quality_score", 0.0)
        )


class CategoryDetector:
    """Detects interaction categories based on content analysis."""
    
    # Category patterns
    COMMAND_PATTERNS = [
        r'\b(open|close|start|stop|run|execute|launch|kill|restart)\b',
        r'\b(create|delete|move|copy|rename|find|search)\b',
        r'\b(play|pause|volume|mute|next|previous)\b',
        r'\b(set|get|show|display|list|check)\b',
    ]
    
    QUESTION_PATTERNS = [
        r'\bwhat\b', r'\bwhen\b', r'\bwhere\b', r'\bwho\b', r'\bwhy\b', r'\bhow\b',
        r'\?$', r'\bcan you\b', r'\bshould\b', r'\bwould\b', r'\bcould\b',
        r'\bis there\b', r'\bare there\b', r'\bdoes\b', r'\bdo you\b',
    ]
    
    CODE_PATTERNS = [
        r'```', r'\bdef\b', r'\bclass\b', r'\bfunction\b', r'\bimport\b',
        r'\breturn\b', r'\bif\b.*\belse\b', r'\bfor\b.*\bin\b',
        r'\bwhile\b', r'\btry\b.*\bexcept\b', r'[{}\[\]();]',
    ]
    
    @classmethod
    def detect_category(cls, user_input: str, ai_response: str) -> str:
        """
        Detect the category of an interaction.
        
        Args:
            user_input: User's input text
            ai_response: AI's response text
            
        Returns:
            Category string: 'command', 'question', 'code', or 'chat'
        """
        combined_text = f"{user_input} {ai_response}".lower()
        
        # Check for code
        code_score = sum(
            1 for pattern in cls.CODE_PATTERNS
            if re.search(pattern, combined_text, re.IGNORECASE)
        )
        if code_score >= 2:
            return "code"
        
        # Check for commands
        command_score = sum(
            1 for pattern in cls.COMMAND_PATTERNS
            if re.search(pattern, user_input.lower())
        )
        if command_score >= 1 and len(user_input.split()) <= 10:
            return "command"
        
        # Check for questions
        question_score = sum(
            1 for pattern in cls.QUESTION_PATTERNS
            if re.search(pattern, user_input.lower())
        )
        if question_score >= 1:
            return "question"
        
        return "chat"


class QualityFilter:
    """Filters interactions based on quality metrics."""
    
    MIN_INPUT_LENGTH = 3
    MIN_RESPONSE_LENGTH = 10
    MAX_INPUT_LENGTH = 4096
    MAX_RESPONSE_LENGTH = 8192
    MIN_QUALITY_SCORE = 0.3
    
    # Patterns that indicate low quality
    LOW_QUALITY_PATTERNS = [
        r'^(um+|uh+|hmm+|err+)$',
        r'^(ok|okay|yes|no|k|y|n)$',
        r'^[.!?]+$',
        r'^\s*$',
    ]
    
    @classmethod
    def calculate_quality_score(cls, interaction: Interaction) -> float:
        """
        Calculate quality score for an interaction.
        
        Args:
            interaction: The interaction to score
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        score = 1.0
        user_input = interaction.user_input.strip()
        ai_response = interaction.ai_response.strip()
        
        # Length checks
        if len(user_input) < cls.MIN_INPUT_LENGTH:
            score -= 0.4
        if len(ai_response) < cls.MIN_RESPONSE_LENGTH:
            score -= 0.4
        
        if len(user_input) > cls.MAX_INPUT_LENGTH:
            score -= 0.2
        if len(ai_response) > cls.MAX_RESPONSE_LENGTH:
            score -= 0.2
        
        # Low quality pattern checks
        for pattern in cls.LOW_QUALITY_PATTERNS:
            if re.match(pattern, user_input.lower()):
                score -= 0.3
            if re.match(pattern, ai_response.lower()):
                score -= 0.3
        
        # Success/failure impact
        if not interaction.metadata.success:
            score -= 0.2
        
        # Confidence impact
        score *= interaction.metadata.confidence
        
        # Response diversity (penalize repetitive responses)
        words = ai_response.lower().split()
        if len(words) > 5:
            unique_ratio = len(set(words)) / len(words)
            score *= unique_ratio
        
        return max(0.0, min(1.0, score))
    
    @classmethod
    def should_include(cls, interaction: Interaction) -> bool:
        """
        Determine if interaction should be included in dataset.
        
        Args:
            interaction: The interaction to evaluate
            
        Returns:
            True if interaction passes quality filters
        """
        if interaction.quality_score < cls.MIN_QUALITY_SCORE:
            return False
        
        user_input = interaction.user_input.strip()
        ai_response = interaction.ai_response.strip()
        
        if len(user_input) < cls.MIN_INPUT_LENGTH:
            return False
        if len(ai_response) < cls.MIN_RESPONSE_LENGTH:
            return False
        
        return True


class DatasetBuilder:
    """
    Main dataset builder class for JARVIS AGI.
    
    Handles logging, formatting, and exporting of user-AI interactions
    for model fine-tuning.
    """
    
    def __init__(
        self,
        data_dir: Path,
        max_interactions: int = 100000,
        auto_categorize: bool = True,
        quality_filtering: bool = True
    ):
        """
        Initialize the DatasetBuilder.
        
        Args:
            data_dir: Directory to store interaction data
            max_interactions: Maximum number of interactions to keep in memory
            auto_categorize: Whether to automatically categorize interactions
            quality_filtering: Whether to filter low-quality interactions
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.interactions_file = self.data_dir / "interactions.jsonl"
        self.stats_file = self.data_dir / "statistics.json"
        
        self.max_interactions = max_interactions
        self.auto_categorize = auto_categorize
        self.quality_filtering = quality_filtering
        
        self.interactions: List[Interaction] = []
        self.session_id = self._generate_session_id()
        
        self.category_detector = CategoryDetector()
        self.quality_filter = QualityFilter()
        
        # Statistics
        self.stats = {
            "total_interactions": 0,
            "successful_interactions": 0,
            "failed_interactions": 0,
            "categories": defaultdict(int),
            "avg_quality_score": 0.0,
            "total_tokens": 0,
            "sessions": set(),
            "date_range": {"start": None, "end": None},
        }
        
        self._load_interactions()
        
        logger.info(f"DatasetBuilder initialized: {len(self.interactions)} interactions loaded")
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:16]
    
    def _generate_interaction_id(self, user_input: str, timestamp: str) -> str:
        """Generate a unique interaction ID."""
        data = f"{user_input}_{timestamp}_{self.session_id}"
        return hashlib.sha256(data.encode()).hexdigest()[:24]
    
    def log_interaction(
        self,
        user_input: str,
        ai_response: str,
        success: bool = True,
        confidence: float = 1.0,
        latency_ms: float = 0.0,
        tokens_used: int = 0,
        model_used: str = "unknown",
        tags: Optional[List[str]] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Interaction:
        """
        Log a new user-AI interaction.
        
        Args:
            user_input: User's input text
            ai_response: AI's response text
            success: Whether the interaction was successful
            confidence: Confidence score (0.0 to 1.0)
            latency_ms: Response latency in milliseconds
            tokens_used: Number of tokens used
            model_used: Name of the model used
            tags: Optional tags for categorization
            additional_metadata: Additional metadata to store
            
        Returns:
            The created Interaction object
        """
        try:
            timestamp = datetime.now().isoformat()
            
            # Auto-categorize
            category = "chat"
            if self.auto_categorize:
                category = self.category_detector.detect_category(user_input, ai_response)
            
            # Create metadata
            metadata = InteractionMetadata(
                timestamp=timestamp,
                session_id=self.session_id,
                category=category,
                success=success,
                confidence=confidence,
                latency_ms=latency_ms,
                tokens_used=tokens_used,
                context_length=len(user_input) + len(ai_response),
                model_used=model_used,
                tags=tags or [],
                metadata=additional_metadata or {}
            )
            
            # Create interaction
            interaction_id = self._generate_interaction_id(user_input, timestamp)
            interaction = Interaction(
                interaction_id=interaction_id,
                user_input=user_input,
                ai_response=ai_response,
                metadata=metadata
            )
            
            # Calculate quality score
            interaction.quality_score = self.quality_filter.calculate_quality_score(interaction)
            
            # Add to memory if quality check passes
            if not self.quality_filtering or self.quality_filter.should_include(interaction):
                self.interactions.append(interaction)
                self._update_statistics(interaction)
                self._save_interaction(interaction)
                
                # Maintain max interactions limit
                if len(self.interactions) > self.max_interactions:
                    self.interactions = self.interactions[-self.max_interactions:]
                
                logger.debug(
                    f"Logged interaction {interaction_id[:8]}... "
                    f"(category: {category}, quality: {interaction.quality_score:.2f})"
                )
            else:
                logger.debug(f"Filtered out low-quality interaction (score: {interaction.quality_score:.2f})")
            
            return interaction
            
        except Exception as e:
            logger.error(f"Error logging interaction: {e}", exc_info=True)
            raise
    
    def _save_interaction(self, interaction: Interaction) -> None:
        """Save interaction to disk."""
        try:
            if jsonlines:
                with jsonlines.open(self.interactions_file, mode='a') as writer:
                    writer.write(interaction.to_dict())
            else:
                with open(self.interactions_file, 'a') as f:
                    f.write(json.dumps(interaction.to_dict()) + '\n')
        except Exception as e:
            logger.error(f"Error saving interaction: {e}", exc_info=True)
    
    def _load_interactions(self) -> None:
        """Load interactions from disk."""
        if not self.interactions_file.exists():
            return
        
        try:
            loaded_count = 0
            if jsonlines:
                with jsonlines.open(self.interactions_file) as reader:
                    for obj in reader:
                        interaction = Interaction.from_dict(obj)
                        self.interactions.append(interaction)
                        self._update_statistics(interaction, loading=True)
                        loaded_count += 1
            else:
                with open(self.interactions_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            obj = json.loads(line)
                            interaction = Interaction.from_dict(obj)
                            self.interactions.append(interaction)
                            self._update_statistics(interaction, loading=True)
                            loaded_count += 1
            
            # Keep only recent interactions if over limit
            if len(self.interactions) > self.max_interactions:
                self.interactions = self.interactions[-self.max_interactions:]
            
            logger.info(f"Loaded {loaded_count} interactions from disk")
            
        except Exception as e:
            logger.error(f"Error loading interactions: {e}", exc_info=True)
    
    def _update_statistics(self, interaction: Interaction, loading: bool = False) -> None:
        """Update statistics with new interaction."""
        if not loading:
            self.stats["total_interactions"] += 1
        
        if interaction.metadata.success:
            self.stats["successful_interactions"] += 1
        else:
            self.stats["failed_interactions"] += 1
        
        self.stats["categories"][interaction.metadata.category] += 1
        self.stats["total_tokens"] += interaction.metadata.tokens_used
        self.stats["sessions"].add(interaction.metadata.session_id)
        
        # Update date range
        timestamp = interaction.metadata.timestamp
        if self.stats["date_range"]["start"] is None:
            self.stats["date_range"]["start"] = timestamp
        self.stats["date_range"]["end"] = timestamp
        
        # Update average quality score
        total = self.stats["total_interactions"]
        if total > 0:
            current_avg = self.stats["avg_quality_score"]
            new_score = interaction.quality_score
            self.stats["avg_quality_score"] = (current_avg * (total - 1) + new_score) / total
    
    def to_alpaca_format(
        self,
        interactions: Optional[List[Interaction]] = None,
        instruction_prefix: str = ""
    ) -> List[Dict[str, str]]:
        """
        Convert interactions to Alpaca format.
        
        Format:
        {
            "instruction": "...",
            "input": "",
            "output": "..."
        }
        
        Args:
            interactions: List of interactions to convert (uses all if None)
            instruction_prefix: Optional prefix for instructions
            
        Returns:
            List of dictionaries in Alpaca format
        """
        if interactions is None:
            interactions = self.interactions
        
        alpaca_data = []
        for interaction in interactions:
            if not self.quality_filter.should_include(interaction):
                continue
            
            instruction = interaction.user_input
            if instruction_prefix:
                instruction = f"{instruction_prefix} {instruction}"
            
            alpaca_data.append({
                "instruction": instruction,
                "input": "",
                "output": interaction.ai_response
            })
        
        logger.info(f"Converted {len(alpaca_data)} interactions to Alpaca format")
        return alpaca_data
    
    def to_sharegpt_format(
        self,
        interactions: Optional[List[Interaction]] = None,
        system_message: str = "You are JARVIS, a helpful AI assistant."
    ) -> List[Dict[str, Any]]:
        """
        Convert interactions to ShareGPT format.
        
        Format:
        {
            "conversations": [
                {"from": "system", "value": "..."},
                {"from": "human", "value": "..."},
                {"from": "gpt", "value": "..."}
            ]
        }
        
        Args:
            interactions: List of interactions to convert (uses all if None)
            system_message: System message to include
            
        Returns:
            List of dictionaries in ShareGPT format
        """
        if interactions is None:
            interactions = self.interactions
        
        sharegpt_data = []
        for interaction in interactions:
            if not self.quality_filter.should_include(interaction):
                continue
            
            conversation = {
                "conversations": [
                    {"from": "system", "value": system_message},
                    {"from": "human", "value": interaction.user_input},
                    {"from": "gpt", "value": interaction.ai_response}
                ]
            }
            sharegpt_data.append(conversation)
        
        logger.info(f"Converted {len(sharegpt_data)} interactions to ShareGPT format")
        return sharegpt_data
    
    def to_instruct_format(
        self,
        interactions: Optional[List[Interaction]] = None,
        template: str = "<|user|>\n{input}\n<|assistant|>\n{output}\n<|end|>"
    ) -> List[Dict[str, str]]:
        """
        Convert interactions to instruction-following format.
        
        Args:
            interactions: List of interactions to convert (uses all if None)
            template: Format template with {input} and {output} placeholders
            
        Returns:
            List of dictionaries with formatted text
        """
        if interactions is None:
            interactions = self.interactions
        
        instruct_data = []
        for interaction in interactions:
            if not self.quality_filter.should_include(interaction):
                continue
            
            text = template.format(
                input=interaction.user_input,
                output=interaction.ai_response
            )
            
            instruct_data.append({
                "text": text,
                "category": interaction.metadata.category,
                "quality_score": interaction.quality_score
            })
        
        logger.info(f"Converted {len(instruct_data)} interactions to Instruct format")
        return instruct_data
    
    def export_dataset(
        self,
        output_path: Path,
        format: str = "alpaca",
        min_quality_score: Optional[float] = None,
        categories: Optional[List[str]] = None,
        date_range: Optional[Tuple[str, str]] = None,
        max_samples: Optional[int] = None
    ) -> int:
        """
        Export dataset to file with filtering options.
        
        Args:
            output_path: Path to save the dataset
            format: Output format ('alpaca', 'sharegpt', 'instruct')
            min_quality_score: Minimum quality score filter
            categories: List of categories to include
            date_range: Tuple of (start_date, end_date) in ISO format
            max_samples: Maximum number of samples to export
            
        Returns:
            Number of samples exported
        """
        try:
            # Filter interactions
            filtered = self._filter_interactions(
                min_quality_score=min_quality_score,
                categories=categories,
                date_range=date_range
            )
            
            if max_samples and len(filtered) > max_samples:
                filtered = filtered[:max_samples]
            
            # Convert to requested format
            if format == "alpaca":
                data = self.to_alpaca_format(filtered)
            elif format == "sharegpt":
                data = self.to_sharegpt_format(filtered)
            elif format == "instruct":
                data = self.to_instruct_format(filtered)
            else:
                raise ValueError(f"Unknown format: {format}")
            
            # Save to file
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if output_path.suffix == '.jsonl':
                if jsonlines:
                    with jsonlines.open(output_path, mode='w') as writer:
                        for item in data:
                            writer.write(item)
                else:
                    with open(output_path, 'w') as f:
                        for item in data:
                            f.write(json.dumps(item) + '\n')
            else:
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=2)
            
            logger.info(f"Exported {len(data)} samples to {output_path} ({format} format)")
            return len(data)
            
        except Exception as e:
            logger.error(f"Error exporting dataset: {e}", exc_info=True)
            raise
    
    def _filter_interactions(
        self,
        min_quality_score: Optional[float] = None,
        categories: Optional[List[str]] = None,
        date_range: Optional[Tuple[str, str]] = None
    ) -> List[Interaction]:
        """Filter interactions based on criteria."""
        filtered = self.interactions
        
        if min_quality_score is not None:
            filtered = [i for i in filtered if i.quality_score >= min_quality_score]
        
        if categories:
            filtered = [i for i in filtered if i.metadata.category in categories]
        
        if date_range:
            start_date, end_date = date_range
            filtered = [
                i for i in filtered
                if start_date <= i.metadata.timestamp <= end_date
            ]
        
        return filtered
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get dataset statistics.
        
        Returns:
            Dictionary containing various statistics
        """
        stats = dict(self.stats)
        stats["sessions"] = len(self.stats["sessions"])
        stats["categories"] = dict(self.stats["categories"])
        
        # Calculate additional metrics
        if stats["total_interactions"] > 0:
            stats["success_rate"] = (
                stats["successful_interactions"] / stats["total_interactions"]
            )
            stats["avg_tokens_per_interaction"] = (
                stats["total_tokens"] / stats["total_interactions"]
            )
        else:
            stats["success_rate"] = 0.0
            stats["avg_tokens_per_interaction"] = 0.0
        
        # Category distribution
        if stats["categories"]:
            total = sum(stats["categories"].values())
            stats["category_distribution"] = {
                cat: count / total for cat, count in stats["categories"].items()
            }
        
        # Quality score distribution
        quality_scores = [i.quality_score for i in self.interactions]
        if quality_scores:
            stats["quality_distribution"] = {
                "min": min(quality_scores),
                "max": max(quality_scores),
                "median": sorted(quality_scores)[len(quality_scores) // 2]
            }
        
        return stats
    
    def save_statistics(self) -> None:
        """Save statistics to file."""
        try:
            stats = self.get_statistics()
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
            logger.info(f"Statistics saved to {self.stats_file}")
        except Exception as e:
            logger.error(f"Error saving statistics: {e}", exc_info=True)
    
    def clear_old_interactions(self, days: int = 30) -> int:
        """
        Clear interactions older than specified days.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of interactions removed
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            original_count = len(self.interactions)
            self.interactions = [
                i for i in self.interactions
                if i.metadata.timestamp >= cutoff_date
            ]
            removed_count = original_count - len(self.interactions)
            
            logger.info(f"Removed {removed_count} interactions older than {days} days")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error clearing old interactions: {e}", exc_info=True)
            return 0
    
    def get_interactions_by_category(self, category: str) -> List[Interaction]:
        """Get all interactions of a specific category."""
        return [i for i in self.interactions if i.metadata.category == category]
    
    def get_failed_interactions(self) -> List[Interaction]:
        """Get all failed interactions."""
        return [i for i in self.interactions if not i.metadata.success]
    
    def get_high_quality_interactions(self, threshold: float = 0.8) -> List[Interaction]:
        """Get high-quality interactions above threshold."""
        return [i for i in self.interactions if i.quality_score >= threshold]


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Initialize builder
    builder = DatasetBuilder(
        data_dir=Path("./data/training_data"),
        auto_categorize=True,
        quality_filtering=True
    )
    
    # Log some interactions
    builder.log_interaction(
        user_input="What is the weather like today?",
        ai_response="I don't have access to real-time weather data, but I can help you check the weather using a command or API.",
        success=True,
        confidence=0.9,
        latency_ms=150.5,
        tokens_used=45,
        model_used="gpt-4",
        tags=["weather", "question"]
    )
    
    builder.log_interaction(
        user_input="Open Chrome",
        ai_response="Opening Google Chrome browser now.",
        success=True,
        confidence=1.0,
        latency_ms=50.2,
        tokens_used=20,
        model_used="gpt-4",
        tags=["command", "browser"]
    )
    
    # Get statistics
    stats = builder.get_statistics()
    print(f"\nDataset Statistics:")
    print(f"Total interactions: {stats['total_interactions']}")
    print(f"Success rate: {stats['success_rate']:.2%}")
    print(f"Average quality score: {stats['avg_quality_score']:.2f}")
    print(f"Categories: {stats['categories']}")
    
    # Export dataset
    builder.export_dataset(
        output_path=Path("./data/training_data/alpaca_dataset.jsonl"),
        format="alpaca",
        min_quality_score=0.5
    )
    
    builder.save_statistics()
    print("\nDataset builder example completed!")
