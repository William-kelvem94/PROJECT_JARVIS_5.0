#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Evolution Manager
==============================
Coordena todos os componentes da camada de evolução (auto-observação,
auto-diagnóstico e auto-correção).

Responsibilities:
- Inicialização coordenada de todos os módulos de evolução
- Gestão do ciclo de vida dos componentes
- Interface de controle para ativar/desativar o sistema
- Monitoramento de saúde dos componentes de evolução
- Coordenação de gatilhos para manutenção

Author: JARVIS 5.0 Evolution Layer
"""

import asyncio
import logging
from typing import Optional
from datetime import datetime

from src.evolution.self_observer import self_observer
from src.evolution.auto_healer import auto_healer
from src.evolution.safe_executor import safe_executor
from src.evolution.knowledge_db import knowledge_db
from src.core.infrastructure.async_event_bus import event_bus, EventType, EventPriority

logger = logging.getLogger(__name__)


class EvolutionManager:
    """
    Gerenciador central da camada de evolução do JARVIS 5.0.
    Coordena os componentes de auto-observação, diagnóstico e correção.
    """

    def __init__(self):
        self.running = False
        self.observer_interval = 300  # 5 minutos por padrão
        self.auto_heal_enabled = True
        self._startup_time = None

    async def start(
        self, 
        observer_interval: int = 300, 
        auto_heal: bool = True,
        initial_scan: bool = True,
        enable_module_generation: bool = True,
        enable_voice_commands: bool = True
    ):
        """
        Inicia o sistema de evolução.

        Args:
            observer_interval: Intervalo entre observações em segundos
            auto_heal: Se True, habilita correção automática
            initial_scan: Se True, executa um scan inicial ao iniciar
            enable_module_generation: Se True, habilita geração de módulos
            enable_voice_commands: Se True, habilita comandos de voz
        """
        if self.running:
            logger.warning("Evolution Manager already running")
            return

        self.running = True
        self.auto_heal_enabled = auto_heal
        self.observer_interval = observer_interval
        self._startup_time = datetime.now()

        logger.info("🧬 Starting JARVIS Evolution Layer...")

        try:
            # 1. Initialize core components
            logger.info("  ├─ Initializing Authorization Manager...")
            from src.evolution.authorization_manager import authorization_manager
            await authorization_manager.start()

            logger.info("  ├─ Initializing Self Observer...")
            await self_observer.start(interval=observer_interval)

            logger.info("  ├─ Initializing Auto Healer...")
            await auto_healer.start()

            logger.info("  ├─ Initializing Safe Executor...")
            await safe_executor.start()

            # 2. Initialize advanced components
            if enable_module_generation:
                logger.info("  ├─ Initializing Module Generator (Auto-Development)...")
                from src.evolution.module_generator import module_generator
                await module_generator.start()

            if enable_voice_commands:
                logger.info("  ├─ Initializing Voice Commands Handler...")
                from src.evolution.voice_commands import evolution_voice_commands
                await evolution_voice_commands.start()

            # 3. Execute initial scan if requested
            if initial_scan:
                logger.info("  ├─ Running initial system scan...")
                await self._trigger_initial_scan()

            # 4. Publish startup event
            event_bus.publish(
                EventType.SYSTEM_STARTUP,
                data={
                    "subsystem": "evolution",
                    "status": "operational",
                    "auto_heal_enabled": self.auto_heal_enabled,
                    "observer_interval": self.observer_interval,
                    "module_generation_enabled": enable_module_generation,
                    "voice_commands_enabled": enable_voice_commands
                },
                priority=EventPriority.HIGH,
                source="evolution_manager"
            )

            logger.info("✅ JARVIS Evolution Layer operational")
            logger.info(f"   └─ Auto-healing: {'ENABLED' if auto_heal else 'DISABLED'}")
            logger.info(f"   └─ Module Generation: {'ENABLED' if enable_module_generation else 'DISABLED'}")
            logger.info(f"   └─ Voice Commands: {'ENABLED' if enable_voice_commands else 'DISABLED'}")
            logger.info(f"   └─ Observation interval: {observer_interval}s")

        except Exception as e:
            logger.error(f"❌ Failed to start Evolution Layer: {e}")
            await self.stop()
            raise

    async def stop(self):
        """Para o sistema de evolução de forma ordenada."""
        if not self.running:
            return

        logger.info("🛑 Stopping JARVIS Evolution Layer...")

        try:
            # Stop components in reverse order
            try:
                from src.evolution.voice_commands import evolution_voice_commands
                await evolution_voice_commands.stop()
            except Exception:
                pass

            try:
                from src.evolution.module_generator import module_generator
                await module_generator.stop()
            except Exception:
                pass

            await safe_executor.stop()
            await auto_healer.stop()
            await self_observer.stop()

            try:
                from src.evolution.authorization_manager import authorization_manager
                await authorization_manager.stop()
            except Exception:
                pass

            # Publish shutdown event
            event_bus.publish(
                EventType.SYSTEM_SHUTDOWN,
                data={
                    "subsystem": "evolution",
                    "uptime_seconds": self._get_uptime()
                },
                priority=EventPriority.HIGH,
                source="evolution_manager"
            )

            self.running = False
            logger.info("✅ Evolution Layer stopped")

        except Exception as e:
            logger.error(f"Error during Evolution Layer shutdown: {e}")

    async def _trigger_initial_scan(self):
        """Executa um scan inicial do sistema."""
        try:
            report = await self_observer.generate_full_report()
            
            # Publicar relatório imediatamente
            event_bus.publish(
                EventType.SYSTEM_OBSERVER_REPORT,
                data=report,
                priority=EventPriority.HIGH,
                source="evolution_manager"
            )
            
            logger.info("✓ Initial scan completed")
        except Exception as e:
            logger.error(f"Initial scan failed: {e}")

    async def trigger_maintenance(self):
        """
        Gatilho manual para ciclo de manutenção.
        Útil para comandos de voz ou UI.
        """
        if not self.running:
            logger.warning("Cannot trigger maintenance: Evolution Layer not running")
            return

        logger.info("🔧 Manual maintenance cycle triggered")
        await self._trigger_initial_scan()

    def get_status(self) -> dict:
        """
        Retorna o status atual do sistema de evolução.

        Returns:
            Dicionário com informações de status
        """
        return {
            "running": self.running,
            "auto_heal_enabled": self.auto_heal_enabled,
            "observer_interval": self.observer_interval,
            "uptime_seconds": self._get_uptime(),
            "components": {
                "self_observer": self_observer.running,
                "auto_healer": auto_healer.running,
                "safe_executor": safe_executor.running
            },
            "knowledge_stats": knowledge_db.get_statistics() if self.running else None
        }

    def enable_auto_heal(self):
        """Habilita a correção automática."""
        self.auto_heal_enabled = True
        logger.info("✅ Auto-healing ENABLED")

    def disable_auto_heal(self):
        """Desabilita a correção automática (apenas observação)."""
        self.auto_heal_enabled = False
        logger.warning("⚠️ Auto-healing DISABLED - observation only mode")

    def _get_uptime(self) -> Optional[float]:
        """Retorna o tempo de execução em segundos."""
        if not self._startup_time:
            return None
        return (datetime.now() - self._startup_time).total_seconds()


# Singleton instance
evolution_manager = EvolutionManager()
