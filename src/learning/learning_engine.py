"""
JARVIS 5.0 - Learning Engine (Singularity Core)
================================================
Módulo unificado para inicializar e gerenciar todos os sistemas de aprendizado:
- Continual Learner (Auto-Training)
- Feedback Loop (RLHF/DPO)
- Knowledge Distiller (Golden Commands)
- Dream Cycle (Nighttime Training)

Este é o "motor evolutivo" que transforma JARVIS de assistente para AGI.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

logger = logging.getLogger("JARVIS-LEARNING-ENGINE")

class LearningEngine:
    """
    Orquestrador central dos sistemas de aprendizado.
    Inicializa e gerencia todos os componentes de forma coordenada.
    """
    
    def __init__(self, project_root: Path, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Learning Engine.
        
        Args:
            project_root: Diretório raiz do projeto
            config: Configuração de learning (se None, carrega de ai_config.yaml)
        """
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.learning_dir = self.data_dir / "learning"
        self.learning_dir.mkdir(parents=True, exist_ok=True)
        
        # Load config
        if config is None:
            config = self._load_config()
        
        self.config = config.get('continual_learning', {})
        self.enabled = self.config.get('enabled', False)
        
        # Components (Lazy initialization)
        self.feedback_loop = None
        self.continual_learner = None
        self.knowledge_distiller = None
        self.dream_cycle = None
        
        # Status tracking
        self.is_initialized = False
        self.components_status = {
            'feedback_loop': False,
            'continual_learner': False,
            'knowledge_distiller': False,
            'dream_cycle': False
        }
        
        logger.info(f"🧠 Learning Engine created (Enabled: {self.enabled})")
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configurações do ai_config.yaml"""
        config_path = self.project_root / "config" / "ai_config.yaml"
        
        if not config_path.exists():
            logger.warning(f"⚠️ Config file not found: {config_path}")
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            return {}
    
    def initialize(self) -> bool:
        """
        Inicializa todos os sistemas de aprendizado habilitados.
        
        Returns:
            True se inicialização bem-sucedida, False caso contrário
        """
        if not self.enabled:
            logger.info("🔒 Learning systems DISABLED in config. Skipping initialization.")
            return False
        
        if self.is_initialized:
            logger.info("✅ Learning Engine already initialized")
            return True
        
        logger.info("🚀 [LEARNING ENGINE] Initializing autonomous learning systems...")
        
        success = True
        
        # 1. Feedback Loop (Foundation)
        if self.config.get('feedback_loop', {}).get('enabled', True):
            success &= self._init_feedback_loop()
        
        # 2. Knowledge Distiller (Golden Commands)
        if self.config.get('knowledge_distiller', {}).get('enabled', True):
            success &= self._init_knowledge_distiller()
        
        # 3. Continual Learner (Auto-Training)
        if self.config.get('continual_learner', {}).get('enabled', True):
            success &= self._init_continual_learner()
        
        # 4. Dream Cycle (Nighttime Training)
        if self.config.get('dream_cycle', {}).get('enabled', True):
            success &= self._init_dream_cycle()
        
        self.is_initialized = success
        
        if success:
            logger.info("✅ [LEARNING ENGINE] All systems ONLINE - JARVIS is now self-evolving")
            self._print_status()
        else:
            logger.warning("⚠️ [LEARNING ENGINE] Some systems failed to initialize")
        
        return success
    
    def _init_feedback_loop(self) -> bool:
        """Inicializa sistema de coleta de feedback"""
        try:
            from src.learning.feedback_loop import FeedbackDatabase
            
            config = self.config.get('feedback_loop', {})
            db_path = self.learning_dir / "feedback.db"
            
            self.feedback_loop = FeedbackDatabase(db_path)
            self.components_status['feedback_loop'] = True
            
            logger.info("✅ Feedback Loop initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Feedback Loop: {e}")
            return False
    
    def _init_knowledge_distiller(self) -> bool:
        """Inicializa Knowledge Distiller (Golden Commands)"""
        try:
            from src.learning.knowledge_distiller import KnowledgeDistiller
            
            self.knowledge_distiller = KnowledgeDistiller(self.data_dir)
            self.components_status['knowledge_distiller'] = True
            
            logger.info("✅ Knowledge Distiller initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Knowledge Distiller: {e}")
            return False
    
    def _init_continual_learner(self) -> bool:
        """Inicializa Continual Learner (Auto-Training)"""
        try:
            from src.learning.continual_learner import ContinualLearner
            
            config = self.config.get('continual_learner', {})
            feedback_threshold = config.get('feedback_threshold', 100)
            check_interval = config.get('check_interval', 3600)
            
            self.continual_learner = ContinualLearner(
                data_dir=self.data_dir,
                feedback_threshold=feedback_threshold,
                check_interval=check_interval
            )
            
            # Start autonomous monitoring loop
            self.continual_learner.start()
            self.components_status['continual_learner'] = True
            
            logger.info(f"✅ Continual Learner initialized (Threshold: {feedback_threshold} interactions)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Continual Learner: {e}")
            return False
    
    def _init_dream_cycle(self) -> bool:
        """Inicializa Dream Cycle (Nighttime Training)"""
        try:
            from src.learning.dream_cycle import DreamCycle, IdleConditions
            
            config = self.config.get('dream_cycle', {})
            
            # Build idle conditions from config
            idle_conditions = IdleConditions(
                max_cpu_percent=config.get('max_cpu_percent', 20.0),
                max_memory_percent=config.get('max_memory_percent', 80.0),
                min_idle_duration_seconds=config.get('min_idle_duration', 300),
                night_start_hour=config.get('night_start_hour', 22),
                night_end_hour=config.get('night_end_hour', 6),
                check_interval_seconds=config.get('check_interval', 60)
            )
            
            self.dream_cycle = DreamCycle(
                data_dir=self.data_dir,
                idle_conditions=idle_conditions
            )
            
            # Start autonomous monitoring
            self.dream_cycle.start()
            self.components_status['dream_cycle'] = True
            
            logger.info(f"✅ Dream Cycle initialized (Active: {config.get('night_start_hour')}h-{config.get('night_end_hour')}h)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Dream Cycle: {e}")
            return False
    
    def record_interaction(
        self,
        user_input: str,
        ai_response: str,
        feedback_value: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Registra uma interação para aprendizado.
        
        Args:
            user_input: Comando do usuário
            ai_response: Resposta do agente
            feedback_value: Valor de feedback (-1.0 a 1.0) se explícito
            metadata: Dados adicionais (latência, provider usado, etc)
        """
        if not self.feedback_loop:
            return
        
        try:
            # Coleta feedback implícito se não houver explícito
            if feedback_value is None:
                # TODO: Implementar heurísticas de feedback implícito
                # - Tempo de resposta
                # - Usuário repetiu comando?
                # - Houve interrupção?
                feedback_value = 0.5  # Neutro por padrão
            
            from src.learning.feedback_loop import FeedbackEntry
            import hashlib
            import time
            from datetime import datetime
            
            interaction_id = hashlib.md5(
                f"{user_input}{time.time()}".encode()
            ).hexdigest()[:16]
            
            feedback_id = hashlib.md5(
                f"{interaction_id}{time.time()}".encode()
            ).hexdigest()[:16]
            
            entry = FeedbackEntry(
                feedback_id=feedback_id,
                interaction_id=interaction_id,
                user_input=user_input,
                ai_response=ai_response,
                feedback_type='implicit',
                feedback_value=feedback_value,
                timestamp=datetime.now().isoformat(),
                metadata=metadata or {}
            )
            
            self.feedback_loop.add_feedback(entry)
            
            # Se foi uma interação bem-sucedida, pode ser um Golden Command
            if feedback_value > 0.7 and self.knowledge_distiller:
                self.knowledge_distiller.distill_interaction(
                    user_command=user_input,
                    thought="",  # TODO: Capturar raciocínio do agente
                    actions=[],  # TODO: Capturar ações executadas
                    success=True
                )
            
        except Exception as e:
            logger.error(f"❌ Failed to record interaction: {e}")
    
    def record_explicit_feedback(
        self,
        interaction_id: str,
        feedback_value: float,
        correction: Optional[str] = None
    ):
        """
        Registra feedback explícito do usuário (👍/👎).
        
        Args:
            interaction_id: ID da interação
            feedback_value: -1.0 (ruim) a 1.0 (excelente)
            correction: Correção fornecida pelo usuário (opcional)
        """
        if not self.feedback_loop:
            return
        
        try:
            # TODO: Atualizar feedback entry existente ou criar nova
            logger.info(f"📝 Explicit feedback recorded: {feedback_value} for {interaction_id}")
        except Exception as e:
            logger.error(f"❌ Failed to record explicit feedback: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status de todos os sistemas de aprendizado"""
        status = {
            'enabled': self.enabled,
            'initialized': self.is_initialized,
            'components': self.components_status.copy()
        }
        
        # Additional stats
        if self.continual_learner:
            status['training_cycles'] = self.continual_learner.training_cycles
        
        if self.feedback_loop:
            try:
                status['total_feedback'] = self.feedback_loop.count_pending() if hasattr(self.feedback_loop, 'count_pending') else 0
            except:
                status['total_feedback'] = 0
        
        return status
    
    def _print_status(self):
        """Imprime status formatado dos sistemas"""
        print("\n" + "="*70)
        print("🧠 JARVIS LEARNING ENGINE - STATUS REPORT")
        print("="*70)
        
        for component, active in self.components_status.items():
            status_icon = "✅" if active else "❌"
            component_name = component.replace('_', ' ').title()
            print(f"  {status_icon} {component_name}: {'ONLINE' if active else 'OFFLINE'}")
        
        print("="*70)
        print("💡 JARVIS is now in CONTINUOUS EVOLUTION MODE!")
        print("   Every interaction will improve the neural model.")
        print("="*70 + "\n")
    
    def shutdown(self):
        """Encerra todos os sistemas de aprendizado de forma segura"""
        logger.info("🔄 Shutting down Learning Engine...")
        
        if self.continual_learner:
            self.continual_learner.is_running = False
        
        if self.dream_cycle:
            self.dream_cycle.stop()
        
        logger.info("✅ Learning Engine shutdown complete")


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================
_learning_engine: Optional[LearningEngine] = None

def get_learning_engine(project_root: Path = None) -> Optional[LearningEngine]:
    """
    Obtém instância singleton do Learning Engine.
    
    Args:
        project_root: Diretório raiz do projeto (necessário na primeira chamada)
    
    Returns:
        Instância do LearningEngine ou None se não inicializado
    """
    global _learning_engine
    
    if _learning_engine is None and project_root:
        _learning_engine = LearningEngine(project_root)
    
    return _learning_engine

def initialize_learning_systems(project_root: Path) -> bool:
    """
    Inicializa todos os sistemas de aprendizado.
    Esta é a função principal a ser chamada pelo launcher.
    
    Args:
        project_root: Diretório raiz do projeto
    
    Returns:
        True se inicialização bem-sucedida
    """
    engine = get_learning_engine(project_root)
    
    if engine:
        return engine.initialize()
    
    return False
