#!/usr/bin/env python3
"""
Script de Treinamento Externo para JARVIS 5.0
==============================================

Este script permite treinar componentes do JARVIS externamente,
sem iniciar o sistema completo, respeitando todas as regras
automatizadas de aprendizado.

Uso:
    python external_trainer.py --component [nome] --config [arquivo]

Componentes disponíveis:
- llm: Fine-tuning de LLMs (LoRA/QLoRA)
- vision: Treinamento de visão computacional
- distributed: Treinamento distribuído
- continual: Aprendizado contínuo
- feedback: Loop de feedback (RLHF/DPO)
- dream: Ciclo de sonho (treinamento noturno)
- study: Estudo baseado em tópicos/prompts (gera dados automaticamente)

Exemplo:
    python external_trainer.py --component llm --config config/training_config.yaml
    python external_trainer.py --component study --topic "Inteligência Artificial" --config config/training_config.yaml
"""

import argparse
import logging
import sys
from pathlib import Path
import yaml
import json
from typing import Optional

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EXTERNAL-TRAINER")

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def load_config(config_path: str) -> dict:
    """Carrega configuração de treinamento."""
    config_file = Path(config_path)
    if not config_file.exists():
        logger.error(f"Arquivo de configuração não encontrado: {config_path}")
        return {}

    with open(config_file, 'r', encoding='utf-8') as f:
        if config_file.suffix.lower() in ['.yaml', '.yml']:
            return yaml.safe_load(f)
        elif config_file.suffix.lower() == '.json':
            return json.load(f)
        else:
            logger.error("Formato de configuração não suportado (use .yaml ou .json)")
            return {}

def train_llm(config: dict):
    """Treina modelo de linguagem."""
    try:
        from src.learning.trainer import LocalTrainer, TrainingConfig
        from pathlib import Path

        # Criar TrainingConfig a partir do dict
        training_config = TrainingConfig(**config.get('training_args', {}))

        output_dir = Path(config.get('output_dir', 'models/fine_tuned'))

        trainer = LocalTrainer(
            config=training_config,
            output_dir=output_dir
        )

        # Dados de exemplo (em produção, carregar de arquivo)
        train_data = [
            {
                "instruction": "Responda de forma útil e precisa.",
                "input": "O que é inteligência artificial?",
                "output": "Inteligência Artificial (IA) é um campo da ciência da computação que visa criar máquinas capazes de realizar tarefas que normalmente requerem inteligência humana."
            }
        ]

        logger.info("🚀 Iniciando treinamento de LLM...")
        results = trainer.train(train_data=train_data)
        logger.info(f"✅ Treinamento de LLM concluído! Resultados: {results}")

    except Exception as e:
        logger.error(f"Erro no treinamento de LLM: {e}")
        return False
    return True

def train_vision(config: dict):
    """Treina modelo de visão."""
    try:
        from src.learning.vision_learner import VisionLearner
        from pathlib import Path

        model_dir = Path(config.get('model_dir', 'data/vision_learner'))
        base_model = config.get('base_model', 'models/vision/yolov8n.pt')
        epochs = config.get('epochs', 50)

        learner = VisionLearner(
            model_dir=model_dir,
            base_model=base_model
        )

        logger.info("👁️ Iniciando treinamento de visão...")
        results = learner.train_incremental(epochs=epochs)
        logger.info(f"✅ Treinamento de visão concluído! Resultados: {results}")

    except Exception as e:
        logger.error(f"Erro no treinamento de visão: {e}")
        return False
    return True

def train_distributed(config: dict):
    """Treina de forma distribuída."""
    try:
        from src.learning.distributed_trainer import DistributedTrainer, DistributedConfig

        dist_config = DistributedConfig(**config.get('distributed_config', {}))
        trainer = DistributedTrainer(dist_config)

        # Criar job de treinamento
        model_config = config.get('model_config', {'model_name': 'microsoft/DialoGPT-medium'})
        dataset_path = config.get('dataset_path', 'data/training_data')
        output_dir = config.get('output_dir', 'models/distributed')

        job_id = trainer.create_training_job(
            model_config=model_config,
            dataset_path=dataset_path,
            output_dir=output_dir
        )

        if job_id:
            logger.info("🔗 Iniciando treinamento distribuído...")
            success = trainer.start_training_job(job_id)
            if success:
                logger.info("✅ Treinamento distribuído concluído!")
            else:
                logger.error("❌ Falha no treinamento distribuído!")
                return False
        else:
            logger.error("❌ Falha ao criar job de treinamento!")
            return False

    except Exception as e:
        logger.error(f"Erro no treinamento distribuído: {e}")
        return False
    return True

