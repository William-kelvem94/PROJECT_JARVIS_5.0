"""
⚙️ JARVIS Management System - Sistema de Gerenciamento
====================================================

Este módulo contém todas as funcionalidades de gerenciamento e manutenção do JARVIS,
incluindo recuperação automática, controle de dispositivos, otimização de performance
e gerenciamento de dependências.

Módulos Principais:
- device_manager: Gerenciamento de dispositivos
- hardware_manager: Controle de hardware
- auto_recovery_system: Recuperação automática
- performance_optimizer: Otimização de performance
- dependency_manager: Gerenciamento de dependências
- shutdown_manager: Controle de desligamento
- system_controller: Controle geral do sistema

Exemplo de uso:
    from src.core.management import DeviceManager, AutoRecoverySystem

    device_mgr = DeviceManager()
    recovery = AutoRecoverySystem()
"""

from .device_manager import AdvancedDeviceManager as DeviceManager
from .hardware_manager import HardwareManager
from .auto_recovery_system import AutoRecoverySystem
from .performance_optimizer import PerformanceOptimizer
from .dependency_manager import DependencyManager
from .shutdown_manager import ShutdownManager
from .system_controller import SystemController

__all__ = [
    'DeviceManager',
    'HardwareManager',
    'AutoRecoverySystem',
    'PerformanceOptimizer',
    'DependencyManager',
    'ShutdownManager',
    'SystemController'
]
