import pytest
from src.learning.training_orchestrator import TrainingOrchestrator
from src.learning.model_registry_manager import ModelRegistryManager
from src.learning.health_monitor import HealthMonitor

def test_training_orchestrator():
    orchestrator = TrainingOrchestrator()
    assert hasattr(orchestrator, 'manage_training_jobs')

def test_model_registry_manager():
    manager = ModelRegistryManager()
    assert hasattr(manager, 'manage_models')

def test_health_monitor():
    monitor = HealthMonitor()
    assert hasattr(monitor, 'monitor_system')
