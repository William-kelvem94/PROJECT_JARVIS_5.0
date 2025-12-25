#!/usr/bin/env python3
"""
Testes básicos para JARVIS 5.0
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from jarvis.core.config import ConfigManager
from jarvis.core.logger import Logger
from jarvis.voice.natural_speech import NaturalSpeechProcessor


class TestConfigManager(unittest.TestCase):
    """Testes para o gerenciador de configuração"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.config = ConfigManager()
    
    def test_get_default_config(self):
        """Testa se configuração padrão é carregada"""
        rate = self.config.get('voice.rate')
        self.assertIsNotNone(rate)
        self.assertIsInstance(rate, int)
        self.assertGreater(rate, 0)
    
    def test_set_and_get_config(self):
        """Testa definir e obter configuração"""
        test_value = 200
        self.config.set('voice.rate', test_value)
        
        retrieved_value = self.config.get('voice.rate')
        self.assertEqual(retrieved_value, test_value)
    
    def test_get_with_default(self):
        """Testa obter valor com padrão"""
        default_value = "test_default"
        value = self.config.get('nonexistent.key', default_value)
        self.assertEqual(value, default_value)
    
    def test_nested_config(self):
        """Testa configuração aninhada"""
        self.config.set('test.nested.value', 42)
        value = self.config.get('test.nested.value')
        self.assertEqual(value, 42)


class TestLogger(unittest.TestCase):
    """Testes para o sistema de logging"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.logger = Logger("TEST", "DEBUG")
    
    def test_logger_creation(self):
        """Testa criação do logger"""
        self.assertIsNotNone(self.logger.logger)
        self.assertEqual(self.logger.logger.name, "TEST")
    
    def test_log_methods(self):
        """Testa métodos de log"""
        # Estes testes apenas verificam se os métodos existem e não geram erro
        self.logger.debug("Debug message")
        self.logger.info("Info message")
        self.logger.warning("Warning message")
        self.logger.error("Error message")
        self.logger.critical("Critical message")
    
    def test_special_log_methods(self):
        """Testa métodos especiais de log"""
        self.logger.voice_event("test_event", "test_details")
        self.logger.command_event("test_command", "executed")
        self.logger.performance_log("test_operation", 0.5)


class TestNaturalSpeechProcessor(unittest.TestCase):
    """Testes para o processador de fala natural"""
    
    def setUp(self):
        """Setup para cada teste"""
        config = {
            'natural_speech': {
                'use_fillers': True,
                'use_hesitations': True,
                'use_breathing': True,
                'emotion_detection': True,
                'conversation_flow': True
            }
        }
        self.processor = NaturalSpeechProcessor(config)
    
    def test_process_text_basic(self):
        """Testa processamento básico de texto"""
        text = "Olá, como você está?"
        processed = self.processor.process_text(text)
        
        self.assertIsInstance(processed, str)
        self.assertGreater(len(processed), 0)
    
    def test_process_text_with_emotion(self):
        """Testa processamento com emoção"""
        text = "Tudo funcionando perfeitamente!"
        processed = self.processor.process_text(text, emotion='entusiasta')
        
        self.assertIsInstance(processed, str)
        self.assertGreater(len(processed), 0)
    
    def test_break_into_phrases(self):
        """Testa quebra em frases"""
        text = "Esta é uma frase longa que deveria ser quebrada em partes menores para facilitar a fala natural."
        phrases = self.processor.break_into_phrases(text)
        
        self.assertIsInstance(phrases, list)
        self.assertGreater(len(phrases), 0)
        
        # Verificar se todas as frases são strings não vazias
        for phrase in phrases:
            self.assertIsInstance(phrase, str)
            self.assertGreater(len(phrase.strip()), 0)
    
    def test_process_markers(self):
        """Testa processamento de marcadores"""
        text_with_markers = "Olá [pausa_curta] como você está?"
        clean_text, pause = self.processor.process_markers(text_with_markers)
        
        self.assertNotIn('[pausa_curta]', clean_text)
        self.assertGreater(pause, 0)
    
    def test_calculate_contextual_speed(self):
        """Testa cálculo de velocidade contextual"""
        phrase = "Esta é uma frase de teste"
        base_speed = 180
        
        speed = self.processor.calculate_contextual_speed(phrase, base_speed)
        
        self.assertIsInstance(speed, int)
        self.assertGreater(speed, 0)
        self.assertLess(speed, 400)  # Velocidade razoável
    
    def test_calculate_contextual_pitch(self):
        """Testa cálculo de pitch contextual"""
        phrase = "Esta é uma frase de teste"
        base_pitch = 50
        
        pitch = self.processor.calculate_contextual_pitch(phrase, base_pitch)
        
        self.assertIsInstance(pitch, int)
        self.assertGreaterEqual(pitch, 20)  # Pitch mínimo
        self.assertLessEqual(pitch, 100)  # Pitch máximo


class TestIntegration(unittest.TestCase):
    """Testes de integração básicos"""
    
    @patch('jarvis.voice.speech_engine.pyttsx3')
    @patch('jarvis.voice.recognition_engine.sr')
    def test_assistant_creation(self, mock_sr, mock_pyttsx3):
        """Testa criação do assistente (com mocks)"""
        # Mock dos engines
        mock_pyttsx3.init.return_value = Mock()
        mock_sr.Recognizer.return_value = Mock()
        
        try:
            from jarvis import JarvisAssistant
            assistant = JarvisAssistant()
            
            # Verificar se assistente foi criado
            self.assertIsNotNone(assistant)
            self.assertIsNotNone(assistant.config)
            self.assertIsNotNone(assistant.speech_engine)
            self.assertIsNotNone(assistant.recognition_engine)
            
        except Exception as e:
            self.fail(f"Falha ao criar assistente: {e}")
    
    def test_config_integration(self):
        """Testa integração entre componentes via configuração"""
        config_manager = ConfigManager()
        
        # Testar se configuração tem todas as seções necessárias
        required_sections = ['voice', 'recognition', 'system', 'commands', 'natural_speech']
        
        for section in required_sections:
            value = config_manager.get(section)
            self.assertIsNotNone(value, f"Seção '{section}' não encontrada na configuração")
            self.assertIsInstance(value, dict, f"Seção '{section}' deve ser um dicionário")


def run_tests():
    """Executa todos os testes"""
    print("JARVIS 5.0 - Executando Testes")
    print("=" * 40)
    
    # Criar suite de testes
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Adicionar testes
    suite.addTests(loader.loadTestsFromTestCase(TestConfigManager))
    suite.addTests(loader.loadTestsFromTestCase(TestLogger))
    suite.addTests(loader.loadTestsFromTestCase(TestNaturalSpeechProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Mostrar resultado
    if result.wasSuccessful():
        print("\nTodos os testes passaram!")
        return True
    else:
        print(f"\n{len(result.failures)} teste(s) falharam")
        print(f"{len(result.errors)} erro(s) encontrado(s)")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
