#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Evolution Voice Commands Handler
=============================================
Real functional implementation of voice commands for Evolution Layer control.

Implements Section 10.1 voice commands:
- "JARVIS, mostre o que você está corrigindo"
- "JARVIS, autorizo a correção XYZ"
- "JARVIS, reverta a última alteração"
- "JARVIS, desative o modo auto-correção por 1 hora"

Author: JARVIS 5.0 Evolution Layer
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import re

from src.core.infrastructure.async_event_bus import event_bus, EventType, EventPriority

logger = logging.getLogger(__name__)


class EvolutionVoiceCommands:
    """
    Handles voice commands for Evolution Layer control.
    Real functional implementation of Section 10.1 requirements.
    """
    
    def __init__(self):
        self.running = False
        self.auto_heal_disabled_until = None
        self.last_correction = None
        self.pending_corrections = []
        
        # Command patterns (Portuguese and English)
        self.command_patterns = {
            'show_corrections': [
                r'mostre.*corrig',
                r'show.*correct',
                r'o que.*corrig',
                r'what.*correct'
            ],
            'authorize_correction': [
                r'autorizo.*corre[cç][aã]o',
                r'authorize.*correction',
                r'aprovar.*corre[cç][aã]o',
                r'approve.*correction'
            ],
            'revert_change': [
                r'reverta.*altera[cç][aã]o',
                r'revert.*change',
                r'desfazer.*altera[cç][aã]o',
                r'undo.*change'
            ],
            'disable_auto_heal': [
                r'desative.*auto.*corre[cç][aã]o',
                r'disable.*auto.*correct',
                r'pausar.*auto.*corre[cç][aã]o',
                r'pause.*auto.*heal'
            ],
            'enable_auto_heal': [
                r'ative.*auto.*corre[cç][aã]o',
                r'enable.*auto.*correct',
                r'retomar.*auto.*corre[cç][aã]o',
                r'resume.*auto.*heal'
            ],
            'system_status': [
                r'status.*evolu[cç][aã]o',
                r'evolution.*status',
                r'sa[uú]de.*sistema',
                r'system.*health'
            ],
            'trigger_maintenance': [
                r'fa[cç]a.*manuten[cç][aã]o',
                r'run.*maintenance',
                r'verificar.*sistema',
                r'check.*system'
            ]
        }
        
    async def start(self):
        """Start the voice commands handler"""
        if self.running:
            return
            
        self.running = True
        
        # Subscribe to voice command events
        event_bus.subscribe(
            EventType.AUDIO_VOICE_COMMAND,
            self._handle_voice_command
        )
        
        # Subscribe to UI commands as well
        event_bus.subscribe(
            EventType.UI_COMMAND,
            self._handle_voice_command
        )
        
        # Subscribe to correction events to track them
        event_bus.subscribe(
            EventType.SYSTEM_CORRECTION_SUCCEEDED,
            self._track_correction
        )
        
        event_bus.subscribe(
            EventType.SYSTEM_DIAGNOSTIC_PLAN,
            self._track_pending_corrections
        )
        
        logger.info("🎤 Evolution Voice Commands Handler started")
        
    async def stop(self):
        """Stop the voice commands handler"""
        self.running = False
        logger.info("🎤 Evolution Voice Commands Handler stopped")
        
    async def _handle_voice_command(self, event):
        """Process incoming voice commands"""
        if not self.running:
            return
            
        command = event.data.get("command", "").lower()
        
        # Check each command pattern
        if self._matches_pattern(command, 'show_corrections'):
            await self._show_corrections()
            
        elif self._matches_pattern(command, 'authorize_correction'):
            correction_id = self._extract_correction_id(command)
            await self._authorize_correction(correction_id)
            
        elif self._matches_pattern(command, 'revert_change'):
            await self._revert_last_change()
            
        elif self._matches_pattern(command, 'disable_auto_heal'):
            duration = self._extract_duration(command)
            await self._disable_auto_heal(duration)
            
        elif self._matches_pattern(command, 'enable_auto_heal'):
            await self._enable_auto_heal()
            
        elif self._matches_pattern(command, 'system_status'):
            await self._show_system_status()
            
        elif self._matches_pattern(command, 'trigger_maintenance'):
            await self._trigger_maintenance()
            
    def _matches_pattern(self, command: str, pattern_key: str) -> bool:
        """Check if command matches any pattern for the given key"""
        patterns = self.command_patterns.get(pattern_key, [])
        return any(re.search(pattern, command) for pattern in patterns)
        
    def _extract_correction_id(self, command: str) -> Optional[str]:
        """Extract correction ID from command"""
        # Look for ID patterns like "XYZ", "abc123", etc.
        match = re.search(r'\b([a-z0-9]{6,16})\b', command.lower())
        return match.group(1) if match else None
        
    def _extract_duration(self, command: str) -> int:
        """Extract duration in minutes from command"""
        # Look for "1 hora", "2 hours", "30 minutos", etc.
        
        # Hours
        match = re.search(r'(\d+)\s*(hora|hour)', command.lower())
        if match:
            return int(match.group(1)) * 60
            
        # Minutes
        match = re.search(r'(\d+)\s*(minuto|minute)', command.lower())
        if match:
            return int(match.group(1))
            
        # Default to 1 hour
        return 60
        
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
                response += f"📋 **Pending Corrections:** {len(self.pending_corrections)}\n"
                for i, correction in enumerate(self.pending_corrections[:3], 1):
                    desc = correction.get('descricao', 'Unknown')
                    response += f"  {i}. {desc}\n"
                    
            if pending_auth:
                response += f"\n⏳ **Awaiting Authorization:** {len(pending_auth)}\n"
                for req in pending_auth[:3]:
                    response += f"  • {req['action'].get('descricao')} (ID: {req['id'][:8]})\n"
                    
            if self.last_correction:
                response += f"\n✅ **Last Correction:**\n"
                response += f"  • {self.last_correction.get('descricao', 'Unknown')}\n"
                response += f"  • Applied: {self.last_correction.get('timestamp', 'Unknown')}\n"
                
            if not self.pending_corrections and not pending_auth:
                response += "\n✨ No corrections pending. System is healthy!"
                
            # Send response via event bus
            event_bus.publish(
                EventType.UI_RESPONSE,
                data={
                    "response": response,
                    "type": "evolution_status"
                },
                priority=EventPriority.HIGH,
                source="evolution_voice_commands"
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
                    correction_id = pending[0]['id']
                else:
                    self._send_error_response("No corrections pending authorization")
                    return
                    
            # Authorize
            success = await authorization_manager.authorize(correction_id, reason="Voice authorization")
            
            if success:
                response = f"✅ Correction authorized (ID: {correction_id[:8]}). Applying now..."
                logger.info(f"✅ Voice authorization granted for {correction_id}")
            else:
                response = f"❌ Could not authorize correction {correction_id[:8]}. It may have already been processed."
                
            event_bus.publish(
                EventType.UI_RESPONSE,
                data={"response": response, "type": "authorization_result"},
                priority=EventPriority.HIGH,
                source="evolution_voice_commands"
            )
            
        except Exception as e:
            logger.error(f"Error authorizing correction: {e}")
            self._send_error_response("Error processing authorization")
            
    async def _revert_last_change(self):
        """Revert the last correction applied"""
        try:
            from src.evolution import safe_executor
            from src.evolution.knowledge_db import knowledge_db
            
            if not self.last_correction:
                self._send_error_response("No recent corrections to revert")
                return
                
            # Get the file that was changed
            file_path = self.last_correction.get('arquivo')
            
            if not file_path:
                self._send_error_response("Cannot revert: file information not available")
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
                source="evolution_voice_commands"
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
            
            self.auto_heal_disabled_until = datetime.now() + timedelta(minutes=duration_minutes)
            
            response = f"⏸️ Auto-correction disabled for {duration_minutes} minutes. "
            response += f"Will re-enable at {self.auto_heal_disabled_until.strftime('%H:%M')}."
            
            event_bus.publish(
                EventType.UI_RESPONSE,
                data={"response": response, "type": "auto_heal_disabled"},
                priority=EventPriority.HIGH,
                source="evolution_voice_commands"
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
                source="evolution_voice_commands"
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
                remaining = (self.auto_heal_disabled_until - datetime.now()).total_seconds() / 60
                response += f"  _(Re-enabling in {int(remaining)} minutes)_\n"
                
            response += f"**Uptime:** {int(status.get('uptime_seconds', 0) / 60)} minutes\n\n"
            
            # Components
            response += "**Components:**\n"
            for name, running in status.get('components', {}).items():
                status_icon = "✅" if running else "❌"
                response += f"  {status_icon} {name}\n"
                
            # Knowledge base
            response += f"\n**Learning:**\n"
            response += f"  • Problems: {kb_stats['total_problems']}\n"
            response += f"  • Solutions: {kb_stats['total_solutions']}\n"
            response += f"  • Success Rate: {kb_stats['success_rate']:.1f}%\n"
            
            event_bus.publish(
                EventType.UI_RESPONSE,
                data={"response": response, "type": "system_status"},
                priority=EventPriority.HIGH,
                source="evolution_voice_commands"
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
                source="evolution_voice_commands"
            )
            
            # Trigger maintenance
            await evolution_manager.trigger_maintenance()
            
            # Send completion message
            response = "✅ Maintenance cycle complete. Check logs for details."
            
            event_bus.publish(
                EventType.UI_RESPONSE,
                data={"response": response, "type": "maintenance_complete"},
                priority=EventPriority.HIGH,
                source="evolution_voice_commands"
            )
            
            logger.info("🔧 Manual maintenance cycle triggered via voice")
            
        except Exception as e:
            logger.error(f"Error triggering maintenance: {e}")
            self._send_error_response("Error starting maintenance")
            
    async def _schedule_reenable(self, minutes: int):
        """Schedule auto-heal re-enable after specified minutes"""
        await asyncio.sleep(minutes * 60)
        
        if self.auto_heal_disabled_until and datetime.now() >= self.auto_heal_disabled_until:
            await self._enable_auto_heal()
            
    async def _track_correction(self, event):
        """Track successful corrections"""
        self.last_correction = event.data.get('action', {})
        self.last_correction['timestamp'] = datetime.now().isoformat()
        
    async def _track_pending_corrections(self, event):
        """Track pending corrections"""
        plan = event.data.get('plan', [])
        self.pending_corrections = plan
        
    def _send_error_response(self, message: str):
        """Send error response via event bus"""
        event_bus.publish(
            EventType.UI_RESPONSE,
            data={
                "response": f"❌ {message}",
                "type": "error"
            },
            priority=EventPriority.HIGH,
            source="evolution_voice_commands"
        )


# Singleton instance
evolution_voice_commands = EvolutionVoiceCommands()
