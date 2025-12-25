"""
Configuration management for JARVIS
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """Gerencia configurações do JARVIS de forma robusta"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configurações do arquivo ou cria configuração padrão"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Validar e completar configuração
                    return self._validate_and_complete_config(config)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Erro ao carregar config: {e}. Usando configuração padrão.")
        
        # Configuração padrão
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna configuração padrão completa"""
        return {
            "voice": {
                "rate": 180,
                "volume": 0.9,
                "language": "pt-BR",
                "use_gtts": True,
                "pitch": 50
            },
            "recognition": {
                "timeout": 5,
                "phrase_limit": 10,
                "energy_threshold": 300,
                "dynamic_energy_threshold": True
            },
            "system": {
                "os": "auto",
                "debug_mode": False,
                "log_level": "INFO"
            },
            "commands": {
                "wake_word": None,
                "exit_phrases": ["sair", "tchau", "até logo"],
                "help_phrases": ["ajuda", "help", "comandos"]
            },
            "natural_speech": {
                "use_fillers": True,
                "use_hesitations": True,
                "use_breathing": True,
                "emotion_detection": True,
                "conversation_flow": True
            }
        }
    
    def _validate_and_complete_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Valida e completa configuração carregada"""
        default = self._get_default_config()
        
        # Merge recursivo mantendo valores existentes
        def merge_dicts(default_dict, user_dict):
            result = default_dict.copy()
            for key, value in user_dict.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dicts(result[key], value)
                else:
                    result[key] = value
            return result
        
        return merge_dicts(default, config)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Obtém valor de configuração usando notação de ponto
        Exemplo: config.get('voice.rate') -> 180
        """
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> None:
        """
        Define valor de configuração usando notação de ponto
        Exemplo: config.set('voice.rate', 200)
        """
        keys = key_path.split('.')
        config_ref = self._config
        
        # Navegar até o penúltimo nível
        for key in keys[:-1]:
            if key not in config_ref:
                config_ref[key] = {}
            config_ref = config_ref[key]
        
        # Definir valor final
        config_ref[keys[-1]] = value
    
    def save(self) -> bool:
        """Salva configuração atual no arquivo"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
            return False
    
    def reload(self) -> None:
        """Recarrega configuração do arquivo"""
        self._config = self._load_config()
    
    def get_all(self) -> Dict[str, Any]:
        """Retorna toda a configuração"""
        return self._config.copy()
    
    def reset_to_default(self) -> None:
        """Reseta configuração para padrão"""
        self._config = self._get_default_config()
        self.save()
