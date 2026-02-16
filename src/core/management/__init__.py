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
from .universal_recovery_manager import UniversalRecoveryManager, get_universal_recovery_manager, universal_recovery_manager
from .performance_optimizer import PerformanceOptimizer
from .dependency_manager import DependencyManager
from .system_controller import SystemController

import logging
logger = logging.getLogger(__name__)

# Optional PyQt6-dependent modules
try:
    from .shutdown_manager import ShutdownManager
    SHUTDOWN_MANAGER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ShutdownManager not available: {e}")
    ShutdownManager = None
    SHUTDOWN_MANAGER_AVAILABLE = False

# Backward compatibility alias
def get_auto_recovery_system():
    return get_universal_recovery_manager()

# Global Instances
auto_recovery_system = get_universal_recovery_manager()

__all__ = [
    'DeviceManager',
    'HardwareManager',
    'UniversalRecoveryManager',
    'get_universal_recovery_manager',
    'universal_recovery_manager',
    'auto_recovery_system',
    'PerformanceOptimizer',
    'DependencyManager',
    'ShutdownManager',
    'SystemController'
]
