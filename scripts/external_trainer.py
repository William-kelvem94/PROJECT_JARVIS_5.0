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
- emotion: Treinamento de voz emocional
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
        from src.learning.trainer import LocalTrainer

        trainer = LocalTrainer(
            model_name=config.get('model_name', 'microsoft/DialoGPT-medium'),
            dataset_path=config.get('dataset_path'),
            output_dir=config.get('output_dir', 'models/fine_tuned'),
            training_args=config.get('training_args', {})
        )

        logger.info("🚀 Iniciando treinamento de LLM...")
        trainer.train()
        logger.info("✅ Treinamento de LLM concluído!")

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
        
        training_config = config.get('training_config', {})
        trainer.start_training(training_config)

        logger.info("🔗 Treinamento distribuído iniciado...")

    except Exception as e:
        logger.error(f"Erro no treinamento distribuído: {e}")
        return False
    return True

def train_continual(config: dict):
    """Treina aprendizado contínuo."""
    try:
        from src.learning.continual_learner import ContinualLearner

        learner = ContinualLearner(config.get('continual_config', {}))
        learner.start_learning_loop()

        logger.info("🔄 Aprendizado contínuo iniciado...")

    except Exception as e:
        logger.error(f"Erro no aprendizado contínuo: {e}")
        return False
    return True

def train_feedback(config: dict):
    """Treina loop de feedback."""
    try:
        from src.learning.feedback_loop import FeedbackLoop

        feedback = FeedbackLoop(config.get('feedback_config', {}))
        feedback.start_collection()

        logger.info("🔄 Loop de feedback iniciado...")

    except Exception as e:
        logger.error(f"Erro no loop de feedback: {e}")
        return False
    return True

def train_dream(config: dict):
    """Treina ciclo de sonho."""
    try:
        from src.learning.dream_cycle import DreamCycle

        dream = DreamCycle(config.get('dream_config', {}))
        dream.start_dream_cycle()

        logger.info("💭 Ciclo de sonho iniciado...")

    except Exception as e:
        logger.error(f"Erro no ciclo de sonho: {e}")
        return False
    return True

def train_emotion(config: dict):
    """Treina voz emocional."""
    try:
        from src.learning.emotion_voice_trainer import EmotionVoiceTrainer

        trainer = EmotionVoiceTrainer(config.get('emotion_config', {}))
        trainer.train_emotion_model()

        logger.info("🎭 Treinamento de voz emocional iniciado...")

    except Exception as e:
        logger.error(f"Erro no treinamento de voz emocional: {e}")
        return False
    return True

def train_study(config: dict, topic: str = None):
    """Treina baseado em estudo de tópicos."""
    try:
        from src.learning.knowledge_distiller import KnowledgeDistiller
        from pathlib import Path

        if not topic:
            topic = config.get('topic', 'Inteligência Artificial')

        # Inicializar distiller
        project_root = Path(config.get('project_root', '.'))
        distiller = KnowledgeDistiller(project_root=project_root)

        logger.info(f"📚 Iniciando estudo sobre: {topic}")

        # Gerar dados de treinamento baseados no tópico
        training_data = distiller.distill_knowledge(topic=topic)

        # Salvar dados gerados
        output_dir = Path(config.get('output_dir', 'data/learning/training_data'))
        output_dir.mkdir(parents=True, exist_ok=True)

        data_file = output_dir / f"study_{topic.replace(' ', '_')}.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Dados de estudo gerados e salvos em: {data_file}")
        logger.info(f"📊 Total de exemplos gerados: {len(training_data.get('examples', []))}")

        # Opcional: Iniciar treinamento com os dados gerados
        if config.get('auto_train', False):
            # Aqui poderia chamar train_llm com os dados gerados
            pass

    except Exception as e:
        logger.error(f"Erro no estudo: {e}")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Treinamento Externo JARVIS 5.0")
    parser.add_argument('--component', required=True,
                       choices=['llm', 'vision', 'distributed', 'continual',
                               'feedback', 'dream', 'emotion', 'study'],
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
        'emotion': train_emotion,
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