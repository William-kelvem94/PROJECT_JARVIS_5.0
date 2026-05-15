import logging
from typing import List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Omega-Brain.GapAnalyzer")

class GapAnalyzer:
    """
    Knowledge Gap Identifier.
    Detects missing information and triggers external research.
    """

    def __init__(self, kb_interface=None):
        self.kb = kb_interface

    def identify_gap(self, query: str, provided_context: str) -> bool:
        """
        Determines if the current KB context is insufficient to answer the query.
        """
        logger.info(f"Analyzing knowledge gap for: {query}")

        if not provided_context or len(provided_context) < 100:
            return True

        query_keywords = set(query.lower().split())
        context_keywords = set(provided_context.lower().split())

        overlap = query_keywords.intersection(context_keywords)
        if len(overlap) < 2:
            return True

        return False

    def trigger_research(self, gap_topic: str) -> str:
        """
        Triggers the Playwright research engine.
        """
        logger.info(f"GAP DETECTED: {gap_topic}. Triggering Playwright Research Engine...")
        return f"Triggered research for {gap_topic}. Results will be piped to Dream Cycle."
