"""
Preparador de Fine-Tuning (EvoluÃ§Ã£o Neural)
Converte o histÃ³rico do Jarvis em formato de treinamento para modelos locais.
"""

import json
import logging
from pathlib import Path
from src.utils.config import config

logger = logging.getLogger(__name__)

class FineTunePreparator:
    """Prepara os dados coletados pelo Jarvis para treinamento de redes neurais"""

    def __init__(self):
        self.data_dir = Path(config.get_setting('app.data_dir', 'data')) / 'training_dataset'
        self.history_file = self.data_dir / 'history.jsonl'
        self.output_file = self.data_dir / 'fine_tune_data.json'

    def prepare_for_llama(self):
        """Converte para o formato Alpaca/Instruction usado para treinar LLMs"""
        if not self.history_file.exists():
            return "Nenhum dado coletado ainda, senhor."

        try:
            dataset = []
            with open(self.history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line)
                    dataset.append({
                        "instruction": "VocÃª Ã© o Jarvis, assistente virtual. Responda ao comando baseado na tela.",
                        "input": data['prompt'],
                        "output": data['response']
                    })

            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(dataset, f, indent=2, ensure_ascii=False)
            
            return f"Dataset neural preparado com {len(dataset)} exemplos em {self.output_file}"
        except Exception as e:
            logger.error(f"Erro ao preparar dataset: {e}")
            return f"Erro na preparaÃ§Ã£o: {str(e)}"

# InstÃ¢ncia global
fine_tune_preparator = FineTunePreparator()
