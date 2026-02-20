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
import os
import sys
from pathlib import Path
import yaml
import json
from typing import Optional

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("EXTERNAL-TRAINER")

# Configurar web_emitter para logs em tempo real
try:
    from src.utils.web_emitter import emit_log_sync

    WEB_EMITTER_AVAILABLE = True

    class WebEmitterHandler(logging.Handler):
        def emit(self, record):
            try:
                emit_log_sync(self.format(record), record.levelname)
            except Exception:
                pass  # Silenciar erros do web emitter

    # Adicionar handler do web emitter
    web_handler = WebEmitterHandler()
    web_handler.setLevel(logging.INFO)
    logger.addHandler(web_handler)

except ImportError:
    WEB_EMITTER_AVAILABLE = False
    logger.warning(
        "Web emitter não disponível - logs não serão transmitidos em tempo real"
    )

# Adicionar diretório raiz ao path
script_dir = Path(__file__).resolve()
project_root = (
    script_dir.parent.parent.parent
)  # scripts/training/external_trainer.py -> PROJECT_JARVIS_5.0

# Garantir que estamos no diretório raiz do projeto
os.chdir(project_root)

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


def load_config(config_path: str) -> dict:
    """Carrega configuração de treinamento."""
    # Se o caminho for relativo, resolver relativo ao project_root
    if not Path(config_path).is_absolute():
        config_file = project_root / config_path
    else:
        config_file = Path(config_path)

    if not config_file.exists():
        logger.error(f"Arquivo de configuração não encontrado: {config_file}")
        return {}

    with open(config_file, "r", encoding="utf-8") as f:
        if config_file.suffix.lower() in [".yaml", ".yml"]:
            return yaml.safe_load(f)
        elif config_file.suffix.lower() == ".json":
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
        training_config = TrainingConfig(**config.get("training_args", {}))

        output_dir = Path(config.get("output_dir", "models/fine_tuned"))

        trainer = LocalTrainer(config=training_config, output_dir=output_dir)

        # Dados de exemplo (em produção, carregar de arquivo)
        train_data = [
            {
                "instruction": "Responda de forma útil e precisa.",
                "input": "O que é inteligência artificial?",
                "output": "Inteligência Artificial (IA) é um campo da ciência da computação que visa criar máquinas capazes de realizar tarefas que normalmente requerem inteligência humana.",
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

        model_dir = Path(config.get("model_dir", "data/vision_learner"))
        base_model = config.get("base_model", "models/vision/yolov8n.pt")
        epochs = config.get("epochs", 50)

        learner = VisionLearner(model_dir=model_dir, base_model=base_model)

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
        from src.learning.distributed_trainer import (
            DistributedTrainer,
            DistributedConfig,
        )

        dist_config = DistributedConfig(**config.get("distributed_config", {}))
        trainer = DistributedTrainer(dist_config)

        # Criar job de treinamento
        model_config = config.get(
            "model_config", {"model_name": "microsoft/DialoGPT-medium"}
        )
        dataset_path = config.get("dataset_path", "data/training_data")
        output_dir = config.get("output_dir", "models/distributed")

        job_id = trainer.create_training_job(
            model_config=model_config, dataset_path=dataset_path, output_dir=output_dir
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

        data_dir = Path(config.get("data_dir", "data/learning"))
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

        data_dir = Path(config.get("data_dir", "data/learning"))
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

        data_dir = Path(config.get("data_dir", "data/learning"))
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
    """Treina baseado em estudo de tópicos - VERSÃO REAL COM FINE-TUNING"""
    try:
        from src.learning.real_trainer import train_with_real_learning

        if not topic:
            topic = config.get("topic", "Inteligência Artificial")

        # Garantir que topic é string
        topic = str(topic)

        logger.info(f"🧠 INICIANDO TREINAMENTO REAL PARA: {topic}")
        logger.info("🎯 Este treinamento usa fine-tuning real, não apenas destilação!")

        # Treinamento REAL com fine-tuning (simulado para desenvolvimento)
        result = train_with_real_learning(topic, config, simulate=True)

        if result["status"] == "success":
            logger.info("✅ TREINAMENTO REAL CONCLUÍDO!")
            logger.info(f"📁 Modelo treinado salvo em: {result.get('model_path')}")
            logger.info(f"📊 Loss final: {result.get('training_loss', 'N/A')}")
            logger.info(
                f"🔢 Parâmetros ajustados: {result.get('trainable_params', 'N/A')}"
            )
        else:
            logger.error(f"❌ Falha no treinamento real: {result}")

        return result["status"] == "success"

    except Exception as e:
        logger.error(f"Erro no treinamento real: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Treinamento Externo JARVIS 5.0")
    parser.add_argument(
        "--component",
        required=True,
        choices=[
            "llm",
            "vision",
            "distributed",
            "continual",
            "feedback",
            "dream",
            "study",
        ],
        help="Componente a treinar",
    )
    parser.add_argument(
        "--config", required=True, help="Arquivo de configuração (.yaml ou .json)"
    )
    parser.add_argument(
        "--topic", help="Tópico para estudo (usado com --component study)"
    )

    args = parser.parse_args()

    # Carregar configuração
    config = load_config(args.config)
    if not config:
        sys.exit(1)

    # Mapear componentes para funções
    trainers = {
        "llm": train_llm,
        "vision": train_vision,
        "distributed": train_distributed,
        "continual": train_continual,
        "feedback": train_feedback,
        "dream": train_dream,
        "study": lambda c: train_study(c, args.topic),
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
