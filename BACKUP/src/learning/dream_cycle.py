# -*- coding: utf-8 -*-
# src/learning/dream_cycle.py
import logging
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any

from src.learning.config_schema import DreamCycleConfig
from src.learning.idle_detector import IdleDetector
from src.learning.training_scheduler import TrainingScheduler, TrainingTask
from src.learning.research_engine import ResearchEngine
from utils.safe_execute import safe_execute

logger = logging.getLogger("JARVIS-DREAM-CYCLE")


class DreamCycle:
    """
    Sistema de aprendizado autônomo que opera durante períodos de ociosidade.
    Versão refatorada com responsabilidades separadas.
    """
    
    def __init__(self, data_dir: Path, config: Optional[DreamCycleConfig] = None):
        self.data_dir = Path(data_dir)
        self.config = config or DreamCycleConfig()
        self.enabled = self.config.enabled
        
        # Componentes especializados
        self.idle_detector = IdleDetector(
            self.config.idle_conditions
        )
        self.training_scheduler = TrainingScheduler()
        self.research_engine = ResearchEngine(self.data_dir)
        
        # Estado do sistema
        self.is_running = False
        self.is_dreaming = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        logger.info("🌙 Dream Cycle inicializado (modo refatorado)")
    
    @safe_execute(default=False)
    def start(self) -> bool:
        """Inicia o monitoramento do Dream Cycle."""
        if not self.enabled:
            logger.info("🔒 Dream Cycle desabilitado na configuração")
            return False
            
        if self.is_running:
            logger.warning("⚠️ Dream Cycle já está rodando")
            return False
            
        self.stop_event.clear()
        self.is_running = True
        
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="DreamCycleMonitor"
        )
        self.monitor_thread.start()
        
        logger.info("🚀 Dream Cycle iniciado")
        return True
    
    @safe_execute()
    def stop(self):
        """Para o Dream Cycle."""
        if not self.is_running:
            return
            
        logger.info("🛑 Parando Dream Cycle...")
        self.stop_event.set()
        self.is_running = False
        self.is_dreaming = False
        
        # Parar componentes
        self.training_scheduler.stop_scheduler()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10.0)
            
        logger.info("✅ Dream Cycle parado")
    
    def _monitor_loop(self):
        """Loop principal de monitoramento."""
        logger.info("👀 Iniciando loop de monitoramento")
        
        while not self.stop_event.is_set() and self.is_running:
            try:
                # Verificar ociosidade do sistema
                if self.idle_detector.is_system_idle() and not self.is_dreaming:
                    self._start_dream_sequence()
                elif not self.idle_detector.is_system_idle() and self.is_dreaming:
                    self._stop_dream_sequence()
                
                # Esperar entre verificações
                self.stop_event.wait(
                    self.config.idle_conditions.check_interval_seconds
                )
                
            except Exception as e:
                logger.error(f"❌ Erro no loop de monitoramento: {e}")
                time.sleep(10)  # Recuperação segura
    
    @safe_execute()
    def _start_dream_sequence(self):
        """Inicia uma sessão de aprendizado autônomo."""
        logger.info("🌌 Iniciando sequência de sonho (aprendizado autônomo)")
        self.is_dreaming = True
        
        try:
            # 1. Executar treinamento agendado
            self._process_training_queue()
            
            # 2. Conduzir pesquisa autônoma (se habilitado)
            if self.config.research_enabled:
                self._conduct_autonomous_research()
                
            logger.info("✅ Sequência de sonho concluída")
            
        except Exception as e:
            logger.error(f"❌ Erro na sequência de sonho: {e}")
        finally:
            self.is_dreaming = False
    
    @safe_execute()
    def _stop_dream_sequence(self):
        """Interrompe a sessão de aprendizado autônomo."""
        logger.info("☀️ Interrompendo sequência de sonho")
        self.is_dreaming = False
        self.training_scheduler.stop_scheduler()
    
    @safe_execute()
    def _process_training_queue(self):
        """Processa a fila de treinamento durante o período ocioso."""
        # Iniciar agendador se não estiver rodando
        if not self.training_scheduler.is_running:
            self.training_scheduler.start_scheduler(self._training_callback)
    
    @safe_execute(default=False)
    def _training_callback(self, task: TrainingTask) -> bool:
        """
        Callback para execução de tarefas de treinamento.
        
        Args:
            task: Tarefa de treinamento a ser executada
            
        Returns:
            True se o treinamento foi bem-sucedido
        """
        try:
            logger.info(f"🎯 Executando treinamento: {task.task_id}")
            
            # TODO: Integrar com DistributedTrainer ou RealTrainer real
            # Por enquanto, apenas simular ou usar placeholder
            time.sleep(2)  # Simulação
            
            # Log do sucesso
            logger.info(f"✅ Treinamento {task.task_id} simulado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no treinamento {task.task_id}: {e}")
            return False
    
    @safe_execute()
    def _conduct_autonomous_research(self):
        """Conduz pesquisa autônoma durante o período ocioso."""
        logger.info("🔍 Iniciando pesquisa autônoma")
        
        # Identificar gaps de conhecimento
        gaps = self.research_engine.analyze_knowledge_gaps(
            self.config.max_research_topics_per_cycle
        )
        
        if not gaps:
            logger.info("💡 Nenhum gap de conhecimento identificado")
            return
        
        logger.info(f"📚 Identificados {len(gaps)} gaps de conhecimento")
        
        # Pesquisar gaps prioritários
        for i, gap in enumerate(gaps):
            if self.stop_event.is_set():  # Verificar se deve parar
                break
                
            logger.info(f"🔬 Pesquisando gap {i+1}/{len(gaps)}: {gap.get('topic', 'Unknown')}")
            self.research_engine.conduct_research(gap)
    
    @safe_execute(default=False)
    def add_training_task(self, task_config: Dict[str, Any]) -> bool:
        """
        Adiciona uma tarefa de treinamento à fila.
        
        Args:
            task_config: Configuração da tarefa de treinamento
            
        Returns:
            True se a tarefa foi adicionada com sucesso
        """
        return self.training_scheduler.schedule_training(task_config)
    
    @safe_execute(default={})
    def get_status(self) -> Dict[str, Any]:
        """Retorna o status atual do Dream Cycle."""
        return {
            'enabled': self.enabled,
            'is_running': self.is_running,
            'is_dreaming': self.is_dreaming,
            'idle_status': self.idle_detector.get_system_stats(),
            'queue_status': self.training_scheduler.get_queue_status(),
            'research_status': self.research_engine.get_research_status()
        }
