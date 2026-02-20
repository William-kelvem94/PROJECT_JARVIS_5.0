#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Evolution Voice Commands Handler (Intelligent Version)
===================================================================
INTELLIGENT implementation using LLM for natural language understanding.

Instead of fixed regex patterns, uses AI to understand user intent naturally.
User can express commands in their own words - JARVIS intelligently understands.

Examples of natural variations:
- "show corrections" / "what are you fixing" / "mostre o que está corrigindo"
- "pause for an hour" / "stop auto-heal temporarily" / "desative por 1 hora"
- "go back" / "undo that" / "reverta a última mudança"

Author: JARVIS 5.0 Evolution Layer
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import requests

from src.core.infrastructure.async_event_bus import event_bus, EventType, EventPriority
from src.core.config.system_manifest import system_manifest

logger = logging.getLogger(__name__)


class EvolutionVoiceCommands:
    """
    Handles voice commands for Evolution Layer control with INTELLIGENT understanding.
    Uses LLM to understand natural language variations instead of fixed patterns.
    """

    def __init__(self):
        self.running = False
        self.auto_heal_disabled_until = None
        self.last_correction = None
        self.pending_corrections = []

        # Available actions that the system can perform
        # LLM will map user's natural language to these intents
        self.available_actions = {
            "show_corrections": {
                "description": "Show current corrections being applied or pending",
                "examples": [
                    "show corrections",
                    "what are you fixing",
                    "mostre correções",
                ],
            },
            "authorize_correction": {
                "description": "Authorize/approve a pending correction",
                "examples": ["authorize correction XYZ", "approve it", "autorizo"],
            },
            "revert_change": {
                "description": "Revert/undo the last change made",
                "examples": ["revert last change", "undo that", "reverta"],
            },
            "disable_auto_heal": {
                "description": "Temporarily disable auto-correction",
                "examples": ["disable auto-correction", "pause healing", "desative"],
            },
            "enable_auto_heal": {
                "description": "Re-enable auto-correction",
                "examples": ["enable auto-correction", "resume healing", "ative"],
            },
            "system_status": {
                "description": "Show evolution system status and health",
                "examples": ["status", "how are you", "system health"],
            },
            "trigger_maintenance": {
                "description": "Trigger a manual maintenance cycle",
                "examples": ["do maintenance", "check yourself", "faça manutenção"],
            },
        }

    async def start(self):
        """Start the voice commands handler"""
        if self.running:
            return

        self.running = True

        # Subscribe to voice command events
        event_bus.subscribe(EventType.AUDIO_VOICE_COMMAND, self._handle_voice_command)

        # Subscribe to UI commands as well
        event_bus.subscribe(EventType.UI_COMMAND, self._handle_voice_command)

        # Subscribe to correction events to track them
        event_bus.subscribe(
            EventType.SYSTEM_CORRECTION_SUCCEEDED, self._track_correction
        )

        event_bus.subscribe(
            EventType.SYSTEM_DIAGNOSTIC_PLAN, self._track_pending_corrections
        )

        logger.info("🎤 Evolution Voice Commands Handler started (INTELLIGENT MODE)")
        logger.info("   └─ Using LLM for natural language understanding")

    async def stop(self):
        """Stop the voice commands handler"""
        self.running = False
        logger.info("🎤 Evolution Voice Commands Handler stopped")

    async def _handle_voice_command(self, event):
        """Process incoming voice commands using LLM for intelligent understanding"""
        if not self.running:
            return

        command = event.data.get("command", "")

        # Use LLM to understand the user's intent
        intent_result = await self._understand_intent(command)

        if not intent_result or not intent_result.get("action"):
            logger.debug(f"Could not understand intent from: {command}")
            return

        action = intent_result["action"]
        parameters = intent_result.get("parameters", {})

        logger.info(f"🧠 Understood intent: {action} with params: {parameters}")

        # Execute the appropriate action
        if action == "show_corrections":
            await self._show_corrections()

        elif action == "authorize_correction":
            correction_id = parameters.get("correction_id")
            await self._authorize_correction(correction_id)

        elif action == "revert_change":
            await self._revert_last_change()

        elif action == "disable_auto_heal":
            duration = parameters.get("duration_minutes", 60)
            await self._disable_auto_heal(duration)

        elif action == "enable_auto_heal":
            await self._enable_auto_heal()

        elif action == "system_status":
            await self._show_system_status()

        elif action == "trigger_maintenance":
            await self._trigger_maintenance()

    async def _understand_intent(self, command: str) -> Optional[Dict[str, Any]]:
        """
        Use LLM to understand user intent from natural language.
        This replaces rigid pattern matching with intelligent understanding.
        """
        try:
            # Build prompt for LLM to classify intent
            prompt = self._build_intent_classification_prompt(command)

            # Call LLM for intent classification
            response = await self._call_llm(prompt)

            if not response:
                return None

            # Parse LLM response
            intent_result = self._parse_intent_response(response)

            return intent_result

        except Exception as e:
            logger.error(f"Error understanding intent: {e}")
            return None

    def _build_intent_classification_prompt(self, command: str) -> str:
        """Build a prompt for LLM to classify user intent"""

        # Build list of available actions for LLM
        actions_description = "\n".join(
            [
                f"- {action}: {info['description']}"
                for action, info in self.available_actions.items()
            ]
        )

        prompt = f"""You are JARVIS, an intelligent AI assistant. Analyze the user's command and determine their intent.

Available actions:
{actions_description}

User command: "{command}"

Analyze the command and respond with JSON containing:
- "action": the matching action name (or null if unclear)
- "confidence": your confidence level (0.0 to 1.0)
- "parameters": any parameters extracted (correction_id, duration_minutes, etc.)

Think about what the user wants to do. Consider:
- Portuguese and English variations
- Natural ways people express these intents
- Context and implied meanings

Respond ONLY with valid JSON, no extra text."""

        return prompt

    async def _call_llm(self, prompt: str) -> Optional[str]:
        """Call LLM (Ollama) for intent understanding"""
        try:
            host = system_manifest.ai.ollama_host
            port = system_manifest.ai.ollama_port
            model = system_manifest.ai.ollama_model

            response = requests.post(
                f"http://{host}:{port}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Low temperature for more consistent results
                        "top_p": 0.9,
                    },
                },
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.warning(f"LLM returned status {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            logger.warning("LLM request timed out")
            return None
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return None

    def _parse_intent_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse LLM's intent classification response"""
        try:
            # Extract JSON from response (might be wrapped in markdown)
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]

            # Parse JSON
            intent_data = json.loads(response.strip())

            # Validate confidence
            confidence = intent_data.get("confidence", 0.0)
            if confidence < 0.5:
                logger.debug(f"Low confidence ({confidence}) in intent classification")
                return None

            return intent_data

        except json.JSONDecodeError as e:
            logger.debug(f"Could not parse JSON from LLM response: {e}")
            # Try to extract action name at least
            response_lower = response.lower()
            for action in self.available_actions.keys():
                if action in response_lower:
                    return {"action": action, "parameters": {}, "confidence": 0.6}
            return None
        except Exception as e:
            logger.error(f"Error parsing intent response: {e}")
            return None

    async def _show_corrections(self):
        """Show current and recent corrections"""
        try:
            from src.evolution import evolution_manager
            from src.evolution.authorization_manager import authorization_manager

            status = evolution_manager.get_status()
            pending_auth = authorization_manager.get_pending_requests()

            # Build response message
            response = "🧬 **Evolution Layer Status:**\n\n"

            if self.pending_corrections:
                response += (
                    f"📋 **Pending Corrections:** {len(self.pending_corrections)}\n"
                )
                for i, correction in enumerate(self.pending_corrections[:3], 1):
                    desc = correction.get("descricao", "Unknown")
                    response += f"  {i}. {desc}\n"

            if pending_auth:
                response += f"\n⏳ **Awaiting Authorization:** {len(pending_auth)}\n"
                for req in pending_auth[:3]:
                    response += (
                        f"  • {req['action'].get('descricao')} (ID: {req['id'][:8]})\n"
                    )

            if self.last_correction:
                response += "\n✅ **Last Correction:**\n"
                response += f"  • {self.last_correction.get('descricao', 'Unknown')}\n"
                response += (
                    f"  • Applied: {self.last_correction.get('timestamp', 'Unknown')}\n"
                )

            if not self.pending_corrections and not pending_auth:
                response += "\n✨ No corrections pending. System is healthy!"

            # Send response via event bus
            event_bus.publish(
                EventType.UI_RESPONSE,
                data={"response": response, "type": "evolution_status"},
                priority=EventPriority.HIGH,
                source="evolution_voice_commands",
            )

            logger.info("📊 Displayed corrections status via voice")

        except Exception as e:
            logger.error(f"Error showing corrections: {e}")
            self._send_error_response("Unable to retrieve corrections status")

    async def _authorize_correction(self, correction_id: Optional[str]):
        """Authorize a pending correction"""
        try:
            from src.evolution.authorization_manager import authorization_manager

            if not correction_id:
                # Try to authorize the first pending request
                pending = authorization_manager.get_pending_requests()
                if pending:
                    correction_id = pending[0]["id"]
                else:
                    self._send_error_response("No corrections pending authorization")
                    return

            # Authorize
            success = await authorization_manager.authorize(
                correction_id, reason="Voice authorization"
            )

            if success:
                response = f"✅ Correction authorized (ID: {correction_id[:8]}). Applying now..."
                logger.info(f"✅ Voice authorization granted for {correction_id}")
            else:
                response = f"❌ Could not authorize correction {correction_id[:8]}. It may have already been processed."

            event_bus.publish(
                EventType.UI_RESPONSE,
                data={"response": response, "type": "authorization_result"},
                priority=EventPriority.HIGH,
                source="evolution_voice_commands",
            )

        except Exception as e:
            logger.error(f"Error authorizing correction: {e}")
            self._send_error_response("Error processing authorization")

    async def _revert_last_change(self):
        """Revert the last correction applied"""
        try:

            if not self.last_correction:
                self._send_error_response("No recent corrections to revert")
                return

            # Get the file that was changed
            file_path = self.last_correction.get("arquivo")

            if not file_path:
                self._send_error_response(
                    "Cannot revert: file information not available"
                )
                return

            # Find the backup
            from pathlib import Path

            backup_dir = Path("data/backups/auto")

            # Get the most recent backup for this file
            file_name = Path(file_path).name
            backups = sorted(backup_dir.glob(f"{file_name}.*.bak"), reverse=True)

            if not backups:
                self._send_error_response(f"No backup found for {file_name}")
                return

            # Restore from backup
            import shutil

            latest_backup = backups[0]
            shutil.copy2(latest_backup, file_path)

            response = f"✅ Reverted changes to {file_name}. Backup restored from {latest_backup.name}"

            event_bus.publish(
                EventType.UI_RESPONSE,
                data={"response": response, "type": "revert_success"},
                priority=EventPriority.HIGH,
                source="evolution_voice_commands",
            )

            logger.info(f"🔄 Reverted correction for {file_name}")

        except Exception as e:
            logger.error(f"Error reverting change: {e}")
            self._send_error_response("Error reverting changes")

    async def _disable_auto_heal(self, duration_minutes: int = 60):
        """Temporarily disable auto-correction"""
        try:
            from src.evolution import evolution_manager

            evolution_manager.disable_auto_heal()

            self.auto_heal_disabled_until = datetime.now() + timedelta(
                minutes=duration_minutes
            )

            response = f"⏸️ Auto-correction disabled for {duration_minutes} minutes. "
            response += (
                f"Will re-enable at {self.auto_heal_disabled_until.strftime('%H:%M')}."
            )

            event_bus.publish(
                EventType.UI_RESPONSE,
                data={"response": response, "type": "auto_heal_disabled"},
                priority=EventPriority.HIGH,
                source="evolution_voice_commands",
            )

            # Schedule re-enable
            asyncio.create_task(self._schedule_reenable(duration_minutes))

            logger.info(f"⏸️ Auto-healing disabled for {duration_minutes} minutes")

        except Exception as e:
            logger.error(f"Error disabling auto-heal: {e}")
            self._send_error_response("Error disabling auto-correction")

    async def _enable_auto_heal(self):
        """Re-enable auto-correction"""
        try:
            from src.evolution import evolution_manager

            evolution_manager.enable_auto_heal()
            self.auto_heal_disabled_until = None

            response = "▶️ Auto-correction re-enabled. System will now automatically fix detected issues."

            event_bus.publish(
                EventType.UI_RESPONSE,
                data={"response": response, "type": "auto_heal_enabled"},
                priority=EventPriority.HIGH,
                source="evolution_voice_commands",
            )

            logger.info("▶️ Auto-healing re-enabled")

        except Exception as e:
            logger.error(f"Error enabling auto-heal: {e}")
            self._send_error_response("Error enabling auto-correction")

    async def _show_system_status(self):
        """Show comprehensive system status"""
        try:
            from src.evolution import evolution_manager
            from src.evolution.knowledge_db import knowledge_db

            status = evolution_manager.get_status()
            kb_stats = knowledge_db.get_statistics()

            response = "🧬 **JARVIS Evolution System Status**\n\n"

            # Overall status
            response += f"**System:** {'🟢 Operational' if status['running'] else '🔴 Offline'}\n"
            response += f"**Auto-Heal:** {'🟢 Enabled' if status['auto_heal_enabled'] else '🔴 Disabled'}\n"

            if self.auto_heal_disabled_until:
                remaining = (
                    self.auto_heal_disabled_until - datetime.now()
                ).total_seconds() / 60
                response += f"  _(Re-enabling in {int(remaining)} minutes)_\n"

            response += (
                f"**Uptime:** {int(status.get('uptime_seconds', 0) / 60)} minutes\n\n"
            )

            # Components
            response += "**Components:**\n"
            for name, running in status.get("components", {}).items():
                status_icon = "✅" if running else "❌"
                response += f"  {status_icon} {name}\n"

            # Knowledge base
            response += "\n**Learning:**\n"
            response += f"  • Problems: {kb_stats['total_problems']}\n"
            response += f"  • Solutions: {kb_stats['total_solutions']}\n"
            response += f"  • Success Rate: {kb_stats['success_rate']:.1f}%\n"

            event_bus.publish(
                EventType.UI_RESPONSE,
                data={"response": response, "type": "system_status"},
                priority=EventPriority.HIGH,
                source="evolution_voice_commands",
            )

            logger.info("📊 Displayed system status via voice")

        except Exception as e:
            logger.error(f"Error showing status: {e}")
            self._send_error_response("Error retrieving system status")

    async def _trigger_maintenance(self):
        """Trigger manual maintenance cycle"""
        try:
            from src.evolution import evolution_manager

            response = "🔧 Initiating system maintenance cycle..."

            event_bus.publish(
                EventType.UI_RESPONSE,
                data={"response": response, "type": "maintenance_started"},
                priority=EventPriority.HIGH,
                source="evolution_voice_commands",
            )

            # Trigger maintenance
            await evolution_manager.trigger_maintenance()

            # Send completion message
            response = "✅ Maintenance cycle complete. Check logs for details."

            event_bus.publish(
                EventType.UI_RESPONSE,
                data={"response": response, "type": "maintenance_complete"},
                priority=EventPriority.HIGH,
                source="evolution_voice_commands",
            )

            logger.info("🔧 Manual maintenance cycle triggered via voice")

        except Exception as e:
            logger.error(f"Error triggering maintenance: {e}")
            self._send_error_response("Error starting maintenance")

    async def _schedule_reenable(self, minutes: int):
        """Schedule auto-heal re-enable after specified minutes"""
        await asyncio.sleep(minutes * 60)

        if (
            self.auto_heal_disabled_until
            and datetime.now() >= self.auto_heal_disabled_until
        ):
            await self._enable_auto_heal()

    async def _track_correction(self, event):
        """Track successful corrections"""
        self.last_correction = event.data.get("action", {})
        self.last_correction["timestamp"] = datetime.now().isoformat()

    async def _track_pending_corrections(self, event):
        """Track pending corrections"""
        plan = event.data.get("plan", [])
        self.pending_corrections = plan

    def _send_error_response(self, message: str):
        """Send error response via event bus"""
        event_bus.publish(
            EventType.UI_RESPONSE,
            data={"response": f"❌ {message}", "type": "error"},
            priority=EventPriority.HIGH,
            source="evolution_voice_commands",
        )


# Singleton instance
evolution_voice_commands = EvolutionVoiceCommands()
