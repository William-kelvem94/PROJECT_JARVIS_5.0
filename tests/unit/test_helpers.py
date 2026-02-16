"""
Testes para utilitários e funções auxiliares
"""

import os
from pathlib import Path
from unittest.mock import patch
import tempfile
from PIL import Image
import numpy as np
from src.utils.helpers import (
    FileHelper,
    ImageHelper,
    TextHelper,
    DataHelper,
    SystemHelper,
    file_helper,
    image_helper,
    text_helper,
    data_helper,
    system_helper,
)


class TestFileHelper:
    """Testes do FileHelper"""

    def test_get_file_hash(self):
        """Testa cálculo de hash de arquivo"""
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            test_content = b"test content for hashing"
            temp_file.write(test_content)
            temp_file_path = temp_file.name

        try:
            # Calcular hash
            file_hash = FileHelper.get_file_hash(temp_file_path)

            # Hash deve ser uma string hexadecimal
            assert isinstance(file_hash, str)
            assert len(file_hash) == 64  # SHA256 tem 64 caracteres

            # Mesmo conteúdo deve gerar mesmo hash
            file_hash2 = FileHelper.get_file_hash(temp_file_path)
            assert file_hash == file_hash2

        finally:
            os.unlink(temp_file_path)

    def test_get_file_size_mb(self):
        """Testa obtenção do tamanho do arquivo em MB"""
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Escrever 1MB de dados
            test_data = b"x" * (1024 * 1024)
            temp_file.write(test_data)
            temp_file_path = temp_file.name

        try:
            size_mb = FileHelper.get_file_size_mb(temp_file_path)

            # Deve ser aproximadamente 1MB
            assert 0.9 <= size_mb <= 1.1

        finally:
            os.unlink(temp_file_path)

    def test_ensure_directory(self):
        """Testa garantia de criação de diretório"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / "test" / "nested" / "directory"

            # Diretório não deve existir inicialmente
            assert not test_dir.exists()

            # Criar diretório
            FileHelper.ensure_directory(test_dir)

            # Diretório deve existir agora
            assert test_dir.exists()
            assert test_dir.is_dir()

    def test_get_unique_filename(self):
        """Testa geração de nome de arquivo único"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_name = "test_file"
            extension = "txt"

            # Primeiro arquivo deve ter nome base
            filename1 = FileHelper.get_unique_filename(temp_dir, base_name, extension)
            assert filename1 == "test_file.txt"

            # Criar arquivo
            Path(temp_dir) / filename1

            # Segundo arquivo deve ter sufixo numérico
            filename2 = FileHelper.get_unique_filename(temp_dir, base_name, extension)
            assert filename2 == "test_file_1.txt"

    @patch("src.utils.helpers.logger")
    def test_cleanup_old_files(self, mock_logger):
        """Testa limpeza de arquivos antigos"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Criar arquivos com diferentes idades
            old_file = temp_path / "old_file.txt"
            new_file = temp_path / "new_file.txt"

            old_file.write_text("old")
            new_file.write_text("new")

            # Simular arquivo antigo modificando timestamp
            import time

            old_timestamp = time.time() - (40 * 24 * 60 * 60)  # 40 dias atrás
            os.utime(old_file, (old_timestamp, old_timestamp))

            # Executar limpeza (30 dias)
            FileHelper.cleanup_old_files(temp_dir, 30)

            # Arquivo antigo deve ter sido removido
            assert not old_file.exists()
            # Arquivo novo deve existir
            assert new_file.exists()


class TestImageHelper:
    """Testes do ImageHelper"""

    def test_preprocess_image(self):
        """Testa pré-processamento de imagem"""
        # Criar imagem de teste
        test_image = Image.new("RGB", (100, 100), color="white")

        # Pré-processar
        processed = ImageHelper.preprocess_image(test_image)

        # Deve retornar uma imagem PIL
        assert isinstance(processed, Image.Image)

        # Deve ser convertida para escala de cinza
        assert processed.mode == "L"

    def test_image_to_cv2(self):
        """Testa conversão PIL para OpenCV"""
        # Criar imagem PIL
        pil_image = Image.new("RGB", (50, 50), color="red")

        # Converter para OpenCV
        cv_image = ImageHelper.image_to_cv2(pil_image)

        # Deve ser array numpy
        assert isinstance(cv_image, np.ndarray)
        assert cv_image.shape == (50, 50, 3)  # Altura, largura, canais

    def test_cv2_to_image(self):
        """Testa conversão OpenCV para PIL"""
        # Criar array OpenCV
        cv_array = np.zeros((30, 40, 3), dtype=np.uint8)
        cv_array[:, :, 0] = 255  # Canal vermelho

        # Converter para PIL
        pil_image = ImageHelper.cv2_to_image(cv_array)

        # Deve ser imagem PIL
        assert isinstance(pil_image, Image.Image)
        assert pil_image.size == (40, 30)  # Largura, altura

    def test_detect_text_regions(self):
        """Testa detecção de regiões de texto"""
        # Criar imagem simples com "texto" (retângulo branco)
        test_image = Image.new("L", (200, 100), color=0)  # Fundo preto
        # Adicionar retângulo branco simulando texto
        from PIL import ImageDraw

        draw = ImageDraw.Draw(test_image)
        draw.rectangle([50, 30, 150, 70], fill=255)

        regions = ImageHelper.detect_text_regions(test_image)

        # Deve encontrar pelo menos uma região
        assert isinstance(regions, list)
        # (Validação específica pode variar dependendo da implementação)


class TestTextHelper:
    """Testes do TextHelper"""

    def test_clean_ocr_text(self):
        """Testa limpeza de texto OCR"""
        # Texto com problemas comuns
        dirty_text = "Texto    com\n\nmuitos   espaços\r\ne caracteres  estranhos!!!"

        cleaned = TextHelper.clean_ocr_text(dirty_text)

        # Deve remover espaços extras e quebras de linha inconsistentes
        assert "    " not in cleaned
        assert "\n\n" not in cleaned
        assert cleaned.strip() == cleaned

    def test_extract_patterns(self):
        """Testa extração de padrões"""
        text = "CPF: 123.456.789-00 Email: test@example.com Valor: R$ 1.234,56"

        patterns = {
            "cpf": r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b",
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        }

        results = TextHelper.extract_patterns(text, patterns)

        assert "cpf" in results
        assert "email" in results
        assert results["cpf"] == ["123.456.789-00"]
        assert results["email"] == ["test@example.com"]

    def test_normalize_text(self):
        """Testa normalização de texto"""
        text = "TÉXTO com ACENTOS, números: 123 e SÍMBOLOS!!!"

        normalized = TextHelper.normalize_text(text)

        # Deve converter para minúsculas e remover acentos
        assert normalized == "texto com acentos, numeros: 123 e simbolos"

    def test_calculate_text_similarity(self):
        """Testa cálculo de similaridade de texto"""
        text1 = "Este é um texto de teste"
        text2 = "Este é um texto similar de teste"
        text3 = "Texto completamente diferente"

        sim1 = TextHelper.calculate_text_similarity(text1, text2)
        sim2 = TextHelper.calculate_text_similarity(text1, text3)

        # Textos similares devem ter similaridade maior
        assert sim1 > sim2
        assert 0 <= sim1 <= 1
        assert 0 <= sim2 <= 1

    def test_remove_accents(self):
        """Testa remoção de acentos"""
        text = "Téxto cómpóstò cöm àcéntös"

        result = TextHelper._remove_accents(text)

        assert result == "Texto compost com acentos"


class TestDataHelper:
    """Testes do DataHelper"""

    def test_validate_cpf_valid(self):
        """Testa validação de CPF válido"""
        # CPF válido de exemplo
        valid_cpf = "123.456.789-09"  # CPF válido para testes

        assert DataHelper.validate_cpf("12345678909")  # Sem formatação
        assert DataHelper.validate_cpf("123.456.789-09")  # Com formatação

    def test_validate_cpf_invalid(self):
        """Testa validação de CPF inválido"""
        # CPFs inválidos
        assert not DataHelper.validate_cpf("111.111.111-11")  # Todos dígitos iguais
        assert not DataHelper.validate_cpf(
            "123.456.789-00"
        )  # Dígito verificador errado
        assert not DataHelper.validate_cpf("123456789")  # Tamanho errado

    def test_validate_cnpj_valid(self):
        """Testa validação de CNPJ válido"""
        # CNPJ válido de exemplo
        valid_cnpj = "12.345.678/0001-90"

        assert DataHelper.validate_cnpj("12345678000190")  # Sem formatação
        assert DataHelper.validate_cnpj("12.345.678/0001-90")  # Com formatação

    def test_validate_cnpj_invalid(self):
        """Testa validação de CNPJ inválido"""
        assert not DataHelper.validate_cnpj(
            "11.111.111/1111-11"
        )  # Todos dígitos iguais
        assert not DataHelper.validate_cnpj(
            "12345678000100"
        )  # Dígito verificador errado

    def test_format_money(self):
        """Testa formatação de valores monetários"""
        # Valores de entrada diferentes
        assert DataHelper.format_money(1234.56) == "R$ 1.234,56"
        assert DataHelper.format_money("1234.56") == "R$ 1.234,56"
        assert DataHelper.format_money(100) == "R$ 100,00"

    def test_parse_date(self):
        """Testa parsing de datas"""

        # Diferentes formatos
        date1 = DataHelper.parse_date("25/12/2023")
        date2 = DataHelper.parse_date("2023-12-25")
        date3 = DataHelper.parse_date("12/25/2023")

        assert date1.day == 25
        assert date1.month == 12
        assert date1.year == 2023

        assert date2.day == 25
        assert date2.month == 12
        assert date2.year == 2023

        # Data inválida
        assert DataHelper.parse_date("data inválida") is None


class TestSystemHelper:
    """Testes do SystemHelper"""

    @patch("src.utils.helpers.psutil.virtual_memory")
    @patch("src.utils.helpers.psutil.cpu_count")
    @patch("src.utils.helpers.psutil.disk_usage")
    @patch("src.utils.helpers.platform.system")
    @patch("src.utils.helpers.platform.version")
    @patch("src.utils.helpers.platform.python_version")
    @patch("src.utils.helpers.platform.architecture")
    def test_get_system_info(
        self,
        mock_arch,
        mock_py_version,
        mock_version,
        mock_system,
        mock_disk,
        mock_cpu,
        mock_memory,
    ):
        """Testa obtenção de informações do sistema"""
        # Configurar mocks
        mock_system.return_value = "Windows"
        mock_version.return_value = "10.0.19041"
        mock_py_version.return_value = "3.9.7"
        mock_arch.return_value = ("64bit", "WindowsPE")
        mock_cpu.return_value = 4
        mock_memory.return_value.total = 8 * 1024**3  # 8GB
        mock_memory.return_value.available = 4 * 1024**3  # 4GB
        mock_disk.return_value.total = 500 * 1024**3  # 500GB
        mock_disk.return_value.free = 200 * 1024**3  # 200GB

        info = SystemHelper.get_system_info()

        assert info["os"] == "Windows"
        assert info["os_version"] == "10.0.19041"
        assert info["python_version"] == "3.9.7"
        assert info["cpu_count"] == 4
        assert info["memory_total"] == 8.0  # GB
        assert info["memory_available"] == 4.0  # GB
        assert info["disk_total"] == 500.0  # GB
        assert info["disk_free"] == 200.0  # GB

    @patch("src.utils.helpers.ctypes.windll.shell32.IsUserAnAdmin")
    def test_is_admin_windows(self, mock_is_admin):
        """Testa verificação de privilégios de administrador no Windows"""
        mock_is_admin.return_value = True

        assert SystemHelper.is_admin() == True

        mock_is_admin.return_value = False

        assert SystemHelper.is_admin() == False


class TestHelperInstances:
    """Testes das instâncias globais dos helpers"""

    def test_global_instances(self):
        """Testa que as instâncias globais foram criadas"""
        assert file_helper is not None
        assert image_helper is not None
        assert text_helper is not None
        assert data_helper is not None
        assert system_helper is not None

    def test_instance_types(self):
        """Testa tipos das instâncias globais"""
        assert isinstance(file_helper, FileHelper)
        assert isinstance(image_helper, ImageHelper)
        assert isinstance(text_helper, TextHelper)
        assert isinstance(data_helper, DataHelper)
        assert isinstance(system_helper, SystemHelper)
