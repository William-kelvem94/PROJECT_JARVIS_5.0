#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Evolution Layer
============================
Camada responsável pela autopoiese (auto-criação/manutenção) do sistema.
Inclui auto-observação, diagnóstico e correção.
"""

from .self_observer import self_observer
from .auto_healer import auto_healer
from .safe_executor import safe_executor

async def start_evolution_services():
    """Inicia todos os serviços de evolução"""
    await self_observer.start()
    await auto_healer.start()
    await safe_executor.start()

async def stop_evolution_services():
    """Para todos os serviços de evolução"""
    await self_observer.stop()
    await auto_healer.stop()
    await safe_executor.stop()