def train_continual(config: dict):
    """Treina aprendizado contínuo."""
    try:
        from src.learning.continual_learner import get_continual_learner
        from pathlib import Path

        data_dir = Path(config.get('data_dir', 'data/learning'))
        learner = get_continual_learner(data_dir)

        logger.info("🔄 Iniciando aprendizado contínuo...")
        learner.start()
        logger.info("✅ Aprendizado contínuo iniciado!")

    except Exception as e:
        logger.error(f"Erro no aprendizado contínuo: {e}")
        return False
    return True

def train_feedback(config: dict):
    """Treina loop de feedback."""
    try:
        from src.learning.feedback_loop import FeedbackLoop
        from pathlib import Path

        data_dir = Path(config.get('data_dir', 'data/learning'))
        feedback = FeedbackLoop(data_dir)

        logger.info("🔄 Loop de feedback inicializado...")
        # O loop roda automaticamente ao registrar feedback
        logger.info("✅ Sistema de feedback pronto!")

    except Exception as e:
        logger.error(f"Erro no loop de feedback: {e}")
        return False
    return True

def train_dream(config: dict):
    """Treina ciclo de sonho."""
    try:
        from src.learning.dream_cycle import DreamCycle
        from pathlib import Path

        data_dir = Path(config.get('data_dir', 'data/learning'))
        dream = DreamCycle(data_dir=data_dir)

        logger.info("💭 Iniciando ciclo de sonho...")
        dream.start()
        logger.info("✅ Ciclo de sonho iniciado!")

    except Exception as e:
        logger.error(f"Erro no ciclo de sonho: {e}")
        return False
    return True

def train_emotion(config: dict):
    """Treina voz emocional."""
    logger.warning("🎭 Treinamento de voz emocional não implementado ainda")
    return True

def train_study(config: dict, topic: Optional[str] = None):
    """Treina baseado em estudo de tópicos."""
    try:
        from src.learning.knowledge_distiller import KnowledgeDistiller
        from pathlib import Path

        if not topic:
            topic = config.get('topic', 'Inteligência Artificial')

        # Garantir que topic é string
        topic = str(topic)

        data_dir = Path(config.get('data_dir', 'data/learning'))
        distiller = KnowledgeDistiller(data_dir=data_dir)

        logger.info(f"📚 Inicializando estudo sobre: {topic}")

        # Simular uma interação para destilar conhecimento
        user_command = f"Explique {topic} em detalhes"
        thought = f"Preciso fornecer uma explicação abrangente sobre {topic}"
        actions = [{"type": "research", "topic": topic}]
        
        distiller.distill_interaction(
            user_command=user_command,
            thought=thought,
            actions=actions,
            success=True
        )

        # Gerar dados simulados
        training_data = {
            "topic": topic,
            "examples": [
                {
                    "instruction": f"Explique o conceito de {topic}",
                    "input": "",
                    "output": f"{topic} é um campo fundamental da ciência da computação..."
                }
            ],
            "metadata": {
                "generated_at": "2026-02-13",
                "total_examples": 1,
                "method": "knowledge_distillation"
            }
        }

        # Salvar dados gerados
        output_dir = Path(config.get('output_dir', 'data/learning/training_data'))
        output_dir.mkdir(parents=True, exist_ok=True)

        data_file = output_dir / f"study_{topic.replace(' ', '_')}.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Dados de estudo gerados e salvos em: {data_file}")
        logger.info(f"📊 Total de exemplos gerados: {len(training_data.get('examples', []))}")

    except Exception as e:
        logger.error(f"Erro no estudo: {e}")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Treinamento Externo JARVIS 5.0")
    parser.add_argument('--component', required=True,
                       choices=['llm', 'vision', 'distributed', 'continual',
                               'feedback', 'dream', 'study'],
                       help='Componente a treinar')
    parser.add_argument('--config', required=True,
                       help='Arquivo de configuração (.yaml ou .json)')
    parser.add_argument('--topic', 
                       help='Tópico para estudo (usado com --component study)')

    args = parser.parse_args()

    # Carregar configuração
    config = load_config(args.config)
    if not config:
        sys.exit(1)

    # Mapear componentes para funções
    trainers = {
        'llm': train_llm,
        'vision': train_vision,
        'distributed': train_distributed,
        'continual': train_continual,
        'feedback': train_feedback,
        'dream': train_dream,
        'study': lambda c: train_study(c, args.topic)
    }

    # Executar treinamento
    success = trainers[args.component](config)

    if success:
        logger.info("🎉 Treinamento concluído com sucesso!")
        sys.exit(0)
    else:
        logger.error("❌ Falha no treinamento!")
        sys.exit(1)

if __name__ == "__main__":
    main()