"""
JARVIS AGI - Machine Learning Core
==================================

Este mÃ³dulo implementa o sistema de aprendizado contÃ­nuo e evoluÃ§Ã£o autÃ´noma do JARVIS.

Componentes:
- dataset_builder: Coleta e formata interaÃ§Ãµes para treinamento
- trainer: Fine-tuning local com LoRA/QLoRA
- dream_cycle: Treinamento automÃ¡tico durante perÃ­odos ociosos
- feedback_loop: RLHF simplificado com DPO
- predictive_engine: PrediÃ§Ã£o de necessidades do usuÃ¡rio
- vision_learner: Aprendizado few-shot para visÃ£o
"""

from pathlib import Path

# Learning data directory
LEARNING_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "learning"
INTERACTIONS_DIR = LEARNING_DATA_DIR / "interactions"
FEEDBACK_DIR = LEARNING_DATA_DIR / "feedback"
MODELS_DIR = LEARNING_DATA_DIR / "models"
CHECKPOINTS_DIR = LEARNING_DATA_DIR / "checkpoints"
TRAINING_DATA_DIR = LEARNING_DATA_DIR / "training_data"
VISION_SAMPLES_DIR = LEARNING_DATA_DIR / "vision_samples"

# Ensure directories exist
for directory in [
    LEARNING_DATA_DIR,
    INTERACTIONS_DIR,
    FEEDBACK_DIR,
    MODELS_DIR,
    CHECKPOINTS_DIR,
    TRAINING_DATA_DIR,
    VISION_SAMPLES_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)

__all__ = [
    "LEARNING_DATA_DIR",
    "INTERACTIONS_DIR",
    "FEEDBACK_DIR",
    "MODELS_DIR",
    "CHECKPOINTS_DIR",
    "TRAINING_DATA_DIR",
    "VISION_SAMPLES_DIR",
]
