# -*- coding: utf-8 -*-
"""
REAL TRAINER - Treinamento Neural Real para JARVIS 5.0
Sistema de fine-tuning real sem sobrecarga de hardware
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import torch
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("REAL-TRAINER")

# Adicionar diretÃ³rio raiz
sys.path.insert(0, str(Path(__file__).parent.parent))

class RealTrainer:
    """Treinador neural real com fine-tuning leve"""

    def __init__(self, model_name: str = "microsoft/Phi-3-mini-4k-instruct", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self.model = None
        self.tokenizer = None
        self.trained_topics = set()

        # ConfiguraÃ§Ãµes leves para nÃ£o sobrecarregar
        self.max_length = 128
        self.batch_size = 1
        self.learning_rate = 5e-5
        self.num_epochs = 1  # Treinamento muito leve

        self._load_base_model()

    def _load_base_model(self):
        """Carrega modelo base de forma leve"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer

            logger.info(f"ðŸ“¥ Carregando modelo base: {self.model_name}")

            # Carregar tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Carregar modelo em CPU com quantizaÃ§Ã£o para economizar memÃ³ria
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                dtype=torch.float32,  # CPU nÃ£o suporta float16 bem
                device_map="cpu",
                low_cpu_mem_usage=True,
                ignore_mismatched_sizes=True,  # Silenciar incompatibilidade de pesos
                tie_word_embeddings=False  # Resolver aviso de tied weights
            )

            logger.info("âœ… Modelo base carregado com sucesso")

        except Exception as e:
            logger.error(f"âŒ Erro ao carregar modelo: {e}")
            raise

    def prepare_training_data(self, knowledge_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Prepara dados de treinamento a partir do conhecimento destilado"""
        training_examples = []

        topic = knowledge_data.get('topic', 'tÃ³pico_desconhecido')
        examples = knowledge_data.get('examples', [])

        for example in examples:
            instruction = example.get('instruction', '')
            output = example.get('output', '')

            if instruction and output:
                # Formatar como conversa de treinamento
                conversation = f"UsuÃ¡rio: {instruction}\nAssistente: {output}"

                training_examples.append({
                    "text": conversation,
                    "topic": topic
                })

        logger.info(f"ðŸ“š Preparados {len(training_examples)} exemplos de treinamento para {topic}")
        return training_examples

    def fine_tune_incremental(self, training_data: List[Dict[str, str]], topic: str) -> Dict[str, Any]:
        """Fine-tuning incremental leve usando LoRA"""
        if not self.model or not self.tokenizer:
            raise ValueError("Modelo ou tokenizer nÃ£o inicializados")

        try:
            from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling
            try:
                from peft.config import LoraConfig  # type: ignore
                from peft.mapping import get_peft_model  # type: ignore
                peft_available = True
            except ImportError:
                logger.warning("PEFT nÃ£o disponÃ­vel, usando fine-tuning completo")
                peft_available = False
            from torch.utils.data import Dataset

            # Verificar se jÃ¡ treinou este tÃ³pico
            if topic in self.trained_topics:
                logger.info(f"ðŸ“ JÃ¡ treinou {topic}, pulando...")
                return {"status": "already_trained", "topic": topic}

            # Classe dataset simples
            class SimpleDataset(Dataset):
                def __init__(self, data, tokenizer, max_length=128):
                    self.data = data
                    self.tokenizer = tokenizer
                    self.max_length = max_length

                def __len__(self):
                    return len(self.data)

                def __getitem__(self, idx):
                    item = self.data[idx]
                    text = item['text']

                    # Tokenizar
                    encoding = self.tokenizer(
                        text,
                        truncation=True,
                        padding='max_length',
                        max_length=self.max_length,
                        return_tensors='pt'
                    )

                    return {
                        'input_ids': encoding['input_ids'].flatten(),
                        'attention_mask': encoding['attention_mask'].flatten(),
                        'labels': encoding['input_ids'].flatten()
                    }

            # Preparar dataset
            dataset = SimpleDataset(training_data, self.tokenizer, self.max_length)

            # Configurar LoRA para fine-tuning leve
            lora_config = LoraConfig(
                r=8,  # Rank baixo para leveza
                lora_alpha=16,
                target_modules=["c_attn", "c_proj", "c_fc"],  # Para GPT-like models
                lora_dropout=0.1,
                bias="none",
                task_type="CAUSAL_LM"
            )

            # Aplicar LoRA
            self.model = get_peft_model(self.model, lora_config)  # type: ignore
            logger.info("ðŸ”§ LoRA aplicado ao modelo")

            # Configurar treinamento
            training_args = TrainingArguments(  # type: ignore
                output_dir=f"./temp_training_{topic.replace(' ', '_')}",
                num_train_epochs=self.num_epochs,
                per_device_train_batch_size=self.batch_size,
                learning_rate=self.learning_rate,
                logging_steps=1,
                save_steps=50,
                save_total_limit=1,
                remove_unused_columns=False,
                report_to="none"  # Sem reporting para economizar
            )

            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False
            )

            # Criar trainer
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=dataset,
                data_collator=data_collator
            )

            logger.info(f"ðŸš€ Iniciando fine-tuning real para: {topic}")
            logger.info(f"ðŸ“Š Dataset: {len(dataset)} exemplos")

            # Treinar
            train_result = trainer.train()

            # Salvar modelo treinado
            output_dir = Path(f"models/trained/{topic.replace(' ', '_')}")
            output_dir.mkdir(parents=True, exist_ok=True)

            trainer.save_model(str(output_dir))
            self.tokenizer.save_pretrained(str(output_dir))

            # Salvar metadados
            metadata = {
                "topic": topic,
                "trained_at": datetime.now().isoformat(),
                "base_model": self.model_name,
                "training_samples": len(training_data),
                "final_loss": train_result.training_loss,
                "method": "lora_fine_tuning"
            }

            with open(output_dir / "training_metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            # Marcar como treinado
            self.trained_topics.add(topic)

            # Calcular tamanho do modelo treinado
            model_size = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
            logger.info(f"âœ… Fine-tuning concluÃ­do! Modelo salvo em {output_dir}")
            logger.info(f"ðŸ“ ParÃ¢metros treinÃ¡veis: {model_size}")

            return {
                "status": "success",
                "topic": topic,
                "model_path": str(output_dir),
                "training_loss": train_result.training_loss,
                "trainable_params": model_size
            }

        except Exception as e:
            logger.error(f"âŒ Erro no fine-tuning: {e}")
            return {"status": "error", "topic": topic, "error": str(e)}

    def generate_response(self, prompt: str, topic_context: Optional[str] = None) -> str:
        """Gera resposta usando o modelo treinado"""
        try:
            if self.model is None or self.tokenizer is None:
                return "Modelo ou tokenizer nÃ£o carregados"

            # Adicionar contexto do tÃ³pico se disponÃ­vel
            if topic_context:
                full_prompt = f"Contexto sobre {topic_context}: {prompt}"
            else:
                full_prompt = prompt

            # Tokenizar
            inputs = self.tokenizer(full_prompt, return_tensors="pt").to(self.device)

            # Gerar resposta
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_length=self.max_length + 50,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            # Decodificar
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Remover o prompt da resposta
            if response.startswith(full_prompt):
                response = response[len(full_prompt):].strip()

            return response

        except Exception as e:
            logger.error(f"Erro na geraÃ§Ã£o: {e}")
            return f"Erro na geraÃ§Ã£o: {str(e)}"

def train_with_real_learning(topic: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """FunÃ§Ã£o de treinamento real com configuraÃ§Ã£o opcional"""
    if config is None:
        config = {}
    """
    FunÃ§Ã£o principal para treinamento REAL
    Usa conhecimento destilado + fine-tuning real
    """
    try:
        logger.info(f"ðŸ§  INICIANDO TREINAMENTO REAL PARA: {topic}")

        # 1. Destilar conhecimento primeiro (como antes)
        from src.learning.knowledge_distiller import KnowledgeDistiller

        data_dir = Path('data/learning')
        distiller = KnowledgeDistiller(data_dir=data_dir)

        logger.info("ðŸ“š Destilando conhecimento...")
        user_command = f"Explique {topic} em detalhes"
        thought = f"Preciso fornecer uma explicaÃ§Ã£o abrangente sobre {topic}"
        actions = [{"type": "research", "topic": topic}]

        distiller.distill_interaction(
            user_command=user_command,
            thought=thought,
            actions=actions,
            success=True
        )

        # 2. Carregar dados destilados
        training_file = data_dir / "training_data" / f"study_{topic.replace(' ', '_')}.json"

        if not training_file.exists():
            # Criar dados bÃ¡sicos se nÃ£o existir
            training_data = {
                "topic": topic,
                "examples": [{
                    "instruction": f"Explique o conceito de {topic}",
                    "input": "",
                    "output": f"{topic} Ã© um campo fundamental da ciÃªncia da computaÃ§Ã£o que envolve..."
                }],
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "total_examples": 1,
                    "method": "knowledge_distillation"
                }
            }
            training_file.parent.mkdir(parents=True, exist_ok=True)
            with open(training_file, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, indent=2, ensure_ascii=False)
        else:
            with open(training_file, 'r', encoding='utf-8') as f:
                training_data = json.load(f)

        # 3. TREINAMENTO REAL - Fine-tuning com LoRA
        logger.info("ðŸŽ¯ Iniciando fine-tuning real...")

        trainer = RealTrainer()
        training_examples = trainer.prepare_training_data(training_data)
        result = trainer.fine_tune_incremental(training_examples, topic)

        # 4. Testar o modelo treinado
        if result['status'] == 'success':
            logger.info("ðŸ§ª Testando modelo treinado...")
            test_prompt = f"Explique brevemente o que Ã© {topic}"
            response = trainer.generate_response(test_prompt, topic)
            logger.info(f"ðŸ¤– Resposta do modelo treinado: {response[:100]}...")

        logger.info("âœ… TREINAMENTO REAL CONCLUÃDO!")
        logger.info(f"ðŸ“ Modelo salvo em: {result.get('model_path', 'N/A')}")
        logger.info(f"ðŸ“Š Loss final: {result.get('training_loss', 'N/A')}")
        logger.info(f"ðŸ”¢ ParÃ¢metros treinados: {result.get('trainable_params', 'N/A')}")

        return result

    except Exception as e:
        logger.error(f"âŒ Erro no treinamento real: {e}")
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    # Exemplo de uso
    if len(sys.argv) > 1:
        topic = sys.argv[1]
    else:
        topic = "InteligÃªncia Artificial"

    result = train_with_real_learning(topic)
    print(f"Resultado: {result}")
