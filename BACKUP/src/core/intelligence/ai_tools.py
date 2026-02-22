#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - AI Tools Module
====================================
External tools for AI agent execution.
Separated from main agent to reduce complexity and improve maintainability.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class AITools:
    """
    Collection of tools that the AI agent can use for execution.
    Separated from the main agent to keep the brain focused on thinking.
    """

    def __init__(self):
        self.web_search_tool = None
        self.voice_controller = None
        self._load_tools()

    def _load_tools(self):
        """Load available tools safely"""
        try:
            from src.utils.web_search import web_search_tool

            self.web_search_tool = web_search_tool
        except ImportError:
            logger.warning("Web search tool not available")

        try:
            from src.core.audio.voice_controller import voice_controller

            self.voice_controller = voice_controller
        except ImportError:
            logger.warning("Voice controller not available")

    def handle_web_search(self, response: str, enriched_command: str) -> str:
        """
        Handle web search requests from AI responses.
        Extracts search query and performs search.
        """
        try:
            start = response.find("[SEARCH:") + 8
            end = response.find("]", start)
            query = response[start:end].strip()

            logger.info(f"AI requested search: {query}")

            if self.voice_controller:
                self.voice_controller.speak(f"Pesquisando sobre {query}...")

            if self.web_search_tool:
                search_results = self.web_search_tool.search_google(
                    query, num_results=2
                )
                search_text = "\n".join(search_results)

                enriched_command += f"\n\n[RESULTADOS DA BUSCA PARA '{query}']:\n{search_text}\n\nResponda agora."
            else:
                enriched_command += "\n\n[ERRO] Ferramenta de busca não disponível."

        except Exception as e:
            logger.error(f"Error in web search handling: {e}")
            enriched_command += f"\n\n[ERRO] Falha na busca: {e}"

        return enriched_command

    def execute_system_action(
        self, action_type: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute system-level actions.
        This is a placeholder for system actions that should be handled by action_controller.
        """
        # This should delegate to action_controller or system_integrator
        logger.info(f"Executing system action: {action_type} with params {parameters}")
        return {
            "status": "not_implemented",
            "message": "System actions should be handled by action_controller",
        }


# Global instance
ai_tools = AITools()


def get_ai_tools() -> AITools:
    """Get global AI tools instance"""
    return ai_tools
