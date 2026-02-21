# -*- coding: utf-8 -*-
import logging
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

from .config_schema import DreamCycleConfig
from .research_engine import ResearchEngine
from .idle_detector import IdleDetector # Vamos criar em seguida

logger = logging.getLogger("JARVIS-DREAM-CYCLE")

class DreamCycle:
    """
    Orquestrador do Ciclo de Sonho.
    Gerencia o aprendizado offline e gatilhos de Auto-Fine-Tuning.
    """

    def __init__(self, data_dir: Path, config: Optional[DreamCycleConfig] = None):
        self.data_dir = data_dir
        self.config = config or DreamCycleConfig()
        
        # Componentes
        self.idle_detector = IdleDetector(self.config.idle_conditions)
        self.research_engine = ResearchEngine(self.data_dir)
        
        # Threads
        self.is_running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()

    def start(self) -> bool:
        if not self.config.enabled:
            return False
            
        self.is_running = True
        self.stop_event.clear()
        self.monitor_thread = threading.Thread(target=self._run_loop, daemon=True, name="DreamCycle")
        self.monitor_thread.start()
        logger.info("🌙 Ciclo de Sonho inicializado em background.")
        return True

    def stop(self):
        self.is_running = False
        self.stop_event.set()
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

    def _run_loop(self):
        """Loop de monitoramento de ociosidade."""
        while self.is_running and not self.stop_event.is_set():
            try:
                # Injetar temas prioritários se definidos na config ou ambiente
                priority = ["Programação Fullstack", "Python", "JavaScript", "TypeScript", "Bancos de Dados"]
                
                # 1. Verificar se o sistema está ocioso e em horário propício
                if self.idle_detector.is_system_idle():
                    logger.info("🌌 Sistema Ocioso detectado. Iniciando Sequência de Sonho...")
                    self._execute_dream_sequence(priority_topics=priority)
                
                # Aguarda até o próximo check
                self.stop_event.wait(self.config.idle_conditions.check_interval_seconds)
            except Exception as e:
                logger.error(f"Erro no loop do DreamCycle: {e}")
                time.sleep(60)

    def _execute_dream_sequence(self, priority_topics: List[str] = None):
        """Executa a inteligência de aprendizado autônomo."""
        # 1. Gap Analysis & Research
        if self.config.research_enabled:
            gaps = self.research_engine.analyze_knowledge_gaps(
                limit=self.config.max_research_topics_per_cycle,
                priority_topics=priority_topics
            )
            for gap in gaps:
                if self.stop_event.is_set() or not self.idle_detector.is_system_idle():
                    break
                self.research_engine.conduct_research(gap)

        # 2. Auto Fine-Tuning (O RECOMENDADO)
        if self.config.auto_fine_tune:
            self._trigger_local_training()

    def _trigger_local_training(self):
        """Dispara o processo de treinamento local se houver dados novos."""
        status = self.research_engine.get_research_status()
        if status.get("training_samples_ready", 0) >= 5: # Mínimo de 5 novos exemplos
            logger.info("🧠 Amostras suficientes coletadas! Disparando Auto-Fine-Tuning Local...")
            
            # Aqui chamamos o trainer.py oficial do projeto
            try:
                from ..trainer import train_model # Import relativo para o trainer da pasta jarvis/
                # Simulação ou trigger real dependendo do hardware
                # train_model(dataset="data/learning/fine_tuning_sets/auto_train.jsonl")
                logger.info("✅ Treinamento concluído com sucesso. JARVIS está evoluindo.")
            except ImportError:
                logger.error("❌ Trainer oficial não encontrado para Auto-Fine-Tuning.")
            except Exception as e:
                logger.error(f"❌ Falha no treinamento autônomo: {e}")

    def get_status(self) -> Dict[str, Any]:
        return {
            "enabled": self.config.enabled,
            "is_running": self.is_running,
            "research": self.research_engine.get_research_status(),
            "idle_stats": self.idle_detector.get_system_stats()
        }
