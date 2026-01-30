"""
Configurações Globais do JARVIS Ultimate
Sistema agnóstico ao hardware e ambiente
"""

import os
import platform
import json
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Sistema de configuração inteligente que se adapta ao ambiente."""

    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.system_info = self._detect_hardware()
        self.config = self._load_config()
        self._apply_hardware_adaptations()

    def _detect_hardware(self) -> Dict[str, Any]:
        """Detecta automaticamente o hardware e ambiente."""
        system = platform.system().lower()
        machine = platform.machine().lower()

        # Detectar tipo de dispositivo
        is_laptop = False
        is_desktop = False

        try:
            if system == "windows":
                # Verificar se é laptop via PowerShell
                import subprocess
                result = subprocess.run(
                    ['powershell', '-Command',
                     'Get-WmiObject Win32_Battery | Select-Object -First 1'],
                    capture_output=True, text=True, timeout=5
                )
                is_laptop = result.returncode == 0 and result.stdout.strip()
            elif system == "linux":
                # Verificar arquivos de bateria no Linux
                battery_paths = [
                    "/sys/class/power_supply/BAT0",
                    "/sys/class/power_supply/BAT1"
                ]
                is_laptop = any(Path(p).exists() for p in battery_paths)
        except:
            pass

        is_desktop = not is_laptop

        return {
            "system": system,
            "machine": machine,
            "is_laptop": is_laptop,
            "is_desktop": is_desktop,
            "hostname": platform.node(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0]
        }

    def _load_config(self) -> Dict[str, Any]:
        """Carrega configurações do arquivo."""
        default_config = {
            # LLM Settings
            "llm_provider": "ollama",
            "ollama_base_url": "http://localhost:11434",
            "ollama_model": "codellama:7b",

            # Hardware Settings (adaptados automaticamente)
            "hardware": {
                "cpu_monitoring": True,
                "memory_monitoring": True,
                "disk_monitoring": True,
                "temperature_monitoring": True,
                "battery_monitoring": self.system_info["is_laptop"]
            },

            # Voice Settings
            "voice": {
                "stt_engine": "whisper",  # whisper, speech_recognition, vosk
                "tts_engine": "pyttsx3",  # pyttsx3, edge_tts, elevenlabs
                "language": "pt-BR",
                "wake_word": "jarvis",
                "voice_volume": 80
            },

            # Learning Settings
            "learning": {
                "rag_enabled": True,
                "continuous_training": True,
                "auto_learn_from_interactions": True,
                "knowledge_retention_days": 365
            },

            # System Control
            "system_control": {
                "allow_file_operations": True,
                "allow_app_launch": True,
                "allow_system_commands": True,
                "max_concurrent_processes": 5
            },

            # Docker Settings
            "docker": {
                "enabled": False,  # Preferir modo nativo
                "network_mode": "host",  # Para acesso ao host
                "volume_mounts": True
            },

            # Personalização William
            "user": {
                "name": "William",
                "preferences": {
                    "volume_preference": 20,  # %
                    "desktop_water_cooling": True,
                    "galaxy_book_optimization": True
                }
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # Merge com default
                self._deep_merge(default_config, user_config)
                return default_config
            except Exception as e:
                print(f"Erro ao carregar config: {e}")
                return default_config
        else:
            return default_config

    def _apply_hardware_adaptations(self):
        """Aplica adaptações específicas do hardware detectado."""
        if self.system_info["is_laptop"]:
            # Otimizações para Galaxy Book2
            self.config["hardware"]["battery_monitoring"] = True
            self.config["hardware"]["power_management"] = True
            self.config["voice"]["voice_volume"] = 70  # Mais baixo para laptop

        if self.system_info["is_desktop"]:
            # Otimizações para Desktop parrudo
            self.config["hardware"]["gpu_monitoring"] = True
            self.config["hardware"]["water_cooling_monitoring"] = True
            self.config["system_control"]["max_concurrent_processes"] = 10

        # Ajustes específicos para Windows
        if self.system_info["system"] == "windows":
            self.config["system_control"]["use_powershell"] = True

    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]):
        """Merge profundo de dicionários."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor da configuração."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """Define valor da configuração."""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def save(self):
        """Salva configurações no arquivo."""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def get_system_info(self) -> Dict[str, Any]:
        """Retorna informações do sistema detectado."""
        return self.system_info

    def is_docker_environment(self) -> bool:
        """Verifica se está rodando em Docker."""
        return os.path.exists('/.dockerenv') or os.environ.get('DOCKER_CONTAINER') == 'true'

    def get_user_name(self) -> str:
        """Retorna nome do usuário personalizado."""
        return self.get("user.name", "Usuário")

# Instância global
config = Config()