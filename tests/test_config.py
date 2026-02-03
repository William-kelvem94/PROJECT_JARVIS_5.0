"""
Testes para o módulo de configuração
"""

import pytest
import json
import os
from pathlib import Path
from unittest.mock import patch, mock_open
from src.utils.config import Config, config


class TestConfig:
    """Testes da classe Config"""

    def test_singleton_pattern(self):
        """Testa padrão singleton da classe Config"""
        config1 = Config()
        config2 = Config()
        assert config1 is config2
        assert config is config1

    def test_default_settings_structure(self):
        """Testa estrutura das configurações padrão"""
        config_obj = Config()
        defaults = config_obj.DEFAULT_SETTINGS

        # Verificar estrutura básica
        assert 'app' in defaults
        assert 'capture' in defaults
        assert 'ocr' in defaults
        assert 'processing' in defaults
        assert 'storage' in defaults
        assert 'analysis' in defaults
        assert 'interface' in defaults

        # Verificar campos obrigatórios
        assert 'name' in defaults['app']
        assert 'version' in defaults['app']
        assert 'language' in defaults['app']

    def test_get_setting(self):
        """Testa obtenção de configurações"""
        config_obj = Config()

        # Testar caminho válido
        assert config_obj.get_setting('app.name') == "Leitor de Tela Inteligente"

        # Testar caminho inválido
        assert config_obj.get_setting('invalid.path', 'default') == 'default'

        # Testar caminho vazio
        assert config_obj.get_setting('', 'default') == 'default'

    def test_set_setting(self):
        """Testa definição de configurações"""
        config_obj = Config()

        # Definir configuração
        config_obj.set_setting('test.value', 'test_data')

        # Verificar se foi definida
        assert config_obj.get_setting('test.value') == 'test_data'

        # Verificar estrutura aninhada
        assert 'test' in config_obj.user_settings
        assert config_obj.user_settings['test']['value'] == 'test_data'

    def test_ocr_config(self):
        """Testa configurações OCR"""
        config_obj = Config()

        # Testar configuração Tesseract
        tesseract_config = config_obj.get_ocr_config('tesseract')
        assert 'path' in tesseract_config
        assert 'config' in tesseract_config
        assert 'timeout' in tesseract_config

        # Testar configuração EasyOCR
        easyocr_config = config_obj.get_ocr_config('easyocr')
        assert 'gpu' in easyocr_config
        assert 'model_storage_directory' in easyocr_config

    def test_document_types_config(self):
        """Testa configurações de tipos de documento"""
        config_obj = Config()

        # Testar tipo de documento existente
        receipt_config = config_obj.get_document_type_config('receipt')
        assert receipt_config['name'] == 'Nota Fiscal'
        assert 'keywords' in receipt_config
        assert 'patterns' in receipt_config

        # Testar tipo inexistente
        unknown_config = config_obj.get_document_type_config('unknown')
        assert unknown_config == {}

    def test_extraction_patterns(self):
        """Testa padrões de extração"""
        config_obj = Config()

        # Testar padrão existente
        cpf_pattern = config_obj.get_extraction_pattern('cpf')
        assert cpf_pattern == r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"

        # Testar padrão inexistente
        unknown_pattern = config_obj.get_extraction_pattern('unknown')
        assert unknown_pattern == ""

    def test_data_categories(self):
        """Testa categorias de dados"""
        config_obj = Config()

        categories = config_obj.get_data_categories()
        assert 'personal' in categories
        assert 'financial' in categories
        assert 'business' in categories

        assert 'nome' in categories['personal']
        assert 'cpf' in categories['personal']
        assert 'valor' in categories['financial']

    @patch('src.utils.config.Path.mkdir')
    def test_create_directories(self, mock_mkdir):
        """Testa criação de diretórios"""
        config_obj = Config()
        config_obj._create_directories()

        # Verificar se mkdir foi chamado para os diretórios necessários
        expected_calls = [
            config_obj.CAPTURES_DIR,
            config_obj.PROCESSED_DIR,
            config_obj.CONFIG_DIR,
            config_obj.DATA_DIR / "models",
            config_obj.DATA_DIR / "temp",
            config_obj.DATA_DIR / "exports"
        ]

        for expected_dir in expected_calls:
            mock_mkdir.assert_any_call(expected_dir, parents=True, exist_ok=True)

    @patch('src.utils.config.open', new_callable=mock_open, read_data='{"test": "data"}')
    def test_load_user_settings_success(self, mock_file):
        """Testa carregamento bem-sucedido das configurações do usuário"""
        config_obj = Config()

        # Simular arquivo existente
        config_obj.SETTINGS_FILE = Path("fake_settings.json")

        result = config_obj._load_user_settings()

        # Verificar se dados foram carregados
        assert result == {"test": "data"}
        mock_file.assert_called_once_with(config_obj.SETTINGS_FILE, 'r', encoding='utf-8')

    @patch('src.utils.config.open', side_effect=FileNotFoundError)
    def test_load_user_settings_file_not_found(self, mock_file):
        """Testa carregamento quando arquivo não existe"""
        config_obj = Config()

        # Simular arquivo inexistente
        config_obj.SETTINGS_FILE = Path("nonexistent.json")

        result = config_obj._load_user_settings()

        # Deve retornar configurações padrão
        assert result == config_obj.DEFAULT_SETTINGS

    @patch('src.utils.config.open', side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
    def test_load_user_settings_invalid_json(self, mock_file):
        """Testa carregamento com JSON inválido"""
        config_obj = Config()

        config_obj.SETTINGS_FILE = Path("invalid.json")

        result = config_obj._load_user_settings()

        # Deve retornar configurações padrão
        assert result == config_obj.DEFAULT_SETTINGS

    @patch('src.utils.config.open', new_callable=mock_open)
    @patch('src.utils.config.json.dump')
    def test_save_user_settings(self, mock_json_dump, mock_file):
        """Testa salvamento das configurações do usuário"""
        config_obj = Config()

        test_settings = {"test": "value"}
        config_obj.save_user_settings(test_settings)

        # Verificar se json.dump foi chamado corretamente
        mock_json_dump.assert_called_once_with(
            test_settings,
            mock_file.return_value,
            indent=2,
            ensure_ascii=False
        )

        # Verificar se arquivo foi aberto corretamente
        mock_file.assert_called_once_with(
            config_obj.SETTINGS_FILE,
            'w',
            encoding='utf-8'
        )


class TestConfigIntegration:
    """Testes de integração da configuração"""

    def test_config_instance_creation(self):
        """Testa criação da instância global de configuração"""
        # A instância global deve ser criada durante o import
        assert config is not None
        assert isinstance(config, Config)

    def test_project_paths(self):
        """Testa caminhos do projeto"""
        assert config.PROJECT_ROOT.exists()
        assert config.SRC_DIR.exists()
        assert config.DATA_DIR.exists()
        assert config.CONFIG_DIR.exists()

    def test_system_info(self):
        """Testa informações do sistema"""
        system_info = config.SYSTEM_INFO

        assert 'os' in system_info
        assert 'python_version' in system_info
        assert 'architecture' in system_info

        # OS deve ser Windows neste caso
        assert system_info['os'] == 'Windows'
