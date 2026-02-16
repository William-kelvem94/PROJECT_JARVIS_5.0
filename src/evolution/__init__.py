#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Evolution Layer
============================
Camada de auto-observação, auto-diagnóstico e auto-correção do sistema.

Este módulo implementa a arquitetura autopoiética do JARVIS 5.0,
permitindo que o sistema:
- Monitore seu próprio estado (Self Observer)
- Diagnostique problemas automaticamente (Auto Healer)
- Aplique correções de forma segura (Safe Executor)
- Aprenda com experiências passadas (Knowledge Database)

Exports:
    evolution_manager: Gerenciador principal da camada de evolução
    self_observer: Componente de auto-observação
    auto_healer: Componente de auto-diagnóstico
    safe_executor: Componente de auto-correção
    knowledge_db: Base de conhecimento
"""

from .evolution_manager import evolution_manager
from .self_observer import self_observer, advanced_metrics_collector
from .auto_healer import auto_healer
from .safe_executor import safe_executor
from .knowledge_db import knowledge_db

# Legacy functions for backward compatibility
async def start_evolution_services():
    """Inicia todos os serviços de evolução"""
    await evolution_manager.start()

async def stop_evolution_services():
    """Para todos os serviços de evolução"""
    await evolution_manager.stop()

__all__ = [
    'evolution_manager',
    'self_observer',
    'advanced_metrics_collector',
    'auto_healer',
    'safe_executor',
    'knowledge_db',
    'start_evolution_services',
    'stop_evolution_services'
]

