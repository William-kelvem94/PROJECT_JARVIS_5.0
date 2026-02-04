"""
Gerenciador de Coleta de Dados para Auto-Treinamento (Dataset Collector)
Salva capturas de tela, prompts e respostas da IA para fine-tuning futuro.
"""

import json
import os
import logging
from datetime import datetime
from pathlib import Path
from src.utils.config import config

logger = logging.getLogger(__name__)

class DatasetCollector:
    """Classe para coletar dados de treinamento enquanto o usuário usa o Jarvis"""

    def __init__(self):
        self.dataset_dir = Path(config.get_setting('app.data_dir', 'data')) / 'training_dataset'
        self.dataset_dir.mkdir(parents=True, exist_ok=True)
        self.logs_file = self.dataset_dir / 'history.jsonl'

    def collect(self, screenshot_path: str, prompt: str, response: str, provider: str):
        """Salva uma entrada no dataset de treinamento padrão"""
        try:
            entry = {
                'timestamp': datetime.now().isoformat(),
                'screenshot': str(screenshot_path),
                'prompt': prompt,
                'response': response,
                'provider': provider,
                'system_status': 'online' if provider != 'ollama' else 'offline'
            }

            with open(self.logs_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            
            logger.info(f"Dados coletados para treinamento: {len(prompt)} chars")
        except Exception as e:
            logger.error(f"Erro ao coletar dados para dataset: {e}")

    def save_sample(self, **kwargs):
        """Alias para o método collect, suportando argumentos nomeados"""
        # Mapeamento de argumentos se necessário
        image_path = kwargs.get('image_path', kwargs.get('screenshot_path'))
        prompt = kwargs.get('prompt')
        response = kwargs.get('response')
        source = kwargs.get('source', 'unknown')
        
        self.collect(image_path, prompt, response, source)

    def collect_correction(self, prompt: str, rejected_response: str, chosen_correction: str):
        """
        Salva uma correção explícita no formato DPO (Direct Preference Optimization)
        Ideal para treinar a IA a evitar erros específicos.
        """
        try:
            correction_file = self.dataset_dir / 'corrections.jsonl'
            entry = {
                'timestamp': datetime.now().isoformat(),
                'prompt': prompt,
                'rejected': rejected_response,
                'chosen': chosen_correction,
                'type': 'human_correction'
            }

            with open(correction_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            
            logger.info("Correção de usuário salva no dataset DPO.")
        except Exception as e:
            logger.error(f"Erro ao salvar correção: {e}")

# Instância global
dataset_collector = DatasetCollector()
