from src.core.config.system_manifest import system_manifest
from pathlib import Path


def test_system_manifest_has_network_config():
    assert hasattr(system_manifest, "network")
    net = system_manifest.network
    assert hasattr(net, "enabled")
    assert hasattr(net, "discovery_port")
    # config file should exist in repo (sane default)
    cfg = Path("config") / "network_mesh_config.yaml"
    assert cfg.exists() is True
    # Basic sanity checks
    assert isinstance(net.enabled, bool)
    assert isinstance(net.discovery_port, int)
