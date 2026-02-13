import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Set
from collections import Counter
import re
import time

logger = logging.getLogger("JARVIS-GAP-ANALYZER")

class KnowledgeGapAnalyzer:
    """
    Analyzes past failures and interactions to detect 'Knowledge Gaps'.
    Generates research topics for autonomous training.
    """
    
    STOP_WORDS = {"how", "what", "where", "why", "who", "the", "and", "can", "you", "please", "help"}

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.feedback_db_path = self.data_dir / "learning" / "feedback.db"
        self.interactions_log = self.data_dir / "logs" / "agent_interactions.jsonl"
        
    def analyze_gaps(self) -> List[Dict[str, Any]]:
        """
        Scans data to find topics where JARVIS failed or was corrected.
        Returns a list of 'Research Needs'.
        """
        logger.info("🔍 Analyzing cognitive gaps in neural history...")
        
        # 1. Analyze failed interactions from log
        failed_commands = self._get_failed_commands()
        
        # 2. Extract keywords/topics from failed commands
        topics = self._extract_topics(failed_commands)
        
        # 3. Analyze feedback database for corrections
        feedback_gaps = self._get_feedback_gaps()
        for topic, count in feedback_gaps.items():
            topics[topic] = topics.get(topic, 0) + (count * 2) # Corrections weigh more
        
        gaps = []
        for topic, count in topics.items():
            if count >= 1: 
                # Cognitive Load Estimation
                complexity = self._estimate_complexity(topic)
                
                gaps.append({
                    "topic": topic,
                    "intensity": count,
                    "complexity": complexity,
                    "priority": min(10, count + (complexity * 2))
                })
                
        return sorted(gaps, key=lambda x: x['priority'], reverse=True)

    def _get_feedback_gaps(self) -> Dict[str, int]:
        """Analyzes the feedback database for consistent corrections."""
        try:
            import sqlite3
            if not self.feedback_db_path.exists(): return {}
            
            conn = sqlite3.connect(self.feedback_db_path)
            cursor = conn.cursor()
            # Find topics from corrections where multiple edits happened
            cursor.execute("SELECT prompt FROM preference_pairs")
            prompts = [r[0] for r in cursor.fetchall()]
            conn.close()
            
            return self._extract_topics(prompts)
        except Exception as e:
            logger.error(f"Error reading feedback DB: {e}")
            return {}

    def _get_failed_commands(self) -> List[str]:
        """Loads user commands that resulted in failure or low confidence"""
        commands = []
        if not self.interactions_log.exists():
            return []
            
        try:
            with open(self.interactions_log, 'r', encoding='utf-8') as f:
                # Read last 500 lines for efficiency
                lines = f.readlines()[-500:]
                for line in lines:
                    try:
                        data = json.loads(line)
                        if not data.get('success', True) or data.get('confidence', 1.0) < 0.6:
                            commands.append(data.get('command', ''))
                    except: continue
        except Exception as e:
            logger.error(f"Error reading interactions log: {e}")
            
        return commands

    def _extract_topics(self, commands: List[str]) -> Dict[str, int]:
        """Extracts significant noun-phrases or keywords from commands"""
        keywords = []
        for cmd in commands:
            # Look for technical terms or specific entities
            # Words with CamelCase or snake_case or specific tech suffixes
            tech_terms = re.findall(r'\b[a-zA-Z_]{5,}\b', cmd)
            for term in tech_terms:
                term = term.lower()
                if term not in self.STOP_WORDS:
                    keywords.append(term)
            
        return dict(Counter(keywords))

    def _estimate_complexity(self, topic: str) -> int:
        """Estimates how 'hard' a topic is based on common patterns."""
        complexity = 1
        if any(tech in topic for tech in ['api', 'python', 'script', 'config', 'install', 'error']):
            complexity += 2
        if any(ai in topic for ai in ['model', 'neural', 'train', 'inference']):
            complexity += 3
        return complexity

    def generate_research_plan(self, gap: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a plan to fix a specific knowledge gap"""
        topic = gap['topic']
        return {
            "task_id": f"research_{topic}_{int(time.time()) % 1000}",
            "topic": topic,
            "actions": [
                f"HUB_DISCOVERY: Search Hugging Face for '{topic}' best datasets",
                f"TEACHER_DISTILL: Generate master technical summary for '{topic}'",
                f"DATASET_SYNTHESIS: Generate 50 high-quality DPO pairs for '{topic}'",
                f"TRAINING_TRIGGER: Schedule LoRA fine-tuning for '{topic}'"
            ],
            "urgency": gap['priority'],
            "status": "planned"
        }
