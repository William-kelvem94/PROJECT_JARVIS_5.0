"""
JARVIS 5.0 - Agent Engagement & Observation
Manages when the agent should speak and passive background observation.
"""

import logging

logger = logging.getLogger(__name__)


class AgentEngagementManager:
    """Handles engagement logic and passive observation cycles."""

    def __init__(self, agent):
        self.agent = agent
        self.observation_mode = True

    def should_engage(self, text: str) -> bool:
        """Determines if the agent should respond based on multiple signals."""
        # Use prompt manager for identity check
        if hasattr(self.agent, "prompt_manager"):
            # Check for user presence / gaze if possible
            user_looking = False
            if (
                hasattr(self.agent, "camera_controller")
                and self.agent.camera_controller
            ):
                if hasattr(self.agent.camera_controller, "is_user_looking"):
                    user_looking = self.agent.camera_controller.is_user_looking()

            return self.agent.prompt_manager.should_engage(
                text, user_looking=user_looking
            )
        return False

    async def passive_observation_cycle(self):
        """Background loop for learning without user intervention."""
        if not self.observation_mode:
            return

        try:
            # 1. Social Perception
            if (
                hasattr(self.agent, "camera_controller")
                and self.agent.camera_controller
            ):
                try:
                    detected = self.agent.camera_controller.get_detected_people()
                    if detected and hasattr(self.agent, "memory_manager"):
                        self.agent.memory_manager.store_passive_context(
                            f"Pessoas presentes: {', '.join(detected)}",
                            metadata={"type": "social_context"},
                        )
                except Exception:
                    pass

            # 2. Workflow Perception
            if hasattr(
                    self.agent,
                    "screen_capture") and self.agent.screen_capture:
                try:
                    activity = "Atividade de tela observada"  # Placeholder for complex analysis
                    if hasattr(self.agent, "memory_manager"):
                        self.agent.memory_manager.store_passive_context(
                            f"Workflow: {activity}",
                            metadata={"type": "workflow_context"},
                        )
                except Exception:
                    pass

        except Exception as e:
            logger.debug(f"Passive observation suppressed: {e}")
