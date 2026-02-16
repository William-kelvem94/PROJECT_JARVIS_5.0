"""
Tests for EnvironmentManager
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from src.utils.env_manager import EnvironmentManager, JarvisConfig, get_config, get_model_for_tier

class TestEnvironmentManager:
    """Tests for EnvironmentManager class"""

    @pytest.fixture
    def env_manager(self):
        """Fixture to create a fresh EnvironmentManager instance"""
        # Reset any existing config
        manager = EnvironmentManager()
        manager.config = None
        return manager

    def test_load_defaults(self, env_manager):
        """Test loading default configuration"""
        with patch.dict(os.environ, {}, clear=True):
            config = env_manager.load_config()

            assert isinstance(config, JarvisConfig)
            assert config.ollama_url == "http://localhost:11434"
            assert config.ollama_timeout == 30
            assert config.web_host == "0.0.0.0"
            assert config.web_port == 5000
            assert config.default_model_tier == "pro"
            assert config.enable_security is True
            assert config.debug_mode is False

    def test_env_overrides(self, env_manager):
        """Test environment variables overriding defaults"""
        env_vars = {
            'JARVIS_OLLAMA_URL': 'http://remote:11434',
            'JARVIS_WEB_PORT': '8080',
            'JARVIS_DEBUG_MODE': 'true',
            'JARVIS_MODEL_TIER': 'ultra'
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = env_manager.load_config()

            assert config.ollama_url == "http://remote:11434"
            assert config.web_port == 8080
            assert config.debug_mode is True
            assert config.default_model_tier == "ultra"

    def test_type_parsing(self, env_manager):
        """Test parsing of different data types"""
        env_vars = {
            # Booleans
            'JARVIS_ENABLE_SECURITY': 'false',
            'JARVIS_ENABLE_CACHE': '0',

            # Integers
            'JARVIS_MAX_TOKENS': '2048',

            # Floats
            'JARVIS_TEMPERATURE': '0.5',
            'JARVIS_GPU_MEMORY_FRACTION': '0.9',

            # Lists
            'JARVIS_ALLOWED_PATHS': '["/tmp", "/var"]',
            'JARVIS_BLOCKED_COMMANDS': 'rm -rf, sudo'
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = env_manager.load_config()

            assert config.enable_security is False
            assert config.enable_cache is False
            assert config.max_tokens == 2048
            assert config.temperature == 0.5
            assert config.gpu_memory_fraction == 0.9
            assert config.allowed_paths == ["/tmp", "/var"]
            assert config.blocked_commands == ["rm -rf", "sudo"]

    def test_path_processing(self, env_manager):
        """Test path processing logic"""
        # Test relative path resolution
        with patch.dict(os.environ, {'JARVIS_DATA_DIR': 'custom_data'}, clear=True):
            config = env_manager.load_config()

            # Should be resolved relative to project root
            assert config.data_dir.is_absolute()
            assert config.data_dir.name == 'custom_data'

        # Test absolute path
        abs_path = str(Path('/tmp/absolute/path').absolute())
        with patch.dict(os.environ, {'JARVIS_DATA_DIR': abs_path}, clear=True):
            # Reset config to force reload
            env_manager.config = None
            config = env_manager.load_config()

            assert str(config.data_dir) == abs_path

    def test_validation(self, env_manager):
        """Test configuration validation"""
        env_vars = {
            'JARVIS_WEB_PORT': '99999',  # Invalid port
            'JARVIS_MODEL_TIER': 'invalid_tier',  # Invalid tier
            'JARVIS_OLLAMA_URL': 'invalid-url'  # Invalid URL format (simple check)
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # Should log warnings but continue with defaults/fallback
            with patch('src.utils.env_manager.logger') as mock_logger:
                config = env_manager.load_config()

                # Should fallback to 5000
                assert config.web_port == 5000

                # Should fallback to pro
                assert config.default_model_tier == 'pro'

                # Verify warnings were logged
                assert mock_logger.warning.call_count >= 2

    def test_get_model_for_tier(self, env_manager):
        """Test getting model for tier"""
        # Test fallback models
        assert env_manager.get_model_for_tier('ultra') == 'deepseek-r1:8b'
        assert env_manager.get_model_for_tier('pro') == 'gemma3:4b'
        assert env_manager.get_model_for_tier('fast') == 'llama3.2'

        # Test default fallback
        assert env_manager.get_model_for_tier('unknown') == 'gemma3:4b'

        # Test loading from ai_config.yaml
        mock_ai_config = {
            'brain_router': {
                'ollama_models': {
                    'tier_ultra': ['custom-ultra'],
                    'tier_pro': ['custom-pro']
                }
            }
        }

        # Mock open to return yaml content
        with patch('builtins.open', mock_open(read_data="")) as mock_file:
            with patch('yaml.safe_load', return_value=mock_ai_config):
                # Ensure config is loaded so config_dir exists
                env_manager.load_config()

                # Mock exists to return True for ai_config.yaml
                with patch.object(Path, 'exists', return_value=True):
                    model = env_manager.get_model_for_tier('ultra')
                    assert model == 'custom-ultra'

    def test_save_config_template(self, env_manager):
        """Test saving configuration template"""
        with patch('builtins.open', mock_open()) as mock_file:
            env_manager.save_config_template(Path('test.env'))

            mock_file.assert_called_once_with(Path('test.env'), 'w', encoding='utf-8')
            handle = mock_file()
            handle.write.assert_called()
            args = handle.write.call_args[0][0]
            assert "JARVIS_PROJECT_ROOT" in args

    def test_convenience_functions(self):
        """Test module-level convenience functions"""
        # Reset global instance for test
        from src.utils import env_manager
        env_manager.env_manager.config = None

        config = get_config()
        assert isinstance(config, JarvisConfig)

        model = get_model_for_tier('pro')
        assert isinstance(model, str)

    def test_get_model_for_tier_malformed_yaml(self, env_manager):
        """Test handling of malformed ai_config.yaml"""
        with patch('builtins.open', mock_open(read_data="invalid: yaml: content")) as mock_file:
            with patch('yaml.safe_load', side_effect=Exception("Invalid YAML")):
                 # Ensure config is loaded so config_dir exists
                env_manager.load_config()

                # Mock exists to return True for ai_config.yaml
                with patch.object(Path, 'exists', return_value=True):
                    # Should fallback to default
                    model = env_manager.get_model_for_tier('ultra')
                    assert model == 'deepseek-r1:8b'
