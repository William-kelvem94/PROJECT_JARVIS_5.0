#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Neural Systems Loader
==========================================
Centralized loader for advanced neural systems with lazy loading
and graceful degradation.

Features:
- Knowledge Graph (Entity/Relationship extraction)
- Multimodal Fusion (Vision + Audio + Text)
- Vision QA (Gemini Vision API)
- ReAct Agent (Reasoning + Action)
- Neural Dashboard integration

Architecture:
- Lazy loading to avoid blocking main boot
- API key validation with fallbacks
- Status reporting for health checks
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger("JARVIS-NEURAL")


@dataclass
class NeuralSystemStatus:
    """Status of a neural system"""

    name: str
    loaded: bool
    error: Optional[str] = None
    requires_api_key: bool = False
    api_key_valid: bool = False


class NeuralSystemsLoader:
    """Manages loading and lifecycle of advanced neural systems"""

    def __init__(self, data_dir: Path, config: Optional[Any] = None):
        """
        Initialize neural systems loader.

        Args:
            data_dir: Data directory for models and storage
            config: Optional configuration object
        """
        self.data_dir = Path(data_dir)
        self.config = config
        self.systems = {}
        self.status = {}

        logger.info("ðŸ§  Initializing Neural Systems Loader...")

        # Load systems
        self._load_knowledge_graph()
        self._load_multimodal_fusion()
        self._load_vision_qa()
        self._load_react_agent()

        # Report
        active = len([s for s in self.status.values() if s.loaded])
        total = len(self.status)
        logger.info(f"âœ… Neural Systems: {active}/{total} active")

        for name, status in self.status.items():
            if status.loaded:
                logger.info(f"   âœ… {name}")
            elif status.error:
                logger.warning(f"   âš ï¸ {name}: {status.error}")

    def _load_knowledge_graph(self):
        """Load Knowledge Graph system"""
        try:
            from src.core.intelligence.knowledge_graph import KnowledgeGraph

            graph_path = str(self.data_dir / "knowledge" / "graph.json")
            kg = KnowledgeGraph(graph_path=graph_path)
            self.systems["knowledge_graph"] = kg
            self.status["Knowledge Graph"] = NeuralSystemStatus(
                name="Knowledge Graph", loaded=True
            )

        except Exception as e:
            logger.warning(f"âš ï¸ Knowledge Graph unavailable: {e}")
            self.status["Knowledge Graph"] = NeuralSystemStatus(
                name="Knowledge Graph", loaded=False, error=str(e)
            )

    def _load_multimodal_fusion(self):
        """Load Multimodal Fusion system"""
        try:
            from src.core.intelligence.multimodal_fusion import MultimodalFusion

            fusion = MultimodalFusion()
            self.systems["multimodal_fusion"] = fusion
            self.status["Multimodal Fusion"] = NeuralSystemStatus(
                name="Multimodal Fusion", loaded=True
            )

        except Exception as e:
            logger.warning(f"âš ï¸ Multimodal Fusion unavailable: {e}")
            self.status["Multimodal Fusion"] = NeuralSystemStatus(
                name="Multimodal Fusion", loaded=False, error=str(e)
            )

    def _load_vision_qa(self):
        """Load Vision QA system (supports Local fallback)"""
        try:
            # Check for API key
            import os

            api_key = os.environ.get("GEMINI_API_KEY")
            if self.config:
                try:
<<<<<<< HEAD
<<<<<<< Updated upstream
                    api_key = api_key or self.config.get_setting('brain.gemini_api_key')
=======
                    api_key = api_key or self.config.get_setting("brain.gemini_api_key")
>>>>>>> dev-new-version
                except:
=======
                    api_key = api_key or self.config.get_setting("brain.gemini_api_key")
                except Exception:
>>>>>>> Stashed changes
                    pass

            from src.core.vision.vision_language_model import VisionQA

            # Initialize (VisionQA handles fallback internally)
            vqa = VisionQA(api_key=api_key)
            self.systems["vision_qa"] = vqa

            if api_key:
                self.status["Vision QA"] = NeuralSystemStatus(
                    name="Vision QA",
                    loaded=True,
                    requires_api_key=True,
                    api_key_valid=True,
                )
            else:
                self.status["Vision QA"] = NeuralSystemStatus(
                    name="Vision QA (Local)",
                    loaded=True,
                    requires_api_key=False,
                    api_key_valid=False,
                )

        except Exception as e:
            logger.warning(f"âš ï¸ Vision QA unavailable: {e}")
            self.status["Vision QA"] = NeuralSystemStatus(
                name="Vision QA", loaded=False, error=str(e)
            )

    def _load_react_agent(self):
        """Load ReAct Agent system (supports Local fallback)"""
        try:
            # Check for API key
            import os

            api_key = os.environ.get("GEMINI_API_KEY")
            if self.config:
                try:
<<<<<<< HEAD
<<<<<<< Updated upstream
                    api_key = api_key or self.config.get_setting('brain.gemini_api_key')
=======
                    api_key = api_key or self.config.get_setting("brain.gemini_api_key")
>>>>>>> dev-new-version
                except:
=======
                    api_key = api_key or self.config.get_setting("brain.gemini_api_key")
                except Exception:
>>>>>>> Stashed changes
                    pass

            from src.core.intelligence.react_agent import ReActAgent

            # Initialize (ReAct handles fallback internally)
            agent = ReActAgent(api_key=api_key)
            self.systems["react_agent"] = agent

            if api_key:
                self.status["ReAct Agent"] = NeuralSystemStatus(
                    name="ReAct Agent",
                    loaded=True,
                    requires_api_key=True,
                    api_key_valid=True,
                )
            else:
                self.status["ReAct Agent"] = NeuralSystemStatus(
                    name="ReAct Agent (Local)",
                    loaded=True,
                    requires_api_key=False,
                    api_key_valid=False,
                )

        except Exception as e:
            logger.warning(f"âš ï¸ ReAct Agent unavailable: {e}")
            self.status["ReAct Agent"] = NeuralSystemStatus(
                name="ReAct Agent", loaded=False, error=str(e)
            )

    def get_system(self, name: str) -> Optional[Any]:
        """Get a loaded neural system by name"""
        return self.systems.get(name)

    def active_systems(self) -> Dict[str, Any]:
        """Get all active systems"""
        return {k: v for k, v in self.systems.items() if v is not None}

    def get_status_report(self) -> Dict[str, NeuralSystemStatus]:
        """Get status of all neural systems"""
        return self.status

    def is_fully_operational(self) -> bool:
        """Check if all systems are loaded"""
        return all(s.loaded for s in self.status.values())

    def get_health_score(self) -> float:
        """Calculate health score contribution (0-1)"""
        if not self.status:
            return 0.0

        loaded = len([s for s in self.status.values() if s.loaded])
        total = len(self.status)
        return loaded / total


def get_neural_systems(
    data_dir: Path, config: Optional[Any] = None
) -> NeuralSystemsLoader:
    """Factory function to get neural systems loader"""
    return NeuralSystemsLoader(data_dir, config)


# Singleton instance
_neural_systems: Optional[NeuralSystemsLoader] = None


def init_neural_systems(
    data_dir: Path, config: Optional[Any] = None
) -> NeuralSystemsLoader:
    """Initialize neural systems singleton"""
    global _neural_systems
    if _neural_systems is None:
        _neural_systems = NeuralSystemsLoader(data_dir, config)
    return _neural_systems


def get_neural_systems_instance() -> Optional[NeuralSystemsLoader]:
    """Get the neural systems singleton instance"""
    return _neural_systems
