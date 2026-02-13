"""
âš™ï¸ JARVIS Management System - Sistema de Gerenciamento
====================================================

Este mÃ³dulo contÃ©m todas as funcionalidades de gerenciamento e manutenÃ§Ã£o do JARVIS,
incluindo recuperaÃ§Ã£o automÃ¡tica, controle de dispositivos, otimizaÃ§Ã£o de performance
e gerenciamento de dependÃªncias.

MÃ³dulos Principais:
- device_manager: Gerenciamento de dispositivos
- hardware_manager: Controle de hardware
- auto_recovery_system: RecuperaÃ§Ã£o automÃ¡tica
- performance_optimizer: OtimizaÃ§Ã£o de performance
- dependency_manager: Gerenciamento de dependÃªncias
- shutdown_manager: Controle de desligamento
- system_controller: Controle geral do sistema

Exemplo de uso:
    from src.core.management import DeviceManager, AutoRecoverySystem

    device_mgr = DeviceManager()
    recovery = AutoRecoverySystem()
"""

from .device_manager import AdvancedDeviceManager as DeviceManager
from .hardware_manager import HardwareManager
from .auto_recovery_system import AutoRecoverySystem, get_auto_recovery_system
from .performance_optimizer import PerformanceOptimizer
from .dependency_manager import DependencyManager
from .shutdown_manager import ShutdownManager
from .system_controller import SystemController

# Global Instances
auto_recovery_system = get_auto_recovery_system()

__all__ = [
    'DeviceManager',
    'HardwareManager',
    'AutoRecoverySystem',
    'PerformanceOptimizer',
    'DependencyManager',
    'ShutdownManager',
    'SystemController'
]
